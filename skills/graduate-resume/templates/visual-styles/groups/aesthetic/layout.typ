#import "base-components.typ": entry, section-body, labels
#import "../../page-flow.typ": page-flow

#let themes = (
  "chinese-classic": (accent: rgb("983F32"), secondary: rgb("766A58"), ink: rgb("303D34"), panel: none, heading: ("Songti SC", "Source Han Serif SC"), body: ("Songti SC", "Source Han Serif SC"), latin: ("Didot", "Liberation Serif", "Source Han Serif SC")),
  "steampunk": (accent: rgb("62401E"), secondary: rgb("806442"), ink: rgb("372B20"), panel: rgb("F0E3C8"), heading: ("Songti SC", "Source Han Serif SC"), body: ("Songti SC", "Source Han Serif SC"), latin: ("American Typewriter", "Liberation Mono", "Noto Sans Mono CJK SC")),
  "dreamcore": (accent: rgb("605287"), secondary: rgb("7D7291"), ink: rgb("3D3654"), panel: rgb("FCF9FF"), heading: "Noto Sans Mono CJK SC", body: "Noto Sans Mono CJK SC", latin: ("Didot", "Liberation Serif", "Source Han Serif SC")),
  "handmade-collage": (accent: rgb("894933"), secondary: rgb("756C60"), ink: rgb("303B35"), panel: rgb("FCF9EE"), heading: ("Songti SC", "Source Han Serif SC"), body: "Noto Sans Mono CJK SC", latin: ("Noteworthy", "Liberation Sans", "Noto Sans Mono CJK SC")),
  "cyberpunk": (accent: rgb("79EFF0"), secondary: rgb("95B8C7"), ink: rgb("E3EFF4"), panel: rgb("142536"), heading: "Noto Sans Mono CJK SC", body: "Noto Sans Mono CJK SC", latin: ("Courier", "Liberation Mono", "Noto Sans Mono CJK SC")),
  "art-deco": (accent: rgb("DFC894"), secondary: rgb("B5C2B6"), ink: rgb("F0EDDE"), panel: none, heading: ("Songti SC", "Source Han Serif SC"), body: ("Songti SC", "Source Han Serif SC"), latin: ("Didot", "Liberation Serif", "Source Han Serif SC")),
  "botanical": (accent: rgb("50694F"), secondary: rgb("7A816C"), ink: rgb("374335"), panel: rgb("EFF0E5"), heading: ("Songti SC", "Source Han Serif SC"), body: ("Songti SC", "Source Han Serif SC"), latin: ("Noteworthy", "Liberation Sans", "Noto Sans Mono CJK SC")),
  "brutalist": (accent: rgb("22272A"), secondary: rgb("667061"), ink: rgb("23272A"), panel: none, heading: "Noto Sans Mono CJK SC", body: "Noto Sans Mono CJK SC", latin: ("Courier", "Liberation Mono", "Noto Sans Mono CJK SC")),
)
#let icon-names = (education: "graduation-cap", skills: "wrench", certificates: "badge-check", projects: "folder-kanban", training: "flask-conical", experience: "briefcase-business")

#let icon(kind, color, size: 3.8mm) = {
  let svg = read("../../../../assets/icons/lucide/" + icon-names.at(kind) + ".svg").replace("currentColor", color.to-hex())
  box(baseline: 14%)[#image(bytes(svg), format: "svg", width: size, height: size)]
}

