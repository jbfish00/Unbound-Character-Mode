#!/usr/bin/env python3
"""Build fill_sources.py's worklist: the roster families whose doc row has no
Source yet.

Derived from `rosters_mapped.json` and the same source lookup
`emit_roster_docs.py` performs, so the worklist is exactly the set of rows that
currently print "—" -- not a guess, and not the full roster.

SAFETY: a family that no audit wave examined is EXCLUDED and reported. Attaching
a mechanically-derived label to unaudited data would present unchecked rows as
checked, which is the precise failure the 2026-07-25 audit exists to correct.
Run `unaudited_families.py`, judge what it finds with
`audit_2026-07-25/wave5/BRIEF.md`, and apply the verdicts with `apply_wave5.py`
BEFORE running this.

Usage: needed_sources.py
Writes: sources_needed.json
"""
import json
from pathlib import Path

import importlib.util

HERE = Path(__file__).parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, str(HERE / (name + ".py")))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


erd = _load("emit_roster_docs")
ms = _load("map_species")


def main():
    const_id = ms.species_ids()
    name_id = ms.name_to_id()
    id_const = {v: k for k, v in const_id.items()}
    base_of = ms.first_stage_map()

    def resolve_base(name):
        sid = name_id.get(ms.NAME_FIXES.get(name, name))
        if sid is None:
            const = ms.regional_fallback(name, const_id, name_id, id_const)
            if const is None:
                pre = ms.GEN9_EVO_OF.get(name)
                const = (id_const.get(name_id.get(ms.NAME_FIXES.get(pre, pre)))
                         if pre else None)
            return base_of.get(const, const) if const else None
        const = id_const.get(sid)
        return base_of.get(const, const) if const else None

    sources = erd.rekey_sources_onto_family_base(erd.load_sources(), resolve_base)
    with open(HERE / "rosters_mapped.json") as f:
        mapped = json.load(f)

    unaudited = {}
    path = HERE / "unaudited_families.json"
    if path.is_file():
        with open(path, encoding="utf-8") as f:
            unaudited = json.load(f).get("unaudited", {})

    need, skipped = {}, 0
    for char, info in sorted(mapped.items()):
        per_base = sources.get(char, {})
        blocked = {n.upper() for n in unaudited.get(char, ())}
        gaps = []
        for entry in info["species"]:
            const = entry["const"]
            if per_base.get(const):
                continue
            plain = const.replace("SPECIES_", "").title()
            if plain.upper() in blocked:
                skipped += 1
                continue
            gaps.append(id_const and (name_id and plain))
        if gaps:
            need[char] = sorted(set(gaps))

    with open(HERE / "sources_needed.json", "w", encoding="utf-8") as f:
        json.dump(need, f, indent=1, ensure_ascii=False, sort_keys=True)
        f.write("\n")

    total = sum(len(v) for v in need.values())
    print("%d families need a source, across %d characters" % (total, len(need)))
    for char, gaps in sorted(need.items(), key=lambda kv: -len(kv[1]))[:12]:
        print("   %-16s %3d  %s" % (char, len(gaps), ", ".join(gaps[:6])))
    if skipped:
        print("EXCLUDED %d families that no audit wave examined -- judge them first"
              % skipped)
    print("wrote sources_needed.json")


if __name__ == "__main__":
    main()
