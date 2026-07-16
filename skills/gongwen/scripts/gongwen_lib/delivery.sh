DELIVERY_ACTIVE=false
DELIVERY_MUTATION_STARTED=false
DELIVERY_HISTORY_SEQUENCE=""
DELIVERY_ROOT=""
DELIVERY_STEM=""
DELIVERY_WORK=""
DELIVERY_LOCK=""
DELIVERY_RUN=""
DELIVERY_CANDIDATE=""
DELIVERY_ROLLBACK=""
DELIVERY_EVIDENCE=""
DELIVERY_RESULT=""
DELIVERY_CURRENT_NAMES=()
DELIVERY_CANDIDATE_NAMES=()
DELIVERY_OLD_NAMES=()
DELIVERY_POSSIBLE_NAMES=()
DELIVERY_SAFE_HELPER="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/gongwen_safe_delivery.py"

delivery_device() {
  stat -f '%d' "$1" 2>/dev/null || stat -c '%d' "$1"
}

delivery_validate_output_path() {
  local raw="$1" suffix="$2" option="$3" parent base stem
  [[ -n "$raw" ]] || die "$option requires a path"
  case "/$raw/" in
    *'/../'*|*'/./'*) die "$option contains an unsafe path component" ;;
  esac
  [[ "$raw" != *'\\'* ]] || die "$option contains an unsafe path component"
  base="${raw##*/}"
  [[ "$base" == *"$suffix" ]] || die "$option must end with $suffix"
  stem="${base%"$suffix"}"
  [[ -n "$stem" && "$stem" != "." && "$stem" != ".." && "$stem" != .* ]] || die "$option must use one safe filename stem"
  parent="${raw%/*}"
  [[ "$parent" != "$raw" ]] || parent="."
  [[ -d "$parent" && ! -L "$parent" ]] || die "$option parent must be a real existing directory"
  parent="$(cd "$parent" && pwd -P)"
  DELIVERY_VALIDATED_ROOT="$parent"
  DELIVERY_VALIDATED_STEM="$stem"
  DELIVERY_VALIDATED_PATH="$parent/$base"
}

delivery_is_regular_nonempty() {
  [[ -f "$1" && ! -L "$1" && -s "$1" ]]
}

delivery_same_file() {
  if command -v cmp >/dev/null 2>&1; then
    cmp -s "$1" "$2"
  else
    same_file_shell "$1" "$2"
  fi
}

delivery_directory_empty() {
  [[ -d "$1" && -z "$(ls -A "$1" 2>/dev/null)" ]]
}

delivery_validate_support_directory() {
  local path="$1"
  [[ ! -e "$path" && ! -L "$path" ]] && return 0
  [[ -d "$path" && ! -L "$path" ]] || die "support entry must be a real directory: ${path##*/}"
}

