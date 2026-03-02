"""
extract_glyphs.py  —  Render the letter "A" from every font in data/raw_fonts/
as a centered 128×128 grayscale PNG, saving results to data/glyphs/A/.

Usage (from the font-ai/ directory):
    python scripts/extract_glyphs.py

Requirements:
    pip install Pillow
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
GLYPH_CHAR = "A"                       # Which character to render
IMG_SIZE = 128                          # Output image dimensions (square)
FONT_SIZE = 100                         # Starting point — auto-scaled to fit
PADDING = 8                             # Min pixels of padding around glyph

# Paths (relative to the font-ai/ project root)
SCRIPT_DIR = Path(__file__).resolve().parent          # font-ai/scripts/
PROJECT_ROOT = SCRIPT_DIR.parent                      # font-ai/
RAW_FONTS_DIR = PROJECT_ROOT / "data" / "raw_fonts"
OUTPUT_DIR = PROJECT_ROOT / "data" / "glyphs" / GLYPH_CHAR

# ---------------------------------------------------------------------------
# Helper: render a centred glyph
# ---------------------------------------------------------------------------

def render_glyph(font_path: Path, char: str, img_size: int) -> Image.Image:
    """
    Render *char* from the font at *font_path* onto a centred grayscale image.

    Strategy:
      1. Load the font at a large size.
      2. Measure the glyph's bounding box.
      3. If it's too big for the canvas (with padding), scale the font down.
      4. Draw the glyph on a blank canvas, centred.

    Returns a PIL Image (mode 'L' = 8-bit grayscale).
    """
    # Start with the configured font size; shrink if the glyph doesn't fit.
    font_size = FONT_SIZE
    max_extent = img_size - 2 * PADDING

    while font_size > 8:
        font = ImageFont.truetype(str(font_path), size=font_size)

        # Create a temporary image just to measure the glyph
        tmp = Image.new("L", (img_size * 2, img_size * 2), color=0)
        draw = ImageDraw.Draw(tmp)
        bbox = draw.textbbox((0, 0), char, font=font)
        # bbox = (left, top, right, bottom)
        glyph_w = bbox[2] - bbox[0]
        glyph_h = bbox[3] - bbox[1]

        if glyph_w <= max_extent and glyph_h <= max_extent:
            break  # fits!
        font_size -= 4  # shrink and retry

    # Final render — white glyph on black background, centred
    img = Image.new("L", (img_size, img_size), color=0)
    draw = ImageDraw.Draw(img)

    # Where does the glyph need to start so it lands in the centre?
    x = (img_size - glyph_w) / 2 - bbox[0]
    y = (img_size - glyph_h) / 2 - bbox[1]
    draw.text((x, y), char, fill=255, font=font)

    return img


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Ensure the output folder exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Gather all .ttf and .otf files
    font_files = sorted(
        p for p in RAW_FONTS_DIR.iterdir()
        if p.suffix.lower() in (".ttf", ".otf")
    )

    if not font_files:
        print(f"⚠  No .ttf or .otf files found in {RAW_FONTS_DIR}")
        print("   Download some fonts into that folder and re-run this script.")
        sys.exit(1)

    print(f"Found {len(font_files)} font file(s) in {RAW_FONTS_DIR}\n")

    succeeded = 0
    skipped = 0
    skipped_names = []

    for font_path in font_files:
        try:
            img = render_glyph(font_path, GLYPH_CHAR, IMG_SIZE)
            out_name = font_path.stem + ".png"   # e.g. "Roboto-Regular.png"
            img.save(OUTPUT_DIR / out_name)
            print(f"  ✓ {font_path.name}  →  {out_name}")
            succeeded += 1
        except Exception as e:
            print(f"  ✗ {font_path.name}  — skipped ({e})")
            skipped += 1
            skipped_names.append(font_path.name)

    # Summary
    print(f"\n{'='*50}")
    print(f"Done!  {succeeded} succeeded,  {skipped} skipped.")
    if skipped_names:
        print("Skipped fonts:")
        for name in skipped_names:
            print(f"  - {name}")
    print(f"\nGlyph images saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
