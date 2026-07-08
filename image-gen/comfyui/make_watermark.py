"""
Generates the MACAL Empire brand watermark PNG (transparent background) used
by batch_runner.py to stamp every generated image before saving to output/.

Uses the exact brand parameters from bot/templates/base.py:
    Gold accent:  #D4AF37
    Brand text:   "EMPIRE ENGLISH" (Cinzel font in the web templates; falls
                  back to a bundled serif font here since Cinzel is a web
                  font not guaranteed to be installed in a Kaggle environment)

Output: watermark.png — a small semi-transparent gold wordmark meant to be
composited into the bottom-right corner of generated images (see
batch_runner.py apply_watermark()).

Usage:
    python make_watermark.py
    # writes watermark.png in this directory
"""
import os
from PIL import Image, ImageDraw, ImageFont

GOLD = (212, 175, 55)  # #D4AF37, from bot/templates/base.py
BRAND_TEXT = "EMPIRE ENGLISH"

WATERMARK_WIDTH = 500
WATERMARK_HEIGHT = 80
FONT_SIZE = 32


def find_font() -> ImageFont.FreeTypeFont:
    """
    Try a few common serif font paths (Cinzel isn't a system font, so we fall
    back gracefully). If none are found, PIL's default bitmap font is used —
    functional but not brand-accurate; install a serif .ttf on Kaggle if you
    want a closer match (see the notebook's font-install cell).
    """
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/kaggle/working/fonts/Cinzel-Bold.ttf",  # if the user installs it
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, FONT_SIZE)
    print("WARNING: no serif .ttf font found — using PIL default bitmap font. "
          "For a brand-accurate look, download Cinzel-Bold.ttf from Google Fonts "
          "into /kaggle/working/fonts/ and re-run this script.")
    return ImageFont.load_default()


def make_watermark(opacity: int = 200) -> Image.Image:
    """
    Build the watermark image: brand text in gold, letter-spaced, on a fully
    transparent background, with a subtle thin gold underline (matches the
    .gold-line motif in bot/templates/base.py).
    """
    img = Image.new("RGBA", (WATERMARK_WIDTH, WATERMARK_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = find_font()

    # Manual letter-spacing since PIL doesn't support it natively
    letter_spacing = 4
    x = 10
    y = 15
    fill = (*GOLD, opacity)
    for char in BRAND_TEXT:
        draw.text((x, y), char, font=font, fill=fill)
        bbox = draw.textbbox((x, y), char, font=font)
        char_width = bbox[2] - bbox[0]
        x += char_width + letter_spacing

    # Thin gold underline, matching the brand's .gold-line accent motif
    line_y = y + FONT_SIZE + 8
    draw.line([(10, line_y), (x, line_y)], fill=(*GOLD, opacity), width=2)

    return img


def main():
    watermark = make_watermark()
    out_path = os.path.join(os.path.dirname(__file__), "watermark.png")
    watermark.save(out_path, "PNG")
    print(f"Wrote {out_path} ({watermark.width}x{watermark.height})")


if __name__ == "__main__":
    main()
