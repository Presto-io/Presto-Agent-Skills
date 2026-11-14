#import "new-layout.typ": resume as new-resume
#import "groups/first/layout.typ": resume as first
#import "groups/second/layout.typ": resume as second
#import "groups/third/layout.typ": resume as third
#import "groups/aesthetic/layout.typ": resume as aesthetic

#import "reference/layout.typ": resume as reference

#let resume(data, style) = {
  if style in ("blue-poster", "serif-blue", "purple-doodle", "purple-sidebar", "rust-editorial", "blue-business", "blue-floral", "beige-notebook") { reference(data, style) }
  else if style in ("single-column-02", "sidebar-left-02", "single-column-03") { first(data, style) }
  else if style in ("banner-navy", "sidebar-right", "timeline-copper", "balanced-columns", "soft-cards", "centered-red") { second(data, style) }
  else if style in ("bento-mosaic", "technical-matrix", "swiss-grid", "feature-dashboard") { third(data, style) }
  else if style in ("chinese-classic", "steampunk", "dreamcore", "handmade-collage", "cyberpunk", "art-deco", "botanical", "brutalist") { aesthetic(data, style) }
  else { new-resume(data, style) }
}
