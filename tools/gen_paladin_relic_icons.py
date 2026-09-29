#!/usr/bin/env python3
"""
Generate Paladin relic icons that were missing, in the Paladin's flat relic style.

The Paladin's relics are flat objects on transparent: a thick dark or gold outline, three or four
solid fills, no shading. Consecrated Plate, Holy Book and the rest were drawn by hand at 128px.
This tool draws the relics that had no art, or had only the 128px tray icon, as vector shapes,
so the 256px tooltip version is a clean render rather than an upscale.

  * Judge's Gavel and Tithing Box: tray icon, _outline and tooltip art.
  * Chained Gauntlet and Libram of Wrath: tooltip art only. The geometry is traced from their
    existing 128px icons, doubled, so tray and tooltip show the same object.

Holy Book's tooltip art is not drawn here. It already existed as big/libram_of_righteousness.png,
left behind when the relic was renamed, and was moved back to the name the game asks for.

_outline files come from the rendered alpha, as in gen_gunslinger_icons.py, so a silhouette
cannot drift from its art.

Requires rsvg-convert (brew install librsvg) and Pillow.

Usage:
    python tools/gen_paladin_relic_icons.py                  # all four
    python tools/gen_paladin_relic_icons.py judges_gavel     # one, by key
    python tools/gen_paladin_relic_icons.py --sheet /tmp/x.png
"""
import argparse
import math
import os
import subprocess
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_gunslinger_icons import (  # noqa: E402  shared svg + rendering helpers
    RELICS_DIR, RELIC_BIG, RELIC_SMALL, circle, path, polygon, rect, render, silhouette, svg, write,
)

# ------------------------------------------------------------------ palette
# Sampled from the hand-drawn Paladin relics, so a generated icon sits beside them.

INK = "#28241e"        # the dark outline (Chained Gauntlet)
GOLD = "#e8c46a"       # the Paladin's colour; Holy Book's trim and cross
GOLD_DK = "#96742c"    # Chained Gauntlet's rings
TOME = "#3a1e10"       # Libram of Wrath's cover
WOOD = "#5c4214"       # Holy Book's shadow brown
WOOD_LT = "#8a6428"
STEEL = "#9696a2"      # Chained Gauntlet's plate
EMBER = "#d47828"      # Libram of Wrath's sunburst


# ------------------------------------------------------------------ glyphs (256x256 viewBox)


def glyph_chained_gauntlet():
    fingers = "".join(rect(x, 36, 13, 52, rx=6.5, fill=STEEL, stroke=INK, sw=5)
                      for x in (94, 123, 152))
    plate = rect(78, 76, 102, 128, rx=16, fill=STEEL, stroke=INK, sw=6)
    rings = "".join(circle(x, y, 15, stroke=GOLD_DK, sw=7)
                    for x, y in ((56, 106), (195, 106), (86, 140), (159, 140), (122, 168)))
    return fingers + plate + rings


def glyph_libram_of_wrath():
    cover = rect(50, 32, 162, 194, rx=12, fill=TOME, stroke=GOLD, sw=7)
    spine = rect(76, 34, 5, 190, fill=GOLD)
    cx, cy = 144, 128
    rays = "".join(
        path(f"M{cx + math.cos(a) * 20:.1f},{cy + math.sin(a) * 20:.1f} "
             f"L{cx + math.cos(a) * 42:.1f},{cy + math.sin(a) * 42:.1f}",
             stroke=EMBER, sw=8, cap="butt")
        for a in (i * math.pi / 3 for i in range(6)))
    sun = circle(cx, cy, 11, fill=GOLD, stroke=INK, sw=3)
    return cover + spine + rays + sun


