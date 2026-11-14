"""Compose runtime-only reference portraits from caller-supplied photos."""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


SCALE = 8
SIZE = (210 * SCALE, 297 * SCALE)
RANDOM = random.Random(20261025)


def point(coordinates):
    return tuple(round(value * SCALE) for value in coordinates)


def rectangle(draw, bounds, fill, radius=0, outline=None, width=1):
    draw.rounded_rectangle(point(bounds), radius=radius * SCALE, fill=fill, outline=outline, width=width)


def path(draw, coordinates, fill, width=1):
    draw.line([point(pair) for pair in coordinates], fill=fill, width=max(1, round(width * SCALE)), joint="curve")


def bezier(points, count=120):
    result = []
    for step in range(count + 1):
        ratio = step / count
        result.append(tuple((1-ratio)**3*points[0][axis] + 3*(1-ratio)**2*ratio*points[1][axis] + 3*(1-ratio)*ratio**2*points[2][axis] + ratio**3*points[3][axis] for axis in (0, 1)))
    return result


def grain(color, strength=2.3):
    base = np.array(Image.new("RGB", SIZE, color), dtype=np.float32)
    random_source = np.random.default_rng(20261025)
    fine = random_source.normal(0, strength, (SIZE[1], SIZE[0], 1))
    coarse = Image.fromarray(random_source.integers(90, 166, (150, 110), dtype=np.uint8)).resize(SIZE, Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(4))
    coarse = (np.asarray(coarse, dtype=np.float32)[..., None]-128) * .035
    return Image.fromarray(np.uint8(np.clip(base + fine + coarse, 0, 255)))


def sketch(draw, coordinates, color="#292630", width=.55, repeats=2):
    for repeat in range(repeats):
        jittered = [(horizontal + RANDOM.uniform(-.25, .25), vertical + RANDOM.uniform(-.25, .25)) for horizontal, vertical in coordinates]
        path(draw, jittered, color, width)


def star(draw, horizontal, vertical, radius=4, color="#332F39"):
    points = [(horizontal + radius * math.sin(index * 4 * math.pi / 5), vertical - radius * math.cos(index * 4 * math.pi / 5)) for index in range(6)]
    sketch(draw, points, color, .45)


def brush(draw, horizontal, vertical, width, height, fill="#B7A1DD"):
    rows = max(20, round(height*SCALE))
    for index in range(rows):
        offset = index * height / rows
        path(draw, [(horizontal + RANDOM.uniform(-1.2, .8), vertical+offset), (horizontal+width+RANDOM.uniform(-.8, 1.3), vertical+offset+RANDOM.uniform(-.3, .3))], fill, .3)


