#!/usr/bin/env python3
"""
Make each character's donor weapon invisible by clearing its regions in the rig's atlas pages.

The three rigs under spine/ are recoloured donors (Ironclad, Silent, Necrobinder), so out of
the box the Paladin swings Ironclad's sword, the Gunslinger twirls Silent's daggers and the
Alchemist reaps with Necrobinder's scythe. Until each character gets its own weapon art they
look more like themselves empty-handed.

Only pixels change. The skeleton, slots, attachments and animations are untouched, so every
animation still plays -- the arms just swing nothing. Swing trails (the `slash` regions) are
kept on purpose: they are the attack effect, not the weapon.

spine/ is a build output of the character workbench (see spine/README.md), so re-packaging a
rig from the workbench brings the weapon back. Re-run this afterwards, or better, hide the
same parts in the workbench. The script is idempotent.

Usage:
    python3 tools/strip_rig_weapons.py              # all three
    python3 tools/strip_rig_weapons.py paladin      # one, by character
"""
import sys
from pathlib import Path

from PIL import Image

SPINE = Path(__file__).resolve().parent.parent / "spine"

# character -> (atlas file, regions that are the weapon or its glint)
WEAPONS = {
    "paladin": ("ironclad.atlas", {"sword blade", "sword_handle", "shine"}),
    "gunslinger": ("silent.atlas", {"top dagger", "back dagger", "blade_shine", "blade_twirls", "shiv_blur"}),
    "alchemist": ("necrobinder.atlas", {"scythe", "scythe_glow", "sythe_dissolve"}),
}


def parse_atlas(path):
    """Yield (page file, region name, (left, top, right, bottom)) for every region."""
    page = region = None
    fields = {}

    def flush():
        if region is None:
            return None
        x, y, w, h = map(int, fields["bounds"].split(","))
        if fields.get("rotate") in ("90", "270", "true"):
            w, h = h, w                       # bounds are unrotated; the packed rect is swapped
        return page, region, (x, y, x + w, y + h)

    for raw in path.read_text().splitlines() + [""]:
        line = raw.strip()
        if not line or ":" not in line:
            if (hit := flush()) is not None:
                yield hit
            region, fields = None, {}
            if not line:
                page = None
            elif page is None:
                page = line
            else:
                region = line
        elif region is not None:
            key, value = line.split(":", 1)
            fields[key] = value


def strip(character):
    atlas_name, wanted = WEAPONS[character]
    folder = SPINE / character
    by_page = {}
    for page, region, rect in parse_atlas(folder / atlas_name):
        if region in wanted:
            by_page.setdefault(page, []).append((region, rect))

    missing = wanted - {r for regions in by_page.values() for r, _ in regions}
    if missing:
        sys.exit(f"{character}: {atlas_name} has no region(s) {sorted(missing)} -- has the donor rig changed?")

    for page, regions in by_page.items():
        png = folder / page
        img = Image.open(png)
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        for region, rect in regions:
            img.paste((0, 0, 0, 0), rect)
            print(f"{character}: cleared {region!r} {rect} in {page}")
        img.save(png, optimize=True)


def main():
    for character in sys.argv[1:] or WEAPONS:
        strip(character)


if __name__ == "__main__":
    main()
