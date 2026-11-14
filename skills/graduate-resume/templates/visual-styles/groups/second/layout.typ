#import "base-components.typ": entry, section-body, contact, labels

#let palettes = (
  "banner-navy": (accent: rgb("173450"), pale: rgb("EAF0F5"), secondary: rgb("64778A")),
  "sidebar-right": (accent: rgb("4E4775"), pale: rgb("F0EEF6"), secondary: rgb("756F88")),
  "timeline-copper": (accent: rgb("995D37"), pale: rgb("F6EEE7"), secondary: rgb("8C796D")),
  "balanced-columns": (accent: rgb("176A71"), pale: rgb("EAF4F4"), secondary: rgb("687E80")),
  "soft-cards": (accent: rgb("405E4D"), pale: rgb("F0F4EF"), secondary: rgb("708072")),
  "centered-red": (accent: rgb("973F42"), pale: rgb("F8EEEE"), secondary: rgb("8E7273")),
)

#let identity(data, palette, centered: false, reversed: false) = {
  let primary = if reversed { white } else { palette.accent }
  let secondary = if reversed { rgb("D8E4ED") } else { palette.secondary }
  let identity-text = [
    #text(size: if centered { 31pt } else { 28pt }, weight: "bold", fill: primary)[#data.profile.name]
    #v(1.5mm)
    #text(size: 10.5pt, weight: "bold", fill: primary)[#data.profile.at("headline", default: "")]
    #for direction in data.profile.at("directions", default: ()) {
      if direction != data.profile.at("headline", default: "") {
        block(above: 1mm)[#text(size: 9pt, fill: secondary)[#direction]]
      }
    }
  ]
  if centered { align(center)[#identity-text] } else { identity-text }
}

#let header(data, palette, style) = {
  if style == "banner-navy" {
    block(width: 100%, fill: palette.accent, inset: 5mm, radius: 1mm)[
      #grid(columns: (1fr, auto), gutter: 6mm, align: top,
        identity(data, palette, reversed: true),
        if data.photo != none { image(data.photo, width: 24mm, height: 32mm, fit: "contain") } else { [] })
    ]
    v(3mm)
    contact(data.profile, palette)
    v(2mm)
    text(size: 8.5pt, fill: palette.secondary)[#data.profile.at("summary", default: "")]
  } else if style == "centered-red" {
    grid(columns: (28mm, 1fr, 28mm), gutter: 3mm, align: horizon,
      [], identity(data, palette, centered: true),
      if data.photo != none { image(data.photo, width: 24mm, height: 32mm, fit: "contain") } else { [] })
    v(3mm)
    line(length: 100%, stroke: 1.6pt + palette.accent)
    v(2mm)
    contact(data.profile, palette)
    v(2mm)
    align(center)[#text(size: 8.5pt, fill: palette.secondary)[#data.profile.at("summary", default: "")]]
  } else if style == "balanced-columns" {
    grid(columns: (1fr, 1fr), gutter: 8mm, align: top,
      identity(data, palette),
      [#grid(columns: (1fr, auto), gutter: 3mm,
        [#contact(data.profile, palette, narrow: true)],
        if data.photo != none { image(data.photo, width: 23mm, height: 31mm, fit: "contain") } else { [] })])
    v(2mm)
    text(size: 8.5pt, fill: palette.secondary)[#data.profile.at("summary", default: "")]
    v(2mm)
    line(length: 100%, stroke: 2pt + palette.accent)
  } else {
    grid(columns: (1fr, auto), gutter: 6mm, align: top,
      [#identity(data, palette)#v(3mm)#contact(data.profile, palette)#v(2mm)#text(size: 8.5pt, fill: palette.secondary)[#data.profile.at("summary", default: "")]],
      if data.photo != none { image(data.photo, width: 25mm, height: 33mm, fit: "contain") } else { [] })
    v(3mm)
    line(length: 100%, stroke: 0.6pt + palette.accent)
  }
}

#let section(kind, entries, palette, style, index) = block(breakable: false)[
  #if style == "timeline-copper" {
    grid(columns: (8mm, 1fr), gutter: 3mm, align: top,
      [#align(center)[#circle(radius: 1.5mm, fill: palette.accent)#v(2mm)#text(size: 8pt, fill: palette.secondary)[0#(index + 1)]]],
      block(inset: (left: 3mm, bottom: 2mm), stroke: (left: 0.7pt + palette.accent))[
        #text(size: 12pt, weight: "bold", fill: palette.accent)[#labels.at(kind)]
        #v(2mm)
        #section-body(entries, palette)
      ])
  } else if style == "soft-cards" {
    block(width: 100%, fill: palette.pale, inset: 3mm, radius: 2mm)[
      #text(size: 11pt, weight: "bold", fill: palette.accent)[#labels.at(kind)]
      #v(1.5mm)
      #section-body(entries, palette)
    ]
  } else if style == "centered-red" {
    grid(columns: (1fr, auto, 1fr), gutter: 3mm, align: horizon,
      line(length: 100%, stroke: 0.5pt + rgb("DCC8C8")),
      text(size: 11.5pt, weight: "bold", fill: palette.accent)[#labels.at(kind)],
      line(length: 100%, stroke: 0.5pt + rgb("DCC8C8")))
    v(2mm)
    section-body(entries, palette)
  } else if style == "banner-navy" {
    block(width: 100%, fill: palette.pale, inset: (x: 2.5mm, y: 1.3mm))[
      #text(size: 11pt, weight: "bold", fill: palette.accent)[#labels.at(kind)]
    ]
    v(2mm)
    section-body(entries, palette)
  } else {
    grid(columns: (1fr, auto), align: horizon,
      text(size: 11.5pt, weight: "bold", fill: palette.accent)[#labels.at(kind)],
      text(size: 8pt, fill: palette.secondary)[0#(index + 1)])
    v(1.2mm)
    line(length: 100%, stroke: 0.6pt + palette.accent)
    v(2mm)
    section-body(entries, palette)
  }
]

#let measured-flow(groups, width, available, max-gap: 8mm) = context {
  let heights = groups.map(group => measure(block(width: width)[#group]).height)
  let natural = heights.sum(default: 0pt)
  let gaps = calc.max(0, groups.len() - 1)
  assert(natural + gaps * 2mm <= available, message: "LAYOUT_OVERFLOW: 当前版式的一页自然高度超限")
  let gap = (available - 2mm - natural) / calc.max(1, gaps)
  for (index, group) in groups.enumerate() {
    group
    if index < gaps { v(gap) }
  }
}

#let resume(data, style) = {
  set block(above: 0pt, below: 0pt)
  set page(paper: "a4", margin: (x: 15mm, y: 14mm))
  set text(font: "Noto Sans Mono CJK SC", lang: "zh", size: 9.8pt, fill: rgb("29343D"))
  set par(justify: false, leading: 0.55em, spacing: 1.5mm)
  let palette = palettes.at(style)
  let kinds = ("education", "skills", "certificates", "projects", "training", "experience").filter(kind => data.sections.any(item => item.kind == kind))
  let group(kind) = section(kind, data.sections.filter(item => item.kind == kind), palette, style, kinds.position(item => item == kind))
  context {
    let width = 180mm
    let height = 269mm
    let head = header(data, palette, style)
    let head-height = measure(block(width: width)[#head]).height
    let available = height - head-height - 9mm
    head
    v(5mm)
    if style in ("sidebar-right", "balanced-columns") {
      let left-kinds = if style == "sidebar-right" { kinds.filter(kind => kind not in ("skills", "certificates")) } else { kinds.filter(kind => kind in ("education", "skills", "certificates")) }
      let right-kinds = kinds.filter(kind => kind not in left-kinds)
      let widths = if style == "sidebar-right" { (109mm, 63mm) } else { (86mm, 86mm) }
      let left-groups = left-kinds.map(group)
      let right-groups = right-kinds.map(group)
      let right-width = widths.at(1) - if style == "sidebar-right" { 8mm } else { 0mm }
      let left-height = left-groups.map(item => measure(block(width: widths.at(0))[#item]).height).sum(default: 0pt)
      let right-height = right-groups.map(item => measure(block(width: right-width)[#item]).height).sum(default: 0pt)
      [#metadata((template: style, header_height_mm: head-height / 1mm, available_mm: available / 1mm, left_natural_mm: left-height / 1mm, right_natural_mm: right-height / 1mm)) <layout-report>]
      grid(columns: widths, gutter: 8mm, align: top,
        measured-flow(left-groups, widths.at(0), available),
        if style == "sidebar-right" {
          block(width: 100%, height: available, fill: palette.pale, inset: 4mm, radius: 1mm)[#measured-flow(right-groups, right-width, available - 8mm)]
        } else { measured-flow(right-groups, right-width, available) })
    } else {
      let groups = kinds.map(group)
      let natural = groups.map(item => measure(block(width: width)[#item]).height).sum(default: 0pt)
      [#metadata((template: style, header_height_mm: head-height / 1mm, content_height_mm: natural / 1mm, available_mm: available / 1mm)) <layout-report>]
      measured-flow(groups, width, available, max-gap: if style == "soft-cards" { 4mm } else { 8mm })
    }
  }
}