delivery_validate_history_entry() {
  local directory="$1" names=() entry base
  [[ -d "$directory" && ! -L "$directory" ]] || die "history entry must be a real directory: ${directory##*/}"
  for entry in "$directory"/* "$directory"/.[!.]* "$directory"/..?*; do
    [[ -e "$entry" || -L "$entry" ]] || continue
    base="${entry##*/}"
    case "$base" in
      "$DELIVERY_STEM.md"|"$DELIVERY_STEM.typ"|"$DELIVERY_STEM.pdf") ;;
      *) die "history entry has an invalid managed set: ${directory##*/}" ;;
    esac
    delivery_is_regular_nonempty "$entry" || die "history artifact must be a regular non-empty file: ${directory##*/}/$base"
    names+=("$base")
  done
  if (( ${#names[@]} == 2 )); then
    [[ " ${names[*]} " == *" $DELIVERY_STEM.md "* && " ${names[*]} " == *" $DELIVERY_STEM.typ "* ]] || die "history entry has an invalid managed set: ${directory##*/}"
  elif (( ${#names[@]} == 3 )); then
    [[ " ${names[*]} " == *" $DELIVERY_STEM.md "* && " ${names[*]} " == *" $DELIVERY_STEM.typ "* && " ${names[*]} " == *" $DELIVERY_STEM.pdf "* ]] || die "history entry has an invalid managed set: ${directory##*/}"
  else
    die "history entry has an invalid managed set: ${directory##*/}"
  fi
}

delivery_inspect_history() {
  local history="$DELIVERY_ROOT/history" entry base
  [[ ! -e "$history" && ! -L "$history" ]] && return 0
  delivery_validate_support_directory "$history"
  for entry in "$history"/* "$history"/.[!.]* "$history"/..?*; do
    [[ -e "$entry" || -L "$entry" ]] || continue
    base="${entry##*/}"
    [[ "$base" =~ ^[0-9]{3,}$ ]] || die "invalid history entry: $base"
    delivery_validate_history_entry "$entry"
  done
}

delivery_discover_current() {
  local md="$DELIVERY_ROOT/$DELIVERY_STEM.md" typ="$DELIVERY_ROOT/$DELIVERY_STEM.typ" pdf="$DELIVERY_ROOT/$DELIVERY_STEM.pdf"
  DELIVERY_CURRENT_NAMES=()
  [[ -e "$md" || -L "$md" ]] && DELIVERY_CURRENT_NAMES+=("$DELIVERY_STEM.md")
  [[ -e "$typ" || -L "$typ" ]] && DELIVERY_CURRENT_NAMES+=("$DELIVERY_STEM.typ")
  [[ -e "$pdf" || -L "$pdf" ]] && DELIVERY_CURRENT_NAMES+=("$DELIVERY_STEM.pdf")
  case "${#DELIVERY_CURRENT_NAMES[@]}:${DELIVERY_CURRENT_NAMES[*]-}" in
    0:|1:"$DELIVERY_STEM.md"|2:"$DELIVERY_STEM.md $DELIVERY_STEM.typ"|3:"$DELIVERY_STEM.md $DELIVERY_STEM.typ $DELIVERY_STEM.pdf") ;;
    *) die "current delivery is a partial gongwen bundle" ;;
  esac
  local name
  if (( ${#DELIVERY_CURRENT_NAMES[@]} > 0 )); then
    for name in "${DELIVERY_CURRENT_NAMES[@]}"; do
      delivery_is_regular_nonempty "$DELIVERY_ROOT/$name" || die "current artifact must be a regular non-empty file: $name"
    done
  fi
}

delivery_inspect_root() {
  local allow_owned_work="$1" entry base
  [[ -d "$DELIVERY_ROOT" && ! -L "$DELIVERY_ROOT" ]] || die "delivery root must be a real directory"
  for entry in "$DELIVERY_ROOT"/* "$DELIVERY_ROOT"/.[!.]* "$DELIVERY_ROOT"/..?*; do
    [[ -e "$entry" || -L "$entry" ]] || continue
    base="${entry##*/}"
    case "$base" in
      "$DELIVERY_STEM.md"|"$DELIVERY_STEM.typ"|"$DELIVERY_STEM.pdf") ;;
      sources|assets|history) delivery_validate_support_directory "$entry" ;;
      .work)
        delivery_validate_support_directory "$entry"
        if [[ "$allow_owned_work" != true ]] && ! delivery_directory_empty "$entry"; then
          die "stale or concurrent .work content requires audit"
        fi
        ;;
      *) die "unknown delivery-root entry: $base" ;;
    esac
  done
  delivery_discover_current
  delivery_inspect_history
}

delivery_next_history_sequence() {
  local max=0 entry base number history="$DELIVERY_ROOT/history"
  if [[ -d "$history" ]]; then
    for entry in "$history"/*; do
      [[ -e "$entry" || -L "$entry" ]] || continue
      base="${entry##*/}"
      [[ "$base" =~ ^[0-9]{3,}$ ]] || die "invalid history entry: $base"
      number=$((10#$base))
      (( number > max )) && max="$number"
    done
  fi
  printf '%03d' "$((max + 1))"
}

delivery_fault() {
  local name="$1"
  if [[ "${PRESTO_CLEAN_DELIVERY_SIGNAL:-}" != "" && "$name" == after_publish_file_1 ]]; then
    case "$PRESTO_CLEAN_DELIVERY_SIGNAL" in
      INT) kill -INT "$$" ;;
      TERM) kill -TERM "$$" ;;
      *) die "invalid delivery signal injection" ;;
    esac
  fi
  if [[ "${PRESTO_CLEAN_DELIVERY_FAULT:-}" == "$name" ]]; then
    die "injected delivery fault: $name"
  fi
}

