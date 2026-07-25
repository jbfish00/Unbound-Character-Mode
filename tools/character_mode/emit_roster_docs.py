#!/usr/bin/env python3
"""Generate ROSTERS.md / ROSTERS_SPRITES.md / sprites/gen_*.md from the data
the ROM actually enforces.

Why this exists: these docs used to be hand-maintained, and in the ROWE
reference project that produced a shipped doc promising 194 family bases the
catch gate refused while omitting thousands it already allowed. Here they are
read straight out of `rosters.bin` - the injected roster blob the enforcement
shim walks - so a doc entry cannot claim anything the ROM does not honour.

Inputs:
  rosters.bin               the injected per-character roster (u16 ids, 0-term)
  characters_manifest.json  character order, names, generation, category,
                            and each roster's offset into rosters.bin
  the DPE Unbound donor     species names, evolution table, National Dex map

"Final evolutions" = allowed species nothing else evolves them into. Mega and
Gigantamax rows in the evolution table are battle transformations, not
evolutions: counting them would drop every mega-capable species out of the
list. Species with no National Dex number (Unbound's alt forms) collapse onto
the base species they share a dex number with.

Run after emit_characters.py:
    python3 tools/character_mode/emit_roster_docs.py
"""
import importlib.util
import json
import os
import re
import struct
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.abspath(os.path.join(HERE, "..", ".."))

GAME_TITLE = "Pokémon Unbound v2.1.1.1"
# Unbound has no Gen 9 content at all (verified in-ROM, see CLAUDE.md), so the
# dex tops out at Enamorus.
MAX_NATIONAL_DEX = 905
NON_EVOLUTION_METHODS = {"EVO_MEGA", "EVO_GIGANTAMAX"}

CATEGORY_LABEL = {
    "protagonist": "Protagonist", "rival": "Rival", "gymleader": "Gym Leader",
    "elite4": "Elite Four", "champion": "Champion", "villain": "Villain",
    "anime": "Anime", "professor": "Professor", "frontier": "Frontier Brain",
}

SPRITE_URL = ("https://cdn.jsdelivr.net/gh/PokeAPI/sprites@master"
              "/sprites/pokemon/%d.png")
SPRITES_PER_ROW = 8


