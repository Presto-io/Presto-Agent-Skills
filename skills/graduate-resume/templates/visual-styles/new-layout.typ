#let badge(body, width: 5.6mm, height: 5.6mm, fill: none, stroke: none, round: false, lift: 0pt) = {
  box(width: width, height: height, inset: 0pt, fill: fill, stroke: stroke, radius: if round { 50% } else { 0pt })[
    #align(center + horizon)[#set text(font: ("Courier", "Liberation Mono", "Noto Sans Mono CJK SC"), top-edge: "cap-height", bottom-edge: "baseline")
      #move(dy: -lift)[#body]]
  ]
}
#import "base-components.typ": section-body, labels
#import "page-flow.typ": page-flow

#let specs = (
  "mono-minimal": (accent: rgb("222222"), secondary: rgb("686868"), ink: rgb("222222"), pale: white, font: "Noto Sans Mono CJK SC", mode: "margin", eyebrow: "CURRICULUM VITAE"),
  "editorial-serif": (accent: rgb("51463E"), secondary: rgb("776D62"), ink: rgb("302F2C"), pale: none, font: ("Songti SC", "Source Han Serif SC"), mode: "margin", eyebrow: "P E R S O N A L   R E C O R D"),
  "nordic": (accent: rgb("815541"), secondary: rgb("736E64"), ink: rgb("353B34"), pale: none, font: "Noto Sans Mono CJK SC", mode: "right", eyebrow: "a considered beginning"),
  "bauhaus": (accent: rgb("A93628"), secondary: rgb("6E645A"), ink: rgb("222222"), pale: none, font: "Noto Sans Mono CJK SC", mode: "single", eyebrow: "FORM / FUNCTION / FUTURE"),
  "power-substation": (accent: rgb("183C5D"), secondary: rgb("697782"), ink: rgb("263947"), pale: none, font: "Noto Sans Mono CJK SC", mode: "single", eyebrow: "ELECTRICAL / PERSONAL RECORD"),
  "distribution-panel": (accent: rgb("2E566F"), secondary: rgb("637783"), ink: rgb("283B46"), pale: white, font: "Noto Sans Mono CJK SC", mode: "cabinet", eyebrow: "EQUIPMENT FILE / PROFILE"),
  "cad-blueprint": (accent: rgb("DCEAF5"), secondary: rgb("AFCCDF"), ink: rgb("EEF5FB"), pale: rgb("1D4365"), font: "Noto Sans Mono CJK SC", mode: "wide", eyebrow: "TECHNICAL DRAWING / RESUME"),
  "industrial-safety": (accent: rgb("272E30"), secondary: rgb("68706E"), ink: rgb("272E30"), pale: none, font: "Noto Sans Mono CJK SC", mode: "margin", eyebrow: "PERSONAL FILE / INDUSTRIAL EDITION"),
  "plc-ladder": (accent: rgb("345A79"), secondary: rgb("6C7F8B"), ink: rgb("293C49"), pale: none, font: "Noto Sans Mono CJK SC", mode: "ladder", eyebrow: "CONTROL LOGIC / PROFILE"),
  "pcb-traces": (accent: rgb("E0D39F"), secondary: rgb("AAC9B6"), ink: rgb("EDF5E9"), pale: rgb("20493D"), font: "Noto Sans Mono CJK SC", mode: "wide", eyebrow: "CIRCUIT / PERSONAL RECORD"),
  "signal-wave": (accent: rgb("8BE5B7"), secondary: rgb("AEC0C7"), ink: rgb("E8EFF1"), pale: rgb("1D2C33"), font: "Noto Sans Mono CJK SC", mode: "scope", eyebrow: "SIGNAL / PERSONAL PROFILE"),
  "network-topology": (accent: rgb("346C89"), secondary: rgb("6A8190"), ink: rgb("2C4251"), pale: none, font: "Noto Sans Mono CJK SC", mode: "single", eyebrow: "CONNECTED / PERSONAL RECORD"),
)
#let icon-names = (education: "graduation-cap", skills: "wrench", certificates: "badge-check", projects: "folder-kanban", training: "flask-conical", experience: "briefcase-business")
#let icon(kind, color) = {
  let source = read("../../assets/icons/lucide/" + icon-names.at(kind) + ".svg").replace("currentColor", color.to-hex())
  box(baseline: 14%)[#image(bytes(source), format: "svg", width: 3.8mm, height: 3.8mm)]
}
#let heading(kind, spec, style, index) = {
  let label = text(size: 11.4pt, weight: "bold", fill: spec.accent)[#labels.at(kind)]
  if style == "mono-minimal" {
    text(size: 8pt, fill: spec.secondary)[0#(index+1)]
    v(1.5mm)
    label
  } else if style == "industrial-safety" {
    box(fill: rgb("EBC847"), inset: (x: 1.6mm, y: 1.2mm))[
      #text(size: 9pt, weight: "bold")[0#(index+1)]
    ]
    v(2mm)
    label
  } else if style == "plc-ladder" {
    let source = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 90 18'><path d='M0 9H20M20 2V16M27 2V16M27 9H61M67 2Q57 9 67 16M74 2Q84 9 74 16M80 9H90' fill='none' stroke='#53758D' stroke-width='1' stroke-linecap='square'/></svg>"
    grid(columns: (auto, 1fr, auto), gutter: 2mm, align: horizon,
      text(size: 8pt, fill: spec.secondary)[0#(index+1)], label, image(bytes(source), format: "svg", width: 28mm))
  } else if style == "power-substation" {
    grid(columns: (auto, 1fr), gutter: 2mm, align: horizon,
      box(stroke: .8pt + rgb("B24C39"), inset: 1mm)[#text(size: 8pt, weight: "bold")[0#(index+1)]],
      [#icon(kind, spec.accent)#h(1.5mm)#label])
    v(1mm)
    line(length: 100%, stroke: .4pt + rgb("BECED8"))
  } else if style == "network-topology" {
    grid(columns: (auto, 1fr), gutter: 2mm, align: horizon,
      badge(text(size: 7pt)[#(index+1)], width: 4.8mm, height: 4.8mm, fill: rgb("E0EEF4"), stroke: .6pt + spec.accent, round: true, lift: float(sys.inputs.at("number-lift-pt", default: "0")) * 1pt),
      [#icon(kind, spec.accent)#h(1.5mm)#label])
    v(.7mm)
    line(length: 100%, stroke: .3pt + rgb("C6D6DF"))
  } else if style == "bauhaus" {
    grid(columns: (auto, 1fr), gutter: 2mm, align: horizon,
      badge(text(size: 8pt, fill: white)[#(index+1)], fill: if calc.even(index) { rgb("2459A3") } else { rgb("A93628") }, round: true, lift: float(sys.inputs.at("number-lift-pt", default: "0")) * 1pt),
      text(size: 13.4pt, weight: "bold", fill: rgb("222222"))[#labels.at(kind)])
  } else if style == "editorial-serif" {
    text(font: ("Didot", "Liberation Serif", "Source Han Serif SC"), size: 24pt, fill: spec.secondary)[0#(index + 1)]
    v(2mm)
    label
  } else if style == "distribution-panel" {
    block(width: 100%, fill: rgb("DEE7EC"), inset: (x: 2mm, y: 1.4mm))[
      #icon(kind, spec.accent)#h(1.5mm)#label
    ]
  } else if style == "signal-wave" {
    grid(columns: (auto, 1fr), gutter: 2mm, align: horizon,
      box(fill: rgb("E8C16D"), inset: 1mm)[#text(size: 7pt, fill: rgb("172127"))[CH#(index+1)]], label)
  } else if style == "pcb-traces" {
    [#box(stroke: .6pt + spec.accent, inset: 1mm)[#text(size: 8pt)[U#(index+1)]]#h(2mm)#icon(kind, spec.accent)#h(1.5mm)#label]
    v(1mm)
    line(length: 100%, stroke: .3pt + rgb("658C70"))
  } else if style == "cad-blueprint" {
    block(width: 100%, stroke: .4pt + spec.accent, inset: (x: 2mm, y: 1.2mm))[
      #text(size: 8pt)[0#(index+1)]#h(2mm)#icon(kind, spec.accent)#h(1.5mm)#label
    ]
  } else {
    [#icon(kind, spec.accent)#h(1.5mm)#label]
    v(1mm)
    line(length: 100%, stroke: .4pt + rgb("B6B3A7"))
  }
}

#let section(kind, data, spec, style, index) = {
  let body = section-body(data.sections.filter(item => item.kind == kind), spec)
  let head = heading(kind, spec, style, index)
  block(width: 100%, breakable: false)[
    #if spec.mode == "margin" {
      grid(columns: (25mm, 1fr), gutter: 5mm, align: top, head, body)
    } else if style == "distribution-panel" {
      block(width: 100%, fill: white, inset: 2mm, stroke: .3pt + rgb("C9D2D7"))[
        #head#v(2mm)#body
      ]
    } else if style in ("signal-wave", "pcb-traces") {
      block(width: 100%, fill: spec.pale, inset: 2.5mm, radius: if style == "signal-wave" { 1.5mm } else { 0mm })[
        #head#v(2mm)#body
      ]
    } else if style == "plc-ladder" {
      block(width: 100%, stroke: (left: .6pt + rgb("53758D")), inset: (left: 3mm))[
        #head#v(2mm)#body
      ]
    } else { [#head#v(2mm)#body] }
  ]
}

#let header(data, spec, style) = {
  let words = [
    #text(font: if style == "editorial-serif" { ("Didot", "Liberation Serif", "Source Han Serif SC") } else { ("Courier", "Liberation Mono", "Noto Sans Mono CJK SC") }, size: 7.5pt, fill: spec.accent)[#spec.eyebrow]
    #v(2mm)
    #text(font: spec.font, size: if style in ("mono-minimal", "bauhaus") { 32pt } else { 28pt }, weight: "bold", fill: spec.accent)[#data.profile.name]
    #v(1.5mm)
    #text(size: 10pt, weight: "bold")[#data.profile.at("headline", default: "")]
    #for direction in data.profile.at("directions", default: ()) {
      if direction != data.profile.at("headline", default: "") { block(above: 1.8mm)[#text(size: 8pt, fill: spec.secondary)[#direction]] }
    }
    #v(2.5mm)
    #text(size: 8pt)[
      #for (key, label) in (("phone", "电话"), ("email", "邮箱"), ("city", "现居")) {
        let value = data.profile.contact.at(key, default: "")
        if value != "" { [#text(fill: spec.secondary)[#label]#h(1mm)#value#h(3mm)] }
      }
    ]
    #v(1.5mm)
    #text(size: 8pt, fill: spec.secondary)[#data.profile.at("summary", default: "")]
  ]
  block(width: 100%, height: 42mm)[
    #grid(columns: (139mm, 33mm), gutter: 8mm, align: top,
      words,
      if data.photo != none {
        align(right)[#block(width: 29mm, height: 38mm, fill: if style in ("cad-blueprint", "pcb-traces", "signal-wave") { spec.pale } else { rgb("FCFBF7") }, inset: 1mm, stroke: .35pt + spec.secondary)[#image(data.photo, width: 27mm, height: 36mm, fit: "cover")]]
      } else { [] })
  ]
}

#let resume(data, style) = {
  let spec = specs.at(style)
  set page(paper: "a4", margin: (x: 15mm, y: 14mm), background: image("assets/" + style + ".svg", width: 210mm, height: 297mm))
  set text(font: spec.font, lang: "zh", size: if spec.mode in ("margin", "ladder", "single") { 10pt } else { 9.6pt }, fill: spec.ink)
  set par(justify: false, leading: .55em, spacing: 1.3mm)
  let kinds = ("education", "skills", "certificates", "projects", "training", "experience").filter(kind => data.sections.any(item => item.kind == kind))
  let flow(selected, width) = page-flow(selected.map(kind => section(kind, data, spec, style, kinds.position(item => item == kind))), width, 216mm, max-size: 11.5pt, max-gap: if style == "nordic" { 18mm } else { 14mm })
  context {
    let head = header(data, spec, style)
    let body = if spec.mode in ("margin", "ladder", "single") { flow(kinds, 180mm) }
    else {
      let left-kinds = if spec.mode == "right" { kinds.filter(kind => kind not in ("skills", "certificates")) } else if spec.mode == "equal" { kinds.filter(kind => kind in ("education", "skills", "certificates")) } else { kinds.filter(kind => kind in ("skills", "certificates")) }
      let right-kinds = kinds.filter(kind => kind not in left-kinds)
      let widths = if spec.mode == "equal" { (86mm, 86mm) } else if spec.mode == "right" { (123mm, 49mm) } else if spec.mode == "cabinet" { (59mm, 113mm) } else if spec.mode == "scope" { (70mm, 102mm) } else { (67mm, 105mm) }
      grid(columns: widths, gutter: 8mm, align: top, flow(left-kinds, widths.at(0)), flow(right-kinds, widths.at(1)))
    }
    let natural = measure(block(width: 180mm)[#body]).height
    let header-height = measure(block(width: 180mm)[#head]).height
    let available = 269mm - header-height - 7mm
    assert(natural <= available, message: "LAYOUT_OVERFLOW: 正文超过 A4 一页安全范围")
    [#metadata((template: style, body_natural_height_mm: natural / 1mm, body_available_mm: available / 1mm, heading_font: spec.font, body_font: spec.font)) <layout-report>]
    head
    v(7mm)
    body
  }
}
