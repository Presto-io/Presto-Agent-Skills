#import "base-components.typ": entry, section-body, labels

#let icons = (education: "graduation-cap", skills: "wrench", certificates: "badge-check", projects: "folder-kanban", training: "flask-conical", experience: "briefcase-business", profile: "user-round", contact: "file-text")
#let palette = (accent: rgb("285D58"), pale: rgb("EDF3EF"), secondary: rgb("627672"))
#let icon(kind, color: palette.accent, size: 4.2mm) = {
  let svg = read("../../../../assets/icons/lucide/" + icons.at(kind) + ".svg").replace("currentColor", color.to-hex())
  box(baseline: 14%)[#image(bytes(svg), format: "svg", width: size, height: size)]
}

#let mini-icon(kind) = {
  let paths = (
    phone: "<path d='M5 3h4l2 5-3 2a15 15 0 0 0 6 6l2-3 5 2v4c0 2-3 3-5 2A22 22 0 0 1 3 8C2 6 3 3 5 3Z'/>",
    email: "<rect x='3' y='5' width='18' height='14' rx='2'/><path d='m3 6 9 7 9-7'/>",
    city: "<path d='M19 10c0 6-7 11-7 11S5 16 5 10a7 7 0 1 1 14 0Z'/><circle cx='12' cy='10' r='2'/>",
  )
  let svg = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='" + palette.accent.to-hex() + "' stroke-width='1.7' stroke-linecap='round' stroke-linejoin='round'>" + paths.at(kind) + "</svg>"
  box(baseline: 14%)[#image(bytes(svg), format: "svg", width: 3.4mm, height: 3.4mm)]
}

#let tool-icon(group) = {
  let paths = if group.contains("办公") or group.contains("计算机") {
    "<rect x='3' y='4' width='18' height='12' rx='2'/><path d='M8 21h8M12 16v5'/><path d='m8 8-2 2 2 2m8-4 2 2-2 2'/>"
  } else if group.contains("PLC") {
    "<rect x='6' y='6' width='12' height='12' rx='2'/><rect x='9' y='9' width='6' height='6'/><path d='M9 2v4m6-4v4M9 18v4m6-4v4M2 9h4m-4 6h4m12-6h4m-4 6h4'/>"
  } else if group.contains("CAD") {
    "<path d='M4 20 9 4l11 16H4Zm3-4h10M9 4l3 16'/><circle cx='9' cy='4' r='2'/>"
  } else if group.contains("团队") {
    "<circle cx='9' cy='8' r='3'/><path d='M3 21v-3a6 6 0 0 1 12 0v3M16 5a3 3 0 0 1 0 6m2 3a5 5 0 0 1 3 5v2'/>"
  } else {
    "<path d='m13 2-9 12h7l-1 8 10-13h-8l1-7Z'/>"
  }
  let svg = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='" + palette.accent.to-hex() + "' stroke-width='1.7' stroke-linecap='round' stroke-linejoin='round'>" + paths + "</svg>"
  box(baseline: 14%)[#image(bytes(svg), format: "svg", width: 5mm, height: 5mm)]
}

#let contact(profile) = {
  for (key, label) in (("phone", "电话"), ("email", "邮箱"), ("city", "现居")) {
    if profile.contact.at(key, default: "") != "" {
      block(above: 1.8mm)[#mini-icon(key)#h(1.5mm)#text(size: 8.6pt)[#profile.contact.at(key)]]
    }
  }
}

#let title(kind, ink: palette.accent, large: false) = block(below: 2mm)[
  #icon(kind, color: ink, size: if large { 5mm } else { 4.2mm })#h(1.6mm)
  #text(size: if large { 12pt } else { 11pt }, weight: "bold", fill: ink)[#labels.at(kind)]
]

#let base-cell(kind, sections, fill: white, border: none, radius: 3mm, inset: 3.5mm, p: palette) = block(width: 100%, fill: fill, stroke: border, radius: radius, inset: inset, breakable: false)[
  #title(kind, ink: p.accent)
  #section-body(sections.filter(item => item.kind == kind), p)
]