def load_map_species():
    """The pipeline's own resolver, reused so names/ids come from exactly the
    same donor files the roster data was built from."""
    spec = importlib.util.spec_from_file_location(
        "map_species", os.path.join(HERE, "map_species.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def evolution_children(donor, const_id):
    """species id -> [ids it really evolves into]."""
    text = open(os.path.join(donor, "src/Evolution Table.c"), encoding="utf-8").read()
    body = re.search(r"gEvolutionTable\[NUM_SPECIES\]\[EVOS_PER_MON\]\s*=\s*\{(.*?)^\};",
                     text, re.S | re.M).group(1)
    rows = [(r.start(), r.group(1)) for r in re.finditer(r"\[(SPECIES_\w+)\]\s*=", body)]
    kids = defaultdict(set)
    for t in re.finditer(r"\{\s*(EVO_\w+)\s*,[^,{}]+,\s*(SPECIES_\w+)", body):
        if t.group(1) in NON_EVOLUTION_METHODS:
            continue
        src = None
        for pos, name in rows:
            if pos < t.start():
                src = name
            else:
                break
        if not src or src == t.group(2):
            continue
        a, b = const_id.get(src), const_id.get(t.group(2))
        if a and b:
            kids[a].add(b)
    return kids


def national_dex(donor, const_id):
    """species id -> National Dex number, from the donor's own
    gSpeciesToNationalPokedexNum + pokedex.h."""
    header = open(os.path.join(donor, "include/pokedex.h"), encoding="utf-8").read()
    nums = {m.group(1): int(m.group(2))
            for m in re.finditer(r"#define\s+(NATIONAL_DEX_\w+)\s+(\d+)", header)}
    if not nums:                       # the header may spell it as an enum
        body = re.search(r"enum\s+\w*\s*\{(.*?)\}\s*;", header, re.S)
        if body:
            n = 0
            for line in body.group(1).splitlines():
                m = re.match(r"\s*(NATIONAL_DEX_\w+)\s*(?:=\s*(\d+))?\s*,", line)
                if not m:
                    continue
                if m.group(2):
                    n = int(m.group(2))
                nums[m.group(1)] = n
                n += 1
    table = open(os.path.join(donor, "src/Species_To_Pokdex_Table.c"),
                 encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"\[(SPECIES_\w+)\s*-\s*1\]\s*=\s*(NATIONAL_DEX_\w+)", table):
        sid = const_id.get(m.group(1))
        if sid and m.group(2) in nums:
            out[sid] = nums[m.group(2)]
    return out


def rosters_from_blob(manifest):
    """[species ids] per character, read out of the injected rosters.bin."""
    blob = open(os.path.join(HERE, "rosters.bin"), "rb").read()
    out = []
    for rec in manifest:
        off, ids = rec["roster_offset"], []
        while True:
            (sid,) = struct.unpack_from("<H", blob, off)
            off += 2
            if sid == 0:               # SPECIES_NONE terminator
                break
            ids.append(sid)
        out.append(ids)
    return out


def main():
    ms = load_map_species()
    donor = ms.DONOR
    const_id = ms.species_ids()
    id_name = {v: k for k, v in ms.name_to_id().items()}
    kids = evolution_children(donor, const_id)
    dex = national_dex(donor, const_id)

    with open(os.path.join(HERE, "characters_manifest.json")) as f:
        manifest = json.load(f)["characters"]
    rosters = rosters_from_blob(manifest)

    # canonical species per dex number (the base form, i.e. the lowest id)
    canonical = {}
    for sid in sorted(dex):
        canonical.setdefault(dex[sid], sid)

    chars = []
    for rec, ids in zip(manifest, rosters):
        finals = set()
        for sid in ids:
            if kids.get(sid):
                continue
            num = dex.get(sid)
            if not num or num > MAX_NATIONAL_DEX:
                continue               # alt form with no dex entry of its own
            base = canonical.get(num, sid)
            if kids.get(base):
                continue               # a cosmetic form of a species that evolves
            finals.add(base)
        ordered = sorted(finals, key=lambda s: (dex[s], id_name.get(s, "")))
        chars.append({
            "name": rec["character"],
            "gen": rec["generation"],
            "label": CATEGORY_LABEL.get(rec["category"], rec["category"].title()),
            "finals": [(id_name.get(s, "#%d" % s), dex[s]) for s in ordered],
        })

    by_gen = defaultdict(list)
    for c in chars:
        by_gen[c["gen"]].append(c)
    for g in by_gen:
        by_gen[g].sort(key=lambda c: c["name"])
    gens = sorted(by_gen)

    generated_note = ("GENERATED by `tools/character_mode/emit_roster_docs.py` "
                      "from `rosters.bin`, the same injected roster blob the "
                      "enforcement shim walks — do not hand-edit, regenerate.")
    dex_note = ("> Species above National Dex #%d are omitted (not present in "
                "this game)." % MAX_NATIONAL_DEX)

    out = ["# Character Mode — Final-Evolution Rosters (%s)" % GAME_TITLE, "",
           "Every playable character and the **final evolutions** their complete "
           "roster resolves to, in **National Pokédex order**. Rosters were "
           "researched from Bulbapedia (union of all games, remakes, rematches, "
           "and anime) and cross-checked where possible. Regional/cosmetic forms "
           "show as their base species. Off-roster Pokémon are routed to your PC.",
           "", dex_note, "",
           "**%d characters.** Sprite version: `ROSTERS_SPRITES.md`." % len(chars),
           "", generated_note, "", "## Contents"]
    for g in gens:
        out.append("- [Generation %d](#generation-%d)" % (g, g))
    out.append("")
    for g in gens:
        out += ["", "## Generation %d" % g, ""]
        for c in by_gen[g]:
            out.append("### %s — %s" % (c["name"], c["label"]))
            out.append("**Final evolutions (%d):**" % len(c["finals"]))
            out.append(", ".join(n for n, _ in c["finals"]))
            out.append("")
    with open(os.path.join(TARGET, "ROSTERS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out).rstrip() + "\n")

    idx = ["# Character Mode — Roster Sprites (%s)" % GAME_TITLE, "",
           "Each character's **final-evolution** roster, in **National Pokédex "
           "order**, with sprites and names. Split by generation to keep pages "
           "fast. Regional/cosmetic forms show as base species. Sprites via "
           "[PokéAPI](https://github.com/PokeAPI/sprites). Text: `ROSTERS.md`.",
           "", "**%d characters.**" % len(chars), "", generated_note,
           "", "## Generations", ""]
    for g in gens:
        idx.append("- [Generation %d](sprites/gen_%d.md) — %d characters"
                   % (g, g, len(by_gen[g])))
    with open(os.path.join(TARGET, "ROSTERS_SPRITES.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(idx).rstrip() + "\n")

    os.makedirs(os.path.join(TARGET, "sprites"), exist_ok=True)
    for g in gens:
        page = ["# %s — Roster Sprites (Generation %d)" % (GAME_TITLE, g), "",
                "Final-evolution rosters in National Pokédex order, sprites with "
                "names. [← back to index](../ROSTERS_SPRITES.md)", ""]
        for c in by_gen[g]:
            page.append("### %s — %s" % (c["name"], c["label"]))
            page.append("<table>")
            row = []
            for name, num in c["finals"]:
                row.append('<td align="center" width="80"><img width="56" src="%s">'
                           "<br><sub>%s</sub></td>" % (SPRITE_URL % num, name))
                if len(row) == SPRITES_PER_ROW:
                    page.append("<tr>" + "".join(row) + "</tr>")
                    row = []
            if row:
                page.append("<tr>" + "".join(row) + "</tr>")
            page += ["</table>", ""]
        with open(os.path.join(TARGET, "sprites/gen_%d.md" % g), "w",
                  encoding="utf-8") as f:
            f.write("\n".join(page).rstrip() + "\n")

    print("wrote ROSTERS.md, ROSTERS_SPRITES.md and %d sprites/gen_*.md: "
          "%d characters, %d final-evolution entries"
          % (len(gens), len(chars), sum(len(c["finals"]) for c in chars)))


if __name__ == "__main__":
    main()
