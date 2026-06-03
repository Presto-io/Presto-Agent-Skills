#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="${BASH_SOURCE[0]%/*}"
if [[ "$SCRIPT_DIR" == "${BASH_SOURCE[0]}" ]]; then
  SCRIPT_DIR="."
fi
SKILL_DIR="${SCRIPT_DIR}/.."
TEMPLATE_MD="${SKILL_DIR}/templates/gongwen-full.md"

usage() {
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'USAGE'
Usage:
  gongwen.sh example --output <gongwen-full.md>
  gongwen.sh render --input <input.md> [--typ <output.typ>]
                    [--expected-typ <reference.typ>]
  gongwen.sh manifest
  gongwen.sh info
  gongwen.sh version

The Markdown-to-Typst conversion is implemented by this Bash script itself. It
does not call the Presto template executable or any external Markdown parser.
USAGE
}

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

format_date() {
  local date="$1"
  if [[ "$date" =~ ^([0-9][0-9][0-9][0-9])-([0-9][0-9]?)-([0-9][0-9]?)$ ]]; then
    local month="${BASH_REMATCH[2]#0}" day="${BASH_REMATCH[3]#0}"
    [[ -n "$month" ]] || month="0"
    [[ -n "$day" ]] || day="0"
    printf 'datetime(\n  year: %s,\n  month: %s,\n  day: %s,\n)\n' "${BASH_REMATCH[1]}" "$month" "$day"
  else
    printf '"%s"' "$(escape_string "$date")"
  fi
}

FM_TITLE="请输入文字"
FM_AUTHOR="请输入文字"
FM_DATE=""
FM_SIGNATURE="false"
BODY_LINES=()