delivery_remove_owned_run() {
  local name
  for name in "${DELIVERY_POSSIBLE_NAMES[@]}"; do
    [[ -n "$DELIVERY_CANDIDATE" ]] && rm -f -- "$DELIVERY_CANDIDATE/$name"
    [[ -n "$DELIVERY_ROLLBACK" ]] && rm -f -- "$DELIVERY_ROLLBACK/$name"
  done
  [[ -n "$DELIVERY_EVIDENCE" ]] && rmdir "$DELIVERY_EVIDENCE" 2>/dev/null || true
  [[ -n "$DELIVERY_CANDIDATE" ]] && rmdir "$DELIVERY_CANDIDATE" 2>/dev/null || true
  [[ -n "$DELIVERY_ROLLBACK" ]] && rmdir "$DELIVERY_ROLLBACK" 2>/dev/null || true
  [[ -n "$DELIVERY_RUN" ]] && rmdir "$DELIVERY_RUN" 2>/dev/null || true
}

delivery_remove_owned_history() {
  local name directory
  [[ -n "$DELIVERY_HISTORY_SEQUENCE" ]] || return 0
  directory="$DELIVERY_ROOT/history/$DELIVERY_HISTORY_SEQUENCE"
  for name in "${DELIVERY_POSSIBLE_NAMES[@]}"; do
    rm -f -- "$directory/$name"
  done
  rmdir "$directory" 2>/dev/null || true
  rmdir "$DELIVERY_ROOT/history" 2>/dev/null || true
  DELIVERY_HISTORY_SEQUENCE=""
}

delivery_cleanup_lock() {
  [[ -n "$DELIVERY_LOCK" ]] && rmdir "$DELIVERY_LOCK" 2>/dev/null || true
  [[ -n "$DELIVERY_WORK" ]] && rmdir "$DELIVERY_WORK" 2>/dev/null || true
}

delivery_abort() {
  [[ "$DELIVERY_ACTIVE" == true ]] || return 0
  set +e
  python3 "$DELIVERY_SAFE_HELPER" cleanup "$DELIVERY_ROOT" "${DELIVERY_RUN##*/}" >/dev/null 2>&1
  DELIVERY_ACTIVE=false
  set -e
}

delivery_exit_trap() {
  local status="$1"
  if [[ "$DELIVERY_ACTIVE" == true ]]; then
    delivery_abort
  fi
  return "$status"
}

delivery_signal_trap() {
  local signal_name="$1" status=130
  [[ "$signal_name" == TERM ]] && status=143
  delivery_abort
  trap - INT TERM EXIT
  exit "$status"
}

delivery_begin() {
  local typ="$1" pdf="$2" typ_root typ_stem pdf_root pdf_stem work_created=false
  delivery_validate_output_path "$typ" ".typ" "--typ"
  typ_root="$DELIVERY_VALIDATED_ROOT"
  typ_stem="$DELIVERY_VALIDATED_STEM"
  if [[ -n "$pdf" ]]; then
    delivery_validate_output_path "$pdf" ".pdf" "--pdf"
    pdf_root="$DELIVERY_VALIDATED_ROOT"
    pdf_stem="$DELIVERY_VALIDATED_STEM"
    [[ "$pdf_root" == "$typ_root" && "$pdf_stem" == "$typ_stem" ]] || die "--pdf must use the same delivery root and stem as --typ"
  fi
  DELIVERY_ROOT="$typ_root"
  DELIVERY_STEM="$typ_stem"
  DELIVERY_POSSIBLE_NAMES=("$DELIVERY_STEM.md" "$DELIVERY_STEM.typ" "$DELIVERY_STEM.pdf")
  DELIVERY_CANDIDATE_NAMES=("$DELIVERY_STEM.md" "$DELIVERY_STEM.typ")
  [[ -n "$pdf" ]] && DELIVERY_CANDIDATE_NAMES+=("$DELIVERY_STEM.pdf")
  DELIVERY_WORK="$DELIVERY_ROOT/.work"
  DELIVERY_LOCK="$DELIVERY_WORK/lock"
  DELIVERY_RUN="$DELIVERY_WORK/run-$$-${RANDOM:-0}"
  DELIVERY_CANDIDATE="$DELIVERY_RUN/candidate"
  DELIVERY_ROLLBACK="$DELIVERY_RUN/rollback"
  DELIVERY_EVIDENCE="$DELIVERY_RUN/evidence"
  DELIVERY_OLD_NAMES=()
  DELIVERY_HISTORY_SEQUENCE=""
  DELIVERY_MUTATION_STARTED=false
  delivery_inspect_root false
  if [[ ! -d "$DELIVERY_WORK" ]]; then
    mkdir -m 700 "$DELIVERY_WORK"
    work_created=true
  fi
  [[ "$(delivery_device "$DELIVERY_ROOT")" == "$(delivery_device "$DELIVERY_WORK")" ]] || die "delivery root and .work must use the same device"
  if ! mkdir -m 700 "$DELIVERY_LOCK" 2>/dev/null; then
    [[ "$work_created" == true ]] && rmdir "$DELIVERY_WORK" 2>/dev/null || true
    die "another delivery session holds the lock"
  fi
  mkdir -m 700 "$DELIVERY_RUN" "$DELIVERY_CANDIDATE" "$DELIVERY_ROLLBACK" "$DELIVERY_EVIDENCE"
  DELIVERY_ACTIVE=true
  trap 'delivery_exit_trap "$?"' EXIT
  trap 'delivery_signal_trap INT' INT
  trap 'delivery_signal_trap TERM' TERM
}

