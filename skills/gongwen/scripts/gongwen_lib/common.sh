die() {
  printf 'gongwen.sh: %s\n' "$*" >&2
  exit 1
}

need_file() {
  [[ -f "$1" ]] || die "file not found: $1"
}

ensure_parent_dir() {
  local path="$1" parent
  parent="${path%/*}"
  if [[ "$parent" != "$path" && -n "$parent" && ! -d "$parent" ]]; then
    die "parent directory does not exist: $parent"
  fi
}

trim() {
  local s="$1"
  s="${s#"${s%%[![:space:]]*}"}"
  s="${s%"${s##*[![:space:]]}"}"
  printf '%s' "$s"
}

strip_quotes() {
  local s
  s="$(trim "$1")"
  if [[ "$s" == \"*\" && "$s" == *\" ]]; then
    s="${s#\"}"
    s="${s%\"}"
  elif [[ "$s" == \'*\' && "$s" == *\' ]]; then
    s="${s#\'}"
    s="${s%\'}"
  fi
  printf '%s' "$s"
}

today() {
  printf '1970-01-01'
}

copy_file_shell() {
  local src="$1" dst="$2" line
  : > "$dst"
  while IFS= read -r line || [[ -n "$line" ]]; do
    printf '%s\n' "$line" >> "$dst"
  done < "$src"
}

same_file_shell() {
  local a="$1" b="$2" left right
  exec 3< "$a"
  exec 4< "$b"
  while true; do
    IFS= read -r left <&3; local ls=$?
    IFS= read -r right <&4; local rs=$?
    if [[ "$ls" -ne "$rs" ]]; then exec 3<&-; exec 4<&-; return 1; fi
    if [[ "$ls" -ne 0 ]]; then exec 3<&-; exec 4<&-; return 0; fi
    if [[ "$left" != "$right" ]]; then exec 3<&-; exec 4<&-; return 1; fi
  done
}
