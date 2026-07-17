#!/usr/bin/env python3
"""Emit the player-facing numbered character list (dist/CHARACTERS.md).

The opt-in prompt tells the player their character's number is "listed in
the patch notes" — this generates that list from characters.txt + the
emitted binary tables, with each character's starter (roster[0], the
signature mon's base stage — exactly what CharacterMode_GetStarterSpecies
grants) named via the ROM's live species-name table.
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from decode_gametext import load_charmap

ROM = os.path.join(ROOT, "rom", "Pokemon Unbound (v2.1.1.1).gba")
CHARMAP = "/home/jbfish00/Documents/Pokemon Rowe Alteration/charmap.txt"
SPECIES_NAMES_OFF = 0x966A98C - 0x08000000  # gSpeciesNames (DPE-repointed), stride 11

CAT = {"protagonist": "Protagonist", "rival": "Rival", "gymleader": "Gym Leader",
       "elite4": "Elite Four", "champion": "Champion", "villain": "Villain",
       "anime": "Anime", "frontier": "Frontier Brain"}


def main(out_path):
    cmap = load_charmap(CHARMAP)
    rom = open(ROM, "rb").read()

    def spname(sid):
        out = ""
        for b in rom[SPECIES_NAMES_OFF + sid * 11: SPECIES_NAMES_OFF + sid * 11 + 11]:
            if b == 0xFF:
                break
            out += cmap.get(b, "?")
        return out

    lines = [l.strip() for l in open(os.path.join(HERE, "characters.txt"))
             if l.strip() and not l.startswith("#")]
    chars = open(os.path.join(HERE, "characters.bin"), "rb").read()
    rosters = open(os.path.join(HERE, "rosters.bin"), "rb").read()
    assert len(chars) // 16 == len(lines), "characters.bin out of sync with characters.txt"

    out = []
    out.append("# Character Mode — Character List (Pokemon Unbound v2.1.1.1)\n")
    out.append("At the Character Mode prompt during a new game, enter the number of the")
    out.append("character you want to play as. You may only catch and keep Pokemon from")
    out.append("that character's roster (canon teams, expanded to full evolution")
    out.append("families). Your starter is replaced by the character's own starter,")
    out.append("listed below. Off-roster gifts and trades are sent to your PC instead")
    out.append("of your party; off-roster wild Pokemon cannot be caught.\n")
    gen_open = None
    for i, l in enumerate(lines):
        name, _pages, cat, gen = [p.strip() for p in l.split("|")]
        if gen != gen_open:
            out.append(f"\n## Generation {gen}\n")
            out.append("| # | Character | Category | Starter | Roster size |")
            out.append("|---|-----------|----------|---------|-------------|")
            gen_open = gen
        roff = struct.unpack_from("<I", chars, 16 * i + 4)[0]
        sig = struct.unpack_from("<H", rosters, roff)[0]
        n = 0
        j = roff
        while struct.unpack_from("<H", rosters, j)[0] != 0:
            n += 1
            j += 2
        out.append(f"| {i + 1} | {name} | {CAT.get(cat, cat.title())} | {spname(sig)} | {n} |")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(out) + "\n")
    print(f"wrote {out_path} ({len(lines)} characters)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "dist", "CHARACTERS.md"))
