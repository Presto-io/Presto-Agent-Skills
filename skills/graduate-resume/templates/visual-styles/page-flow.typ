#let page-flow(groups, width, available, max-size: 11.5pt, min-size: 9.6pt) = context {
  set block(above: 0pt, below: 0pt)
  if groups.len() > 0 {
    let chosen = min-size
    let natural = 0pt
    for candidate in (12pt, 11.5pt, 11pt, 10.5pt, 10pt, 9.6pt, 9.2pt) {
      if candidate <= max-size and candidate >= min-size {
        let total = groups.map(item => measure(block(width: width)[#set text(size: candidate)
          #set par(leading: .62em)
          #item]).height).sum(default: 0pt)
        if total + (groups.len() - 1) * 3mm <= available { chosen = candidate; natural = total; break }
      }
    }
    assert(natural > 0pt, message: "LAYOUT_OVERFLOW: 满页排版无法容纳正文")
    let gap = (available - 3mm - natural) / calc.max(1, groups.len() - 1)
    set text(size: chosen)
    set par(leading: .62em)
    for (index, item) in groups.enumerate() {
      item
      if index < groups.len() - 1 { v(gap) }
    }
    [#metadata((font_pt: chosen / 1pt, natural_mm: natural / 1mm, available_mm: available / 1mm, gap_mm: gap / 1mm)) <page-flow-report>]
  }
}