parse_input() {
  local input="$1" line first=true in_fm=false in_author=false item
  BODY_LINES=()
  FM_TITLE="请输入文字"
  FM_AUTHOR="请输入文字"
  FM_DATE="$(today)"
  FM_SIGNATURE="false"

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

emit_template_head() {
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'TYP'
// 中文字号转换函数
#import "@preview/pointless-size:0.1.2": zh

// 定义常用字体名称
#let FONT_XBS = "FZXiaoBiaoSong-B05" // 方正小标宋
#let FONT_HEI = "STHeiti" // 黑体
#let FONT_FS = "STFangsong" // 仿宋
#let FONT_KAI = "STKaiti" // 楷体
#let FONT_SONG = "STSong" // 宋体
#let FONT_CODE = "Noto Sans Mono CJK SC" // 代码块

// 设置页面、页边距、页脚
#set page(
  paper: "a4",
  margin: (
    inside: 28mm,
    outside: 26mm,
    top: 37mm,
    bottom: 35mm,
  ),

  // 将页脚基线放到"版心下边缘之下 7mm"
  footer-descent: 7mm,

  // 使用更稳定的奇偶页判断和页码格式
  footer: context {
    let page-num = here().page()
    let is-even = calc.even(page-num)
    let num = str(page-num)
    let pm = text(font: FONT_SONG, size: zh(4))[— #num —] // 4 号宋体

    if is-even {
      align(left, [#h(1em) #pm]) // 偶数页：居左
    } else {
      align(right, [#pm #h(1em)]) // 奇数页：居右
    }
  },
)

// 设置文档默认语言和正文字体
#set text(
  lang: "zh",
  font: FONT_FS,
  size: zh(3),
  hyphenate: false,
  cjk-latin-spacing: auto,
)

// 设置段落样式，以满足"每行28字符，每页22行"的网格标准，首行缩进2字符
#set par(
  first-line-indent: (amount: 2em, all: true),
  justify: true,
  leading: 15.6pt, // 行间距
  spacing: 15.6pt, // 段间距
)

// 计数器设置
#let h2-counter = counter("h2")
#let h3-counter = counter("h3")
#let h4-counter = counter("h4")
#let h5-counter = counter("h5")

// 图片样式设置
#show figure: it => {
  // 居中对齐，无首行缩进
  set par(first-line-indent: 0pt)
  align(center, block({
    // 图片尺寸由 Lua filter 控制
    it.body

    // 图注样式：3号仿宋，格式为"图1 标题"
    text(
      font: FONT_FS,
      size: zh(3),
      it.caption,
    )
  }))
}

// 自定义标题函数
#let maybe-bold(enabled, body) = if enabled {
  text(weight: "bold", stroke: 0.2pt + black)[#body]
} else {
  body
}

#let custom-heading(level, body, numbering: auto, bold: false) = {
  if level == 1 {
    v(0pt)
    align(center)[
      #text(
        font: FONT_XBS,
        size: zh(2),
        weight: "bold",
      )[
        #set par(leading: 35pt - zh(2))
        #body
      ]
    ]
    v(28.7pt)
  } else if level == 2 {
    h2-counter.step()
    h3-counter.update(0)
    h4-counter.update(1)
    h5-counter.update(1)
    text(
      font: FONT_HEI,
      size: zh(3),
    )[#maybe-bold(bold)[#context h2-counter.display("一、")#body]]
  } else if level == 3 {
    h3-counter.step()
    h4-counter.update(1)
    h5-counter.update(1)

    text(
      font: FONT_KAI,
      size: zh(3),
    )[#maybe-bold(bold)[#context h3-counter.display("（一）")#body]]
  } else if level == 4 {
    h4-counter.step()
    h5-counter.update(1)

    text(
      size: zh(3),
    )[#maybe-bold(bold)[#context h4-counter.display("1.")#body]]
  } else if level == 5 {
    h5-counter.step()

    text(
      size: zh(3),
    )[#maybe-bold(bold)[#context h5-counter.display("（1）")#body]]
  }
}

#let custom-heading-block(level, body, numbering: auto, bold: false) = {
  if level == 1 {
    custom-heading(level, body, numbering: numbering, bold: bold)
  } else {
    let spacing = 13.9pt
    let threshold = 3em

    block(
      sticky: true,
      above: spacing,
      below: spacing,
      {
        block(
          custom-heading(level, body, numbering: numbering, bold: bold) + v(threshold),
          breakable: false,
        )
        v(-threshold)
      },
    )
  }
}

#show heading: it => {
  custom-heading-block(it.level, it.body, numbering: it.numbering)
}

#h2-counter.update(0)
#h3-counter.update(0)
#h4-counter.update(0)
#h5-counter.update(0)

#let list-depth = state("list-depth", 0)

#let flush-left-list(it) = {
  list-depth.update(d => d + 1)

  let is-enum = (it.func() == enum)
  let children = it.children

  context {
    let depth = list-depth.get()
    let block-indent = if depth > 1 { 2em } else { 0pt }

    pad(left: block-indent, block({
      for (count, item) in children.enumerate(start: 1) {
        if item.func() == list.item or item.func() == enum.item {
          let marker = if is-enum {
            let pattern = if it.has("numbering") and it.numbering != auto { it.numbering } else { "1." }
            numbering(pattern, count)
          } else {
            if it.has("marker") and it.marker.len() > 0 { it.marker.at(0) } else { [•] }
          }

          par(
            first-line-indent: par.first-line-indent,
            hanging-indent: 0pt,
          )[#marker#h(0.25em)#item.body]
        } else {
          item
        }
      }
    }))

    list-depth.update(d => d - 1)
  }
}

#show list: flush-left-list
#show enum: flush-left-list

#let code-block(body) = block(width: 100%)[
  #text(font: FONT_CODE, size: zh(4))[
    #body
  ]
]

#let name(name) = align(center, pad(bottom: 0.8em)[
  #text(font: FONT_KAI, size: zh(3))[#name]
])
TYP
}

emit_auto_meta() {
  emit_template_head
  printf '#let autoTitle = "%s"\n\n' "$(escape_string "$FM_TITLE")"
  printf '#let autoAuthor = "%s"\n\n' "$(escape_string "$FM_AUTHOR")"
  printf '#let autoDate = '
  format_date "$FM_DATE"
  printf '\n'
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'TYP'
#set document(
  title: autoTitle.replace("|", " "),
  author: autoAuthor,
  keywords: "工作总结, 年终报告",
  date: autoDate,
)

= #autoTitle.split("|").map(s => s.trim()).join(linebreak())

TYP
  if [[ "$FM_SIGNATURE" != "true" && "$FM_SIGNATURE" != "yes" ]]; then
    printf '\n#name(autoAuthor)\n'
  fi
  printf '\n'
}

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

image_basename_no_ext() {
  local path="$1" base
  base="${path##*/}"
  printf '%s' "${base%.*}"
}

emit_single_image() {
  local path="$1" caption fig="$2"
  caption="$(image_basename_no_ext "$path")"
  printf '#figure(\n'
  printf '  context {\n'
  printf '    let img = image("%s")\n' "$(escape_string "$path")"
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'IMG'
    let img-size = measure(img)
    let x = img-size.width
    let y = img-size.height
    let max-size = 13.4cm

    let new-x = x
    let new-y = y

    if x > max-size {
      let scale = max-size / x
      new-x = max-size
      new-y = y * scale
    }

    if new-y > max-size {
      let scale = max-size / new-y
      new-x = new-x * scale
      new-y = max-size
    }

IMG
  printf '    image("%s", width: new-x, height: new-y)\n' "$(escape_string "$path")"
  printf '  },\n'
  printf '  placement: auto,\n'
  printf '  caption: [%s],\n' "$(escape_content "$caption")"
  printf ') <fig-%s>\n' "$fig"
}

