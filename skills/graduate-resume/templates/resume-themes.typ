// Controlled visual contract for the three graduate-resume compositions.
// The Python emitter supplies verified structural slots; this file owns only
// typography, geometry, and the visual treatment of those slots.

#set page(paper: "a4", margin: (top: 15mm, bottom: 15mm, left: 15mm, right: 15mm))
#set text(lang: "zh", font: "Noto Sans Mono CJK SC", weight: 400, size: 9.6pt)

#let space-xs = 1.058mm
#let space-sm = 2.117mm
#let space-md = 4.233mm
#let space-lg = 6.350mm
#let space-xl = 8.467mm

// These are intentionally theme-owned rather than a shared UI scale. The
// compositions have different column measures, so one fixed body size would
// make either the rail or the reading column feel cramped.
#let themes = (
  conservative: (surface: rgb("FFFFFF"), secondary: rgb("F2F4F7"), accent: rgb("183B62"), ink: rgb("172033"), body: 10.5pt, meta: 9pt, heading: 12pt, display: 27pt, leading: 0.65em),
  modern: (surface: rgb("FFFFFF"), secondary: rgb("EAF4F2"), accent: rgb("0F766E"), ink: rgb("172033"), body: 10.2pt, meta: 9pt, heading: 12pt, display: 27pt, leading: 0.65em),
  expressive: (surface: rgb("FFFEFA"), secondary: rgb("F0E8D9"), accent: rgb("9A6C18"), ink: rgb("1D3B35"), body: 10.2pt, meta: 9pt, heading: 12pt, display: 27pt, leading: 0.65em),
)

#let default-photo-policy = (
  photo_fit: "contain",
  crop_policy: "forbid",
  preserve_aspect_ratio: true,
  allow_stretch: false,
  allow_controlled_crop: false,
)

#let section-label(section) = (
  candidate: "基本信息", summary: "个人概述", education: "教育经历", skills: "专业技能",
  certificates: "证书与资格", projects: "项目经历", training: "实训经历", experience: "相关经历",
).at(section, default: section)

#let section-icon-license = "ISC License\n\nCopyright (c) for portions of Lucide are held by Cole Bemis 2013-2022 as part of Feather (MIT). All other copyright (c) for Lucide are held by Lucide Contributors 2022.\n\nPermission to use, copy, modify, and/or distribute this software for any\npurpose with or without fee is hereby granted, provided that the above\ncopyright notice and this permission notice appear in all copies.\n\nTHE SOFTWARE IS PROVIDED \"AS IS\" AND THE AUTHOR DISCLAIMS ALL WARRANTIES\nWITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF\nMERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR\nANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES\nWHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN\nACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF\nOR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.\n"
#let section-icons = (
  candidate: "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" > <circle cx=\"12\" cy=\"8\" r=\"5\" /> <path d=\"M20 21a8 8 0 0 0-16 0\" /> </svg>",
  summary: "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" > <path d=\"M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z\" /> <path d=\"M14 2v4a2 2 0 0 0 2 2h4\" /> <path d=\"M10 9H8\" /> <path d=\"M16 13H8\" /> <path d=\"M16 17H8\" /> </svg>",
  education: "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" > <path d=\"M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z\" /> <path d=\"M22 10v6\" /> <path d=\"M6 12.5V16a6 3 0 0 0 12 0v-3.5\" /> </svg>",
  skills: "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" > <path d=\"M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z\" /> </svg>",
  certificates: "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" > <path d=\"M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z\" /> <path d=\"m9 12 2 2 4-4\" /> </svg>",
  projects: "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" > <path d=\"M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z\" /> <path d=\"M8 10v4\" /> <path d=\"M12 10v2\" /> <path d=\"M16 10v6\" /> </svg>",
  training: "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" > <path d=\"M14 2v6a2 2 0 0 0 .245.96l5.51 10.08A2 2 0 0 1 18 22H6a2 2 0 0 1-1.755-2.96l5.51-10.08A2 2 0 0 0 10 8V2\" /> <path d=\"M6.453 15h11.094\" /> <path d=\"M8.5 2h7\" /> </svg>",
  experience: "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" > <path d=\"M12 12h.01\" /> <path d=\"M16 6V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2\" /> <path d=\"M22 13a18.15 18.15 0 0 1-20 0\" /> <rect width=\"20\" height=\"14\" x=\"2\" y=\"6\" rx=\"2\" /> </svg>",
)

#let section-icon(theme, section) = {
  let spec = themes.at(theme)
  let svg = section-icons.at(section, default: section-icons.at("summary"))
  box(baseline: 14%)[#image(bytes(svg.replace("currentColor", spec.accent.to-hex())), format: "svg", width: 4.2mm, height: 4.2mm)]
}

