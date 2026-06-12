split_table_row() {
  local row="$1" cell
  TABLE_CELLS=()
  row="$(trim "$row")"
  row="${row#|}"
  row="${row%|}"
  while [[ "$row" == *"|"* ]]; do
    cell="${row%%|*}"
    TABLE_CELLS+=("$(trim "$cell")")
    row="${row#*|}"
  done
  TABLE_CELLS+=("$(trim "$row")")
}

table_delim_aligns() {
  local row="$1" cell
  TABLE_ALIGNS=()
  row="$(trim "$row")"
  row="${row#|}"
  row="${row%|}"
  while [[ "$row" == *"|"* ]]; do
    cell="$(trim "${row%%|*}")"
    table_one_align "$cell"
    row="${row#*|}"
  done
  cell="$(trim "$row")"
  table_one_align "$cell"
}

table_one_align() {
  local cell="$1"
  if [[ "$cell" == :* && "$cell" == *: ]]; then
    TABLE_ALIGNS+=("center")
  elif [[ "$cell" == *":" ]]; then
    TABLE_ALIGNS+=("right")
  else
    TABLE_ALIGNS+=("left")
  fi
}

is_delim_row() {
  local s="$1"
  s="${s//|/}"
  s="${s//:/}"
  s="${s//-/}"
  s="${s// /}"
  [[ -z "$s" ]]
}

cell_content() {
  local text="$1" strong="$2"
  printf 'table.cell(inset: (x: 2pt, y: ((((297mm - 37mm - 35mm) / 22) - zh(3)) / 2)))[#set par(leading: (((297mm - 37mm - 35mm) / 22) - zh(3)), spacing: 0pt, first-line-indent: 0pt)\n'
  if [[ "$strong" == true ]]; then
    printf '#strong['
    render_inline "$text"
    printf ']'
  else
    render_inline "$text"
  fi
  printf ']'
}

estimate_cell_lines() {
  local s="$1" lines=0 part rest="$1" chars
  while [[ "$rest" == *"<br>"* ]]; do
    part="${rest%%<br>*}"
    chars="${#part}"
    (( lines += (chars + 21) / 22 ))
    rest="${rest#*<br>}"
  done
  chars="${#rest}"
  (( lines += (chars + 21) / 22 ))
  (( lines < 1 )) && lines=1
  printf '%s' "$lines"
}