#let identity(data, fill: palette.pale, border: none, radius: 3mm, large: false, height: auto) = block(width: 100%, height: height, fill: fill, stroke: border, radius: radius, inset: 4mm)[
  #grid(columns: (1fr, auto), gutter: 4mm, align: top,
    [#icon("profile", size: 5mm)#v(2mm)
     #text(size: if large { 34pt } else { 28pt }, weight: "bold", fill: palette.accent)[#data.profile.name]
     #v(1.5mm)
     #text(size: 10pt, weight: "bold")[#data.profile.at("headline", default: "")]
     #for direction in data.profile.at("directions", default: ()) {
       if direction != data.profile.at("headline", default: "") { block(above: 1mm)[#text(size: 8.5pt)[#direction]] }
     }
    ],
    if data.photo != none { image(data.photo, width: 23mm, height: 31mm, fit: "contain") } else { [] })
]

#let contacts(data, border: none, radius: 3mm, fill: white, height: auto) = block(width: 100%, height: height, fill: fill, stroke: border, radius: radius, inset: 4mm)[
  #text(size: 8pt, fill: palette.secondary)[联系与个人信息]
  #contact(data.profile)
  #v(2mm)
  #text(size: 8pt, fill: palette.secondary)[#data.profile.at("summary", default: "")]
]

#let skills-matrix(data, hard: false) = {
  let skills = data.sections.filter(item => item.kind == "skills")
  title("skills", large: true)
  grid(columns: (1fr,) * skills.len(), gutter: if hard { 0mm } else { 3mm }, align: top,
    ..skills.enumerate().map(((index, item)) => block(width: 100%, fill: if hard { white } else { palette.pale }, stroke: if hard { 0.6pt + rgb("283332") } else { none }, radius: if hard { 0mm } else { 2mm }, inset: 3mm)[
      #grid(columns: (auto, 1fr), gutter: 2mm, align: horizon,
        tool-icon(item.value.group),
        text(size: 8pt, fill: palette.secondary)[技术模块 0#(index + 1)])
      #v(2mm)
      #entry(item, palette)
    ]))
}

#let stack-cells(kinds, data, fill: white, border: none, radius: 3mm, gap: 3mm) = {
  for (index, kind) in kinds.enumerate() {
    cell(kind, data.sections, fill: fill, border: border, radius: radius)
    if index < kinds.len() - 1 { v(gap) }
  }
}

