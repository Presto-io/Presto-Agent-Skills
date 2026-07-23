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
  conservative: (surface: rgb("FFFFFF"), secondary: rgb("F2F4F7"), accent: rgb("183B62"), ink: rgb("172033"), body: 10.1pt, meta: 9pt, heading: 12.6pt, display: 23pt, leading: 1.44em),
  modern: (surface: rgb("FFFFFF"), secondary: rgb("EAF4F2"), accent: rgb("0F766E"), ink: rgb("172033"), body: 9.45pt, meta: 8.5pt, heading: 12pt, display: 18pt, leading: 1.42em),
  expressive: (surface: rgb("FFFEFA"), secondary: rgb("F0E8D9"), accent: rgb("9A6C18"), ink: rgb("1D3B35"), body: 9.8pt, meta: 8.7pt, heading: 12.5pt, display: 21pt, leading: 1.46em),
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
    block(above: space-lg, below: space-xs)[
      #text(size: spec.heading, weight: 700, fill: spec.ink)[#section-label(section)]
      #h(space-xs)#text(size: spec.meta, weight: 700, fill: spec.accent)[#if section == "projects" [01] else if section == "education" [02] else if section == "skills" [03]]
      #v(space-xs)#line(length: 100%, stroke: 0.6pt + spec.accent)
    ]
  } else {
    block(above: space-lg, below: space-xs)[
      #text(size: spec.heading, weight: 700, fill: spec.accent)[#section-label(section)]
      #v(space-xs)#line(length: 100%, stroke: 0.65pt + spec.accent)
    ]
  }
}

#let identity-block(theme, name: [], headline: [], summary: [], contact: [], directions: [], photo: none) = {
  let spec = themes.at(theme)
  if theme == "expressive" {
    block(fill: spec.ink, inset: 5.5mm)[
      #grid(columns: (1fr, auto), gutter: space-lg)[
        #text(size: spec.display, weight: 700, fill: white)[#name]
        #if headline != [] [#v(space-xs)#text(size: 11pt, weight: 700, fill: rgb("F6D894"))[#headline]]
        #if directions != [] [#v(space-sm)#text(size: spec.meta, fill: white)[#directions]]
        #if contact != [] [#v(space-xs)#text(size: spec.meta, fill: white)[#contact]]
      ][#photo-slot(theme, image_handle: photo)]
      #if summary != [] [#v(space-sm)#text(size: spec.body, fill: white)[#summary]]
    ]
  } else if theme == "modern" {
    [
      #text(size: spec.display, weight: 700, fill: spec.accent)[#name]
      #if headline != [] [#v(space-xs)#text(size: 10pt, weight: 700, fill: spec.ink)[#headline]]
      #if directions != [] [#v(space-sm)#text(size: spec.meta, fill: spec.accent)[#directions]]
      #if contact != [] [#v(space-sm)#text(size: spec.meta, fill: spec.ink)[#contact]]
      #if summary != [] [#v(space-sm)#text(size: spec.body)[#summary]]
      #if photo != none [#v(space-md)#photo-slot(theme, image_handle: photo)]
    ]
  } else {
    let words = [
      #text(size: spec.display, weight: 700, fill: spec.accent)[#name]
      #if headline != [] [#v(space-xs)#text(size: 12pt, weight: 700, fill: spec.ink)[#headline]]
      #if directions != [] [#v(space-sm)#text(size: spec.meta, fill: spec.accent)[#directions]]
      #if contact != [] [#v(space-sm)#text(size: spec.meta, fill: spec.ink)[#contact]]
      #if summary != [] [#v(space-sm)#text(size: spec.body)[#summary]]
    ]
    if photo == none {
      block(inset: (bottom: space-md), stroke: (bottom: 0.75pt + spec.accent))[#words]
    } else {
      grid(columns: (1fr, auto), gutter: space-lg)[#block(inset: (bottom: space-md), stroke: (bottom: 0.75pt + spec.accent))[#words]][#photo-slot(theme, image_handle: photo)]
    }
  }
}

#let fact-block(theme, section, values, show-heading: true) = block[
  #if show-heading [#section-heading(theme, section)]
  #for (index, value) in values.enumerate() [#text(size: themes.at(theme).body)[#value]#if index < values.len() - 1 [#linebreak()]]
]

#let skills-block(theme, section, group: [], items: (), note: [], show-heading: true) = block[
  #if show-heading [#section-heading(theme, section)]
  #if group != [] [#text(size: themes.at(theme).body, weight: 700, fill: themes.at(theme).ink)[#group]#v(space-xs)]
  #for (index, item) in items.enumerate() [#text(size: themes.at(theme).body)[#item]#if (index < items.len() - 1) { text(fill: themes.at(theme).accent, "  /  ") }]
  #if note != [] [#v(space-xs)#text(size: themes.at(theme).meta)[#note]]
]

#let resume-entry(theme, section, id, title: [], meta: [], summary: [], outcomes: (), show-heading: true) = {
  let spec = themes.at(theme)
  block(breakable: false)[
    #metadata((section: section, id: id))
    #if show-heading [#section-heading(theme, section)]
    #block(above: space-xs, inset: (left: if theme == "expressive" { space-sm } else { 0pt }), stroke: if theme == "expressive" { (left: 0.9pt + spec.secondary) } else { none })[
      #text(size: spec.body, weight: 700, fill: spec.ink)[#title]
      #if meta != [] [#h(space-sm)#text(size: spec.meta, fill: spec.accent)[#meta]]
      #if summary != [] [#v(space-xs)#text(size: spec.body)[#summary]]
      #for outcome in outcomes [#v(space-xs)#text(size: spec.body)[#text(fill: spec.accent)[•] #outcome]]
    ]
  ]
}

#let rail-block(theme, content) = block(above: space-md)[#content]
#let continuation-anchor(theme) = block(above: 0pt, below: space-sm)[#line(length: 100%, stroke: 0.75pt + themes.at(theme).accent)]

// New structural entry point. Unlike theme-layout, each theme receives actual
// semantic slots so a rail, a header, and a main column cannot collapse into
// the same generic body flow.
#let resume-page(theme, header: [], sidebar: [], main: [], continuation: false) = {
  let spec = themes.at(theme)
  set page(fill: spec.surface)
  set text(font: "Noto Sans Mono CJK SC", size: spec.body)
  set par(leading: spec.leading)
  if continuation [#continuation-anchor(theme)]
  if theme == "conservative" { [#header #main]
  } else if theme == "modern" {
    [#grid(columns: (31%, 1fr), gutter: 6mm)[
      #block(fill: spec.secondary, inset: 4.5mm, height: 264mm)[#header #sidebar]
    ][#main]]
  } else if theme == "expressive" {
    [#header
    #grid(columns: (38%, 1fr), gutter: 6mm)[#sidebar][#main]]
  } else { panic("unknown frozen theme") }
}

// Compatibility entry point for external probes. Runtime output uses
// resume-page above.
#let theme-layout(theme, body) = resume-page(theme, main: body)
