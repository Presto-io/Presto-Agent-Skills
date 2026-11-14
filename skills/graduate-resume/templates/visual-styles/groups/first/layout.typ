#import "../../page-flow.typ": page-flow
#set text(font: "Noto Sans Mono CJK SC", lang: "zh", size: 10pt, fill: rgb("24303C"))
#set par(justify: false, leading: 0.57em, spacing: 1.6mm)

#let labels = (education: "教育经历", skills: "专业技能", certificates: "资格证书", projects: "项目经历", training: "实训经历", experience: "相关经历")
#let palettes = (
  "single-column-02": (accent: rgb("1A6660"), pale: rgb("EDF5F3"), secondary: rgb("687775")),
  "sidebar-left-02": (accent: rgb("234B7A"), pale: rgb("EDF2F8"), secondary: rgb("65758B")),
  "single-column-03": (accent: rgb("20272D"), pale: rgb("F2F2EF"), secondary: rgb("707777")),
)

#let sentence(value) = {
  if value == "" { [] } else { str(value).trim(regex("[。，；;、,]+$")) + if value.ends-with("！") or value.ends-with("？") { "" } else { "。" } }
}

#let detail(value, bullet: false) = {
  if value != "" {
    block(above: 1.2mm, inset: (left: if bullet { 0pt } else { 1em }))[
      #if bullet { grid(columns: (1em, 1fr), [#align(center)[#text(size: 8pt)[•]]], [#sentence(value)]) } else { sentence(value) }
    ]
  }
}