#let photo-slot(theme, image_handle: none, policy: default-photo-policy) = {
  let dimensions = if theme == "conservative" { (32mm, 42mm) } else if theme == "modern" { (28mm, 36mm) } else { (30mm, 40mm) }
  if image_handle == none { []
  } else if policy.crop_policy == "controlled" and policy.allow_controlled_crop {
    box(width: dimensions.at(0), height: dimensions.at(1), clip: true)[#image_handle]
  } else {
    box(width: dimensions.at(0), height: dimensions.at(1))[#image_handle]
  }
}

#let section-heading(theme, section) = {
  let spec = themes.at(theme)
  if theme == "expressive" {
    block(above: 3.5mm, below: 2mm)[
      #text(size: spec.heading, weight: 700, fill: spec.ink)[#section-icon(theme, section)#h(1mm)#section-label(section)]
      #v(1mm, weak: false)#line(length: 100%, stroke: 0.6pt + spec.accent)
      #v(1.5mm, weak: false)
    ]
  } else {
    block(above: 3.5mm, below: 2mm)[
      #text(size: spec.heading, weight: 700, fill: spec.accent)[#section-icon(theme, section)#h(1mm)#section-label(section)]
      #v(1mm, weak: false)#line(length: 100%, stroke: 0.65pt + spec.accent)
      #v(1.5mm, weak: false)
    ]
  }
}

#let body-paragraph(body, size: 10.2pt, fill: rgb("172033")) = {
  set text(size: size, fill: fill)
  block(width: 100%, inset: (left: 1em, bottom: 1.5mm))[#par(first-line-indent: 0pt)[#body]]
}

#let identity-details(theme, contact, personal, fill) = {
  let spec = themes.at(theme)
  let primary = contact.filter(pair => pair.at(0) in ([电话], [邮箱]))
  let remaining = contact.filter(pair => pair.at(0) not in ([电话], [邮箱]))
  let values = primary + personal + remaining
  let label-fill = if theme == "expressive" { rgb("B9CDC6") } else { rgb("667685") }
  let cells = values.map(pair => grid(columns: (15mm, 1fr), column-gutter: 1mm, align: (left, top),
    text(size: spec.meta, fill: label-fill)[#pair.at(0)],
    text(size: spec.meta, fill: fill)[#pair.at(1)],
  ))
  if values != () {
    block(above: 3mm)[#grid(columns: (1fr, 1fr), column-gutter: 8mm, row-gutter: 2.5mm, ..cells)]
  }
}

#let identity-block(theme, name: [], headline: [], summary: [], contact: (), personal: (), directions: [], photo: none) = {
  let spec = themes.at(theme)
  if theme == "expressive" {
    block(width: 100%, fill: spec.ink, inset: 5mm, below: 3mm)[
      #grid(columns: (1fr, auto), gutter: space-lg)[
        #block(below: 2mm)[#text(size: spec.display, weight: 700, fill: white)[#name]]
        #if headline != [] [#block(below: 2mm)[#text(size: 11pt, weight: 700, fill: rgb("F6D894"))[#headline]]]
        #if directions != [] [#v(space-sm)#text(size: spec.meta, fill: white)[#directions]]
        #identity-details(theme, contact, personal, white)
      ][#photo-slot(theme, image_handle: photo)]
      #if summary != [] [#v(space-sm)#body-paragraph(summary, size: spec.meta, fill: white)]
    ]
  } else {
    let words = [
      #block(below: 2mm)[#text(size: spec.display, weight: 700, fill: spec.accent)[#name]]
      #if headline != [] [#block(below: 2mm)[#text(size: 12pt, weight: 700, fill: spec.ink)[#headline]]]
      #if directions != [] [#v(space-sm)#text(size: spec.meta, fill: spec.accent)[#directions]]
      #identity-details(theme, contact, personal, spec.ink)
      #if summary != [] [#v(space-sm)#body-paragraph(summary, size: spec.meta, fill: spec.ink)]
    ]
    if photo == none {
      block(width: 100%, inset: (bottom: 3mm), stroke: (bottom: 0.75pt + spec.accent), below: 3mm)[#words]
    } else {
      block(inset: (bottom: 3mm))[
        #grid(columns: (1fr, auto), gutter: space-lg)[#block(inset: (bottom: space-md), stroke: (bottom: 0.75pt + spec.accent))[#words]][#photo-slot(theme, image_handle: photo)]
      ]
    }
  }
}

#let outcome-paragraph(theme, body) = {
  let spec = themes.at(theme)
  set text(size: spec.body, fill: spec.ink)
  grid(columns: (1em, 1fr), gutter: 0pt, align: top,
    box(width: 1em, height: 1em)[#align(center + horizon)[#move(dy: -0.1335em)[#text(fill: spec.accent)[•]]]],
    par(first-line-indent: 0pt)[#body],
  )
}

#let fact-block(theme, section, values, show-heading: true, detail-gap: 0mm) = block[
  #if show-heading [#section-heading(theme, section)]
  #for (index, value) in values.enumerate() [#body-paragraph(value, size: themes.at(theme).body, fill: themes.at(theme).ink)#if index < values.len() - 1 [#v(detail-gap, weak: false)]]
]

#let skills-block(theme, section, group: [], items: (), note: [], show-heading: true, detail-gap: 0mm) = block(above: 1.5mm, below: 1.5mm, breakable: false)[
  #if show-heading [#section-heading(theme, section)]
  #if group != [] [#text(size: themes.at(theme).body, weight: 700, fill: themes.at(theme).ink)[#group]#v(1.3mm + detail-gap, weak: false)]
  #for (index, item) in items.enumerate() [#body-paragraph(item, size: themes.at(theme).body, fill: themes.at(theme).ink)#if index < items.len() - 1 [#v(detail-gap, weak: false)]]
  #if note != [] [#v(space-xs)#body-paragraph(note, size: themes.at(theme).meta, fill: themes.at(theme).ink)]
  #v(2mm, weak: false)
]

#let resume-entry(theme, section, id, title: [], meta: [], summary: [], outcomes: (), show-heading: true, detail-gap: 0mm) = {
  let spec = themes.at(theme)
  block(breakable: false)[
    #metadata((section: section, id: id))
    #if show-heading [#section-heading(theme, section)]
    #block(above: space-xs, inset: (left: if theme == "expressive" { space-sm } else { 0pt }), stroke: if theme == "expressive" { (left: 0.9pt + spec.secondary) } else { none })[
      #text(size: spec.body, weight: 700, fill: spec.ink)[#title]
      #if meta != [] [#v(1.2mm + detail-gap, weak: false)#text(size: spec.meta, fill: spec.accent)[#meta]]
      #if summary != [] [#v(1.2mm + detail-gap, weak: false)#body-paragraph(summary, size: spec.body, fill: spec.ink)]
      #for outcome in outcomes [#v(space-xs + detail-gap, weak: false)#outcome-paragraph(theme, outcome)]
    ]
    #v(2.5mm, weak: false)
  ]
}

