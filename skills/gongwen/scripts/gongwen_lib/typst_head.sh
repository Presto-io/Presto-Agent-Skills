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

emit_template_head() {
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'TYP'
// 中文字号转换函数
#import "@preview/pointless-size:0.1.2": zh

// 定义常用字体名称。同类字体可以 fallback，但不跨字体类型。
#let FONT_XBS = ("FZXiaoBiaoSong-B05", "FZXiaoBiaoSong-B05S", "FZXiaoBiaoSongS-B-GB", "方正小标宋简体", "方正小标宋_GBK") // 小标宋类
#let FONT_HEI = ("SimHei", "STHeiti", "Heiti SC", "Noto Sans CJK SC", "Source Han Sans SC", "思源黑体", "Microsoft YaHei") // 黑体类
#let FONT_FS = ("FangSong", "STFangsong", "FangSong_GB2312", "Fangsong SC") // 仿宋类
#let FONT_KAI = ("KaiTi", "STKaiti", "Kaiti SC", "KaiTi_GB2312") // 楷体类
#let FONT_SONG = ("SimSun", "NSimSun", "Songti SC", "STSong", "Noto Serif CJK SC", "Source Han Serif SC", "思源宋体") // 宋体类
#let FONT_CODE = ("Noto Sans Mono CJK SC", "Source Han Mono SC", "Sarasa Mono SC", "Menlo") // 等宽类

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

// 强制加粗在缺少粗体字重的中文字体环境中仍可见
#show strong: it => text(weight: "bold", stroke: 0.2pt + black)[#it.body]

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
