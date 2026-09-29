#!/usr/bin/env python3
"""
Cut round face tokens out of each character's portrait art.

Writes, per character, into HelloSpire/images/charui/<character>/:
    map_marker.png                 128x128  the token that walks the map
    character_icon.png             128x128  top-panel face chip   (--chip only)
    character_icon_outline.png     128x128  its white silhouette  (--chip only)

The chip matches the Paladin/Alchemist chips already shipped: a 123px disc with a
7px ring in the theme color. The map marker is the same face cropped tighter,
with a dark rim outside the ring so it reads against the map's parchment.

Usage:
    python tools/gen_face_tokens.py            # every character below
    python tools/gen_face_tokens.py gunslinger

Requires Pillow.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.join(os.path.dirname(__file__), "..")
SS = 4  # supersampling factor
SIZE = 128

# source image, face centre (x, y) and crop radius in source pixels, ring color,
# and whether to (re)write the top-panel chip too. Paladin and Alchemist chips
# were made by hand earlier and are left alone.
CHARACTERS = {
    "paladin": dict(src="art_reference/paladin/portrait.png",
                    centre=(375, 520), radius=290, ring="e8c46a", chip=False),
    "alchemist": dict(src="art_reference/alchemist/portrait.png",
                      centre=(440, 500), radius=340, ring="b5824a", chip=False),
    "gunslinger": dict(src="HelloSpire/images/charui/gunslinger/char_select.png",
                       centre=(66, 98), radius=62, ring="d4703c", chip=True),
}


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def disc_mask(size, inset):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).ellipse((inset, inset, size - 1 - inset, size - 1 - inset), fill=255)
    return m


def face(cfg, px):
    """The face crop, scaled to a px-wide square."""
    im = Image.open(os.path.join(ROOT, cfg["src"])).convert("RGB")
    cx, cy = cfg["centre"]
    r = cfg["radius"]
    crop = im.crop((cx - r, cy - r, cx + r, cy + r)).resize((px, px), Image.LANCZOS)
    # the small gunslinger source upscales soft; a light unsharp brings the lines back
    if 2 * r < px:
        crop = crop.filter(ImageFilter.UnsharpMask(radius=2 * SS, percent=80, threshold=2))
    return crop


def token(cfg, rim, ring_w, disc_inset):
    """Face in a ring. rim > 0 adds a dark outer edge of that many pixels."""
    S = SIZE * SS
    ring = hex_rgb(cfg["ring"])
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    edge = disc_inset * SS
    if rim:
        d.ellipse((edge, edge, S - 1 - edge, S - 1 - edge), fill=(24, 20, 16, 255))
        edge += rim * SS
    d.ellipse((edge, edge, S - 1 - edge, S - 1 - edge), fill=ring + (255,))
    inner = edge + ring_w * SS
    fpx = S - 2 * inner
    out.paste(face(cfg, fpx), (inner, inner), disc_mask(fpx, 0))
    return out.resize((SIZE, SIZE), Image.LANCZOS)


def outline(disc_inset):
    S = SIZE * SS
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(out).ellipse((disc_inset * SS, disc_inset * SS, S - 1 - disc_inset * SS,
                                 S - 1 - disc_inset * SS), fill=(255, 255, 255, 255))
    return out.resize((SIZE, SIZE), Image.LANCZOS)


def main(names):
    for name in names:
        cfg = CHARACTERS[name]
        dest = os.path.join(ROOT, "HelloSpire", "images", "charui", name)
        token(cfg, rim=4, ring_w=6, disc_inset=2).save(os.path.join(dest, "map_marker.png"))
        written = ["map_marker.png"]
        if cfg["chip"]:
            token(cfg, rim=0, ring_w=7, disc_inset=3).save(os.path.join(dest, "character_icon.png"))
            outline(3).save(os.path.join(dest, "character_icon_outline.png"))
            written += ["character_icon.png", "character_icon_outline.png"]
        print(f"{name}: {', '.join(written)}")


if __name__ == "__main__":
    main(sys.argv[1:] or list(CHARACTERS))
