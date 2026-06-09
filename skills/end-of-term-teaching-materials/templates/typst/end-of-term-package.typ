// Fixed Typst package template for end-of-term teaching materials.
// The renderer replaces the placeholders below with escaped Typst content.
// Fixed artifacts: 成绩记分册, 成绩汇总表, 成绩分析表, 教学日志封面, 过程考核评价表封面, 交接班记录封面.

#set page(paper: "a4", margin: (x: 22mm, y: 16mm))
#set text(lang: "zh", font: ("Noto Serif CJK SC", "Songti SC", "STSong"), size: 10.5pt)
#set par(justify: true, leading: 0.65em)

#show heading.where(level: 1): it => block(above: 0pt, below: 1em)[
  #align(center)[#text(size: 20pt, weight: "bold")[#it.body]]
]

#show heading.where(level: 2): it => block(above: 1em, below: 0.55em)[
  #text(size: 14pt, weight: "bold")[#it.body]
]

#show heading.where(level: 3): it => block(above: 0.7em, below: 0.3em)[
  #text(size: 12pt, weight: "bold")[#it.body]
]

#let meta-line(label, value) = if value != "" [
  #text(weight: "bold")[#label：]#value#linebreak()
]

#let cover(title, subtitle, rows) = [
  #pagebreak(weak: true)
  #align(center)[
    #v(24mm)
    #text(size: 24pt, weight: "bold")[#title]
    #v(8mm)
    #text(size: 14pt)[#subtitle]
    #v(18mm)
  ]
  #block(stroke: 0.7pt, inset: 10pt, width: 100%)[#rows]
]

#let simple-table(cols, rows) = table(
  columns: cols,
  inset: 4pt,
  stroke: 0.45pt,
  align: horizon,
  ..rows,
)

#let excel-diag(width, height, top-left, bottom-right) = box(width: width, height: height)[
  #place(dx: 0pt, dy: 0pt)[#line(length: width * 1.08, angle: 28deg, stroke: 0.45pt)]
  #place(dx: 4pt, dy: 2pt)[#text(size: 8pt)[#top-left]]
  #place(dx: width - 18mm, dy: height - 8mm)[#text(size: 8pt)[#bottom-right]]
]

#set document(title: "{{DOCUMENT_TITLE}}", author: "{{DOCUMENT_AUTHOR}}")

{{PACKAGE_BODY}}
