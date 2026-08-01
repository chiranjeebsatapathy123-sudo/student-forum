#!/usr/bin/env python3
"""
Generate PNG (192x192, 512x512) and favicon.ico from existing SVG icons.
Usage: python generate_icons.py
"""
from pathlib import Path
from PIL import Image, ImageDraw

try:
    from cairosvg import svg2png
except Exception:
    svg2png = None

HERE = Path(__file__).resolve().parent
SVG_DIR = HERE / 'static' / 'images'
OUT_DIR = SVG_DIR

SVG_FILE = SVG_DIR / 'favicon.svg'
MARK_SVG = SVG_DIR / 'logo-mark.svg'
SMALL_SVG = SVG_DIR / 'logo-small.svg'

PNG_192 = OUT_DIR / 'favicon-192.png'
PNG_512 = OUT_DIR / 'favicon-512.png'
ICO_PATH = OUT_DIR / 'favicon.ico'


def convert(svg_path: Path, out_path: Path, size: int):
    if not svg2png:
        raise RuntimeError('cairosvg is not installed')
    svg2png(url=str(svg_path), write_to=str(out_path), output_width=size, output_height=size)


def fallback_draw(out_path: Path, size: int):
    # Simple generated icon: colored rounded square with circle and "SF" text
    img = Image.new('RGBA', (size, size), '#0b2545')
    draw = ImageDraw.Draw(img)
    # circle
    cx = cy = size // 2
    r = int(size * 0.35)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill='#ff7a59')
    # text
    try:
        from PIL import ImageFont
        # Try to use a truetype font if available
        font_size = int(size * 0.42)
        try:
            font = ImageFont.truetype('arial.ttf', font_size)
        except Exception:
            font = ImageFont.load_default()
    except Exception:
        font = None

    txt = 'SF'
    if font:
        try:
            bbox = draw.textbbox((0, 0), txt, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except Exception:
            w, h = draw.textsize(txt, font=font)
        draw.text(((size - w) / 2, (size - h) / 2), txt, fill='white', font=font)
    else:
        draw.text((size * 0.35, size * 0.40), txt, fill='white')

    img.save(out_path)


def make_ico(png_sizes, ico_path: Path):
    imgs = [Image.open(p) for p in png_sizes]
    imgs[0].save(ico_path, format='ICO', sizes=[(img.width, img.height) for img in imgs])


if __name__ == '__main__':
    if not SVG_FILE.exists():
        # fallback to mark SVG if favicon.svg missing
        if MARK_SVG.exists():
            source = MARK_SVG
        elif SMALL_SVG.exists():
            source = SMALL_SVG
        else:
            raise SystemExit('No SVG source found in static/images/')
    else:
        source = SVG_FILE

    print('Using source SVG:', source)

    if not svg2png:
        print('\nCairoSVG not available; using Pillow fallback generator')

    print('Generating PNG 192x192...')
    try:
        convert(source, PNG_192, 192)
    except Exception:
        fallback_draw(PNG_192, 192)
    print('Generating PNG 512x512...')
    try:
        convert(source, PNG_512, 512)
    except Exception:
        fallback_draw(PNG_512, 512)

    print('Creating favicon.ico (192,32,16)')
    # Create smaller variants for ICO
    tmp32 = OUT_DIR / 'favicon-32.png'
    tmp16 = OUT_DIR / 'favicon-16.png'
    try:
        convert(source, tmp32, 32)
    except Exception:
        fallback_draw(tmp32, 32)
    try:
        convert(source, tmp16, 16)
    except Exception:
        fallback_draw(tmp16, 16)

    make_ico([PNG_192, tmp32, tmp16], ICO_PATH)

    # cleanup temp files
    try:
        tmp32.unlink()
        tmp16.unlink()
    except Exception:
        pass

    print('Icons generated:')
    print(' -', PNG_192)
    print(' -', PNG_512)
    print(' -', ICO_PATH)
