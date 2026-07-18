#!/usr/bin/env python3
"""Generate a dense per-species metadata table for the wild-encounter roster
override (tools/build_patch.py's wild-encounter hook; src/character_mode.c's
CharacterMode_PickWildRosterSpecies).

For every species id 0..NUM_SPECIES-1 (donor include/species.h), computes:
  - levelMin/levelMax: the canon level range for THIS evolutionary stage,
    derived from the DPE donor's real 'Evolution Table.c' (same source
    emit_characters.py already walks for family expansion). An incoming
    EVO_LEVEL*-family edge sets levelMin to that edge's level; an outgoing
    one sets levelMax to (that level - 1). Species with no such edge get
    the open bound (1 or 100) — non-level evolutions (stone/trade/friendship)
    don't further constrain the range, which is an accepted approximation
    (the wild-encounter spec explicitly allows "nearest available stage"
    fallback for exactly this reason).
  - familyRoot: the species id of this evolution line's true base (the node
    with no incoming non-mega/gigantamax edge), used at runtime to group a
    roster's flat, family-expanded species list back into distinct lines
    before picking a random one.
  - legendary flag: species is a LEGENDARY_BASES entry or one of its
    (non-mega/gigantamax) evolution descendants — reuses the exact same
    LEGENDARY_BASES set emit_characters.py already uses for starter
    eligibility, so "excluded from wild encounters" and "excluded from
    starters" always agree on what counts as legendary/mythical.

Output: wild_species_meta.bin — NUM_SPECIES records of 6 bytes each
  (u8 levelMin, u8 levelMax, u8 flags [bit0=legendary], u8 reserved,
   u16 familyRoot), native ROM byte order. Species id 0 (SPECIES_NONE) and
  any id with no roster/evolution-table presence still get a well-formed
  record (levelMin=1, levelMax=100, familyRoot=self, not legendary) so an
  out-of-range or off-family lookup never reads garbage.
"""
import os
import re
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
DONOR = os.path.join(HERE, "..", "dpe_unbound_donor")

# Same list emit_characters.py uses for starter eligibility — kept identical
# so wild-encounter exclusion and starter exclusion never disagree.
LEGENDARY_BASES = {"SPECIES_" + s for s in """ARTICUNO ZAPDOS MOLTRES MEWTWO MEW
RAIKOU ENTEI SUICUNE LUGIA HO_OH CELEBI
REGIROCK REGICE REGISTEEL LATIAS LATIOS KYOGRE GROUDON RAYQUAZA JIRACHI DEOXYS
UXIE MESPRIT AZELF DIALGA PALKIA HEATRAN REGIGIGAS GIRATINA CRESSELIA PHIONE MANAPHY DARKRAI SHAYMIN ARCEUS
VICTINI COBALION TERRAKION VIRIZION TORNADUS THUNDURUS RESHIRAM ZEKROM LANDORUS KYUREM KELDEO MELOETTA GENESECT
XERNEAS YVELTAL ZYGARDE DIANCIE HOOPA VOLCANION
TYPE_NULL TAPU_KOKO TAPU_LELE TAPU_BULU TAPU_FINI COSMOG NECROZMA MAGEARNA MARSHADOW ZERAORA MELTAN
NIHILEGO BUZZWOLE PHEROMOSA XURKITREE CELESTEELA KARTANA GUZZLORD POIPOLE STAKATAKA BLACEPHALON
ZACIAN ZAMAZENTA ETERNATUS KUBFU ZARUDE REGIELEKI REGIDRAGO GLASTRIER SPECTRIER CALYREX ENAMORUS""".split()}

NON_EVOLUTIONS = {"EVO_MEGA", "EVO_GIGANTAMAX"}
# unknown field is a level for every EVO_LEVEL* variant except the packed
# day/night time-range one (docs/evolution.h line 45).
LEVEL_EVO_RE = re.compile(r"^EVO_LEVEL(?!_SPECIFIC_TIME_RANGE)")


def load_species_ids():
    with open(os.path.join(DONOR, "include/species.h"), encoding="utf-8") as f:
        text = f.read()
    const_to_id = {}
    for m in re.finditer(r"#define\s+(SPECIES_\w+)\s+(0x[0-9A-Fa-f]+|\d+)", text):
        const_to_id[m.group(1)] = int(m.group(2), 0)
    m = re.search(r"#define\s+NUM_SPECIES\s+\(SPECIES_\w+\s*\+\s*1\)", text)
    assert m, "couldn't find NUM_SPECIES definition"
    last_const = re.search(r"NUM_SPECIES\s+\((SPECIES_\w+)\s*\+\s*1\)", text).group(1)
    num_species = const_to_id[last_const] + 1
    return const_to_id, num_species


