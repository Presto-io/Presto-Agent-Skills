marker_block() {
  local text
  text="$(trim "$1")"
  case "$text" in
    "{v}"|"{.br}"|"{.blank}") printf '#linebreak(justify: false)\n'; return 0 ;;
    "{pagebreak}"|"{.pagebreak}") printf '#pagebreak()\n'; return 0 ;;
    "{pagebreak:weak}"|"{.pagebreak:weak}") printf '#pagebreak(weak: true)\n'; return 0 ;;
  esac
  if [[ "$text" =~ ^\{v:([0-9]+)\}$ ]]; then
    local count="${BASH_REMATCH[1]}"
    for ((; count > 0; count--)); do
      printf '#linebreak(justify: false)\n'
    done
    return 0
  fi
  if [[ "$text" =~ ^\{\.(br|blank):([0-9]+)\}$ ]]; then
    local count="${BASH_REMATCH[2]}"
    for ((; count > 0; count--)); do
      printf '#linebreak(justify: false)\n'
    done
    return 0
  fi
  return 1
}

strip_trailing_markers() {
  local s
  s="$(trim "$1")"
  STRIPPED_TEXT="$s"
  MARKER_NOINDENT=false
  MARKER_INDENT=false
  MARKER_BOLD=false
  while true; do
    case "$STRIPPED_TEXT" in
      *"{.noindent}") MARKER_NOINDENT=true; STRIPPED_TEXT="$(trim "${STRIPPED_TEXT%"{.noindent}"}")" ;;
      *"{.indent}") MARKER_INDENT=true; STRIPPED_TEXT="$(trim "${STRIPPED_TEXT%"{.indent}"}")" ;;
      *"{indent}") MARKER_INDENT=true; STRIPPED_TEXT="$(trim "${STRIPPED_TEXT%"{indent}"}")" ;;
      *"{.bold}") MARKER_BOLD=true; STRIPPED_TEXT="$(trim "${STRIPPED_TEXT%"{.bold}"}")" ;;
      *) break ;;
    esac
  done
}

normalize_heading_text() {
  local s="$1" before
  s="$(trim "$s")"
  while true; do
    before="$s"
    if [[ "$s" =~ ^[一二三四五六七八九十百千万零〇两壹贰叁肆伍陆柒捌玖拾佰仟]+[、.．][[:space:]]*(.+)$ ]]; then
      s="$(trim "${BASH_REMATCH[1]}")"
    elif [[ "$s" =~ ^（[一二三四五六七八九十百千万零〇两壹贰叁肆伍陆柒捌玖拾佰仟]+）[[:space:]]*(.+)$ ]]; then
      s="$(trim "${BASH_REMATCH[1]}")"
    elif [[ "$s" =~ ^\([一二三四五六七八九十百千万零〇两壹贰叁肆伍陆柒捌玖拾佰仟]+\)[[:space:]]*(.+)$ ]]; then
      s="$(trim "${BASH_REMATCH[1]}")"
    elif [[ "$s" =~ ^[0-9]+([.．][0-9]+)+[、.．]?[[:space:]]*(.+)$ ]]; then
      s="$(trim "${BASH_REMATCH[2]}")"
    elif [[ "$s" =~ ^[0-9]+[、.．][[:space:]]*(.+)$ ]]; then
      s="$(trim "${BASH_REMATCH[1]}")"
    elif [[ "$s" =~ ^[（\(][0-9]+[）\)][[:space:]]*(.+)$ ]]; then
      s="$(trim "${BASH_REMATCH[1]}")"
    fi
    [[ "$s" != "$before" ]] || break
  done
  NORMALIZED_HEADING_TEXT="$s"
}

emit_paragraph() {
  local text="$1" noindent="${2:-false}" rendered
  strip_trailing_markers "$text"
  text="$STRIPPED_TEXT"
  [[ "$MARKER_NOINDENT" == true ]] && noindent=true
  rendered="$(render_inline "$text")"
  if [[ "$noindent" == true ]]; then
    printf '#block[#set par(first-line-indent: 0pt)\n#block[\n%s\n\n]\n]\n' "$rendered"
  else
    printf '%s\n\n' "$rendered"
  fi
}

emit_heading() {
  local level="$1" text="$2" prefix i
  strip_trailing_markers "$text"
  text="$STRIPPED_TEXT"
  normalize_heading_text "$text"
  text="$NORMALIZED_HEADING_TEXT"
  if [[ "$MARKER_BOLD" == true && "$level" -ge 2 && "$level" -le 5 ]]; then
    printf '#custom-heading-block(%s, [' "$level"
    render_inline "$text"
    printf '], bold: true)\n\n'
    return
  fi
  prefix=""
  for ((i = 0; i < level; i++)); do prefix+="="; done
  printf '%s ' "$prefix"
  render_inline "$text"
  printf '\n\n'
}