emit_table_cell_lines() {
  local start="$1" idx cell row_idx
  for ((row_idx = start; row_idx < ${#TABLE_EMIT_ROWS[@]}; row_idx++)); do
    split_table_row "${TABLE_EMIT_ROWS[$row_idx]}"
    for cell in "${TABLE_CELLS[@]}"; do
      printf '  '
      cell_content "$cell" false
      printf ',\n'
    done
  done
}

emit_table_measure_cell_lines() {
  local start="$1" cell row_idx
  for ((row_idx = start; row_idx < ${#TABLE_EMIT_ROWS[@]}; row_idx++)); do
    split_table_row "${TABLE_EMIT_ROWS[$row_idx]}"
    for cell in "${TABLE_CELLS[@]}"; do
      printf '      '
      cell_content "$cell" false
      printf ',\n'
    done
  done
}

emit_table() {
  local caption="$1"; shift
  local rows=("$@") max_cols caption_no keep=true estimated=0 row_idx cell_lines max_line cell i
  TABLE_EMIT_ROWS=("${rows[@]}")
  split_table_row "${rows[0]}"
  max_cols="${#TABLE_CELLS[@]}"
  if [[ "${#rows[@]}" -gt 1 ]]; then
    if is_delim_row "${rows[1]}"; then
      table_delim_aligns "${rows[1]}"
    else
      TABLE_ALIGNS=()
      for ((i = 0; i < max_cols; i++)); do TABLE_ALIGNS+=("left"); done
    fi
  else
    TABLE_ALIGNS=()
    for ((i = 0; i < max_cols; i++)); do TABLE_ALIGNS+=("left"); done
  fi
  [[ -n "$caption" ]] && ((TABLE_COUNTER++))
  caption_no="$TABLE_COUNTER"
  estimated=2
  [[ -n "$caption" ]] && (( estimated += 2 ))
  for ((row_idx = 2; row_idx < ${#rows[@]}; row_idx++)); do
    split_table_row "${rows[$row_idx]}"
    max_line=1
    for cell in "${TABLE_CELLS[@]}"; do
      cell_lines="$(estimate_cell_lines "$cell")"
      (( cell_lines > max_line )) && max_line="$cell_lines"
    done
    (( estimated += max_line ))
  done
  (( estimated > 22 )) && keep=false

  if [[ "$keep" == true ]]; then
    printf '#block(breakable: false, width: 100%%)[\n'
    printf '#align(center)[\n#table(\n'
  else
    printf '#context {\n'
    printf '  let table-start-page = here().page()\n'
    printf '  let table-caption-width = calc.max(\n'
    printf '    measure(text(font: FONT_FS, size: zh(3))[表%s#h(1em)' "$caption_no"
    render_inline "$caption"
    printf '（续）]).width,\n'
    printf '    measure(table(\n'
  fi

  printf '  columns: ('
  for ((i = 0; i < max_cols; i++)); do
    (( i > 0 )) && printf ', '
    printf 'auto'
  done
  printf '),\n'
  printf '  align: ('
  for ((i = 0; i < max_cols; i++)); do
    (( i > 0 )) && printf ', '
    printf '%s' "${TABLE_ALIGNS[$i]:-left}"
  done
  printf '),\n'
  if [[ "$keep" == false ]]; then
    printf '      stroke: none,\n'
    split_table_row "${rows[0]}"
    for cell in "${TABLE_CELLS[@]}"; do printf '      '; cell_content "$cell" true; printf ',\n'; done
    emit_table_measure_cell_lines 2
    printf '    )).width,\n'
    printf '  )\n'
    printf '  align(center)[\n  #table(\n'
    printf '  columns: ('
    for ((i = 0; i < max_cols; i++)); do (( i > 0 )) && printf ', '; printf 'auto'; done
    printf '),\n'
    printf '  align: ('
    for ((i = 0; i < max_cols; i++)); do (( i > 0 )) && printf ', '; printf '%s' "${TABLE_ALIGNS[$i]:-left}"; done
    printf '),\n'
  fi
  printf '  stroke: none,\n'
  printf '  table.hline(y: 1, stroke: 0.75pt),\n'
  printf '  table.hline(y: 2, stroke: 0.5pt),\n'
  printf '  table.hline(y: %s, stroke: 0.75pt),\n' "${#rows[@]}"

  split_table_row "${rows[0]}"
  if [[ "$keep" == true ]]; then
    if [[ -n "$caption" ]]; then
      printf '  table.cell(colspan: %s, align: center, stroke: none, inset: 0pt)[#align(center)[#pad(bottom: (((297mm - 37mm - 35mm) / 22) - zh(3)))[#text(font: FONT_FS, size: zh(3))[表%s#h(1em)' "$max_cols" "$caption_no"
      render_inline "$caption"
      printf ']]]],\n'
    fi
    for cell in "${TABLE_CELLS[@]}"; do printf '  '; cell_content "$cell" true; printf ',\n'; done
  else
    printf '  table.header(repeat: true,\n'
    printf '  table.cell(colspan: %s, align: center, stroke: none, inset: 0pt)[#context if here().page() == table-start-page { box(width: table-caption-width)[#align(center)[#pad(bottom: (((297mm - 37mm - 35mm) / 22) - zh(3)))[#text(font: FONT_FS, size: zh(3))[表%s#h(1em)' "$max_cols" "$caption_no"
    render_inline "$caption"
    printf ']]]] } else { box(width: table-caption-width)[#align(center)[#pad(bottom: (((297mm - 37mm - 35mm) / 22) - zh(3)))[#text(font: FONT_FS, size: zh(3))[表%s#h(1em)' "$caption_no"
    render_inline "$caption"
    printf '（续）]]]] }],\n'
    for cell in "${TABLE_CELLS[@]}"; do printf '  '; cell_content "$cell" true; printf ',\n'; done
    printf '  ),\n'
  fi
  emit_table_cell_lines 2
  printf ')\n]\n\n'
  if [[ "$keep" == true ]]; then
    printf ']\n\n'
  else
    printf '}\n\n'
  fi
}
