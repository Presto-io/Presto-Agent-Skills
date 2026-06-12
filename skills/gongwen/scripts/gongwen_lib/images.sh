image_basename_no_ext() {
  local path="$1" base
  base="${path##*/}"
  printf '%s' "${base%.*}"
}

emit_single_image() {
  local path="$1" caption fig="$2"
  caption="$(image_basename_no_ext "$path")"
  printf '#figure(\n'
  printf '  context {\n'
  printf '    let img = image("%s")\n' "$(escape_string "$path")"
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'IMG'
    let img-size = measure(img)
    let x = img-size.width
    let y = img-size.height
    let max-size = 13.4cm

    let new-x = x
    let new-y = y

    if x > max-size {
      let scale = max-size / x
      new-x = max-size
      new-y = y * scale
    }

    if new-y > max-size {
      let scale = max-size / new-y
      new-x = new-x * scale
      new-y = max-size
    }

IMG
  printf '    image("%s", width: new-x, height: new-y)\n' "$(escape_string "$path")"
  printf '  },\n'
  printf '  placement: auto,\n'
  printf '  caption: [%s],\n' "$(escape_content "$caption")"
  printf ') <fig-%s>\n' "$fig"
}

parse_images_in_line() {
  local line="$1" rest="$1" before
  IMAGE_ALTS=()
  IMAGE_PATHS=()
  while [[ "$rest" == *"!["* && "$rest" == *"]("* && "$rest" == *")"* ]]; do
    before="${rest#*!\[}"
    IMAGE_ALTS+=("${before%%]*}")
    before="${before#*](}"
    IMAGE_PATHS+=("${before%%)*}")
    rest="${before#*)}"
  done
}

emit_multi_image() {
  local count="${#IMAGE_PATHS[@]}" i main alt path cap
  main="${IMAGE_ALTS[0]}"
  printf '\n#context {\n'
  printf '  let paths = ('
  for ((i = 0; i < count; i++)); do
    (( i > 0 )) && printf ', '
    printf '"%s"' "$(escape_string "${IMAGE_PATHS[$i]}")"
  done
  printf ')\n'
  printf '  let captions = ('
  for ((i = 0; i < count; i++)); do
    (( i > 0 )) && printf ', '
    cap="$(image_basename_no_ext "${IMAGE_PATHS[$i]}")"
    printf '"%s"' "$(escape_string "$cap")"
  done
  printf ')\n'
  printf '  let alts = ('
  for ((i = 0; i < count; i++)); do
    (( i > 0 )) && printf ', '
    printf '"%s"' "$(escape_string "${IMAGE_ALTS[$i]}")"
  done
  printf ')\n\n'
  printf '  let is_subfigure = true\n'
  printf '  let main_caption = "%s"\n\n' "$(escape_string "$main")"
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'MULTI'
  let gap = 0.3cm
  let max-width = 13.4cm
  let min-height = 6cm

  let sizes = paths.zip(captions).zip(alts).map(item => {
    let p = item.at(0).at(0)
    let c = item.at(0).at(1)
    let alt = item.at(1)
    let img = image(p)
    let s = measure(img)
    (width: s.width, height: s.height, path: p, caption: c, alt: alt, ratio: s.width / s.height)
  })

  let calc-row-height(imgs, total-width) = {
    let ratio-sum = imgs.map(i => i.ratio).sum()
    total-width / ratio-sum
  }

  let rows = ()

  if is_subfigure {
    rows.push(sizes)
  } else {
    let remaining = sizes

    while remaining.len() > 0 {
      let row = ()
      let found = false

      for n in range(1, remaining.len() + 1) {
        let candidate = remaining.slice(0, n)
        let gaps = (n - 1) * gap
        let available-width = max-width - gaps
        let row-h = calc-row-height(candidate, available-width)

        if row-h < min-height and n > 1 {
          row = remaining.slice(0, n - 1)
          remaining = remaining.slice(n - 1)
          found = true
          break
        }
      }

      if not found {
        row = remaining
        remaining = ()
      }

      rows.push(row)
    }
  }

  let render-rows(rows) = {
    for row in rows {
      let n = row.len()
      let gaps = (n - 1) * gap
      let available-width = max-width - gaps
      let row-height = calc-row-height(row, available-width)

      if row-height > max-width {
        row-height = max-width
      }

      align(center, grid(
        columns: n,
        gutter: gap,
        ..row.enumerate().map(item => {
          let i = item.at(0)
          let img-data = item.at(1)
          let w = row-height * img-data.ratio

          if is_subfigure {
             let sub-label = numbering("a", i + 1)
             let sub-text = [ (#sub-label) #img-data.caption ]

             v(0.5em)
             align(center, block({
               image(img-data.path, width: w, height: row-height)
               align(center, text(font: FONT_FS, size: zh(3))[#sub-text])
             }))
          } else {
             figure(
               image(img-data.path, width: w, height: row-height),
               caption: [ #img-data.caption ]
             )
          }
        })
      ))
      if is_subfigure { v(0.5em) } else { v(0.3em) }
    }
  }

  if is_subfigure {
    figure(
      context { render-rows(rows) },
      placement: auto,
      caption: [ #main_caption ]
    )
  } else {
    render-rows(rows)
  }
}

MULTI
}
