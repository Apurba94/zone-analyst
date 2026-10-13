"""
Draw the desktop and Android app icons from the site's favicon design.

    py -m pip install pillow
    python scripts/make_app_icons.py

Pillow can't read SVG, so the four shapes in website/assets/favicon.svg are
redrawn here on the same 32-unit grid. Change both together.

Writes:
    desktop-app/build/icon.png              1024 px, rounded tile (window icon)
    desktop-app/build/icon.ico              16-256 px, the same tile for the .exe and shortcuts
    android-app/assets/icon-only.png        1024 px, full-bleed tile
    android-app/assets/icon-foreground.png  1024 px, rings only, inside the adaptive-icon safe zone
    android-app/assets/icon-background.png  1024 px, plain tile colour
    android-app/assets/splash.png           2732 px
    android-app/assets/splash-dark.png      2732 px
Then `npm run icons` in android-app/ turns the Android set into mipmaps.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
TILE = "#132430"
SS = 4  # supersampling factor


def rings(d: ImageDraw.ImageDraw, ox: float, oy: float, u: float) -> None:
    """The favicon's three circles; (ox, oy) is grid (0, 0) and u is one grid unit in pixels."""

    def ring(cx, cy, r, w, colour, dash=None):
        R = (r + w / 2) * u
        box = [ox + cx * u - R, oy + cy * u - R, ox + cx * u + R, oy + cy * u + R]
        if dash is None:
            d.ellipse(box, outline=colour, width=round(w * u))
            return
        on, off = (x / r * 180 / math.pi for x in dash)  # dash lengths as degrees
        a = 0.0
        while a < 360:
            d.arc(box, a, min(a + on, 360), fill=colour, width=round(w * u))
            a += on + off

    ring(16, 16, 11, 2.4, "#E4629A")
    ring(18.5, 14.5, 6.2, 1.6, "#CBDDE8", dash=(3, 2))
    r = 3.2 * u
    d.ellipse([ox + 16 * u - r, oy + 16 * u - r, ox + 16 * u + r, oy + 16 * u + r], fill="#6FB3D6")


def draw(size: int, design: float, tile: str | None, radius: float = 0) -> Image.Image:
    """`design` is the share of the canvas the 32-unit grid spans; `radius` the tile corner as a share."""
    S = size * SS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if tile:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=radius * S, fill=tile)
    span = S * design
    rings(d, (S - span) / 2, (S - span) / 2, span / 32)
    return img.resize((size, size), Image.LANCZOS)


def save(img: Image.Image, rel: str) -> None:
    out = ROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print("wrote", rel)


def main() -> None:
    tile = draw(1024, 1.0, TILE, radius=6 / 32)
    save(tile, "desktop-app/build/icon.png")
    tile.save(ROOT / "desktop-app/build/icon.ico", sizes=[(n, n) for n in (16, 24, 32, 48, 64, 128, 256)])
    print("wrote desktop-app/build/icon.ico")
    save(draw(1024, 1.0, TILE), "android-app/assets/icon-only.png")
    # Adaptive icons crop to the middle 66 of 108 units; keep the rings inside it.
    save(draw(1024, 0.76, None), "android-app/assets/icon-foreground.png")
    save(Image.new("RGBA", (1024, 1024), TILE), "android-app/assets/icon-background.png")
    splash = Image.new("RGBA", (2732, 2732), TILE)
    mark = draw(640, 1.0, None)
    splash.alpha_composite(mark, ((2732 - 640) // 2, (2732 - 640) // 2))
    save(splash, "android-app/assets/splash.png")
    save(splash, "android-app/assets/splash-dark.png")


if __name__ == "__main__":
    main()
