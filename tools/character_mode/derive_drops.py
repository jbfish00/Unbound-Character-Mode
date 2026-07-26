#!/usr/bin/env python3
"""Re-derive character_drops.json from THIS repo's own roster data.

The rule (user, 2026-07-25): a character with fewer than six fully-evolved
Pokemon obtainable in this game is not offered here -- unless a legendary or
mythical is on the roster, which exempts them. Characters already in the table
keep their slot and are hidden from the menu (saves store the character INDEX,
so deleting a row repoints every existing save at a different character).

Why this exists rather than the audit's own per_game_threshold.py: that script
reads the audit's `final_rosters.json`, which does NOT include this repo's
`roster_additions.json` overlay or its wave-5 verdicts, so its answer drifts from
what the ROM actually enforces in both directions. Applying it verbatim to ROWE
left 20 Legends: Arceus wardens selectable with a single final evolution each.

The two walks below are borrowed, not reimplemented:
  * `emit_characters.expand_family` -- the exact expansion written into
    rosters.bin, the blob the enforcement shim scans.
  * `emit_roster_docs`'s finals rule -- childless species, collapsed onto the
    canonical species for their National Dex number, skipping alt forms with no
    dex entry and cosmetic forms whose base still evolves.
Sharing both means the threshold, the blob and the docs cannot disagree about
who is thin.

Run BEFORE emit_characters.py; it rewrites character_drops.json in place.

Usage: derive_drops.py [--dry-run] [--new-only]
"""
import argparse
import importlib.util
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--new-only", metavar="BASELINE_JSON",
                    help="report only characters absent from this baseline "
                         "rosters_mapped.json (used when deciding which newly "
                         "appended characters are worth adding at all)")
    args = ap.parse_args()

    ms = _load("map_species")
    emit = _load("emit_characters")
    docs = _load("emit_roster_docs")

    const_id = ms.species_ids()
    kids = docs.evolution_children(ms.DONOR, const_id)
    dex = docs.national_dex(ms.DONOR, const_id)
    children = emit.family_children_map()

    canonical = {}
    for sid in sorted(dex):
        canonical.setdefault(dex[sid], sid)

    def finals_of(ids):
        """Fully-evolved species this roster reaches -- same rule as the docs."""
        out = set()
        for sid in list(ids) + emit.expand_family(list(ids), children):
            if kids.get(sid):
                continue
            num = dex.get(sid)
            if not num or num > docs.MAX_NATIONAL_DEX:
                continue                      # alt form with no dex entry
            base = canonical.get(num, sid)
            if kids.get(base):
                continue                      # cosmetic form of an evolver
            out.add(base)
        return out

    with open(os.path.join(HERE, "rosters_mapped.json")) as f:
        mapped = json.load(f)

    baseline = None
    if args.new_only:
        with open(args.new_only) as f:
            baseline = set(json.load(f))

    under, kept, exempt = [], [], []
    for char, info in sorted(mapped.items()):
        if baseline is not None and char in baseline:
            continue
        name = re.sub(r"\s*\(anime\)$", "", char)
        ids = [s["id"] for s in info["species"]]
        consts = {s["const"] for s in info["species"]}
        if consts & emit.LEGENDARY_BASES:
            exempt.append(name)
            kept.append(name)
            continue                          # legendary/mythical exemption
        n = len(finals_of(ids))
        if n < 6:
            under.append((name, n))
        else:
            kept.append(name)

    considered = len(kept) + len(under)
    print("%d characters considered: %d clear the threshold (%d by legendary "
          "exemption), %d fall under it"
          % (considered, len(kept), len(exempt), len(under)))
    for n, c in sorted(under, key=lambda x: (x[1], x[0])):
        print("   %-14s %d final%s" % (n, c, "" if c == 1 else "s"))

    if args.new_only:
        print("(--new-only: reporting the %d characters absent from %s; "
              "character_drops.json not touched)"
              % (considered, os.path.basename(args.new_only)))
        return

    path = os.path.join(HERE, "character_drops.json")
    old = set()
    if os.path.isfile(path):
        with open(path) as f:
            old = set(json.load(f).get("unselectable", []))
    new = sorted(n for n, _ in under)
    if not args.dry_run:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"_comment": "Characters that stay in the table (saves "
                                   "store the INDEX) but fall under the "
                                   "six-fully-evolved threshold in this game's "
                                   "dex, with no legendary to exempt them. "
                                   "GENERATED by derive_drops.py -- do not "
                                   "hand-edit.",
                       "unselectable": new}, f, indent=1, sort_keys=True,
                      ensure_ascii=False)
            f.write("\n")
    for n in sorted(set(new) - old):
        print("   + newly under threshold: %s" % n)
    for n in sorted(old - set(new)):
        print("   - now clears threshold:  %s" % n)
    if args.dry_run:
        print("(dry run -- character_drops.json not rewritten)")


if __name__ == "__main__":
    main()
