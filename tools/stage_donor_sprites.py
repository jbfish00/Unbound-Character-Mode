#!/usr/bin/env python3
"""Stage reusable donor sprite assets from the ROWE Character Mode project.

Our Gen 1-8 roster heavily overlaps ROWE's already-sourced character cast.
ROWE ships not just source PNGs but pre-compiled .4bpp / .4bpp.lz (GBA tile
data, some already LZ77-compressed) — if Unbound turns out to use standard
GBA compression (still unconfirmed, Phase 1), these could be injected with
little/no reprocessing.

Cross-references our characters.txt against ROWE's sprite_report.txt (symbol
names) and resolves those to actual files by trying ROWE's known naming
conventions:
  front pic (character-mode custom): trainers/front_pics/cm_<key>.*
  front pic (native FRLG costume):   trainers/front_pics/<key>_front_pic.*
  back pic  (character-mode custom): trainers/back_pics/cm_<key>_back_pic.*
  back pic  (native):                trainers/back_pics/<key>_back_pic.*
  OW sprite (character-mode custom): object_events/pics/people/cm_<key>.*
  OW sprite (native FRLG costume):   object_events/pics/people/frlg/<key>_normal.*
  palette:                           trainers/palettes/cm_<key>.gbapal (+.pal)
                                      object_events/palettes/cm_<key>.pal (OW)

Copies whatever's found into assets/donor_sprites_staged/<character>/ and
writes a manifest. This is asset STAGING only — actual injection into the
Unbound ROM needs Phase 1 to confirm sprite table addresses + compression
format first.
"""
import json
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, ".."))
ROWE = "/home/jbfish00/Documents/Pokemon Rowe Alteration"
STAGE_DIR = os.path.join(PROJECT_ROOT, "assets", "donor_sprites_staged")

FRONT_DIR = os.path.join(ROWE, "graphics/trainers/front_pics")
BACK_DIR = os.path.join(ROWE, "graphics/trainers/back_pics")
OW_DIR = os.path.join(ROWE, "graphics/object_events/pics/people")
TRAINER_PAL_DIR = os.path.join(ROWE, "graphics/trainers/palettes")
OW_PAL_DIR = os.path.join(ROWE, "graphics/object_events/palettes")

ASSET_EXTS = (".png", ".4bpp", ".4bpp.lz", ".pal", ".gbapal")


def key_for(name):
    base = name.split(" (")[0]
    return re.sub(r"[^A-Za-z0-9]+", "_", base).strip("_").lower()


def find_files(directory, stem_candidates):
    """Return {ext: path} for the first stem_candidate that has any files."""
    if not os.path.isdir(directory):
        return {}
    for root, _, files in os.walk(directory):
        fileset = set(files)
        for stem in stem_candidates:
            hits = {}
            for ext in ASSET_EXTS:
                fname = stem + ext
                if fname in fileset:
                    hits[ext] = os.path.join(root, fname)
            if hits:
                return hits
    return {}


def load_sprite_report():
    rowe_report = {}
    path = os.path.join(ROWE, "tools/character_mode/sprite_report.txt")
    with open(path) as f:
        for line in f:
            m = re.match(r"^(\S.*?)\s+ow=(\S+)\s+front=(\S+)\s+back=(\S+)", line)
            if m:
                name, ow, front, back = m.groups()
                rowe_report[name.strip()] = (ow, front, back)
    return rowe_report


def main():
    our_chars = []
    with open(os.path.join(HERE, "character_mode", "characters.txt")) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            our_chars.append(line.split("|")[0].strip())

    rowe_report = load_sprite_report()
    os.makedirs(STAGE_DIR, exist_ok=True)

    manifest = []
    staged_count = 0
    for name in our_chars:
        entry = rowe_report.get(name)
        key = key_for(name)
        candidates = [key, "cm_" + key]

        front = find_files(FRONT_DIR, ["cm_" + key, key + "_front_pic"])
        back = find_files(BACK_DIR, ["cm_" + key + "_back_pic", key + "_back_pic", "cm_" + key + "_back", key + "_back"])
        ow = find_files(OW_DIR, ["cm_" + key, key + "_normal", key])
        trainer_pal = find_files(TRAINER_PAL_DIR, ["cm_" + key])
        ow_pal = find_files(OW_PAL_DIR, ["cm_" + key])

        found_any = bool(front or back or ow)
        char_dir = os.path.join(STAGE_DIR, key)
        copied = {"front": [], "back": [], "ow": [], "trainer_pal": [], "ow_pal": []}
        if found_any:
            os.makedirs(char_dir, exist_ok=True)
            for label, hits in (("front", front), ("back", back), ("ow", ow),
                                 ("trainer_pal", trainer_pal), ("ow_pal", ow_pal)):
                for ext, path in hits.items():
                    dest = os.path.join(char_dir, label + ext)
                    shutil.copy2(path, dest)
                    copied[label].append(os.path.basename(dest))
            staged_count += 1

        manifest.append({
            "character": name,
            "key": key,
            "rowe_symbols": {"ow": entry[0], "front": entry[1], "back": entry[2]} if entry else None,
            "staged_files": copied,
            "has_any_asset": found_any,
        })

    with open(os.path.join(PROJECT_ROOT, "assets", "staging_manifest.json"), "w") as f:
        json.dump({"staged_character_count": staged_count, "total_characters": len(our_chars),
                   "characters": manifest}, f, indent=1)

    print(f"staged assets for {staged_count}/{len(our_chars)} characters -> {STAGE_DIR}")
    missing = [m["character"] for m in manifest if not m["has_any_asset"]]
    print(f"{len(missing)} characters with no staged assets (expected: Gen 6-8 + a few anime)")


if __name__ == "__main__":
    main()