parse_images_in_line() {
  local line="$1" rest="$1" before
  IMAGE_ALTS=()
  IMAGE_PATHS=()
  while [[ "$rest" == *"!["* && "$rest" == *"]("* && "$rest" == *")"* ]]; do
    before="${rest#*!\[}"
    IMAGE_ALTS+=("${before%%]*}")
    before="${before#*](}"
    IMAGE_PATHS+=("${before%%)*}")
    rest="${before#*)}"
  done
}

emit_multi_image() {
  local count="${#IMAGE_PATHS[@]}" i main alt path cap
  main="${IMAGE_ALTS[0]}"
  printf '\n#context {\n'
  printf '  let paths = ('
  for ((i = 0; i < count; i++)); do
    (( i > 0 )) && printf ', '
    printf '"%s"' "$(escape_string "${IMAGE_PATHS[$i]}")"
  done
  printf ')\n'
  printf '  let captions = ('
  for ((i = 0; i < count; i++)); do
    (( i > 0 )) && printf ', '
    cap="$(image_basename_no_ext "${IMAGE_PATHS[$i]}")"
    printf '"%s"' "$(escape_string "$cap")"
  done
  printf ')\n'
  printf '  let alts = ('
  for ((i = 0; i < count; i++)); do
    (( i > 0 )) && printf ', '
    printf '"%s"' "$(escape_string "${IMAGE_ALTS[$i]}")"
  done
  printf ')\n\n'
  printf '  let is_subfigure = true\n'
  printf '  let main_caption = "%s"\n\n' "$(escape_string "$main")"
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'MULTI'
  let gap = 0.3cm
  let max-width = 13.4cm
  let min-height = 6cm

  let sizes = paths.zip(captions).zip(alts).map(item => {
    let p = item.at(0).at(0)
    let c = item.at(0).at(1)
    let alt = item.at(1)
    let img = image(p)
    let s = measure(img)
    (width: s.width, height: s.height, path: p, caption: c, alt: alt, ratio: s.width / s.height)
  })

  let calc-row-height(imgs, total-width) = {
    let ratio-sum = imgs.map(i => i.ratio).sum()
    total-width / ratio-sum
  }

  let rows = ()

  if is_subfigure {
    rows.push(sizes)
  } else {
    let remaining = sizes

    while remaining.len() > 0 {
      let row = ()
      let found = false

      for n in range(1, remaining.len() + 1) {
        let candidate = remaining.slice(0, n)
        let gaps = (n - 1) * gap
        let available-width = max-width - gaps
        let row-h = calc-row-height(candidate, available-width)

        if row-h < min-height and n > 1 {
          row = remaining.slice(0, n - 1)
          remaining = remaining.slice(n - 1)
          found = true
          break
        }
      }

      if not found {
        row = remaining
        remaining = ()
      }

      rows.push(row)
    }
  }

  let render-rows(rows) = {
    for row in rows {
      let n = row.len()
      let gaps = (n - 1) * gap
      let available-width = max-width - gaps
      let row-height = calc-row-height(row, available-width)

      if row-height > max-width {
        row-height = max-width
      }

      align(center, grid(
        columns: n,
        gutter: gap,
        ..row.enumerate().map(item => {
          let i = item.at(0)
          let img-data = item.at(1)
          let w = row-height * img-data.ratio

          if is_subfigure {
             let sub-label = numbering("a", i + 1)
             let sub-text = [ (#sub-label) #img-data.caption ]

             v(0.5em)
             align(center, block({
               image(img-data.path, width: w, height: row-height)
               align(center, text(font: FONT_FS, size: zh(3))[#sub-text])
             }))
          } else {
             figure(
               image(img-data.path, width: w, height: row-height),
               caption: [ #img-data.caption ]
             )
          }
        })
      ))
      if is_subfigure { v(0.5em) } else { v(0.3em) }
    }
  }

  if is_subfigure {
    figure(
      context { render-rows(rows) },
      placement: auto,
      caption: [ #main_caption ]
    )
  } else {
    render-rows(rows)
  }
}

MULTI
}

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

render_body() {
  local total="${#BODY_LINES[@]}" i=0 line next next2 noindent=false in_comment=false code lang rows caption j last_list_kind="" marker_output
  HAS_SEEN_HEADER=false
  TABLE_COUNTER=0
  FIGURE_COUNTER=0
  while (( i < total )); do
    if [[ "${SKIP_SIGNATURE_INDEX:-}" == "$i" ]]; then
      ((i++))
      continue
    fi
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

    if [[ "$line" =~ ^[[:space:]]*([0-9]+)\.[[:space:]]+(.*)$ ]]; then
      [[ "$last_list_kind" == "ul" ]] && printf '\n\n'
      printf '+ '
      render_inline "${BASH_REMATCH[2]}"
      printf '\n'
      last_list_kind="ol"
      ((i++)); continue
    fi

    if [[ "$line" =~ ^[[:space:]]*-[[:space:]]+(.*)$ ]]; then
      printf -- '- '
      render_inline "${BASH_REMATCH[1]}"
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

signature_stick_candidate() {
  local line
  line="$(trim "$1")"
  [[ -n "$line" ]] || return 1
  case "$line" in
    "#"*|"|"*|">"*|"- "*|"!"*|"\`\`\`"*|"{pagebreak}"|"{.pagebreak}"|"{pagebreak:weak}"|"{.pagebreak:weak}") return 1 ;;
  esac
  [[ "$line" =~ ^[0-9]+\. ]] && return 1
  return 0
}

prepare_signature_stick() {
  local idx
  SKIP_SIGNATURE_INDEX=""
  STICK_SIGNATURE_TEXT=""
  for ((idx = ${#BODY_LINES[@]} - 1; idx >= 0; idx--)); do
    [[ -z "$(trim "${BODY_LINES[$idx]}")" ]] && continue
    if signature_stick_candidate "${BODY_LINES[$idx]}"; then
      SKIP_SIGNATURE_INDEX="$idx"
      STICK_SIGNATURE_TEXT="${BODY_LINES[$idx]}"
    fi
    break
  done
}

render_markdown_to_typst() {
  local input="$1" output="$2" body
  parse_input "$input"
  SKIP_SIGNATURE_INDEX=""
  STICK_SIGNATURE_TEXT=""
  if [[ "$FM_SIGNATURE" == "true" || "$FM_SIGNATURE" == "yes" ]]; then
    prepare_signature_stick
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
      if [[ -n "$STICK_SIGNATURE_TEXT" ]]; then
        render_inline "$STICK_SIGNATURE_TEXT"
        printf '\n\n'
      fi
      render_signature
      printf ']\n'
    else
      printf '%s' "$body"
    fi
  } >> "$output"
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

cmd_example() {
  local output=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --output) output="${2:-}"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      *) die "unknown argument for example: $1" ;;
    esac
  done
  [[ -n "$output" ]] || die "example requires --output"
  need_file "$TEMPLATE_MD"
  ensure_parent_dir "$output"
  copy_file_shell "$TEMPLATE_MD" "$output"
  printf 'wrote %s\n' "$output"
}

cmd_render() {
  local input="" typ="" expected_typ=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --input) input="${2:-}"; shift 2 ;;
      --typ) typ="${2:-}"; shift 2 ;;
      --expected-typ) expected_typ="${2:-}"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      *) die "unknown argument for render: $1" ;;
    esac
  done
  [[ -n "$input" ]] || die "render requires --input"
  need_file "$input"
  [[ -n "$typ" ]] || typ="${input%.*}.typ"
  render_markdown_to_typst "$input" "$typ"
  printf 'wrote %s\n' "$typ"
  if [[ -n "$expected_typ" ]]; then
    need_file "$expected_typ"
    same_file_shell "$expected_typ" "$typ" || die "Typst differs from expected file: $expected_typ"
    printf 'verified Typst matches %s\n' "$expected_typ"
  fi
}

cmd_manifest() {
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'JSON'
{
  "name": "gongwen",
  "displayName": "类公文模板",
  "version": "0.2.0-shell-only",
  "description": "Bash-only Markdown-to-Typst renderer aligned to the Presto gongwen black-box output."
}
JSON
}

cmd_info() {
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'INFO'
gongwen shell-only renderer
- Markdown-to-Typst conversion is performed inside this Bash script.
- The script does not call external template binaries or Markdown converters.
- PDF compilation is intentionally outside this script.
INFO
}

cmd_version() {
  printf 'gongwen.sh 0.2.0-shell-only\n'
}

main() {
  local command="${1:-}"
  [[ $# -gt 0 ]] && shift
  case "$command" in
    example) cmd_example "$@" ;;
    render) cmd_render "$@" ;;
    manifest) cmd_manifest "$@" ;;
    info) cmd_info "$@" ;;
    version) cmd_version "$@" ;;
    -h|--help|"") usage ;;
    *) die "unknown command: $command" ;;
  esac
}

main "$@"
