#!/usr/bin/env python3
"""
Package the deployed HelloSpire build as a single zip, and optionally publish it.

`dotnet publish` already assembles the exact file set the game loads -- HelloSpire.dll,
.json, .pck, .pdb and the spine/ rigs -- in the game's mods/HelloSpire/ folder. This script
zips THAT folder rather than re-deriving the file list, so the zip is by construction what
you just playtested.

    dist/HelloSpire-<version>.zip
        HelloSpire/HelloSpire.dll
        HelloSpire/HelloSpire.json
        HelloSpire/HelloSpire.pck
        HelloSpire/HelloSpire.pdb        (kept: playtest crash logs get line numbers)
        HelloSpire/spine/...

Usage:
    python tools/package-release.py                     # zip only
    python tools/package-release.py --github            # zip + GitHub release (needs gh)
    python tools/package-release.py --workshop ../hellospire-workshop
                                                        # also refresh a ModUploader workspace
    python tools/package-release.py --mods-dir "D:/SteamLibrary/steamapps/common/Slay the Spire 2/mods"

The version comes from HelloSpire.json. Bump it there first -- a co-op lobby rejects
players whose gameplay-affecting mods differ, so every build you hand out needs its own number.
See PUBLISHING.md for the whole flow.
"""
import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD_ID = "HelloSpire"
REQUIRED = ["HelloSpire.dll", "HelloSpire.json", "HelloSpire.pck"]


def manifest():
    # The file is saved with a BOM; utf-8-sig tolerates it.
    with open(os.path.join(ROOT, "HelloSpire.json"), encoding="utf-8-sig") as f:
        return json.load(f)


def default_mods_dir():
    """Mirror Sts2PathDiscovery.props: Directory.Build.props wins, then the OS's Steam default."""
    props = os.path.join(ROOT, "Directory.Build.props")
    if os.path.exists(props):
        text = open(props, encoding="utf-8").read()
        m = re.search(r"<ModsPath>(.*?)</ModsPath>", text)
        if m and "$(" not in m.group(1):
            return m.group(1)
        m = re.search(r"<Sts2Path>(.*?)</Sts2Path>", text)
        if m and "$(" not in m.group(1):
            return _mods_under(m.group(1))

    home = os.path.expanduser("~")
    system = platform.system()
    if system == "Darwin":
        game = os.path.join(home, "Library/Application Support/Steam/steamapps/common/Slay the Spire 2")
    elif system == "Linux":
        game = os.path.join(home, ".local/share/Steam/steamapps/common/Slay the Spire 2")
    else:
        game = r"C:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2"
    return _mods_under(game)


def _mods_under(game_dir):
    if platform.system() == "Darwin":
        return os.path.join(game_dir, "SlayTheSpire2.app", "Contents", "MacOS", "mods")
    return os.path.join(game_dir, "mods")


def check_build(src, version):
    missing = [f for f in REQUIRED if not os.path.exists(os.path.join(src, f))]
    if missing:
        sys.exit(f"{src} is missing {', '.join(missing)}. Run `dotnet publish` first "
                 "(not `dotnet build` -- only publish exports the .pck).")
    with open(os.path.join(src, "HelloSpire.json"), encoding="utf-8-sig") as f:
        deployed = json.load(f)["version"]
    if deployed != version:
        sys.exit(f"The deployed build is {deployed} but HelloSpire.json says {version}. "
                 "Run `dotnet publish` again so the zip matches the version it is labelled with.")


def make_zip(src, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    count = 0
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, _, files in os.walk(src):
            for name in sorted(files):
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, src)
                z.write(full, os.path.join(MOD_ID, rel))
                count += 1
    return count


def refresh_workshop(src, workspace):
    """Replace a ModUploader workspace's content/ with this build. workshop.json is left alone."""
    if not os.path.exists(os.path.join(workspace, "workshop.json")):
        sys.exit(f"{workspace} has no workshop.json -- create it with ModUploader first (PUBLISHING.md).")
    content = os.path.join(workspace, "content")
    if os.path.exists(content):
        shutil.rmtree(content)
    shutil.copytree(src, content)


def github_release(version, zip_path, notes):
    if shutil.which("gh") is None:
        sys.exit("gh not found; install the GitHub CLI or upload the zip by hand.")
    tag = version
    if subprocess.run(["gh", "release", "view", tag], capture_output=True).returncode == 0:
        sys.exit(f"Release {tag} already exists. Bump the version in HelloSpire.json.")
    subprocess.run(["gh", "release", "create", tag, zip_path, "--title", f"HelloSpire {version}",
                    "--notes", notes], check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--mods-dir", help="the game's mods/ folder (default: auto-detect)")
    ap.add_argument("--github", action="store_true", help="create a GitHub release with the zip")
    ap.add_argument("--notes", default="Playtest build. Install with the one-liner in PUBLISHING.md.",
                    help="release notes for --github")
    ap.add_argument("--workshop", help="a ModUploader workspace whose content/ to refresh")
    args = ap.parse_args()

    m = manifest()
    version = m["version"]
    src = os.path.join(args.mods_dir or default_mods_dir(), MOD_ID)
    if not os.path.isdir(src):
        sys.exit(f"No deployed build at {src}. Pass --mods-dir, or run `dotnet publish`.")
    check_build(src, version)
    if version == "v0.0.0":
        print("warning: version is still v0.0.0 -- bump it in HelloSpire.json before handing this out.")

    out = os.path.join(ROOT, "dist", f"{MOD_ID}-{version}.zip")
    n = make_zip(src, out)
    print(f"wrote {out} ({n} files, {os.path.getsize(out) / 1e6:.1f} MB)")

    if args.workshop:
        refresh_workshop(src, args.workshop)
        print(f"refreshed {args.workshop}/content -- now run ModUploader upload -w {args.workshop}")
    if args.github:
        github_release(version, out, args.notes)
        print(f"published GitHub release {version}")


if __name__ == "__main__":
    main()
