#!/usr/bin/env python3
"""Assemble the distributable package (Phase 6).

Contents of dist/:
  unbound-character-mode.bps   the patch (copy of build/unbound-cm.bps)
  README.md                    what it is + how to apply + limitations
  CHARACTERS.md                the numbered character list
  unbound-character-mode.zip   all of the above

Never includes a ROM. The BPS applies to Pokemon Unbound v2.1.1.1 (which
players build themselves from a FireRed ROM + Skeli's official patch).
"""
import hashlib
import json
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

An opt-in game mode: at the start of a new game, pick one of {n_chars} iconic
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
- **Wild encounters**: about 10% of wild encounters are replaced by a
  Pokemon from your character's roster, at a level that fits the area,
  so you can actually find your team instead of hunting for it. The
  other ~90% are the game's own encounters, unchanged.
- **Legendaries**: if your character's roster includes a legendary, it
  has about a 1% chance of appearing in any wild encounter, at the
  area's level. Each one is offered until you catch it, then stops
  appearing — unless your character's roster is legendaries only, in
  which case they keep appearing so you always have something to catch.
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
- The character portrait shown when you pick appears only on that
  confirmation screen. Your overworld sprite, trainer card and battle
  back-sprite stay the normal Unbound player art.
- {n_no_art} of the {n_sel} selectable characters have no portrait staged
  yet; picking one shows the confirmation with no art beside it.
- If your character's roster makes a required trade species uncatchable,
  that side quest reward may be unreachable — pick accordingly.

## Credits

- Pokemon Unbound by Skeli789 and team.
- Complete FireRed Upgrade (CFRU) engine by Skeli789 et al.
- Character rosters compiled from Bulbapedia.
- Character Mode port: see the project repository.

### Character portrait art

This patch injects trainer front-pic art from several fan projects. Credit is a
condition of use for these, so it travels with the patch:

- **Pokemon Ash Gray** by **metapod23** — anime-cast portraits.
- **Emerald Rogue** (Pokabbie) — the largest set. It ships no per-artist
  mapping, so its whole ~42-name "Additional Sprites" credits roll travels with
  any subset of the art; see CREDITS.md in the project repository.
- **Team Aqua's Asset Repo** — free to use and edit **with credit to the
  original creator** of each sprite.
- **pokemonHnS**, **pokeemerald-platinum**, **Pokesho (ポケしょ)**, **LouLilie**.

Full per-set terms and per-sprite provenance: CREDITS.md, shipped alongside.

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
        # DERIVE the count -- it read a literal 179 and would have shipped a
        # README advertising the wrong number of characters the moment the roster
        # changed, which is exactly how this file came to say 156 once before.
        # ...and it counts what the player can actually PICK, not how many
        # records the table holds: the threshold gate hides some, and promising
        # a number the select screen refuses is the same defect in a new place.
        with open(os.path.join(HERE, "character_mode",
                               "characters_manifest.json")) as mf:
            selectable = [c for c in json.load(mf)["characters"]
                          if not c.get("hidden")]
        n_chars = len(selectable)
        # Portrait coverage is derived the same way, and counted over the
        # SELECTABLE characters only -- a player cannot pick a hidden one, so
        # folding those into "no art yet" would overstate the gap.
        with open(os.path.join(HERE, "character_mode",
                               "cm_sprite_manifest.json")) as sf:
            with_art = {e["character"] for e in json.load(sf)["entries"]}
        n_no_art = sum(1 for c in selectable if c["character"] not in with_art)
        f.write(README.format(src_sha1=src_sha1, out_sha1=out_sha1,
                              n_chars=n_chars, n_sel=n_chars,
                              n_no_art=n_no_art))
    chars_out = os.path.join(DIST, "CHARACTERS.md")
    emit_character_list.main(chars_out)

    # CREDITS.md is not optional packaging: the patch injects third-party
    # sprite art whose licences REQUIRE attribution, and shipping the art
    # without it was a real obligation gap, not a documentation nicety.
    credits_src = os.path.join(ROOT, "CREDITS.md")
    credits_out = os.path.join(DIST, "CREDITS.md")
    assert os.path.isfile(credits_src), (
        "CREDITS.md missing -- refusing to build a dist that ships donor "
        "sprite art with no attribution")
    shutil.copyfile(credits_src, credits_out)

    zip_out = os.path.join(DIST, "unbound-character-mode.zip")
    with zipfile.ZipFile(zip_out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in (bps_out, readme_out, chars_out, credits_out):
            z.write(p, os.path.basename(p))
    print(f"dist assembled: {DIST}")
    for p in sorted(os.listdir(DIST)):
        print(f"  {p} ({os.path.getsize(os.path.join(DIST, p))} bytes)")


if __name__ == "__main__":
    main()
