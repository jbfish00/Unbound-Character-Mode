#!/usr/bin/env python3
"""Emit ENCOUNTERS.md — what each character can actually meet in the wild.

game_plans/legendary_encounters.md §3. Generated, never hand-written, the way
ROSTERS.md is: the source is `wild_species_meta.bin` + `characters.bin` +
`rosters.bin` — the exact blobs the injected picker walks — so the doc cannot
promise an encounter the ROM will not produce.

⚠️ Deliberately NOT derived from rosters_mapped.json. That file sits upstream
of the level-band computation and of the per-game dex filter, so it lists
families this ROM cannot spawn. The spec calls this out by name.

Two pools per character, matching the two independent rolls in
CharacterMode_MaybeOverrideWildSpecies:

    ~1%  legendary families   (Pokedex-filtered: once each, or repeatable
                               when the roster is legendaries-only)
    ~10% non-legendary families
    rest the game's own encounter tables

Characters whose non-legendary pool is EMPTY are called out explicitly — that
is the catch-nothing failure mode and it must be impossible to miss here.

Run after emit_characters.py / emit_wild_meta.py.
"""
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from decode_gametext import load_charmap

ROM = os.path.join(ROOT, "rom", "Pokemon Unbound (v2.1.1.1).gba")
CHARMAP = "/home/jbfish00/Documents/Pokemon Rowe Alteration/charmap.txt"
SPECIES_NAMES_OFF = 0x966A98C - 0x08000000   # gSpeciesNames (DPE-repointed), stride 11
META_STRIDE = 6
GAME_TITLE = "Pokemon Unbound v2.1.1.1"

# Must match src/character_mode.c
LEGENDARY_CHANCE_PERCENT = 1
OVERRIDE_CHANCE_PERCENT = 10

CATEGORY_LABEL = {"protagonist": "Protagonist", "rival": "Rival",
                  "gymleader": "Gym Leader", "elite4": "Elite Four",
                  "champion": "Champion", "villain": "Villain",
                  "anime": "Anime", "frontier": "Frontier Brain"}


