// Pure visual contract for the Phase 47 frozen resume plan.
// The emitter supplies verified content and an already-contained image handle.

#set page(
  paper: "a4",
  margin: (top: 14mm, bottom: 14mm, left: 15mm, right: 15mm),
)
#set text(lang: "zh", font: "Noto Sans Mono CJK SC", weight: 400, size: 10.5pt)
#set par(leading: 1.45em)

#let type-metadata = 9pt
#let type-body = 10.5pt
#let type-heading = 14pt
#let type-display = 22pt

// UI-SPEC spacing scale: 4px at 96dpi is 1.058mm.
#let space-xs = 1.058mm
#let space-sm = 2.117mm
#let space-md = 4.233mm
#let space-lg = 6.350mm
#let space-xl = 8.467mm

#let themes = (
  conservative: (
    layout: "single-column-right-photo",
    colors: (surface: rgb("FFFFFF"), secondary: rgb("F2F4F7"), accent: rgb("1F4E79")),
    photo_slot: (width: 32mm, height: 42mm, position: "top-right"),
    no_photo: "remove-slot-and-decoration",
  ),
  modern: (
    layout: "sidebar-photo",
    colors: (surface: rgb("FFFFFF"), secondary: rgb("EFF5F4"), accent: rgb("0F766E")),
    photo_slot: (width: 28mm, height: 36mm, position: "left-sidebar"),
    no_photo: "move-sidebar-content-up",
  ),
  expressive: (
    layout: "header-photo",
    colors: (surface: rgb("FFFEFA"), secondary: rgb("F3F1EA"), accent: rgb("8A6A20")),
    photo_slot: (width: 30mm, height: 40mm, position: "header-right"),
    no_photo: "expand-identity-bar",
  ),
)

#let default-photo-policy = (
  photo_fit: "contain",
  crop_policy: "forbid",
  preserve_aspect_ratio: true,
  allow_stretch: false,
  allow_controlled_crop: false,
)

#let fact-block(section, body) = block[
  #text(size: type-heading, weight: 600)[#section]
  #v(space-xs)
  #body
]

#let list-entry(section, id, body) = block(breakable: false)[
  #metadata((section: section, id: id))
  #body
]

#let photo-slot(theme, image_handle: none, policy: default-photo-policy) = {
  let slot = themes.at(theme).photo_slot
  if image_handle == none {
    // no-photo: no image, border, accent stripe, or reserved slot is emitted.
    []
  } else if policy.crop_policy == "controlled" and policy.allow_controlled_crop {
    // Only a registered ThemeSpec with a verified subject-safe-area contract reaches here.
    box(width: slot.width, height: slot.height, clip: true, inset: 0pt)[#image_handle]
  } else {
    // The frozen default is contain: preserve aspect ratio and never stretch or crop.
    box(width: slot.width, height: slot.height, clip: false, inset: 0pt)[#image_handle]
  }
}

#let theme-layout(theme, photo: none, photo_policy: default-photo-policy, body) = {
  let spec = themes.at(theme)
  set page(fill: spec.colors.surface)
  set text(font: "Noto Sans Mono CJK SC", size: type-body)
  if theme == "conservative" {
    align(left)[#body]
  } else if theme == "modern" {
    grid(columns: (31%, 69%), gutter: 6mm)[#body]
  } else if theme == "expressive" {
    grid(columns: (38%, 62%), gutter: 6mm)[#body]
  } else {
    panic("unknown frozen theme")
  }
}
