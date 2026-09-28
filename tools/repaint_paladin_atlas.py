"""
Repaints the Paladin's hand-edited spine atlas pages (spine/paladin/ironclad*.png) to the
grey/baby-blue/gold palette, using the exact same HSV-bucket remap as
HelloSpire/shaders/paladin_repaint.gdshader -- so the hand-painted combat sprite matches the
shader-driven rest-site/shop/energy-counter appearance pixel-for-pixel in intent.

This is a straight offline port of that shader's fragment logic (rgb2hsv/hsv2rgb + the three
hue-bucket branches), applied per-pixel instead of per-fragment. Transparent pixels are left
alone. Run from the repo root:

    python tools/repaint_paladin_atlas.py            # all 4 atlas pages
    python tools/repaint_paladin_atlas.py --dry-run   # report pixel counts touched, no write
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PAGES = [
    ROOT / "spine/paladin/ironclad.png",
    ROOT / "spine/paladin/ironclad_2.png",
    ROOT / "spine/paladin/ironclad_3.png",
    ROOT / "spine/paladin/ironclad_4.png",
]


def rgb_to_hsv(rgb: np.ndarray) -> np.ndarray:
    """rgb: float array (...,3) in [0,1]. Returns hsv (...,3), h in [0,1]."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    maxc = np.maximum(np.maximum(r, g), b)
    minc = np.minimum(np.minimum(r, g), b)
    v = maxc
    d = maxc - minc
    s = np.where(maxc > 1e-10, d / np.where(maxc > 1e-10, maxc, 1.0), 0.0)

    rc = np.where(d > 1e-10, (maxc - r) / np.where(d > 1e-10, d, 1.0), 0.0)
    gc = np.where(d > 1e-10, (maxc - g) / np.where(d > 1e-10, d, 1.0), 0.0)
    bc = np.where(d > 1e-10, (maxc - b) / np.where(d > 1e-10, d, 1.0), 0.0)

    h = np.zeros_like(r)
    is_r = (maxc == r) & (d > 1e-10)
    is_g = (maxc == g) & (d > 1e-10) & ~is_r
    is_b = (maxc == b) & (d > 1e-10) & ~is_r & ~is_g
    h = np.where(is_r, bc - gc, h)
    h = np.where(is_g, 2.0 + rc - bc, h)
    h = np.where(is_b, 4.0 + gc - rc, h)
    h = (h / 6.0) % 1.0
    return np.stack([h, s, v], axis=-1)


def hsv_to_rgb(hsv: np.ndarray) -> np.ndarray:
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    i = np.floor(h * 6.0)
    f = h * 6.0 - i
    p = v * (1.0 - s)
    q = v * (1.0 - f * s)
    t = v * (1.0 - (1.0 - f) * s)
    i_mod = (i.astype(np.int64) % 6)

    r = np.select(
        [i_mod == 0, i_mod == 1, i_mod == 2, i_mod == 3, i_mod == 4, i_mod == 5],
        [v, q, p, p, t, v],
    )
    g = np.select(
        [i_mod == 0, i_mod == 1, i_mod == 2, i_mod == 3, i_mod == 4, i_mod == 5],
        [t, v, v, q, p, p],
    )
    b = np.select(
        [i_mod == 0, i_mod == 1, i_mod == 2, i_mod == 3, i_mod == 4, i_mod == 5],
        [p, p, t, v, v, q],
    )
    return np.stack([r, g, b], axis=-1)


def remap(hsv: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Exactly the three branches from paladin_repaint.gdshader's fragment(), vectorized."""
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    hd = h * 360.0
    red = (hd < 25.0) | (hd > 335.0)

    out = hsv.copy()

    # rage glow (small, rare highlight) -> baby-blue holy glow
    m1 = red & (s > 0.45) & (v > 0.55)
    out[..., 0] = np.where(m1, 200.0 / 360.0, out[..., 0])
    out[..., 1] = np.where(m1, s * 0.7, out[..., 1])
    out[..., 2] = np.where(m1, np.minimum(1.0, v * 1.15), out[..., 2])

    # maroon cloth -> steel grey (only where m1 didn't already match)
    m2 = (~m1) & ((hd < 22.0) | (hd > 330.0)) & (s > 0.25)
    out[..., 0] = np.where(m2, 220.0 / 360.0, out[..., 0])
    out[..., 1] = np.where(m2, s * 0.08, out[..., 1])
    out[..., 2] = np.where(m2, np.minimum(1.0, v * 1.3), out[..., 2])

    # leather/bronze (the bulk of the armor) -> holy gold
    m3 = (~m1) & (~m2) & (hd >= 22.0) & (hd < 52.0) & (s > 0.28)
    out[..., 0] = np.where(m3, 46.0 / 360.0, out[..., 0])
    out[..., 1] = np.where(m3, np.minimum(1.0, s * 0.85), out[..., 1])
    out[..., 2] = np.where(m3, np.minimum(1.0, v * 1.25), out[..., 2])

    touched = m1 | m2 | m3
    return out, touched


def process(path: Path, dry_run: bool) -> None:
    img = Image.open(path).convert("RGBA")
    arr = np.asarray(img).astype(np.float64) / 255.0
    rgb, a = arr[..., :3], arr[..., 3]

    hsv = rgb_to_hsv(rgb)
    new_hsv, touched = remap(hsv)
    touched &= a > 0.0  # never touch fully transparent pixels

    new_rgb = hsv_to_rgb(new_hsv)
    out_rgb = np.where(touched[..., None], new_rgb, rgb)

    n = int(touched.sum())
    print(f"{path.name}: {n} px remapped of {touched.size} ({img.width}x{img.height})")

    if dry_run:
        return

    out = np.concatenate([out_rgb, a[..., None]], axis=-1)
    out = np.clip(out * 255.0 + 0.5, 0, 255).astype(np.uint8)
    Image.fromarray(out, mode="RGBA").save(path)


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    for page in PAGES:
        if not page.exists():
            print(f"missing: {page}", file=sys.stderr)
            continue
        process(page, dry_run)


if __name__ == "__main__":
    main()