def parse_evolution_table(const_to_id):
    """Returns (edges, all_edges) where:
      edges: list of (src_id, level, dst_id) for LEVEL-family evolutions
      all_edges: list of (src_id, dst_id) for every non-mega/gmax evolution
                 (used for family-root/lineage grouping)."""
    with open(os.path.join(DONOR, "src", "Evolution Table.c"), encoding="utf-8") as f:
        text = f.read()
    m = re.search(r"gEvolutionTable\[NUM_SPECIES\]\[EVOS_PER_MON\]\s*=\s*\{(.*?)^\};",
                  text, re.S | re.M)
    body = m.group(1)

    rows = [(r.start(), r.group(1)) for r in re.finditer(r"\[(SPECIES_\w+)\]\s*=", body)]

    def src_for(pos):
        src = None
        for p, name in rows:
            if p < pos:
                src = name
            else:
                break
        return src

    level_edges = []
    all_edges = []
    for t in re.finditer(r"\{\s*(EVO_\w+)\s*,\s*([^,{}]+?)\s*,\s*(SPECIES_\w+)", body):
        kind, val, dst_const = t.group(1), t.group(2).strip(), t.group(3)
        if kind in NON_EVOLUTIONS:
            continue
        src_const = src_for(t.start())
        if src_const is None or src_const == dst_const:
            continue
        sid, did = const_to_id.get(src_const), const_to_id.get(dst_const)
        if sid is None or did is None:
            continue
        all_edges.append((sid, did))
        if LEVEL_EVO_RE.match(kind):
            try:
                level = int(val, 0)
            except ValueError:
                continue  # non-numeric (e.g. a #define) — skip, no level signal
            if 1 <= level <= 100:
                level_edges.append((sid, level, did))
    return level_edges, all_edges


def compute_family_roots(num_species, all_edges):
    parent = {}
    for sid, did in all_edges:
        parent.setdefault(did, sid)  # first incoming edge wins (matches source's own ordering)

    def root_of(sid):
        seen = set()
        while sid in parent and sid not in seen:
            seen.add(sid)
            sid = parent[sid]
        return sid

    return [root_of(sid) for sid in range(num_species)]


def compute_legendary_flags(num_species, all_edges, legendary_base_ids):
    children = {}
    for sid, did in all_edges:
        children.setdefault(sid, []).append(did)
    flags = [False] * num_species
    frontier = list(legendary_base_ids)
    for sid in frontier:
        flags[sid] = True
    seen = set(frontier)
    while frontier:
        nxt = []
        for sid in frontier:
            for c in children.get(sid, []):
                if c not in seen:
                    seen.add(c)
                    flags[c] = True
                    nxt.append(c)
        frontier = nxt
    return flags


def compute_level_ranges(num_species, level_edges):
    level_min = [1] * num_species
    level_max = [100] * num_species
    for sid, level, did in level_edges:
        # outgoing edge from sid caps sid's own stage just below the
        # threshold; multiple outgoing edges (e.g. Silcoon/Cascoon-style
        # branches) take the lowest threshold (most conservative cap).
        level_max[sid] = min(level_max[sid], max(level - 1, 1))
        # incoming edge into did raises did's floor; multiple incoming
        # edges take the highest threshold.
        level_min[did] = max(level_min[did], level)
    # guard against inverted ranges from unusual/edge-case data
    for i in range(num_species):
        if level_min[i] > level_max[i]:
            level_max[i] = 100
    return level_min, level_max


def main():
    const_to_id, num_species = load_species_ids()
    level_edges, all_edges = parse_evolution_table(const_to_id)
    legendary_base_ids = {const_to_id[c] for c in LEGENDARY_BASES if c in const_to_id}
    missing = LEGENDARY_BASES - {c for c in const_to_id if const_to_id[c] in legendary_base_ids}
    if missing:
        print("NOTE: legendary consts not found in donor species.h (skipped): %s"
              % ", ".join(sorted(missing)))

    roots = compute_family_roots(num_species, all_edges)
    legendary_flags = compute_legendary_flags(num_species, all_edges, legendary_base_ids)
    level_min, level_max = compute_level_ranges(num_species, level_edges)

    out = bytearray()
    manifest = []
    for sid in range(num_species):
        flags = 0x1 if legendary_flags[sid] else 0x0
        out += struct.pack("<BBBBH", level_min[sid], level_max[sid], flags, 0, roots[sid])
        if sid != 0 and (level_min[sid] != 1 or level_max[sid] != 100 or legendary_flags[sid]):
            manifest.append({"species": sid, "levelMin": level_min[sid],
                              "levelMax": level_max[sid], "legendary": legendary_flags[sid],
                              "familyRoot": roots[sid]})

    with open(os.path.join(HERE, "wild_species_meta.bin"), "wb") as f:
        f.write(out)
    import json
    with open(os.path.join(HERE, "wild_species_meta_manifest.json"), "w") as f:
        json.dump({"num_species": num_species, "record_size_bytes": 6,
                   "legendary_base_count": len(legendary_base_ids),
                   "legendary_family_total": sum(legendary_flags),
                   "entries_with_data": manifest}, f, indent=1)

    print("emitted wild_species_meta.bin: %d bytes (%d records x 6)"
          % (len(out), num_species))
    print("legendary bases: %d, full legendary/mythical family size: %d"
          % (len(legendary_base_ids), sum(legendary_flags)))
    print("level-edges parsed: %d, lineage edges parsed: %d" % (len(level_edges), len(all_edges)))


if __name__ == "__main__":
    main()