def prepare_portrait(source_path):
    with Image.open(source_path) as original:
        source = ImageOps.exif_transpose(original).convert("RGBA")
    source.thumbnail((1100, 1400), Image.Resampling.LANCZOS)
    if source.width < 32 or source.height < 32:
        raise ValueError("PORTRAIT_SOURCE_TOO_SMALL")
    pixels = np.asarray(source.convert("RGB")).astype(np.float32)
    if source.getchannel("A").getextrema()[0] < 250:
        image = source
    else:
        # Remove only near-neutral pale pixels connected to the photo edges.
        low = pixels.min(axis=2)
        spread = pixels.max(axis=2) - low
        # fromarray may share a read-only NumPy buffer; floodfill needs writable pixels.
        candidate = Image.fromarray(np.uint8((low > 170) & (spread < 38)) * 255).copy()
        for x in range(0, source.width, max(1, source.width // 32)):
            for y in (0, source.height-1):
                if candidate.getpixel((x,y)) == 255: ImageDraw.floodfill(candidate, (x,y), 128)
        for y in range(0, source.height, max(1, source.height // 32)):
            for x in (0, source.width-1):
                if candidate.getpixel((x,y)) == 255: ImageDraw.floodfill(candidate, (x,y), 128)
        connected = np.asarray(candidate) == 128
        if np.mean(connected) < .03 or np.mean(connected) > .85:
            raise ValueError("PORTRAIT_CUTOUT_REQUIRED: provide a transparent PNG or a plain pale-background portrait")
        alpha = np.full(low.shape, 255, dtype=np.uint8)
        alpha[connected] = np.uint8(np.clip((255-low[connected])*1.18, 0, 255))
        image = source.copy()
        image.putalpha(Image.fromarray(alpha))
    gray = ImageEnhance.Contrast(ImageOps.grayscale(source)).enhance(1.18)
    dot_canvas = Image.new("L", source.size, 248)
    dots = ImageDraw.Draw(dot_canvas)
    values = np.asarray(gray)
    for y in range(0, source.height, 5):
        for x in range(0, source.width, 5):
            radius = 3.5 * math.sqrt((255-float(values[y,x]))/255)
            dots.ellipse((x-radius,y-radius,x+radius,y+radius), fill=19)
    halftone = Image.blend(gray, dot_canvas, .32)
    screen = Image.merge("RGBA", (halftone, halftone, halftone, image.getchannel("A")))
    border = image.getchannel("A").filter(ImageFilter.MaxFilter(33)).point(lambda v: 255 if v > 45 else 0)
    paper = Image.new("RGBA", source.size, "#E9E8E1")
    paper.putalpha(border)
    paper.alpha_composite(screen)
    return image, screen, paper


def paste_image(canvas, image, bounds, fit="contain"):
    horizontal, vertical, width, height = bounds
    target = point((width, height))
    resized = ImageOps.fit(image, target, Image.Resampling.LANCZOS, centering=(.5, .35)) if fit == "cover" else ImageOps.contain(image, target, Image.Resampling.LANCZOS)
    position = point((horizontal, vertical))
    position = (position[0] + (target[0]-resized.width)//2, position[1]+target[1]-resized.height)
    canvas.paste(resized, position, resized if resized.mode == "RGBA" else None)


def polaroid(portrait, tint, angle, signature=False):
    canvas = Image.new("RGBA", point((57, 76)), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((1, 1, canvas.width-2, canvas.height-2), radius=3*SCALE, fill="#FFFDF7", outline="#AAA1B2", width=1)
    inset = Image.new("RGBA", point((49, 61)), tint)
    resized = ImageOps.fit(portrait, inset.size, Image.Resampling.LANCZOS, centering=(.5, .3))
    inset.alpha_composite(resized)
    canvas.alpha_composite(inset, point((4, 4)))
    if signature:
        sketch(draw, bezier([(12,69),(20,58),(5,77),(27,68)]), "#524879", .35, 1)
        sketch(draw, bezier([(23,69),(25,65),(29,73),(40,67)]), "#524879", .3, 1)
    return canvas.rotate(angle, Image.Resampling.BICUBIC, expand=True)


def compose_background(style, source_path, plain_path, output):
    global RANDOM
    RANDOM = random.Random(20261025)
    cutout, halftone, torn = prepare_portrait(source_path)
    canvas = Image.open(plain_path).convert("RGB")
    draw = ImageDraw.Draw(canvas)
    if style == "blue-poster":
        paste_image(canvas, torn, (126,12,72,86))
    elif style == "serif-blue":
        paste_image(canvas, cutout, (120,15,78,95))
    elif style == "purple-doodle":
        paste_image(canvas, polaroid(cutout, "#C3BFCE", -2), (131,10,66,83))
        sketch(draw, [(132,13),(196,11),(197,93),(132,94),(132,13)], width=.45)
        brush(draw,180,82,18,6); brush(draw,151,17,16,4); star(draw,136,69,4,"#B3A0D4")
    elif style == "purple-sidebar":
        paste_image(canvas, polaroid(cutout,"#B9B6C5",6,signature=True),(7,8,65,80))
    elif style == "rust-editorial":
        # The no-photo design has a large burst here; replace it for the portrait variant.
        patch = grain("#EDE7DD", 1.8).crop(point((113,17,200,114)))
        canvas.paste(patch,point((113,17)))
        paste_image(canvas,halftone,(113,17,77,96))
        rectangle(draw,(184,17,199,113),"#B7472E")
        draw.ellipse(point((190,23,193,26)),fill="#EEE7DB")
    elif style == "blue-business":
        portrait=Image.new("RGBA",point((62,74)),"#EDF0F5")
        paste_image(portrait,cutout,(0,0,62,74),"cover")
        canvas.paste(portrait,point((14,50)),portrait)
    elif style == "blue-floral":
        paste_image(canvas,cutout,(117,8,88,114))
        boundary=[(0,100)]+bezier([(0,100),(57,70),(89,104),(143,112)])+bezier([(143,112),(173,118),(196,119),(210,119)])+[(210,164)]+bezier([(210,164),(190,210),(192,260),(184,297)])+[(0,297)]
        draw.polygon([point(p) for p in boundary],fill="#F8FAFC")
        path(draw,bezier([(0,99),(57,69),(89,103),(143,111)]),"#D5E7F1",1.1)
        path(draw,bezier([(210,164),(190,210),(192,260),(184,297)]),"#D4E4EF",.8)
    elif style == "beige-notebook":
        patch=grain("#F7F4F0",1.8).crop(point((123,12,198,103)))
        canvas.paste(patch,point((123,12)))
        portrait=Image.new("RGBA",point((70,85)),"#DDD0BD")
        paste_image(portrait,cutout,(0,0,70,85),"cover")
        mask=Image.new("L",portrait.size);ImageDraw.Draw(mask).ellipse((0,0,mask.width,mask.height),fill=255)
        portrait.putalpha(mask);canvas.paste(portrait,point((126,14)),portrait)
        path(draw,bezier([(162,12),(207,12),(210,102),(158,102)]),"#7F624D",.35)
        path(draw,bezier([(158,102),(136,104),(119,88),(125,60)]),"#7F624D",.35)
    else:
        raise ValueError("PORTRAIT_STYLE_UNKNOWN")
    canvas.save(output)
