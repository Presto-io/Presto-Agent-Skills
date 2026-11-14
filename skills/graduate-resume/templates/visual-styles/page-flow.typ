#import "body-policy.typ": body-size
#let page-flow(groups, width, available, max-size: 11.5pt, min-size: 9.6pt, max-gap: 14mm) = context {
  set block(above: 0pt, below: 0pt)
  if groups.len() > 0 {
    let chosen = body-size()
    let leading = .62em
    let natural = groups.map(item => measure(block(width: width)[#set text(size: chosen)
      #set par(leading: leading)
      #item]).height).sum(default: 0pt)
    assert(natural + (groups.len() - 1) * 3mm <= available, message: "LAYOUT_OVERFLOW: 正文无法容纳")
    // Spread short columns through readable line spacing before adding section gaps.
    for candidate in (.76em, .9em, 1.05em, 1.2em, 1.35em) {
      let total = groups.map(item => measure(block(width: width)[#set text(size: chosen)
        #set par(leading: candidate)
        #item]).height).sum(default: 0pt)
      if natural < available * .9 and total + (groups.len() - 1) * 3mm <= available - 3mm {
        leading = candidate
        natural = total
      }
    }
    let gap = calc.min(max-gap, (available - 3mm - natural) / calc.max(1, groups.len() - 1))
    set text(size: chosen)
    set par(leading: leading)
    for (index, item) in groups.enumerate() {
      item
      if index < groups.len() - 1 { v(gap) }
    }
    [#metadata((font_pt: chosen / 1pt, natural_mm: natural / 1mm, available_mm: available / 1mm, gap_mm: gap / 1mm, groups: groups.len(), used_mm: (natural + gap * (groups.len() - 1)) / 1mm)) <page-flow-report>]
  }
}