#let resume(data, style) = {
  set page(paper: "a4", margin: (x: 14mm, y: 14mm), fill: if style == "bento-mosaic" { rgb("F0F1ED") } else { white })
  set text(font: "Noto Sans Mono CJK SC", lang: "zh", size: 10.5pt, fill: rgb("273532"))
  set par(justify: false, leading: 0.52em, spacing: 1.3mm)
  let has(kind) = data.sections.any(item => item.kind == kind)
  let filtered(kinds) = kinds.filter(has)
  context {
    let compose(padding) = {
      let cell(kind, sections, fill: white, border: none, radius: 3mm) = base-cell(kind, sections, fill: fill, border: border, radius: radius, inset: (x: 3.5mm, y: padding))
      let stack-cells(kinds, data, fill: white, border: none, radius: 3mm, gap: 3mm) = {
        for (index, kind) in kinds.enumerate() {
          cell(kind, data.sections, fill: fill, border: border, radius: radius)
          if index < kinds.len() - 1 { v(gap) }
        }
      }
    if style == "bento-mosaic" { [
      #grid(columns: (110mm, 68mm), gutter: 4mm, align: top,
        identity(data, fill: rgb("DDE9DF"), large: true), contacts(data))
      #v(4mm)
      #grid(columns: (68mm, 110mm), gutter: 4mm, align: top,
        stack-cells(filtered(("education", "certificates", "skills")), data),
        stack-cells(filtered(("projects", "training", "experience")), data, fill: rgb("FAFBF8")))
    ] } else if style == "technical-matrix" { [
      #grid(columns: (108mm, 70mm), gutter: 4mm, align: top,
        identity(data, fill: rgb("E6F0F2")), contacts(data, border: 0.6pt + rgb("B9CFCF")))
      #v(4mm)
      #skills-matrix(data)
      #v(4mm)
      #if has("certificates") { grid(columns: (112mm, 66mm), gutter: 4mm, align: top,
        cell("education", data.sections, fill: rgb("F2F5F5")),
        cell("certificates", data.sections, fill: rgb("F5EFDC")))
      } else { cell("education", data.sections, fill: rgb("F2F5F5")) }
      #v(4mm)
      #if has("projects") or has("training") { grid(columns: (89mm, 89mm), gutter: 4mm, align: top,
        stack-cells(filtered(("projects", "training")), data, border: 0.5pt + rgb("C8D5D4")),
        stack-cells(filtered(("experience",)), data, fill: rgb("F2F5F5")))
      } else { cell("experience", data.sections, fill: rgb("F2F5F5")) }
    ] } else if style == "swiss-grid" { [
      #set block(spacing: 0pt)
      #let head-height = calc.max(
        measure(block(width: 112mm)[#identity(data, large: true)]).height,
        measure(block(width: 70mm)[#contacts(data)]).height)
      #grid(columns: (112mm, 70mm), gutter: 0mm, align: top,
        identity(data, fill: rgb("F2E7A0"), border: 0.7pt + black, radius: 0mm, large: true, height: head-height),
        contacts(data, border: 0.7pt + black, radius: 0mm, height: head-height))
      #v(3mm)
      #grid(columns: (89mm, 93mm), gutter: 0mm, align: top,
        stack-cells(filtered(("education", "training", "certificates")), data, border: 0.7pt + black, radius: 0mm, gap: 0mm),
        stack-cells(filtered(("skills", "projects", "experience")), data, border: 0.7pt + black, radius: 0mm, gap: 0mm))
    ] } else { [
      #grid(columns: (112mm, 66mm), gutter: 4mm, align: top,
        identity(data, fill: white, large: true), contacts(data, fill: rgb("F2ECE4")))
      #v(3mm)
      #if has("projects") {
        cell("projects", data.sections, fill: rgb("E9EEE7"), border: (left: 3pt + palette.accent))
      } else if has("training") {
        cell("training", data.sections, fill: rgb("E9EEE7"), border: (left: 3pt + palette.accent))
      } else {
        cell("education", data.sections, fill: rgb("E9EEE7"), border: (left: 3pt + palette.accent))
      }
      #v(4mm)
      #let feature = if has("projects") { "projects" } else if has("training") { "training" } else { "education" }
      #grid(columns: (80mm, 98mm), gutter: 4mm, align: top,
        [#stack-cells(filtered(("skills", "certificates")), data, fill: rgb("F4F1EB"))],
        stack-cells(filtered(("education", "training", "experience")).filter(kind => kind != feature), data, border: 0.5pt + rgb("CCD6CC")))
    ] }
    }
    let lower = 3.5mm
    let upper = 50mm
    for iteration in range(12) {
      let midpoint = (lower + upper) / 2
      let height = measure(block(width: 182mm)[#compose(midpoint)]).height
      if height <= 263mm { lower = midpoint } else { upper = midpoint }
    }
    let body = compose(lower)
    let natural = measure(block(width: 182mm)[#body]).height
    assert(natural <= 266mm, message: "LAYOUT_OVERFLOW: 矩阵模块自然高度超出单页安全范围")
    [#metadata((template: style, natural_height_mm: natural / 1mm, available_mm: 266, icon_family: "Lucide 0.468.0", layout: "modular-grid")) <layout-report>]
    body
  }
}