emit_runin_heading() {
  local level="$1" heading="$2" para="$3"
  strip_trailing_markers "$heading"
  heading="$STRIPPED_TEXT"
  normalize_heading_text "$heading"
  heading="$NORMALIZED_HEADING_TEXT"
  printf '#custom-heading(%s, [' "$level"
  render_inline "$heading"
  printf '], bold: %s)' "$MARKER_BOLD"
  render_inline "$para"
  printf '\n\n'
}

is_plain_following_paragraph() {
  local line
  line="$(trim "$1")"
  [[ -n "$line" ]] || return 1
  case "$line" in
    "#"*|"|"*|">"*|"- "*|"!"*|"\`\`\`"*) return 1 ;;
  esac
  [[ "$line" =~ ^[0-9]+\. ]] && return 1
  return 0
}

emit_code_block() {
  local lang="$1" code="$2"
  if [[ -n "$lang" ]]; then
    printf '#code-block[```%s\n%s```]\n\n' "$lang" "$code"
  else
    printf '#code-block[```\n%s```]\n\n' "$code"
  fi
}

render_body() {
  local total="${#BODY_LINES[@]}" i=0 line next next2 noindent=false in_comment=false code lang rows caption j last_list_kind="" marker_output canonical_title
  HAS_SEEN_HEADER=false
  TABLE_COUNTER=0
  FIGURE_COUNTER=0
  while (( i < total )); do
    line="${BODY_LINES[$i]}"
    if [[ "$in_comment" == true ]]; then
      [[ "$line" == *"-->"* ]] && in_comment=false
      ((i++)); continue
    fi
    if [[ "$line" == *"<!--"* ]]; then
      [[ "$line" != *"-->"* ]] && in_comment=true
      ((i++)); continue
    fi
    if [[ -z "$(trim "$line")" ]]; then ((i++)); continue; fi
    if [[ "$line" == '::: {.noindent}' ]]; then noindent=true; ((i++)); continue; fi
    if [[ "$line" == ":::" ]]; then noindent=false; ((i++)); continue; fi
    if marker_output="$(marker_block "$line")"; then
      [[ -n "$last_list_kind" ]] && printf '\n'
      printf '%s\n' "$marker_output"
      last_list_kind=""
      ((i++))
      continue
    fi

    if [[ "$line" =~ ^\`\`\`(.*)$ ]]; then
      lang="$(trim "${BASH_REMATCH[1]}")"
      code=""
      ((i++))
      while (( i < total )) && [[ ! "${BODY_LINES[$i]}" =~ ^\`\`\` ]]; do
        code+="${BODY_LINES[$i]}"$'\n'
        ((i++))
      done
      ((i++))
      emit_code_block "$lang" "$code"
      last_list_kind=""
      continue
    fi

    if [[ "$line" =~ ^#[[:space:]]+(.*)$ ]]; then
      normalize_heading_text "${BASH_REMATCH[1]}"
      local heading_title="$NORMALIZED_HEADING_TEXT"
      canonical_title="${FM_TITLE//|/ }"
      normalize_heading_text "$canonical_title"
      if [[ "$heading_title" == "$NORMALIZED_HEADING_TEXT" ]]; then
        ((i++))
        continue
      fi
    fi

    if [[ "$line" =~ ^(#{2,5})[[:space:]]+(.*)$ ]]; then
      HAS_SEEN_HEADER=true
      local level="${#BASH_REMATCH[1]}" heading="${BASH_REMATCH[2]}"
      j=$((i + 1))
      if (( j < total )) && is_plain_following_paragraph "${BODY_LINES[$j]}"; then
        emit_runin_heading "$level" "$heading" "${BODY_LINES[$j]}"
        i=$((j + 1))
      else
        emit_heading "$level" "$heading"
        ((i++))
      fi
      last_list_kind=""
      continue
    fi

    if [[ "$line" =~ ^[[:space:]]*\|.*\|[[:space:]]*$ ]]; then
      rows=()
      while (( i < total )) && [[ "${BODY_LINES[$i]}" =~ ^[[:space:]]*\|.*\|[[:space:]]*$ ]]; do
        rows+=("${BODY_LINES[$i]}")
        ((i++))
      done
      j="$i"
      while (( j < total )) && [[ -z "$(trim "${BODY_LINES[$j]}")" ]]; do ((j++)); done
      caption=""
      if (( j < total )) && [[ "${BODY_LINES[$j]}" =~ ^:[[:space:]]*(.*)$ ]]; then
        caption="${BASH_REMATCH[1]}"
        i=$((j + 1))
      fi
      emit_table "$caption" "${rows[@]}"
      last_list_kind=""
      continue
    fi

    if [[ "$line" == *"!["* ]]; then
      parse_images_in_line "$line"
      if (( ${#IMAGE_PATHS[@]} == 1 )); then
        ((FIGURE_COUNTER++))
        emit_single_image "${IMAGE_PATHS[0]}" "$FIGURE_COUNTER"
      elif (( ${#IMAGE_PATHS[@]} > 1 )); then
        ((FIGURE_COUNTER++))
        emit_multi_image
      fi
      last_list_kind=""
      ((i++)); continue
    fi

    if [[ "$line" =~ ^([[:space:]]*)[0-9]+\.[[:space:]]+(.*)$ ]]; then
      [[ "$last_list_kind" == "ul" ]] && printf '\n\n'
      printf '%s+ ' "${BASH_REMATCH[1]}"
      render_inline "${BASH_REMATCH[2]}"
      printf '\n'
      last_list_kind="ol"
      ((i++)); continue
    fi

    if [[ "$line" =~ ^([[:space:]]*)-[[:space:]]+(.*)$ ]]; then
      printf '%s- ' "${BASH_REMATCH[1]}"
      render_inline "${BASH_REMATCH[2]}"
      printf '\n'
      last_list_kind="ul"
      ((i++)); continue
    fi

    if [[ "$line" =~ ^\>[[:space:]]?(.*)$ ]]; then
      printf '#quote['
      render_inline "${BASH_REMATCH[1]}"
      printf ']\n\n'
      last_list_kind=""
      ((i++)); continue
    fi

    if [[ "$HAS_SEEN_HEADER" == false ]]; then
      local rendered
      rendered="$(render_inline "$line")"
      if [[ "$rendered" == *"：" || "$rendered" == *":" ]]; then
        printf '#block[#set par(first-line-indent: 0pt)\n#block[\n%s\n\n]\n]\n' "$rendered"
        last_list_kind=""
        ((i++)); continue
      fi
    fi
    emit_paragraph "$line" "$noindent"
    last_list_kind=""
    ((i++))
  done
}

render_signature() {
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'TYP'
#v(18pt)
#block(width: 100%)[
#align(right)[
#box[
  #set align(center)
  #autoAuthor \
  #autoDate.display(
    "[year]年[month padding:none]月[day padding:none]日",
  )
]
]
]
TYP
}

body_line_is_author() {
  local line="$1" authors rest part
  authors="$FM_AUTHOR"
  [[ "$line" == "$authors" ]] && return 0
  rest="$authors"
  while [[ "$rest" == *"、"* ]]; do
    part="${rest%%、*}"
    [[ "$line" == "$part" ]] && return 0
    rest="${rest#*、}"
  done
  [[ "$line" == "$rest" ]] && return 0
  return 1
}

body_line_is_date() {
  local line="$1"
  [[ "$line" =~ ^[0-9][0-9][0-9][0-9]-[0-9][0-9]?-[0-9][0-9]?$ ]] && return 0
  [[ "$line" =~ ^[0-9][0-9][0-9][0-9]年[0-9]{1,2}月[0-9]{1,2}日$ ]] && return 0
  return 1
}

validate_no_manual_signature_block() {
  local idx line checked=0 in_noindent=false block_has_author=false block_has_date=false
  for ((idx = 0; idx < ${#BODY_LINES[@]}; idx++)); do
    line="$(trim "${BODY_LINES[$idx]}")"
    if [[ "$line" == '::: {.noindent}' ]]; then
      in_noindent=true
      block_has_author=false
      block_has_date=false
      continue
    fi
    if [[ "$line" == ":::" ]]; then
      if [[ "$in_noindent" == true && "$block_has_author" == true && "$block_has_date" == true ]]; then
        die "signature:true forbids handwritten author/date/signature lines in body"
      fi
      in_noindent=false
      continue
    fi
    if [[ "$in_noindent" == true ]]; then
      body_line_is_author "$line" && block_has_author=true
      body_line_is_date "$line" && block_has_date=true
    fi
  done

  for ((idx = ${#BODY_LINES[@]} - 1; idx >= 0 && checked < 6; idx--)); do
    line="$(trim "${BODY_LINES[$idx]}")"
    [[ -z "$line" || "$line" == ":::" || "$line" == '::: {.noindent}' ]] && continue
    checked=$((checked + 1))
    if body_line_is_author "$line" || body_line_is_date "$line"; then
      die "signature:true forbids handwritten author/date/signature lines in body"
    fi
  done
}

render_markdown_to_typst() {
  local input="$1" output="$2" body
  parse_input "$input"
  validate_frontmatter
  if [[ "$FM_SIGNATURE" == "true" || "$FM_SIGNATURE" == "yes" ]]; then
    validate_no_manual_signature_block
  fi
  ensure_parent_dir "$output"
  : > "$output"
  {
    emit_auto_meta
    body="$(render_body)"
    if [[ "$FM_SIGNATURE" == "true" || "$FM_SIGNATURE" == "yes" ]]; then
      printf '%s' "$body"
      [[ -n "$body" ]] && printf '\n\n'
      printf '#place.flush()\n'
      printf '#block(sticky: true, width: 100%%)[\n'
      render_signature
      printf ']\n'
    else
      printf '%s' "$body"
    fi
  } >> "$output"
}
