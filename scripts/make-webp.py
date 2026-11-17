#!/usr/bin/env python3
"""Build WebP copies of the figures for the web build.

The gallery shows all 42 figures, and the PNGs are print-resolution: 15 MB for
pages that load on a phone. WebP copies at display size cut that by roughly
four-fifths, and the PNGs stay untouched for the PDF, which cannot read WebP.

Usage: python3 scripts/make-webp.py [--width 1400] [--quality 82]
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("make-webp: Pillow is required (pip install pillow)")
    sys.exit(2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=1400)
    parser.add_argument("--quality", type=int, default=82)
    args = parser.parse_args()

    out = Path("figures/webp")
    out.mkdir(exist_ok=True)

    pngs = sorted(Path("figures").glob("*.png"))
    before = after = 0
    for png in pngs:
        target = out / (png.stem + ".webp")
        before += png.stat().st_size
        if target.exists() and target.stat().st_mtime >= png.stat().st_mtime:
            after += target.stat().st_size
            continue
        with Image.open(png) as img:
            img = img.convert("RGBA") if img.mode in ("P", "LA") else img
            if img.width > args.width:
                height = round(img.height * args.width / img.width)
                img = img.resize((args.width, height), Image.LANCZOS)
            img.save(target, "WEBP", quality=args.quality, method=6)
        after += target.stat().st_size

    print(
        f"make-webp: {len(pngs)} figures -> {out} "
        f"({before / 1e6:.1f} MB PNG, {after / 1e6:.1f} MB WebP, "
        f"{100 - after * 100 / max(before, 1):.0f}% smaller)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
