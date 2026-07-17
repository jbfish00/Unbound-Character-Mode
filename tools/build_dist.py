#!/usr/bin/env python3
"""Assemble the distributable package (Phase 6).

Contents of dist/:
  unbound-character-mode.bps   the patch (copy of build/unbound-cm.bps)
  README.md                    what it is + how to apply + limitations
  CHARACTERS.md                the numbered 156-character list
  unbound-character-mode.zip   all of the above

Never includes a ROM. The BPS applies to Pokemon Unbound v2.1.1.1 (which
players build themselves from a FireRed ROM + Skeli's official patch).
"""
import hashlib
import os
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIST = os.path.join(ROOT, "dist")
BPS = os.path.join(ROOT, "build", "unbound-cm.bps")
PATCHED = os.path.join(ROOT, "build", "unbound-cm.gba")

sys.path.insert(0, os.path.join(HERE, "character_mode"))
import emit_character_list

README = """# Character Mode for Pokemon Unbound v2.1.1.1

An opt-in game mode: at the start of a new game, pick one of 156 iconic
Pokemon characters (protagonists, rivals, gym leaders, Elite Four,
champions, villains, and anime cast, Generations 1-8) and play the whole
game restricted to that character's canon Pokemon.

## What it does

- **New-game prompt**: right after Unbound's difficulty questionnaire, an
  extra question offers Character Mode. Enter your character's number
  (see CHARACTERS.md), confirm, and the mode is locked in for that save.
- **Starter**: your starter is replaced by your character's own starter
  (their signature Pokemon's base stage).
- **Catching**: wild Pokemon outside your character's roster cannot be
  caught — the ball is dodged, like the game's own no-catching zones.
  Rosters include full evolution families of every canon team member.
- **Gifts**: scripted gift Pokemon that are off-roster go to your PC
  instead of your party (so nothing is ever lost, and gift events never
  block progress).
- **In-game trades**: you can still complete every Borrius trade; an
  off-roster incoming Pokemon is sent to your PC after the trade.
- Answering "No" at the prompt (or cancelling the number entry) leaves
  the game completely vanilla. The choice is made once per save file.

## How to apply

1. Obtain a Pokemon FireRed (USA) ROM and apply Skeli's official
   Pokemon Unbound v2.1.1.1 patch to it, producing
   `Pokemon Unbound (v2.1.1.1).gba` (sha1
   `{src_sha1}`).
2. Apply `unbound-character-mode.bps` to that ROM with Flips
   (https://github.com/Alcaro/Flips), or any BPS patcher.
3. The result should have sha1 `{out_sha1}`.

## Known limitations

- The starter scene's dialogue/preview sprite still shows the original
  species; the Pokemon you actually receive (and its "received!" text)
  is your character's starter.
- Characters keep the normal player sprites (no custom character art).
- If your character's roster makes a required trade species uncatchable,
  that side quest reward may be unreachable — pick accordingly.

## Credits

- Pokemon Unbound by Skeli789 and team.
- Complete FireRed Upgrade (CFRU) engine by Skeli789 et al.
- Character rosters compiled from Bulbapedia.
- Character Mode port: see the project repository.

This is a fan-made, non-profit patch. Never distributed as a ROM.
"""


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    assert os.path.exists(BPS), "build/unbound-cm.bps missing — run tools/build_patch.py first"
    os.makedirs(DIST, exist_ok=True)

    with open(os.path.join(ROOT, "rom.sha1")) as f:
        src_sha1 = f.read().split()[0]
    out_sha1 = sha1(PATCHED)

    bps_out = os.path.join(DIST, "unbound-character-mode.bps")
    shutil.copyfile(BPS, bps_out)
    readme_out = os.path.join(DIST, "README.md")
    with open(readme_out, "w") as f:
        f.write(README.format(src_sha1=src_sha1, out_sha1=out_sha1))
    chars_out = os.path.join(DIST, "CHARACTERS.md")
    emit_character_list.main(chars_out)

    zip_out = os.path.join(DIST, "unbound-character-mode.zip")
    with zipfile.ZipFile(zip_out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in (bps_out, readme_out, chars_out):
            z.write(p, os.path.basename(p))
    print(f"dist assembled: {DIST}")
    for p in sorted(os.listdir(DIST)):
        print(f"  {p} ({os.path.getsize(os.path.join(DIST, p))} bytes)")


if __name__ == "__main__":
    main()