#let rail-block(theme, content) = block(above: space-md)[#content]
#let continuation-anchor(theme) = block(above: 0pt, below: space-sm)[#line(length: 100%, stroke: 0.75pt + themes.at(theme).accent)]

// New structural entry point. Unlike theme-layout, each theme receives actual
// semantic slots so a rail, a header, and a main column cannot collapse into
// the same generic body flow.
#let resume-metrics(theme, header: [], sidebar: [], main: [], continuation: false, sidebar-width: 70mm, leading: 0.65em) = context {
  let spec = themes.at(theme)
  let styled(content) = [
    #set text(font: "Noto Sans Mono CJK SC", size: spec.body)
    #set par(leading: leading, spacing: 0pt, justify: false)
    #block(width: 100%)[#content]
  ]
  let header-size = measure(styled([#if continuation [#continuation-anchor(theme)]#header]), width: 180mm).height / 1mm
  let has-sidebar = sidebar != [] and theme != "conservative"
  let side-size = if has-sidebar { measure(styled(sidebar), width: sidebar-width - if theme == "modern" { 7mm } else { 0mm }).height / 1mm + if theme == "modern" { 7 } else { 0 } } else { 0 }
  let main-size = measure(styled(main), width: if has-sidebar { 174mm - sidebar-width } else { 180mm }).height / 1mm + if has-sidebar and theme == "modern" { 3.5 } else { 0 }
  [#metadata((header: header-size, sidebar: side-size, main: main-size)) <resume-measurement>]
}

#let resume-body(theme, header: [], sidebar: [], main: [], continuation: false, sidebar-width: 70mm, leading: 0.65em) = {
  let spec = themes.at(theme)
  if theme in ("modern", "expressive") and (sidebar == [] or main == []) {
    panic("two-column themes require content in both columns")
  }
  set text(font: "Noto Sans Mono CJK SC", size: spec.body)
  set par(leading: leading, spacing: 0pt, justify: false)
  block(width: 100%)[
    #if continuation [#continuation-anchor(theme)]
    #header
    #if theme == "conservative" {
      main
    } else if theme == "modern" {
      grid(columns: (sidebar-width, 174mm - sidebar-width), gutter: 6mm, align: top)[
        #block(width: 100%, fill: spec.secondary, inset: 3.5mm, radius: 1.5mm)[#sidebar]
      ][#block(inset: (top: 3.5mm))[#main]]
    } else if theme == "expressive" {
      grid(columns: (sidebar-width, 174mm - sidebar-width), gutter: 6mm, align: top)[#sidebar][#main]
    } else { panic("unknown frozen theme") }
  ]
}

#let resume-page(theme, header: [], sidebar: [], main: [], continuation: false, sidebar-width: 70mm, leading: 0.65em) = {
  set page(fill: themes.at(theme).surface)
  resume-body(theme, header: header, sidebar: sidebar, main: main, continuation: continuation, sidebar-width: sidebar-width, leading: leading)
}

// Compatibility entry point for external probes. Runtime output uses
// resume-page above.
#let theme-layout(theme, body) = resume-page(theme, main: body)
