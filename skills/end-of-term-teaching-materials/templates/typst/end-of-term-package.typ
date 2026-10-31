// Fixed absolute-position Typst package template for end-of-term teaching materials.
// The renderer replaces PACKAGE_BODY with generated page fragments.
// Coordinates follow the reference scorebook prototype and use A4 points.

#set page(width: 595.3pt, height: 841.9pt, margin: 0pt)
#set text(lang: "zh", font: ("SimSun", "NSimSun", "Songti SC", "STSong"), size: 12pt)
#set par(leading: 0.05em)

#let ptext(x, y, w, h, size, body, pos: center + horizon, weight: "regular") = place(dx: x, dy: y)[#box(width: w, height: h, clip: true, inset: 0pt)[
#align(pos)[#text(size: size, weight: weight)[#body]]]]
#let ptext_nc(x, y, w, h, size, body, pos: center + horizon, weight: "regular") = place(dx: x, dy: y)[#box(width: w, height: h, clip: false, inset: 0pt)[
#align(pos)[#text(size: size, weight: weight)[#body]]]]
// Preserve the existing scorebook-cover rendering independently of body changes.
#let cover-fitted-body(w, h, size, body, weight: "regular") = context {
  let usable-w = w - 2pt
  let usable-h = h - 1pt
  let candidate(s) = block(width: usable-w, breakable: false, inset: 0pt)[
    #set text(size: s, weight: weight)
    #set par(leading: 0.05em, spacing: 0pt)
    #body
  ]
  let chosen = size
  for step in range(121) {
    let bounds = measure(candidate(chosen))
    if bounds.height <= usable-h { break }
    chosen -= 0.2pt
    assert(chosen >= 5pt, message: "Text cannot fit its fixed cell at a readable size; enlarge the field or use a continuation page.")
  }
  assert(measure(candidate(chosen)).height <= usable-h, message: "Text exceeds fixed cell height.")
  candidate(chosen)
}
#let pcover(x, y, w, h, size, body, pos: center + horizon, weight: "regular") = place(dx: x, dy: y)[#box(width: w, height: h, clip: false, inset: 0pt)[
#align(pos)[#cover-fitted-body(w, h, size, body, weight: weight)]]]

// Variable-length metadata/tasks use their own centered box. Explicit text
// edges make each wrapped baseline >= the glyph height, independent of font metrics.
#let fitted-body(w, h, size, body) = context {
  let candidate(s) = block(width: w - 8pt, breakable: false, inset: 0pt)[
    #set text(size: s, top-edge: 0.85em, bottom-edge: 0.2em, overhang: false)
    #set par(leading: 0.30em, spacing: 0pt, justify: false)
    #align(center)[#body]
  ]
  let chosen = size
  for step in range(121) {
    let bounds = measure(candidate(chosen))
    if bounds.height <= h - 2pt and bounds.width <= w { break }
    chosen -= 0.2pt
    assert(chosen >= 5pt, message: "Name cannot fit its field; enlarge or reflow the field.")
  }
  let bounds = measure(candidate(chosen))
  assert(bounds.height <= h - 2pt and bounds.width <= w,
    message: "Name exceeds its field.")
  candidate(chosen)
}
#let pfit(x, y, w, h, size, body) = place(dx: x, dy: y)[
  #box(width: w, height: h, clip: false, inset: 0pt)[
    #align(center + horizon)[#fitted-body(w, h, size, body)]
  ]
]

// Each class/major is a single unbroken line. Labels are sibling fields,
// outside this left-aligned stack; fit the longest complete name before shrinking.
#let pnames(x, y, w, h, size, names) = context {
  let candidate(s) = stack(dir: ttb, spacing: s * 0.18,
    ..names.map(name => box(text(size: s, top-edge: 0.85em, bottom-edge: 0.2em, name))))
  let chosen = size
  while measure(candidate(chosen)).width > w - 2pt or measure(candidate(chosen)).height > h - 2pt {
    chosen -= 0.2pt
    assert(chosen >= 5pt, message: "Complete names cannot fit one name per line; enlarge the field.")
  }
  place(dx: x, dy: y)[#box(width: w, height: h, clip: false)[
    #align(left + horizon)[#candidate(chosen)]
  ]]
}

// Scores fit on one line; never wrap a decimal or spill into the next column.
#let pscore(x, y, w, h, size, body) = context {
  let candidate(s) = text(size: s, top-edge: 0.85em, bottom-edge: 0.2em)[#body]
  let chosen = size
  while measure(candidate(chosen)).width > w - 2pt or measure(candidate(chosen)).height > h - 1pt {
    chosen -= 0.2pt
    assert(chosen >= 5pt, message: "Score cannot fit its cell.")
  }
  place(dx: x, dy: y)[#box(width: w, height: h, clip: false)[
    #align(center + horizon)[#candidate(chosen)]
  ]]
}

#let ppara_nc(x, y, w, h, size, body, first-indent: 0em, pos: center + horizon, body-ratio: 0.94) = place(dx: x, dy: y)[#box(width: w, height: h, clip: false, inset: 0pt)[
#align(pos)[#box(width: w * body-ratio)[#align(left)[
#set text(size: size)
#par(leading: 0.65em)[#box(width: first-indent)[]#body]
]]]
]]
#let ptitle_nc(x, y, w, h, size, body, pos: center + horizon) = place(dx: x, dy: y)[#box(width: w, height: h, clip: false, inset: 0pt)[
#align(pos)[#text(size: size, weight: "bold", font: ("FZXiaoBiaoSong-B05", "FZXiaoBiaoSong-B05S", "SimSun", "Songti SC"))[#body]]]]
#let hline(x1, x2, y, s: 0.580pt) = place(dx: x1, dy: y)[#line(length: x2 - x1, stroke: s)]
#let vline(x, y1, y2, s: 0.580pt) = place(dx: x, dy: y1)[#line(length: y2 - y1, angle: 90deg, stroke: s)]
#let diag(x1, y1, len, deg, s: 0.580pt) = place(dx: x1, dy: y1)[#line(length: len, angle: deg, stroke: s)]
#let pagebox(body) = box(width: 595.3pt, height: 841.9pt)[#body]

#set document(title: "{{DOCUMENT_TITLE}}", author: "{{DOCUMENT_AUTHOR}}")

{{PACKAGE_BODY}}
