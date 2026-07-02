FM_TITLE="请输入文字"
FM_AUTHOR="请输入文字"
FM_DATE=""
FM_SIGNATURE="false"
FM_TEMPLATE=""
BODY_LINES=()

parse_input() {
  local input="$1" line first=true in_fm=false in_author=false item
  BODY_LINES=()
  FM_TITLE="请输入文字"
  FM_AUTHOR=""
  FM_DATE=""
  FM_SIGNATURE=""
  FM_TEMPLATE=""

  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%$'\r'}"
    if [[ "$first" == true ]]; then
      first=false
      if [[ "$line" == "---" ]]; then
        in_fm=true
        continue
      fi
    fi

    if [[ "$in_fm" == true ]]; then
      if [[ "$line" == "---" ]]; then
        in_fm=false
        in_author=false
        continue
      fi
      if [[ "$line" =~ ^title:[[:space:]]*(.*)$ ]]; then
        FM_TITLE="$(strip_quotes "${BASH_REMATCH[1]}")"
        in_author=false
      elif [[ "$line" =~ ^date:[[:space:]]*(.*)$ ]]; then
        FM_DATE="$(strip_quotes "${BASH_REMATCH[1]}")"
        in_author=false
      elif [[ "$line" =~ ^signature:[[:space:]]*(.*)$ ]]; then
        FM_SIGNATURE="$(strip_quotes "${BASH_REMATCH[1]}")"
        in_author=false
      elif [[ "$line" =~ ^template:[[:space:]]*(.*)$ ]]; then
        FM_TEMPLATE="$(strip_quotes "${BASH_REMATCH[1]}")"
        in_author=false
      elif [[ "$line" =~ ^author:[[:space:]]*(.*)$ ]]; then
        in_author=true
        item="$(strip_quotes "${BASH_REMATCH[1]}")"
        if [[ -n "$item" ]]; then
          FM_AUTHOR="$item"
          in_author=false
        else
          FM_AUTHOR=""
        fi
      elif [[ "$in_author" == true && "$line" =~ ^[[:space:]]*-[[:space:]]*(.*)$ ]]; then
        item="$(strip_quotes "${BASH_REMATCH[1]}")"
        if [[ -z "$FM_AUTHOR" ]]; then
          FM_AUTHOR="$item"
        else
          FM_AUTHOR="${FM_AUTHOR}、${item}"
        fi
      fi
    else
      BODY_LINES+=("$line")
    fi
  done < "$input"
}

validate_frontmatter() {
  [[ -n "$FM_AUTHOR" ]] || die "frontmatter requires author"
  [[ -n "$FM_DATE" ]] || die "frontmatter requires date"
  [[ -n "$FM_SIGNATURE" ]] || die "frontmatter requires signature"
  [[ "$FM_TEMPLATE" == "gongwen" ]] || die "frontmatter template must be gongwen"
  [[ "$FM_DATE" =~ ^[0-9][0-9][0-9][0-9]-[0-9][0-9]?-[0-9][0-9]?$ ]] || die "frontmatter date must use YYYY-MM-DD"
  case "$FM_SIGNATURE" in
    true|false|yes|no) ;;
    *) die "frontmatter signature must be true or false" ;;
  esac
}
