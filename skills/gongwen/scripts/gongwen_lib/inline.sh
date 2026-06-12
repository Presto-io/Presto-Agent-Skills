escape_string() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  printf '%s' "$s"
}

escape_content() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\[/\\[}"
  s="${s//\]/\\]}"
  s="${s//#/\\#}"
  s="${s//\$/\\$}"
  s="${s//%/\\%}"
  s="${s//&/\\&}"
  printf '%s' "$s"
}

convert_punctuation() {
  local s="$1"
  s="${s//,/，}"
  s="${s//;/；}"
  s="${s//\?/？}"
  s="${s//\(/（}"
  s="${s//\)/）}"
  s="${s//:/：}"
  printf '%s' "$s"
}

render_plain_segment() {
  local s="$1" part
  while [[ "$s" == *"<br>"* ]]; do
    part="${s%%<br>*}"
    escape_content "$(convert_punctuation "$part")"
    printf '#linebreak()'
    s="${s#*<br>}"
  done
  escape_content "$(convert_punctuation "$s")"
}

render_inline() {
  local s="$1" before strong
  while [[ "$s" == *"**"* ]]; do
    before="${s%%\*\**}"
    s="${s#*\*\*}"
    if [[ "$s" != *"**"* ]]; then
      render_plain_segment "$before"
      printf '**'
      render_plain_segment "$s"
      return
    fi
    strong="${s%%\*\**}"
    s="${s#*\*\*}"
    render_plain_segment "$before"
    printf '#strong['
    render_plain_segment "$strong"
    printf ']'
  done
  render_plain_segment "$s"
}
