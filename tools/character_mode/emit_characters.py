#!/usr/bin/env python3
"""Generate a flat binary character table from rosters_mapped.json.

Adapted from ROWE's emit_characters.py, which generates C source
(src/data/characters.h) compiled straight into the ROWE build. Unbound has
no compile step for us to hook into — this instead emits raw,
position-independent POD data, matching the semantics of ROWE's
`struct CharacterInfo` but as three flat blobs to be injected into ROM free
space and pointer-patched by a later insert script (once Phase 1 confirms
real hook/table addresses):

  characters.bin  - fixed-size records, one per character (layout below)
  rosters.bin     - each character's roster: u16 species ids, SPECIES_NONE-
                    terminated, concatenated back to back
  names.bin       - each character's display name, Gen3-charmap-encoded
                    (reusing the validated charmap from
                    tools/search_gametext.py's technique), 0xFF-terminated,
                    concatenated back to back
  characters_manifest.json - human-readable record of every field + offset,
                    for the later insert step and for debugging

Record layout (12 bytes, native ROM byte order = little-endian), OFFSETS
ARE RELATIVE TO THE START OF THEIR OWN BLOB, not final ROM addresses — the
insert step (Phase 1-informed) adds each blob's actual injected base address
and writes real 0x08xxxxxx pointers:
    u32 name_offset      -- offset into names.bin
    u32 roster_offset     -- offset into rosters.bin
    u16 sprite_asset_id   -- PLACEHOLDER 0xFFFF ("TBD") until Phase 3 finds
                             Unbound's OW/trainer-pic tables; CHAR_ASSET_NONE
                             equivalent once real ids exist
    u8  generation
    u8  flags             -- bit0: hasSignature: signature ace is roster[0]

species IDs referenced in rosters.bin are the PROVISIONAL DPE-donor ids from
map_species.py — NOT yet cross-checked against the real compiled ROM. Do not
trust for actual injection until Phase 1's routine-mapping work verifies
them (same caveat map_species.py already carries).
"""
import json
import os
import re
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
CHARMAP_PATH = "/home/jbfish00/Documents/Pokemon Rowe Alteration/charmap.txt"

# Legendary/mythical/Ultra Beast evolution-family bases: kept on rosters
# (catchable) but never offered as starters. Trimmed from ROWE's list to
# Gen 1-8 only (Gen 9 legendaries removed — Unbound has no Gen 9 species).
LEGENDARY_BASES = {"SPECIES_" + s for s in """ARTICUNO ZAPDOS MOLTRES MEWTWO MEW
RAIKOU ENTEI SUICUNE LUGIA HO_OH CELEBI
REGIROCK REGICE REGISTEEL LATIAS LATIOS KYOGRE GROUDON RAYQUAZA JIRACHI DEOXYS
UXIE MESPRIT AZELF DIALGA PALKIA HEATRAN REGIGIGAS GIRATINA CRESSELIA PHIONE MANAPHY DARKRAI SHAYMIN ARCEUS
VICTINI COBALION TERRAKION VIRIZION TORNADUS THUNDURUS RESHIRAM ZEKROM LANDORUS KYUREM KELDEO MELOETTA GENESECT
XERNEAS YVELTAL ZYGARDE DIANCIE HOOPA VOLCANION
TYPE_NULL TAPU_KOKO TAPU_LELE TAPU_BULU TAPU_FINI COSMOG NECROZMA MAGEARNA MARSHADOW ZERAORA MELTAN
NIHILEGO BUZZWOLE PHEROMOSA XURKITREE CELESTEELA KARTANA GUZZLORD POIPOLE STAKATAKA BLACEPHALON
ZACIAN ZAMAZENTA ETERNATUS KUBFU ZARUDE REGIELEKI REGIDRAGO GLASTRIER SPECTRIER CALYREX ENAMORUS""".split()}

CATEGORIES = ["protagonist", "rival", "gymleader", "elite4", "champion", "villain", "anime"]


def load_charmap(path):
    table = {}
    pat = re.compile(r"^'(.)'\s*=\s*([0-9A-Fa-f]{2})\s*$")
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            m = pat.match(line.rstrip("\n"))
            if m:
                table[m.group(1)] = int(m.group(2), 16)
    return table


