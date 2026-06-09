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
#let hline(x1, x2, y, s: 0.580pt) = place(dx: x1, dy: y)[#line(length: x2 - x1, stroke: s)]
#let vline(x, y1, y2, s: 0.580pt) = place(dx: x, dy: y1)[#line(length: y2 - y1, angle: 90deg, stroke: s)]
#let diag(x1, y1, len, deg, s: 0.580pt) = place(dx: x1, dy: y1)[#line(length: len, angle: deg, stroke: s)]
#let pagebox(body) = box(width: 595.3pt, height: 841.9pt)[#body]

#set document(title: "{{DOCUMENT_TITLE}}", author: "{{DOCUMENT_AUTHOR}}")

{{PACKAGE_BODY}}