delivery_validate_candidate() {
  local name entry base
  for name in "${DELIVERY_CANDIDATE_NAMES[@]}"; do
    delivery_is_regular_nonempty "$DELIVERY_CANDIDATE/$name" || die "candidate artifact must be a regular non-empty file: $name"
    case "$name" in
      *.md|*.typ) LC_ALL=C command grep -q '[^[:space:]]' "$DELIVERY_CANDIDATE/$name" || die "candidate text artifact is empty: $name" ;;
      *.pdf) [[ "$(head -c 5 "$DELIVERY_CANDIDATE/$name")" == "%PDF-" ]] || die "candidate PDF has an invalid header" ;;
    esac
  done
  for entry in "$DELIVERY_CANDIDATE"/* "$DELIVERY_CANDIDATE"/.[!.]* "$DELIVERY_CANDIDATE"/..?*; do
    [[ -e "$entry" || -L "$entry" ]] || continue
    base="${entry##*/}"
    [[ " ${DELIVERY_CANDIDATE_NAMES[*]} " == *" $base "* ]] || die "candidate contains an unknown file: $base"
  done
}

delivery_sets_identical() {
  local name
  (( ${#DELIVERY_CURRENT_NAMES[@]} == ${#DELIVERY_CANDIDATE_NAMES[@]} )) || return 1
  [[ "${DELIVERY_CURRENT_NAMES[*]-}" == "${DELIVERY_CANDIDATE_NAMES[*]}" ]] || return 1
  for name in "${DELIVERY_CANDIDATE_NAMES[@]}"; do
    delivery_same_file "$DELIVERY_ROOT/$name" "$DELIVERY_CANDIDATE/$name" || return 1
  done
  return 0
}

delivery_verify_published() {
  local name
  delivery_inspect_root true
  [[ "${DELIVERY_CURRENT_NAMES[*]-}" == "${DELIVERY_CANDIDATE_NAMES[*]}" ]] || die "published root does not match the exact managed set"
  for name in "${DELIVERY_CANDIDATE_NAMES[@]}"; do
    delivery_is_regular_nonempty "$DELIVERY_ROOT/$name" || die "published artifact is invalid: $name"
    [[ "$name" != *.pdf || "$(head -c 5 "$DELIVERY_ROOT/$name")" == "%PDF-" ]] || die "published PDF has an invalid header"
  done
}

delivery_finish_success() {
  delivery_remove_owned_run
  delivery_cleanup_lock
  DELIVERY_ACTIVE=false
  trap - INT TERM EXIT
}

delivery_publish() {
  local result
  delivery_validate_candidate
  if [[ -n "${PRESTO_CLEAN_DELIVERY_LOCK_HOLD_SECONDS:-}" ]]; then
    sleep "$PRESTO_CLEAN_DELIVERY_LOCK_HOLD_SECONDS"
  fi
  result="$(python3 "$DELIVERY_SAFE_HELPER" publish "$DELIVERY_ROOT" "${DELIVERY_RUN##*/}" "$DELIVERY_STEM" "${#DELIVERY_CANDIDATE_NAMES[@]}")"
  DELIVERY_RESULT="$result"
  DELIVERY_ACTIVE=false
  trap - INT TERM EXIT
}