def glyph_judges_gavel():
    """A gavel mid-knock over its sounding block. The Judge verb as an object."""
    block = (rect(58, 196, 140, 26, rx=8, fill=WOOD, stroke=INK, sw=7)
             + rect(74, 184, 108, 18, rx=6, fill=WOOD_LT, stroke=INK, sw=6))
    handle = rect(118, 70, 20, 132, rx=10, fill=WOOD_LT, stroke=INK, sw=7,
                  rot=-40, cx=128, cy=128)
    # The head is centred on the handle's top end, (128, 128) + 58 along the rotated handle.
    hx, hy = 128 - 58 * math.sin(math.radians(40)), 128 - 58 * math.cos(math.radians(40))
    head = (rect(hx - 56, hy - 27, 112, 54, rx=14, fill=WOOD, stroke=INK, sw=7, rot=-40, cx=hx, cy=hy)
            + rect(hx - 42, hy - 29, 14, 58, fill=GOLD, stroke=INK, sw=4, rot=-40, cx=hx, cy=hy)
            + rect(hx + 28, hy - 29, 14, 58, fill=GOLD, stroke=INK, sw=4, rot=-40, cx=hx, cy=hy))
    return block + handle + head


def glyph_tithing_box():
    """A chapel alms box: iron-banded wood, a coin slot, the cross on its face, a coin going in."""
    lid = polygon([(52, 92), (204, 92), (188, 64), (68, 64)], fill=WOOD_LT, stroke=INK, sw=7)
    slot = rect(104, 72, 48, 10, rx=5, fill=INK)
    body = rect(52, 92, 152, 124, rx=10, fill=WOOD, stroke=INK, sw=7)
    bands = rect(52, 110, 152, 12, fill=STEEL, stroke=INK, sw=4) + \
        rect(52, 186, 152, 12, fill=STEEL, stroke=INK, sw=4)
    cross = rect(118, 128, 20, 52, rx=3, fill=GOLD, stroke=INK, sw=4) + \
        rect(104, 142, 48, 18, rx=3, fill=GOLD, stroke=INK, sw=4)
    coin = circle(128, 38, 20, fill=GOLD, stroke=INK, sw=6) + circle(128, 38, 9, stroke=GOLD_DK, sw=4)
    return lid + slot + body + bands + cross + coin


# key -> (glyph, draw the 128px tray icon and _outline too?)
RELICS = {
    "judges_gavel": (glyph_judges_gavel, True),
    "tithing_box": (glyph_tithing_box, True),
    "chained_gauntlet": (glyph_chained_gauntlet, False),
    "libram_of_wrath": (glyph_libram_of_wrath, False),
}


def build(only=None):
    made = []
    for key, (glyph, with_small) in RELICS.items():
        if only and key not in only:
            continue
        markup = svg(glyph())
        write(render(markup, RELIC_BIG), os.path.join(RELICS_DIR, "big", f"{key}.png"))
        if with_small:
            small = render(markup, RELIC_SMALL)
            write(small, os.path.join(RELICS_DIR, f"{key}.png"))
            write(silhouette(small), os.path.join(RELICS_DIR, f"{key}_outline.png"))
        made.append(key)
    return made


def contact_sheet(path_out, cell=256):
    tiles = [render(svg(glyph()), cell) for glyph, _ in RELICS.values()]
    sheet = Image.new("RGBA", (len(tiles) * cell, cell), (60, 60, 70, 255))
    for i, tile in enumerate(tiles):
        sheet.alpha_composite(tile, (i * cell, 0))
    sheet.convert("RGB").save(path_out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("keys", nargs="*", help="relic keys to rebuild (default: all)")
    parser.add_argument("--sheet", default=None, help="also write a contact sheet here")
    args = parser.parse_args()

    if subprocess.run(["which", "rsvg-convert"], capture_output=True).returncode != 0:
        sys.exit("rsvg-convert not found; brew install librsvg")

    for key in build(set(args.keys) or None):
        print(f"relic  {key}")
    if args.sheet:
        contact_sheet(args.sheet)
        print(f"sheet  {args.sheet}")


if __name__ == "__main__":
    main()