#let heading(kind, theme, style, index) = {
  let text-label = text(font: theme.heading, size: 11.5pt, weight: "bold", fill: theme.accent)[#labels.at(kind)]
  if style == "chinese-classic" {
    block(inset: (left: 2.5mm), stroke: (left: 2pt + theme.accent))[
      #text-label#h(2mm)#text(font: theme.latin, size: 8pt, fill: theme.secondary)[0#(index + 1)]
    ]
    v(1.2mm)
    line(length: 100%, stroke: 0.3pt + rgb("C7B9A0"))
  } else if style == "steampunk" {
    block(inset: (x: 2mm, y: 1.2mm), fill: rgb("E0C598"), stroke: 0.5pt + theme.accent)[
      #icon(kind, theme.accent)#h(1.5mm)#text-label#h(2mm)#text(font: theme.latin, size: 7pt)[0#(index + 1)]
    ]
  } else if style == "dreamcore" {
    block(inset: (x: 2.5mm, y: 1.5mm), fill: rgb("E9DCF5"), radius: 4mm)[
      #icon(kind, theme.accent)#h(1.8mm)#text-label
    ]
  } else if style == "handmade-collage" {
    rotate(if calc.even(index) { -1.5deg } else { 1deg }, reflow: true)[
      #box(fill: if calc.even(index) { rgb("E4C989") } else { rgb("B9CCBA") }, inset: (x: 3mm, y: 1.2mm))[
        #icon(kind, theme.accent)#h(1.5mm)#text-label
      ]
    ]
  } else if style == "cyberpunk" {
    grid(columns: (auto, 1fr, auto), gutter: 1.6mm, align: horizon,
      icon(kind, theme.accent), text-label, text(font: theme.latin, size: 8pt, fill: rgb("E88EC9"))[0#(index + 1)])
    v(1.2mm)
    line(length: 100%, stroke: 0.7pt + theme.accent)
  } else if style == "art-deco" {
    grid(columns: (1fr, auto, 1fr), gutter: 2mm, align: horizon,
      line(length: 100%, stroke: 0.3pt + theme.accent),
      [#icon(kind, theme.accent, size: 3.3mm)#h(1.5mm)#text-label],
      line(length: 100%, stroke: 0.3pt + theme.accent))
  } else if style == "botanical" {
    block(inset: (x: 2mm, y: 1mm), fill: rgb("DEE5D4"), radius: (top-right: 4mm, bottom-left: 4mm))[
      #icon(kind, theme.accent)#h(1.8mm)#text-label
    ]
  } else {
    grid(columns: (auto, 1fr), gutter: 2mm, align: horizon,
      box(fill: rgb("B6ED33"), inset: 1mm)[#text(size: 13pt, weight: "bold")[0#(index + 1)]],
      [#text(font: theme.heading, size: 14pt, weight: "bold")[#labels.at(kind)]])
    v(1mm)
    line(length: 100%, stroke: 1.3pt + theme.accent)
  }
}

#let group(kind, data, theme, style, index) = {
  let framed = style in ("dreamcore", "handmade-collage", "cyberpunk")
  block(width: 100%, breakable: false, fill: if framed { theme.panel } else { none }, inset: if framed { 2.6mm } else { 0mm },
    radius: if style == "dreamcore" { 3mm } else { 0mm },
    stroke: if style == "cyberpunk" { 0.35pt + rgb("346174") } else { none })[
    #heading(kind, theme, style, index)
    #v(2mm)
    #section-body(data.sections.filter(item => item.kind == kind), theme)
  ]
}

#let contact(data, theme, centered: false) = {
  let info = data.profile.contact
  let rows = (("电话", info.at("phone", default: "")), ("邮箱", info.at("email", default: "")), ("现居", info.at("city", default: ""))).filter(pair => pair.at(1) != "")
  let details = [
    #grid(columns: (auto, auto, auto), column-gutter: 5mm, row-gutter: 1mm,
      ..rows.map(pair => [#text(size: 8pt, fill: theme.secondary)[#pair.at(0)]#h(1.5mm)#text(size: 8.5pt, fill: theme.ink)[#pair.at(1)]]))
    #v(2mm)
    #text(size: 8pt, fill: theme.secondary)[#data.profile.at("summary", default: "")]
  ]
  if centered { align(center)[#details] } else { details }
}

#let header(data, theme, style) = block(height: 44mm)[
  #let centered = style == "art-deco"
  #let eyebrow = (
    "chinese-classic": "履 历 · 简 介", "steampunk": "CURRICULUM VITAE / PERSONAL RECORD", "dreamcore": "somewhere, a new beginning.",
    "handmade-collage": "a little about me", "cyberpunk": "PROFILE_ / HUMAN INTERFACE", "art-deco": "C U R R I C U L U M   V I T A E", "botanical": "notes for a new season", "brutalist": "RESUME / PERSONAL PROFILE")
  #let words = [
    #text(font: theme.latin, size: 8pt, fill: theme.accent)[#eyebrow.at(style)]
    #v(2mm)
    #text(font: theme.heading, size: if style == "brutalist" { 36pt } else { 29pt }, weight: "bold", fill: theme.accent)[#data.profile.name]
    #v(1.6mm)
    #text(size: 10pt, fill: theme.ink, weight: "bold")[#data.profile.at("headline", default: "")]
    #for direction in data.profile.at("directions", default: ()) {
      if direction != data.profile.at("headline", default: "") { block(above: 1mm)[#text(size: 8pt, fill: theme.secondary)[#direction]] }
    }
    #v(3mm)
    #contact(data, theme, centered: centered)
  ]
  #let separate = style in ("chinese-classic", "steampunk", "dreamcore", "handmade-collage", "botanical") and data.photo != none
  #if separate {
    grid(columns: (29mm, 96mm, 39mm), gutter: 8mm, align: top,
      block(width: 29mm, height: 39mm, fill: if style == "steampunk" { rgb("F0E3C8") } else { rgb("FCF9EE") }, inset: 1mm, stroke: .4pt + theme.secondary)[#image(data.photo, width: 27mm, height: 37mm, fit: "cover")],
      words, [])
  } else { grid(columns: (1fr, auto), gutter: 5mm, align: top,
    if centered { align(center)[#words] } else { block(width: 119mm)[#words] },
    if data.photo != none {
      block(inset: if style == "handmade-collage" { (x: 2mm, top: 2mm, bottom: 5mm) } else { 1mm }, fill: if style == "handmade-collage" { white } else { none }, stroke: if style in ("steampunk", "art-deco") { 0.5pt + theme.accent } else { none })[
        #image(data.photo, width: 23mm, height: 31mm, fit: "contain")
      ]
    } else { box(width: if centered { 0mm } else { 48mm }) }) }
]

#let resume(data, style) = {
  let theme = themes.at(style)
  set page(paper: "a4", margin: (x: 15mm, y: 14mm), background: image("assets/" + style + ".svg", width: 210mm, height: 297mm))
  set text(font: theme.body, lang: "zh", size: 9.6pt, fill: theme.ink)
  set par(justify: false, leading: 0.52em, spacing: 1.3mm)
  let kinds = ("education", "skills", "certificates", "projects", "training", "experience").filter(kind => data.sections.any(item => item.kind == kind))
  let render-group(kind) = group(kind, data, theme, style, kinds.position(item => item == kind))
  let flow(selected, width) = page-flow(selected.map(render-group), width, 216mm, max-size: 11.5pt)
  context {
    let head = header(data, theme, style)
    let body = if style in ("chinese-classic", "brutalist", "botanical") {
      flow(kinds, 180mm)
    } else {
      let left-kinds = if style == "art-deco" { kinds.filter(kind => kind in ("education", "skills", "certificates")) } else { kinds.filter(kind => kind in ("skills", "certificates")) }
      let right-kinds = kinds.filter(kind => kind not in left-kinds)
      let widths = if style == "art-deco" { (86mm, 86mm) } else if style == "handmade-collage" { (72mm, 100mm) } else if style == "dreamcore" { (66mm, 106mm) } else { (64mm, 108mm) }
      grid(columns: widths, gutter: 8mm, align: top, flow(left-kinds, widths.at(0)), flow(right-kinds, widths.at(1)))
    }
    let natural = measure(block(width: 180mm)[#body]).height
    assert(natural <= 218mm, message: "LAYOUT_OVERFLOW: 风格正文超过一页安全范围")
    [#metadata((template: style, body_natural_height_mm: natural / 1mm, body_available_mm: 218, heading_font: theme.heading, body_font: theme.body)) <layout-report>]
    head
    v(6mm)
    body
  }
}