def encode_text(text, charmap):
    out = bytearray()
    for ch in text:
        if ch not in charmap:
            raise ValueError(f"character {ch!r} not in charmap (name: {text!r})")
        out.append(charmap[ch])
    out.append(0xFF)  # Gen3 string terminator
    return bytes(out)


def display_name(disp):
    if disp.endswith(" (anime)"):
        return disp[: -len(" (anime)")]
    return disp


def main():
    with open(os.path.join(HERE, "rosters_mapped.json")) as f:
        mapped = json.load(f)
    charmap = load_charmap(CHARMAP_PATH)

    order = []
    with open(os.path.join(HERE, "characters.txt")) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            disp = line.split("|")[0].strip()
            if disp in mapped:
                order.append(disp)

    names_blob = bytearray()
    rosters_blob = bytearray()
    records = bytearray()
    manifest = []
    skipped = []

    for disp in order:
        info = mapped[disp]
        species = info["species"]
        if not species:
            skipped.append(disp)
            continue

        ids = [s["id"] for s in species]
        const_by_id = {s["id"]: s["const"] for s in species}
        starters = [i for i in ids if const_by_id[i] not in LEGENDARY_BASES]
        legends = [i for i in ids if const_by_id[i] in LEGENDARY_BASES]

        sig = info.get("signature")
        has_signature = 0
        if sig and sig.get("id") is not None:
            sig_id = sig["id"]
            if sig_id in starters:
                starters.remove(sig_id)
            elif sig_id in legends:
                legends.remove(sig_id)
            starters.insert(0, sig_id)
            has_signature = 1

        ordered_ids = starters + legends
        if not starters:
            manifest.append({"character": disp, "warning": "all-legendary roster, starter fallback needed"})

        name_off = len(names_blob)
        names_blob += encode_text(display_name(disp), charmap)

        roster_off = len(rosters_blob)
        for sid in ordered_ids:
            rosters_blob += struct.pack("<H", sid)
        rosters_blob += struct.pack("<H", 0)  # SPECIES_NONE terminator

        generation = info.get("gen", 0) or 1
        flags = has_signature & 0x1
        sprite_asset_id = 0xFFFF  # TBD — Unbound OW/trainer-pic table not yet located (Phase 1/3)

        records += struct.pack("<IIHBB", name_off, roster_off, sprite_asset_id, generation, flags)

        manifest.append({
            "character": disp,
            "category": info.get("category"),
            "generation": generation,
            "name_offset": name_off,
            "roster_offset": roster_off,
            "roster_species_ids_PROVISIONAL": ordered_ids,
            "starter_count": len(starters),
            "has_signature": bool(has_signature),
            "signature_id_PROVISIONAL": sig.get("id") if sig else None,
            "sprite_asset_id": "TBD",
        })

    with open(os.path.join(HERE, "characters.bin"), "wb") as f:
        f.write(records)
    with open(os.path.join(HERE, "rosters.bin"), "wb") as f:
        f.write(rosters_blob)
    with open(os.path.join(HERE, "names.bin"), "wb") as f:
        f.write(names_blob)
    with open(os.path.join(HERE, "characters_manifest.json"), "w") as f:
        json.dump({"record_count": len(order) - len(skipped), "record_size_bytes": 12,
                   "skipped_empty_roster": skipped, "characters": manifest}, f, indent=1)

    print("emitted %d characters (%d skipped empty)" % (len(order) - len(skipped), len(skipped)))
    print("  characters.bin: %d bytes (%d records x 12)" % (len(records), len(records) // 12))
    print("  rosters.bin:    %d bytes" % len(rosters_blob))
    print("  names.bin:      %d bytes" % len(names_blob))
    print("\nsprite_asset_id is a PLACEHOLDER (0xFFFF) for every record — Phase 3 fills")
    print("this in once Unbound's OW/trainer-pic tables are located (Phase 1).")
    print("All species ids are still PROVISIONAL (DPE donor, not ROM-verified).")


if __name__ == "__main__":
    main()
