#import "../body-policy.typ": body-size
#let labels = (education: "教育背景", skills: "专业技能", certificates: "资格证书", projects: "项目经历", training: "实训经历", experience: "相关经历", contact: "联系方式")
#let english = (education: "Education", skills: "Skills", certificates: "Certificates", projects: "Projects", training: "Practice", experience: "Experience", contact: "Contact")
#let icon-names = (education: "graduation-cap", skills: "wrench", certificates: "badge-check", projects: "folder-kanban", training: "flask-conical", experience: "briefcase-business", contact: "user-round")
#let schemes = (
  "blue-poster": (accent: rgb("F2F0E6"), secondary: rgb("CDD9ED"), ink: rgb("F6F5EF"), pale: rgb("2A5DA0")),
  "serif-blue": (accent: rgb("133BAA"), secondary: rgb("576B9E"), ink: rgb("283C66"), pale: rgb("E4E6EF")),
  "purple-doodle": (accent: rgb("4A3B5E"), secondary: rgb("8D75AB"), ink: rgb("302B34"), pale: rgb("C5B0E0")),
  "purple-sidebar": (accent: rgb("413168"), secondary: rgb("8F7EAC"), ink: rgb("423C51"), pale: rgb("ECE7F6")),
  "rust-editorial": (accent: rgb("AB452E"), secondary: rgb("AD6D56"), ink: rgb("854531"), pale: rgb("E7D8CB")),
  "blue-business": (accent: rgb("3064B3"), secondary: rgb("6F7C90"), ink: rgb("273344"), pale: rgb("EAF0F8")),
  "blue-floral": (accent: rgb("598AAD"), secondary: rgb("80A1BA"), ink: rgb("40596B"), pale: rgb("E1EDF4")),
  "beige-notebook": (accent: rgb("745641"), secondary: rgb("9B8774"), ink: rgb("4F463E"), pale: rgb("E9DED2")),
)
#let body-font = "Source Han Sans SC"
#let serif-font = "Source Han Serif SC"
#let slot(rect, content) = place(top + left, dx: rect.at(0)*1mm, dy: rect.at(1)*1mm, block(width: rect.at(2)*1mm, height: rect.at(3)*1mm)[#content])
#let nameplate(data, palette, size: 64pt, serif: true) = block(inset: (top: 4mm, bottom: 2.5mm))[
  #text(font: if serif { serif-font } else { body-font }, size: size, weight: if serif { 900 } else { 700 }, fill: palette.accent, top-edge: "cap-height", bottom-edge: "baseline")[#data.profile.name]
]
#let titleline(data, palette) = {
  text(size: 10pt, weight: "bold", fill: palette.accent)[#data.profile.at("headline", default: "")]
  for direction in data.profile.at("directions", default: ()) {
    if direction != data.profile.at("headline", default: "") { v(1mm); text(size: 8.5pt, fill: palette.secondary)[#direction] }
  }
}
#let summary(data, palette) = text(size: 8.8pt, fill: palette.secondary)[#data.profile.at("summary", default: "")]
#let icon(kind, color, size: 3.8mm) = {
  let source = read("../../../assets/icons/lucide/" + icon-names.at(kind) + ".svg").replace("currentColor", color.to-hex())
  box(baseline: 14%)[#image(bytes(source), format: "svg", width: size, height: size)]
}
#let heading(kind, palette, style, index) = {
  if style == "purple-doodle" {
    box(fill: palette.pale, inset: (x: 2mm, y: 1mm))[
      #text(font: ("Noteworthy", "Liberation Sans", "Noto Sans Mono CJK SC"), size: 11pt, weight: "bold")[#upper(english.at(kind))]#h(2mm)#text(size: 9pt)[#labels.at(kind)]
    ]
    v(.7mm)
    line(length: 72%, stroke: .85pt + palette.ink)
  } else if style == "rust-editorial" {
    grid(columns: (auto, auto, 1fr), gutter: 2mm, align: horizon,
      text(font: ("Didot", "Liberation Serif", "Source Han Serif SC"), style: "italic", size: 20pt, fill: palette.accent, top-edge: "ascender", bottom-edge: "descender")[#english.at(kind)],
      text(size: 8pt, fill: palette.secondary)[#labels.at(kind)],
      line(length: 100%, stroke: .45pt + palette.accent))
  } else if style == "serif-blue" {
    grid(columns: (1fr, auto), align: horizon,
      [#text(font: serif-font, size: 15pt, weight: 900, fill: palette.accent)[#labels.at(kind)]#h(2mm)#text(font: ("Didot", "Liberation Serif", "Source Han Serif SC"), size: 12pt, fill: palette.accent)[#english.at(kind)]],
      text(font: ("Didot", "Liberation Serif", "Source Han Serif SC"), size: 25pt, fill: palette.accent)[0#(index + 2).])
    v(.9mm)
    line(length: 100%, stroke: .4pt + palette.accent)
  } else if style == "blue-floral" {
    grid(columns: (auto, 1fr), gutter: 3mm, align: horizon,
      circle(radius: 3.3mm, fill: palette.accent)[#icon(kind, white, size: 4mm)],
      [#text(font: serif-font, size: 15pt, fill: palette.accent)[#labels.at(kind)]#h(3mm)#text(fill: palette.secondary)[· · ·]])
  } else if style == "purple-sidebar" {
    [#icon(kind, palette.accent)#h(2mm)#text(size: 11.5pt, weight: "bold", fill: palette.accent)[#labels.at(kind)]]
    v(1.5mm)
    line(length: 100%, stroke: .35pt + palette.secondary)
  } else if style == "blue-business" {
    grid(columns: (auto, 1fr), gutter: 3mm, align: horizon,
      [#text(size: 10pt, weight: "bold", fill: palette.accent)[#upper(english.at(kind))]#h(2mm)#text(size: 9pt, fill: palette.accent)[#labels.at(kind)]],
      line(length: 100%, stroke: .3pt + palette.accent))
  } else if style == "beige-notebook" {
    [#text(size: 10pt, weight: "bold")[#upper(english.at(kind))]#h(2mm)#text(size: 8pt)[#labels.at(kind)]]
    v(1.3mm)
    line(length: 8mm, stroke: 1.2pt + palette.accent)
  } else {
    [#text(size: 13pt, weight: "bold", fill: palette.accent)[#english.at(kind)]#h(2mm)#text(size: 10pt, fill: palette.accent)[#labels.at(kind)]]
    v(1.7mm)
    line(length: 100%, stroke: .3pt + palette.secondary)
  }
}
#let paragraph(value, palette, bullet: false, compact: false) = {
  if value != "" {
    let sentence = str(value).trim(regex("[。，；;、,]+$")) + if value.ends-with("！") or value.ends-with("？") { "" } else { "。" }
    block(above: if compact { 1.1mm } else { 1.5mm })[
      #if bullet { grid(columns: (2.7mm, 1fr), align: top, text(fill: palette.accent, size: .85em)[•], [#sentence]) } else { sentence }
    ]
  }
}
#let entry(section, palette, style, compact: false) = {
  let value = section.value
  let kind = section.kind
  let body = {
    if kind == "skills" {
      text(weight: "bold", fill: palette.accent)[#value.group]
      for item in value.items { paragraph(item, palette, compact: compact) }
      paragraph(value.at("note", default: ""), palette, compact: compact)
    } else if kind == "certificates" {
      [#icon(kind, palette.accent, size: 3mm)#h(2mm)#text(weight: "bold")[#value.name]]
      if value.at("note", default: "") != "持有" + value.name + "。" { paragraph(value.at("note", default: ""), palette, compact: compact) }
    } else {
      text(weight: "bold", fill: palette.accent)[#if kind == "education" { value.school } else { value.title }]
      let dates = value.at("start", default: "") + if value.at("end", default: "") != "" { " — " + value.end } else { "" }
      let information = if kind == "education" { (value.major, value.at("degree", default: ""), dates) } else { (dates, value.at("role", default: ""), value.at("organization", default: "")) }
      information = information.filter(item => item != "")
      if information.len() > 0 { block(above: 1.2mm)[#text(size: .88em, fill: palette.secondary)[#information.join("  /  ")]] }
      if kind == "education" {
        if value.at("courses", default: ()).len() > 0 { paragraph("相关课程：" + value.courses.join("、"), palette, compact: compact) }
        for honor in value.at("honors", default: ()) { paragraph(honor, palette, bullet: true, compact: compact) }
      } else {
        paragraph(value.at("summary", default: ""), palette, compact: compact)
        for outcome in value.at("outcomes", default: ()) { paragraph(outcome, palette, bullet: true, compact: compact) }
      }
    }
  }
  block(breakable: false)[
    #if style in ("blue-business", "beige-notebook") and kind not in ("skills", "certificates") {
      grid(columns: (3mm, 1fr), gutter: 1.8mm, align: top,
        [#circle(radius: .8mm, fill: palette.accent)],
        block(inset: (left: 2.5mm), stroke: (left: .3pt + palette.pale))[#body])
    } else { body }
  ]
}
#let contacts(data, palette, narrow: false) = {
  for (key, label) in (("phone", "电话 / Phone"), ("email", "邮箱 / Email"), ("city", "现居 / Location")) {
    let value = data.profile.contact.at(key, default: "")
    if value != "" {
      block(above: 2mm)[
        #if narrow {
          text(size: 7.5pt, fill: palette.secondary)[#label]
          v(.8mm)
          text(size: 8.7pt, fill: palette.ink)[#value]
        } else {
          grid(columns: (14mm, 1fr), gutter: 2mm, text(size: 8pt, fill: palette.secondary)[#label.split(" /").first()], text(size: 9pt, fill: palette.ink)[#value])
        }
      ]
    }
  }
}
#let section(kind, data, palette, style, index, compact: false, card: false, entry-gap: 3mm) = {
  let contents = [
    #heading(kind, palette, style, index)
    #v(if compact { 1.7mm } else { 2.7mm })
    #if kind == "contact" { contacts(data, palette, narrow: style in ("beige-notebook", "purple-sidebar", "blue-business")) } else {
      let entries = data.sections.filter(item => item.kind == kind)
      if kind == "certificates" and style in ("serif-blue", "blue-floral") {
        grid(columns: (1fr, 1fr), column-gutter: 5mm, row-gutter: entry-gap,
          ..entries.map(item => entry(item, palette, style, compact: compact)))
      } else {
        for (entry-index, item) in entries.enumerate() {
          entry(item, palette, style, compact: compact)
          if entry-index < entries.len() - 1 { v(entry-gap) }
        }
      }
    }
  ]
  block(width: 100%, breakable: false, inset: if card { 3mm } else { 0mm }, fill: if card { rgb("FBFAFD") } else { none }, stroke: if card { .35pt + rgb("D0C6E3") } else { none }, radius: if card { 3mm } else { 0mm })[#contents]
}
#let flow(data, selected, rect, palette, style, max-size: 10.6pt, card: false, compact: false, entry-gap: 3mm) = context {
  let kinds = selected.filter(kind => kind == "contact" or data.sections.any(item => item.kind == kind))
  if kinds.len() > 0 {
    let groups = kinds.enumerate().map(((index, kind)) => section(kind, data, palette, style, index, compact: compact, card: card, entry-gap: entry-gap))
    let width = rect.at(2) * 1mm
    let available = rect.at(3) * 1mm
    let gaps = groups.len() - 1
    let size = body-size(default: 10.2pt)
    let natural = groups.map(item => measure(block(width: width)[#set text(size: size)
      #set par(leading: if compact { .38em } else { .48em })
      #item]).height).sum(default: 0pt)
    assert(natural + gaps * 3mm <= available, message: "LAYOUT_OVERFLOW: " + style)
    let gap = calc.min(if card { 5mm } else if compact { 8mm } else { 14mm }, (available - natural) / calc.max(1, gaps))
    slot(rect, [
      #set text(size: size, fill: palette.ink)
      #set par(leading: if compact { .38em } else { .48em })
      #for (index, item) in groups.enumerate() { item; if index < gaps { v(gap) } }
      #metadata((kinds: kinds, rect_mm: rect, font_pt: size / 1pt, natural_mm: natural / 1mm, gap_mm: gap / 1mm, groups: groups.len(), available_mm: available / 1mm, used_mm: (natural + gap * gaps) / 1mm)) <slot-report>
    ])
  }
}
#let resume(data, style) = {
  let palette = schemes.at(style)
  let photo = data.photo != none
  let background = data.at("reference_background", default: "backgrounds/" + style + "-plain.png")
  set page(paper: "a4", margin: 0mm, background: image(background, width: 210mm, height: 297mm))
  set text(font: body-font, size: 9.8pt, lang: "zh", fill: palette.ink)
  set par(justify: false, leading: .48em, spacing: 0pt)
  set block(above: 0pt, below: 0pt)
  let main = ("projects", "training", "experience")
  let all = ("education", "skills", "certificates", "projects", "training", "experience")
  let main-size = 12pt
  if style == "blue-poster" {
    if not photo { slot((133, 33, 63, 46), [#set text(font: ("Didot", "Liberation Serif", "Source Han Serif SC"), size: 30pt, fill: rgb("75A1CA"), top-edge: "ascender", bottom-edge: "descender")
      #stack(dir: ttb, spacing: 1mm, [Personal], [Resume])]) }
    slot((14, 18, 111, 73), [
      #text(font: ("Helvetica Neue", "Liberation Sans", "Noto Sans Mono CJK SC"), size: 58pt, weight: "black", fill: palette.accent)[Hello!]
      #v(5mm)#nameplate(data, palette, size: 58pt)
      #v(3mm)#titleline(data, palette)#v(3mm)#summary(data, palette)
    ])
    flow(data, ("contact", "education", "skills", "certificates"), (14, 106, 83, 175), palette, style, max-size: 11.4pt, compact: true)
    flow(data, main, (111, 106, 85, 175), palette, style, max-size: main-size)
  } else if style == "serif-blue" {
    slot((14, 18, 102, 61), [#nameplate(data, palette, size: 90pt)#v(4mm)#titleline(data, palette)#v(3mm)#summary(data, palette)])
    slot((14, 86, 95, 27), [#text(font: serif-font, size: 12pt, fill: palette.accent)[基本信息]#v(2mm)#contacts(data, palette)])
    flow(data, all, (14, 118, 182, 163), palette, style, max-size: 11.4pt, compact: true, entry-gap: 2mm)
  } else if style == "purple-doodle" {
    slot((14, 17, 109, 77), [
      #text(font: ("Noteworthy", "Liberation Sans", "Noto Sans Mono CJK SC"), size: 27pt, weight: "bold")[HEY, I'M]
      #v(2mm)#nameplate(data, palette, size: 46pt, serif: false)
      #v(4mm)#titleline(data, palette)#v(5mm)#summary(data, palette)
    ])
    flow(data, main, (14, 110, 101, 162), palette, style, max-size: main-size)
    flow(data, ("skills", "education", "certificates", "contact"), (129, 110, 67, 162), palette, style, max-size: 11.4pt, compact: true)
  } else if style == "purple-sidebar" {
    let reversed = (accent: rgb("F3EDF9"), secondary: rgb("CEC1E3"), ink: rgb("ECE8F4"), pale: rgb("9D83C7"))
    if not photo { slot((14, 20, 49, 50), text(font: serif-font, size: 40pt, fill: rgb("AE9DB8"))[个人\ 简历]) }
    slot((83, 17, 113, 48), [#nameplate(data, palette, size: 43pt)#v(4mm)#titleline(data, palette)#v(5mm)#summary(data, palette)])
    flow(data, ("contact", "skills"), (14, 100, 47, 176), reversed, "purple-doodle", max-size: 11.4pt, compact: true, entry-gap: 5mm)
    flow(data, ("education", "certificates", "projects", "training", "experience"), (82, 74, 114, 205), palette, style, max-size: 11.4pt, card: true, compact: true, entry-gap: 2.7mm)
  } else if style == "rust-editorial" {
    slot((14, 18, 99, 91), [
      #nameplate(data, palette, size: 74pt)#v(3mm)
      #block[#set text(font: ("Didot", "Liberation Serif", "Source Han Serif SC"), style: "italic", size: 28pt, fill: palette.accent, top-edge: "ascender", bottom-edge: "descender")
        #stack(dir: ttb, spacing: 1mm, [Personal], [Resume])]
      #v(4mm)#titleline(data, palette)#v(3mm)#summary(data, palette)
    ])
    flow(data, ("contact", "education", "skills", "certificates"), (14, 124, 76, 153), palette, style, max-size: 11.4pt, compact: true, entry-gap: 2.5mm)
    flow(data, main, (105, 124, 91, 153), palette, style, max-size: main-size, compact: true, entry-gap: 3.2mm)
  } else if style == "blue-business" {
    slot((14, 15, 75, 32), [#nameplate(data, palette, size: 35pt, serif: false)#v(3mm)#titleline(data, palette)])
    slot((91, 19, 105, 26), [#summary(data, palette)])
    flow(data, ("contact", "education", "certificates"), (18, if photo { 131 } else { 58 }, 54, if photo { 146 } else { 219 }), palette, style, max-size: 11.4pt, compact: true, entry-gap: 3mm)
    flow(data, ("projects", "training", "experience", "skills"), (88, 54, 108, 226), palette, style, max-size: main-size, entry-gap: 4mm)
  } else if style == "blue-floral" {
    let light = (accent: white, secondary: rgb("EFF6FA"), ink: white, pale: palette.pale)
    let head-ink = (accent: rgb("244B68"), secondary: rgb("315B77"), ink: rgb("244B68"), pale: palette.pale)
    slot((16, 17, 106, 50), [#nameplate(data, light, size: 48pt)#v(4mm)#titleline(data, head-ink)#v(4mm)#summary(data, head-ink)])
    slot((17, 71, 97, 23), [#contacts(data, head-ink)])
    flow(data, all, (16, 113, 166, 168), palette, style, max-size: 11.4pt, compact: true, entry-gap: 2mm)
  } else if style == "beige-notebook" {
    slot((14, 20, 108, 77), [
      #text(font: ("Noteworthy", "Liberation Sans", "Noto Sans Mono CJK SC"), size: 26pt, fill: palette.accent)[Hi there! ♡]
      #v(3mm)#nameplate(data, palette, size: 60pt)
      #v(4mm)#titleline(data, palette)#v(5mm)#summary(data, palette)
    ])
    flow(data, ("contact", "education", "skills", "certificates"), (17, 113, 65, 165), palette, style, max-size: 11.4pt, compact: true)
    flow(data, main, (94, 113, 102, 165), palette, style, max-size: main-size, entry-gap: 4mm)
  }
  [#metadata((template: style, revision: "refined-3", photo: photo, body_font: body-font, display_font: serif-font)) <layout-report>]
}