#let entry(section, palette) = {
  let value = section.value
  let kind = section.kind
  block(breakable: false)[
    #if kind == "skills" {
      text(weight: "bold", fill: palette.accent)[#value.group]
      for item in value.items { detail(item) }
      detail(value.at("note", default: ""))
    } else if kind == "certificates" {
      text(weight: "bold")[#value.name]
      if value.at("note", default: "") != "持有" + value.name + "。" { detail(value.at("note", default: "")) }
    } else {
      let title = if kind == "education" { value.school } else { value.title }
      text(weight: "bold")[#title]
      let dates = value.at("start", default: "") + if value.at("end", default: "") != "" { " — " + value.end } else { "" }
      let meta = if kind == "education" {
        (value.major, value.at("degree", default: ""), dates).filter(item => item != "").join("  /  ")
      } else {
        (dates, value.at("role", default: ""), value.at("organization", default: "")).filter(item => item != "").join("  /  ")
      }
      if meta != "" { block(above: 1.3mm)[#text(size: 8.8pt, fill: palette.secondary)[#meta]] }
      if kind == "education" {
        if value.at("courses", default: ()).len() > 0 { detail("相关课程：" + value.courses.join("、")) }
        for honor in value.at("honors", default: ()) { detail(honor, bullet: true) }
      } else {
        detail(value.at("summary", default: ""))
        for outcome in value.at("outcomes", default: ()) { detail(outcome, bullet: true) }
      }
    }
  ]
}

#let section-body(entries, palette) = {
  for (entry-index, section) in entries.enumerate() {
    entry(section, palette)
    if entry-index < entries.len() - 1 { v(2.5mm) }
  }
}

#let section-group(kind, entries, palette, style, index) = block(breakable: false)[
  #if style == "single-column-03" {
    grid(columns: (26mm, 1fr), column-gutter: 5mm, align: top,
      [#text(size: 8pt, fill: palette.secondary)[0#(index + 1)]#v(1.5mm)#text(size: 11pt, weight: "bold")[#labels.at(kind)]],
      section-body(entries, palette),
    )
  } else {
  if style == "single-column-02" {
    grid(columns: (10mm, 1fr), column-gutter: 3mm,
      text(size: 9pt, fill: palette.secondary)[0#(index + 1)],
      [#text(size: 12pt, weight: "bold", fill: palette.accent)[#labels.at(kind)]#v(1.2mm)#line(length: 100%, stroke: 0.5pt + rgb("B9CFCA"))],
    )
  } else if style == "sidebar-left-02" {
    block(inset: (left: 2.2mm), stroke: (left: 2pt + palette.accent))[
      #text(size: 12pt, weight: "bold", fill: palette.accent)[#labels.at(kind)]
    ]
  } else {
    grid(columns: (1fr, auto), text(size: 12pt, weight: "bold")[#labels.at(kind)], text(size: 8pt, fill: palette.secondary)[0#(index + 1)])
    v(1.3mm)
    line(length: 100%, stroke: 0.7pt + palette.accent)
  }
  v(2mm)
  section-body(entries, palette)
  }
]

#let contact(profile, palette, narrow: false) = {
  let info = profile.contact
  let values = (("电话", info.at("phone", default: "")), ("邮箱", info.at("email", default: "")), ("现居", info.at("city", default: ""))).filter(pair => pair.at(1) != "")
  if narrow {
    for pair in values {
      block(above: 3mm)[#text(size: 8pt, fill: palette.secondary)[#pair.at(0)]#v(0.7mm)#text(size: 9pt)[#pair.at(1)]]
    }
  } else {
    grid(columns: (1fr, 1.35fr), column-gutter: 6mm, row-gutter: 2mm,
      ..values.map(pair => [#text(size: 8.5pt, fill: palette.secondary)[#pair.at(0)]#h(2mm)#text(size: 9pt)[#pair.at(1)]]))
  }
}

#let header(data, palette, style) = block(breakable: false, inset: (bottom: 4mm), stroke: (bottom: 1.3pt + palette.accent))[
  #grid(columns: (1fr, auto), gutter: 6mm, align: (left, top), [
    #text(size: 29pt, weight: "bold", fill: palette.accent)[#data.profile.name]
    #v(2mm)
    #text(size: 11pt, weight: "bold")[#data.profile.at("headline", default: "")]
    #for direction in data.profile.at("directions", default: ()) {
      if direction != data.profile.at("headline", default: "") { block(above: 1mm)[#text(size: 9pt, fill: palette.secondary)[#direction]] }
    }
    #v(3mm)
    #contact(data.profile, palette)
    #v(2.5mm)
    #text(size: 8.5pt, fill: palette.secondary)[#data.profile.at("summary", default: "")]
  ], if data.photo != none { image(data.photo, width: 25mm, height: 33mm, fit: "contain") } else { [] })
]

#let resume(data, style) = {
  set block(above: 0pt, below: 0pt)
  set page(paper: "a4", margin: (x: 15mm, y: 14mm))
  set text(font: "Noto Sans Mono CJK SC", lang: "zh", size: 10pt, fill: rgb("24303C"))
  set par(justify: false, leading: 0.57em, spacing: 1.6mm)
  let palette = palettes.at(style)
  let kinds = ("education", "skills", "certificates", "projects", "training", "experience").filter(kind => data.sections.any(section => section.kind == kind))
  let groups(selected) = selected.enumerate().map(((index, kind)) => section-group(kind, data.sections.filter(section => section.kind == kind), palette, style, index))
  context {
    let width = 180mm
    let height = 269mm
    let head = header(data, palette, style)
    let head-height = measure(block(width: width)[#head]).height
    if style == "sidebar-left-02" {
      let rail-kinds = kinds.filter(kind => kind in ("skills", "certificates"))
      let main-kinds = kinds.filter(kind => kind not in ("skills", "certificates"))
      let rail = [
        #text(size: 25pt, weight: "bold", fill: palette.accent)[#data.profile.name]
        #v(2.5mm)
        #text(size: 9pt, weight: "bold")[#data.profile.at("headline", default: "")]
        #for direction in data.profile.at("directions", default: ()) {
          if direction != data.profile.at("headline", default: "") { block(above: 1mm)[#text(size: 9pt, fill: palette.secondary)[#direction]] }
        }
        #if data.photo != none { v(4mm); image(data.photo, width: 25mm, height: 33mm, fit: "contain") }
        #v(3mm)
        #contact(data.profile, palette, narrow: true)
        #v(3mm)
        #text(size: 8.5pt, fill: palette.secondary)[#data.profile.at("summary", default: "")]
        #v(6mm)
        #for group in groups(rail-kinds) { group; v(5mm) }
      ]
      let main-groups = groups(main-kinds)
      let rail-height = measure(block(width: 52mm)[#rail]).height
      let natural-main = main-groups.map(group => measure(block(width: 110mm)[#group]).height).sum()
      assert(rail-height <= height - 12mm, message: "LAYOUT_OVERFLOW: 侧栏内容超出一页")
      assert(natural-main <= height - 4mm * (main-groups.len() - 1), message: "LAYOUT_OVERFLOW: 主栏内容超出一页")
      let gap = (height - 3mm - natural-main) / calc.max(1, main-groups.len() - 1)
      [#metadata((template: style, rail_height_mm: rail-height / 1mm, main_height_mm: natural-main / 1mm, main_gap_mm: gap / 1mm, available_mm: height / 1mm)) <layout-report>]
      grid(columns: (64mm, 110mm), gutter: 6mm, align: top,
        block(width: 64mm, height: height, fill: palette.pale, inset: 6mm)[#rail],
        [#for (index, group) in main-groups.enumerate() { group; if index < main-groups.len() - 1 { v(gap) } }],
      )
    } else {
      let contents = groups(kinds)
      let natural = contents.map(group => measure(block(width: width)[#group]).height).sum()
      let available = height - head-height - 5mm
      assert(natural <= available - 3mm * (contents.len() - 1), message: "LAYOUT_OVERFLOW: 单栏内容超出一页")
      let gap = (available - 3mm - natural) / calc.max(1, contents.len() - 1)
      [#metadata((template: style, header_height_mm: head-height / 1mm, content_height_mm: natural / 1mm, gap_mm: gap / 1mm, available_mm: available / 1mm)) <layout-report>]
      head
      v(5mm)
      page-flow(contents, width, available - 3mm, min-size: 9.6pt, max-size: 11.5pt)
    }
  }
}
