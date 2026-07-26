#!/usr/bin/env python3
"""Fill missing source labels from the 2026-07-25 audit's own batch results.

The audit's `batch_*_result.json` files record, per kept species, both a
`source` and a `why` -- 2,650 labelled species across 198 characters. None of it
was ever read: `roster_sources.json` was built from a different pass, so rows the
audit had already attributed still printed "—".

This is the same shape of miss `push_rosters.md` §1.5 records for Radical Red,
where `roster_additions.json` turned out to carry a per-row source that nothing
consumed -- worth 57 points of coverage there with no network calls. It is easy
to miss because the audit files are keyed CHARACTER -> {"keep": [{species,
source, ...}]}, so a search for objects carrying `character` + `species` +
`source` together finds nothing.

GAP-FILL ONLY, in two senses: a character/species that already has a non-null
source is never touched, and an entry whose recorded source is null IS filled
(those nulls are what mask a family's good label -- see pick_source).

Idempotent. Run before emit_roster_docs.py.

Usage: merge_audit_sources.py [--dry-run] [--audit-dir DIR]
"""
import argparse
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_AUDIT = HERE.parents[2] / "audit_2026-07-25"
SOURCES = HERE / "roster_sources.json"
# Buckets in a batch result that hold KEPT species. "remove"/"drop" are
# deliberately excluded: a species the audit rejected must not gain a label and
# come back looking legitimate.
KEEP_BUCKETS = ("keep", "keeps", "add", "additions")


def harvest(audit_dir):
    """{character: {species: {"owned_form": ..., "source": ...}}}"""
    out = {}
    files = sorted(Path(audit_dir).glob("batch_*_result.json"))
    for path in files:
        try:
            data = json.loads(path.read_text())
        except (ValueError, OSError):
            continue
        if not isinstance(data, dict):
            continue
        for char, rec in data.items():
            if not isinstance(rec, dict) or char.startswith("_"):
                continue
            for bucket in KEEP_BUCKETS:
                for entry in (rec.get(bucket) or []):
                    if not isinstance(entry, dict):
                        continue
                    species, source = entry.get("species"), entry.get("source")
                    if not species or not source:
                        continue
                    out.setdefault(char, {}).setdefault(species, {
                        "owned_form": entry.get("owned_form") or species,
                        "source": source,
                        "derived": "audit-2026-07-25-batch-result",
                    })
    return out, len(files)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--audit-dir", default=str(DEFAULT_AUDIT))
    args = ap.parse_args()

    if not os.path.isdir(args.audit_dir):
        raise SystemExit("audit directory not found: %s" % args.audit_dir)

    found, n_files = harvest(args.audit_dir)
    doc = json.loads(SOURCES.read_text())
    sources = doc["sources"]

    added = filled = kept = 0
    for char, rows in found.items():
        target = sources.setdefault(char, {})
        for species, info in rows.items():
            cur = target.get(species)
            if cur is None:
                target[species] = dict(info)
                added += 1
            elif not cur.get("source"):
                cur["source"] = info["source"]
                cur.setdefault("owned_form", info["owned_form"])
                cur["derived"] = "%s + audit-2026-07-25-batch-result" % (
                    cur.get("derived") or "unknown")
                filled += 1
            else:
                kept += 1

    print("%d batch result files -> %d characters, %d labelled species"
          % (n_files, len(found), sum(len(v) for v in found.values())))
    print("  %d new entries, %d null sources filled, %d existing labels kept"
          % (added, filled, kept))
    if args.dry_run:
        print("  (dry run -- nothing written)")
        return 0
    SOURCES.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    print("  wrote %s" % SOURCES.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
