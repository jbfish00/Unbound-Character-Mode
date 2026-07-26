#!/usr/bin/env python3
"""Which of this repo's roster families has NO audit verdict behind them?

The 2026-07-25 adversarial audit was scoped to the roster data as it stood then.
Every game's `rosters_raw.json` is curated data with its own history, so each one
holds families no wave ever looked at -- ROWE had 156, Radical Red 89. Those
families are UNVERIFIED, not verified-clean, and the distinction matters at
attribution time: running `fill_sources.py` over them would stamp a source on
data nobody checked, presenting unchecked rows as checked. That is the exact
failure the audit exists to fix, so this finds them before any label is written.

An entry counts as AUDITED if some wave returned a verdict on it for that
character -- a keep, a removal, or an explicit `audit_keeps.json` shield. FAMILY
level, not species level: the audit judged "Ash's Pikachu" and the roster stores
"Pichu", and a species-level comparison reports huge numbers of false positives
by counting every unexamined stage of an examined family.

Usage: unaudited_families.py [--json out.json]
Writes: unaudited_families.json (the wave-5 work list)
"""
import argparse
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "audit_2026-07-25"))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load(path, key=None):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data[key] if key else data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=os.path.join(HERE, "unaudited_families.json"))
    args = ap.parse_args()

    ms = _load("map_species")
    ids = ms.species_ids()
    name_id = ms.name_to_id()
    id_const = {v: k for k, v in ids.items()}
    base = ms.first_stage_map()

    def resolve(name):
        sid = name_id.get(ms.NAME_FIXES.get(name, name))
        if sid is None:
            const = ms.regional_fallback(name, ids, name_id, id_const)
            if const is not None:
                return base.get(const, const)
            pre = ms.GEN9_EVO_OF.get(name)
            if pre:
                sid = name_id.get(ms.NAME_FIXES.get(pre, pre))
        if sid is None:
            return None
        const = id_const.get(sid)
        return base.get(const, const) if const else None

    mapped = load(os.path.join(HERE, "rosters_mapped.json"))
    removals = load(os.path.join(HERE, "roster_removals.json"), "removals")
    keeps = load(os.path.join(HERE, "audit_keeps.json"), "keeps")
    final = load(os.path.join(AUDIT, "final_rosters.json"), "rosters")
    compiled = load(os.path.join(AUDIT, "audit_compiled.json"))

    verdicts = {}
    for src in (final, keeps, compiled.get("keep", {})):
        for char, rows in src.items():
            if char.startswith("_"):
                continue
            names = rows.keys() if isinstance(rows, dict) else rows
            verdicts.setdefault(char, set()).update(names)
    for src in (removals, compiled.get("remove", {})):
        for char, rows in src.items():
            if char.startswith("_"):
                continue
            verdicts.setdefault(char, set()).update(
                r["species"] if isinstance(r, dict) else r for r in rows)

    audited = {}
    for char, names in verdicts.items():
        audited[char] = {b for b in (resolve(n) for n in names) if b}

    out, unseen, total = {}, [], 0
    for char, info in sorted(mapped.items()):
        known = audited.get(char)
        if known is None:
            unseen.append(char)
            known = set()
        gap = sorted(s["const"].replace("SPECIES_", "").title()
                     for s in info["species"] if s["const"] not in known)
        if gap:
            out[char] = gap
            total += len(gap)

    payload = {
        "_comment": "Roster families in this repo that NO audit wave examined. "
                    "Judge these with audit_2026-07-25/wave5/BRIEF.md before any "
                    "attribution pass labels them -- sourcing an unaudited row "
                    "presents unchecked data as checked.",
        "characters_never_audited": unseen,
        "unaudited": out,
    }
    with open(args.json, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1, ensure_ascii=False, sort_keys=True)
        f.write("\n")

    covered = sum(len(v["species"]) for v in mapped.values())
    print("families in rosters_mapped.json: %d across %d characters"
          % (covered, len(mapped)))
    print("NEVER AUDITED: %d families across %d characters (%.1f%%)"
          % (total, len(out), 100.0 * total / max(1, covered)))
    print("characters with no audit verdict at all: %d%s"
          % (len(unseen), (" -- " + ", ".join(unseen)) if unseen else ""))
    for char, gap in sorted(out.items(), key=lambda kv: -len(kv[1]))[:12]:
        print("  %-16s %3d  %s" % (char, len(gap), ", ".join(gap[:8])))
    print("wrote %s" % os.path.relpath(args.json, HERE))


if __name__ == "__main__":
    main()