def load_meta():
    with open(os.path.join(HERE, "wild_species_meta.bin"), "rb") as f:
        blob = f.read()
    out = {}
    for sp in range(len(blob) // META_STRIDE):
        lmin, lmax, flags, _pad, root = struct.unpack_from("<BBBBH", blob, sp * META_STRIDE)
        out[sp] = {"levelMin": lmin, "levelMax": lmax,
                   "legendary": bool(flags & 1), "familyRoot": root}
    return out


def main(out_path=None):
    out_path = out_path or os.path.join(ROOT, "ENCOUNTERS.md")
    cmap = load_charmap(CHARMAP)
    with open(ROM, "rb") as f:
        rom = f.read()

    def spname(sid):
        s = ""
        for b in rom[SPECIES_NAMES_OFF + sid * 11: SPECIES_NAMES_OFF + sid * 11 + 11]:
            if b == 0xFF:
                break
            s += cmap.get(b, "?")
        return s

    meta = load_meta()
    with open(os.path.join(HERE, "characters_manifest.json")) as f:
        manifest = json.load(f)["characters"]

    def pools(rec):
        """Split a roster into {familyRoot: [members]}, legendary and not.

        Mirrors CharacterMode_PickWildFamily exactly: a species outside the
        metadata table is skipped (it can never be picked), families are keyed
        by familyRoot, and the two pools are disjoint by the legendary bit."""
        legend, plain = {}, {}
        for sp in (rec.get("roster_species_ids") or []):
            m = meta.get(sp)
            if m is None:
                continue
            (legend if m["legendary"] else plain).setdefault(m["familyRoot"], []).append(sp)
        return legend, plain

    def fam_cell(members):
        """One family: each stage with the level band the picker matches on."""
        parts = []
        for sp in sorted(members, key=lambda s: (meta[s]["levelMin"], s)):
            m = meta[sp]
            parts.append("%s (L%d-%d)" % (spname(sp), m["levelMin"], m["levelMax"]))
        return " → ".join(parts)

    rows = []
    hidden = 0
    for rec in manifest:
        if rec.get("hidden"):
            hidden += 1
            continue          # not selectable, so not documented (same rule as ROSTERS.md)
        legend, plain = pools(rec)
        rows.append({
            "name": rec["character"],
            "gen": rec["generation"],
            "label": CATEGORY_LABEL.get(rec["category"], (rec["category"] or "").title()),
            "legend": legend,
            "plain": plain,
            # The §1.2 exemption, computed the same way the ROM computes it:
            # no non-legendary family at all -> legendaries stay repeatable.
            "repeatable": bool(legend) and not plain,
        })

    empty = [r for r in rows if not r["plain"] and not r["legend"]]
    no_plain = [r for r in rows if not r["plain"] and r["legend"]]
    with_legend = [r for r in rows if r["legend"]]

    out = []
    out.append("# Character Mode — Wild Encounter Pools (%s)" % GAME_TITLE)
    out.append("")
    out.append("What each playable character can meet in the wild, derived from "
               "`wild_species_meta.bin` and `rosters.bin` — the same blobs the "
               "injected encounter hook walks, so nothing here is promised that "
               "the ROM will not produce.")
    out.append("")
    out.append("GENERATED by `tools/character_mode/emit_encounter_tables.py` — "
               "do not hand-edit, regenerate.")
    out.append("")
    out.append("## How encounters work in Character Mode")
    out.append("")
    out.append("Every wild encounter runs two independent rolls before the game's "
               "own table is consulted:")
    out.append("")
    out.append("| roll | chance | result |")
    out.append("|---|---|---|")
    out.append("| legendary | **~%d%%** | a legendary family from your roster, "
               "level-matched to the area |" % LEGENDARY_CHANCE_PERCENT)
    out.append("| roster | **~%d%%** | a non-legendary family from your roster, "
               "level-matched to the area |" % OVERRIDE_CHANCE_PERCENT)
    out.append("| — | rest | the game's own encounter, untouched |")
    out.append("")
    out.append("Within a family, the stage whose level band best fits the area's "
               "rolled level is the one that appears, so a low route gives the "
               "first stage and a late one gives the final evolution.")
    out.append("")
    out.append("**Legendaries are offered until you catch them**, then drop out of "
               "the pool — tracked by the Pokédex's own caught flag, so it costs no "
               "extra save data. Two consequences: a legendary caught *before* "
               "enabling Character Mode is never offered, and one caught then "
               "released or traded away still counts as caught. The flag is per "
               "National Dex number, so catching one form of a multi-form legendary "
               "marks them all.")
    out.append("")
    out.append("**Exception:** a character whose roster is *entirely* legendary "
               "keeps them repeatable forever. Without that they would catch their "
               "one family and then be unable to catch anything at all for the rest "
               "of the run.")
    out.append("")
    out.append("### Coverage")
    out.append("")
    out.append("- **%d selectable characters** documented (%d more are hidden from "
               "the character-select screen and are not listed)."
               % (len(rows), hidden))
    out.append("- **%d of %d have at least one legendary** in their pool."
               % (len(with_legend), len(rows)))
    out.append("- **%d have a legendaries-only roster**, so their legendaries "
               "repeat: %s."
               % (len(no_plain), ", ".join(r["name"] for r in no_plain) or "none"))
    if empty:
        out.append("- ⚠️ **%d have NO wild pool at all** and can catch nothing "
                   "beyond the game's own encounters: %s."
                   % (len(empty), ", ".join(r["name"] for r in empty)))
    else:
        out.append("- **No character has an empty pool** — every selectable "
                   "character can find something of their own in the wild.")
    out.append("")

    gens = sorted({r["gen"] for r in rows})
    out.append("## Contents")
    out.append("")
    for g in gens:
        out.append("- [Generation %d](#generation-%d)" % (g, g))
    out.append("")

    for g in gens:
        out.append("## Generation %d" % g)
        out.append("")
        for r in sorted((x for x in rows if x["gen"] == g), key=lambda x: x["name"]):
            rate_plain = OVERRIDE_CHANCE_PERCENT if r["plain"] else 0
            rate_legend = LEGENDARY_CHANCE_PERCENT if r["legend"] else 0
            note = " · legendaries **repeat**" if r["repeatable"] else ""
            out.append("### %s — %s" % (r["name"], r["label"]))
            out.append("")
            out.append("Roster encounters **~%d%%** · legendary **~%d%%**%s"
                       % (rate_plain, rate_legend, note))
            out.append("")
            if not r["plain"] and not r["legend"]:
                out.append("> ⚠️ **No wild pool.** Nothing on this character's "
                           "roster can appear in the wild.")
                out.append("")
                continue
            if r["plain"]:
                out.append("| Roster family (~%d%%) |" % rate_plain)
                out.append("|---|")
                for root in sorted(r["plain"], key=lambda k: min(r["plain"][k])):
                    out.append("| %s |" % fam_cell(r["plain"][root]))
                out.append("")
            else:
                out.append("> No non-legendary family can appear in the wild for "
                           "this character.")
                out.append("")
            if r["legend"]:
                out.append("| Legendary family (~%d%%, %s) |"
                           % (rate_legend,
                              "repeatable" if r["repeatable"] else "once each"))
                out.append("|---|")
                for root in sorted(r["legend"], key=lambda k: min(r["legend"][k])):
                    out.append("| %s |" % fam_cell(r["legend"][root]))
                out.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("wrote %s: %d characters, %d with a legendary, %d legendaries-only, "
          "%d with no pool"
          % (os.path.relpath(out_path, ROOT), len(rows), len(with_legend),
             len(no_plain), len(empty)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
