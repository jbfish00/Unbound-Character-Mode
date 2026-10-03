#!/usr/bin/env python3
"""The player's walk/run sprite follows the chosen character (2026-10-03).

Radical Red's behaviour, ported (../game_plans/overworld_sprites.md): with
Character Mode on, the character's own sprite is used walking and running; bike,
surf, fishing, field moves and underwater keep the stock player. Nothing the
game already draws is edited: new graphics ids go into NULL slots, palettes get
new tags in a copied table.

Where each character's sprite comes from, in order of preference:
  1. Unbound's OWN player costume set (NATIVE_COSTUMES): a full player sprite
     with run frames, already in the ROM, so it costs one id reference.
  2. a player-grade sheet in sprites/ow_player/ (import_ow_sheets.py).
  3. nothing: the stock player.

All measured on the base ROM and asserted before anything is written:

  * CFRU's GetCustomGraphicsIdByState (0x089C9AA4) returns VarGet(a per-state
    var) or 0; a non-zero value replaces the gender default. Five callers
    (0x089C9D36, 0x089C9D78, 0x089C9DD0, 0x089C9E10, 0x089C9E2A) use it: the id
    getters AND the reverse lookups (gfx id -> avatar state). The state order,
    from its case table: walk/run 0x4054, bike 0x4055, surf 0x4056, field move
    0x4057, fishing 0x4058, Vs Seeker 0x5032, underwater 0x4062. The hook
    (src/character_mode.c CharacterMode_CustomAvatarGfx) answers state 0 itself
    when Character Mode is on, so no var is ever written: Unbound's own costume
    vars keep their values and come back the moment the mode is off.
  * the overworld lookup (0x089C9CB4) splits a 16-bit id: high byte 0-2 picks a
    table from the switcher at 0x08A69530 (3 slots, no free one), anything else
    falls back to table 0. So new ids go into NULL entries of tables 1 and 2;
    a NULL entry draws table 0's entry 0x10, so nothing references them.
    ObjectEventGetGraphicsId (0x089C9E54) DROPS a high byte of 3-254, which is
    another reason a fresh switcher slot (RR's 0x300+k) would not work here.
  * graphics info: Unbound's own player walk struct (table 0 entry 0: 32x32,
    anims = FireRed's player walk/run table 0x083A3470) with images, palette
    and reflection tags replaced. A 16x32 sheet takes FireRed's 16x32 oam and
    subsprite tables (0x083A3710 / 0x083A379C) instead.
  * frames: RR's FRAME_MAP (FireRed groups each run direction's stand + two
    steps; the sheets are pokeemerald's player layout). Frames are deduplicated
    across all characters and placed one by one in free space, because the ROM
    is a full 32 MiB and the sheets do not fit in one run.
  * palettes: sObjectEventSpritePalettes was repointed by Unbound to
    0x08EB9E9C (366 {data, tag} entries, tags 0x1100-0x126D, with holes; there
    is no 0x11FF terminator). Exactly three literals read it (0x0805F4D8,
    0x0805F570, 0x0805F5C8). It is copied, our tags 0x1400 + k appended, then
    a {0, 0x11FF} terminator, and the three literals repointed.

    python3 tools/character_mode/unbound_ow_player.py     # print the plan
"""
import array
import bisect
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHEETS = ROOT / "sprites" / "ow_player"
CHAR_MANIFEST = ROOT / "tools" / "character_mode" / "characters_manifest.json"

ROM_BASE = 0x08000000
AVATAR_FN = 0x089C9AA4                  # GetCustomGraphicsIdByState
AVATAR_FN_ORIG = bytes.fromhex("0300 10b5 0020 062b".replace(" ", ""))
AVATAR_STATE_VARS = (0x4054, 0x4055, 0x4056, 0x4057, 0x4058, 0x5032, 0x4062)
AVATAR_VAR_POOL = 0x089C9AE4            # 7 x u32, the vars above, in pool order
AVATAR_POOL_ORDER = (0x4054, 0x4055, 0x4056, 0x4057, 0x5032, 0x4058, 0x4062)
OW_TABLES = (0x088110E0, 0x088B2720, 0x088B2B20)
OW_SWITCHER = 0x08A69530                # == 0x08A694DC + 0x54, three slots
# NULL entries used for our ids, in order of preference: table 2's tail, the
# rest of table 2, then table 1's tail, then the last costume-sized hole in
# table 1 (0x1D4-0x1DB; the holes between costume sets look like reserved
# costumes, so they come last and the earlier ones stay untouched).
ID_RANGES = ((0x297, 0x300), (0x25D, 0x25E), (0x261, 0x274), (0x1EC, 0x200),
             (0x1D4, 0x1DC))
PLAYER_WALK = (0, 0x00)                 # table 0 entry 0: Unbound's male walk/run
OAM_16x32, SUBSPRITES_16x32 = 0x083A3710, 0x083A379C
PLAYER_ANIMS = 0x083A3470
PAL_TABLE = 0x08EB9E9C
PAL_TABLE_ENTRIES = 366
PAL_TABLE_REFS = (0x0805F4D8, 0x0805F570, 0x0805F5C8)
PAL_TAG_NONE = 0x11FF
PAL_TAG_BASE = 0x1400
INFO_SIZE = 0x24
FRAMES = 20
FRAME_MAP = [0, 1, 2, 3, 4, 5, 6, 7, 8,
             9, 12, 13,        # run south: stand, step, step
             10, 14, 15,       # run north
             11, 16, 17,       # run west (east is west flipped)
             0, 0]
# Unbound's own player costume sets (8 ids each; the first is walk/run, with
# FireRed's player anims). Identified by rendering every table entry
# (2026-10-03); asserted below to be 32x32 player walk structs.
NATIVE_COSTUMES = {"Red": 0x184, "Leaf": 0x18C, "Ethan": 0x1A4, "Lyra": 0x1AC}

# Free space. The ROM is a full 32 MiB; the biggest 0xFF runs are taken or
# have blank NPC frames pointing into them (0x09648800 + n*0x200 is a table of
# real frame pointers). A byte is usable only if it is 0xFF in the base ROM and
# no CREDIBLE pointer (an aligned ROM word with another ROM word within two
# words of it, i.e. part of a table or a literal pool) targets it or the
# 0x800 bytes before it. A lone pointer-looking word is noise: random data hits
# the ROM range once per ~512 bytes. Ranges this repo already fills are
# excluded by the caller (RESERVED_BY_CALLER) and re-checked as 0xFF on write.
FREE_MIN_RUN = 0x800
POINTER_MARGIN = 0x800


def R(a):
    return a - ROM_BASE


def credible_targets(rom):
    """Sorted file offsets that a credible pointer in `rom` targets."""
    a = array.array("I")
    a.frombytes(bytes(rom[:len(rom) & ~3]))
    n, out = len(a), set()
    for i, v in enumerate(a):
        if ROM_BASE <= v < 0x0A000000:
            for j in (i - 2, i - 1, i + 1, i + 2):
                if 0 <= j < n and ROM_BASE <= a[j] < 0x0A000000:
                    out.add((v & ~1) - ROM_BASE)
                    break
    return sorted(out)


def free_pieces(base_rom, reserved, targets=None):
    """[(start, end)] file ranges usable for overworld data."""
    targets = credible_targets(base_rom) if targets is None else targets
    out = []
    for m in re.finditer(rb"\xff{%d,}" % FREE_MIN_RUN, bytes(base_rom)):
        s, e = m.start(), m.end()
        cuts = [(t, t + POINTER_MARGIN) for t in
                targets[bisect.bisect_left(targets, s - POINTER_MARGIN):
                        bisect.bisect_left(targets, e)]]
        cuts += [(rs, re_) for rs, re_ in reserved if rs < e and re_ > s]
        cur = s
        for cs, ce in sorted(cuts):
            if cs > cur:
                out.append((cur, cs))
            cur = max(cur, ce)
        if cur < e:
            out.append((cur, e))
    return [((s + 3) & ~3, e) for s, e in out if e - ((s + 3) & ~3) >= 0x100]


class Allocator:
    def __init__(self, pieces):
        self.pieces = [list(p) for p in pieces]
        self.used = []

    def alloc(self, size, align=4):
        for p in self.pieces:
            s = (p[0] + align - 1) & ~(align - 1)
            if s + size <= p[1]:
                p[0] = s + size
                self.used.append((s, s + size))
                return s
        raise RuntimeError(f"out of free space for {size} bytes")


def sheets():
    return json.loads((SHEETS / "manifest.json").read_text())["characters"]


def _info(rom, table_idx, entry):
    p = struct.unpack_from("<I", rom, R(OW_TABLES[table_idx]) + entry * 4)[0]
    return bytearray(rom[R(p):R(p) + INFO_SIZE])


def _id_slots(rom):
    out = []
    for lo, hi in ID_RANGES:
        for gid in range(lo, hi):
            slot = R(OW_TABLES[gid >> 8]) + (gid & 0xFF) * 4
            assert struct.unpack_from("<I", rom, slot)[0] == 0, \
                f"overworld id {gid:#x} is no longer a NULL entry"
            out.append(gid)
    return out


def check_engine(rom):
    """Every engine fact this module relies on, against the base ROM."""
    assert rom[R(AVATAR_FN):R(AVATAR_FN) + 8] == AVATAR_FN_ORIG, \
        "GetCustomGraphicsIdByState moved"
    pool = struct.unpack_from("<7I", rom, R(AVATAR_VAR_POOL))
    assert pool == AVATAR_POOL_ORDER, [hex(v) for v in pool]
    sw = struct.unpack_from("<3I", rom, R(OW_SWITCHER))
    assert sw == OW_TABLES, [hex(v) for v in sw]
    for ref in PAL_TABLE_REFS:
        assert struct.unpack_from("<I", rom, R(ref))[0] == PAL_TABLE, hex(ref)
    walk = _info(rom, *PLAYER_WALK)
    assert struct.unpack_from("<HHHHhh", walk, 0) == (0xFFFF, 0x1100, 0x1102, 512, 32, 32), walk.hex()
    assert struct.unpack_from("<III", walk, 0x10) == (0x083A3718, 0x083A37F0, PLAYER_ANIMS), walk.hex()
    for name, gid in NATIVE_COSTUMES.items():
        info = _info(rom, gid >> 8, gid & 0xFF)
        assert struct.unpack_from("<HhhI", info, 6)[:3] == (512, 32, 32), name
        assert struct.unpack_from("<I", info, 0x18)[0] == PLAYER_ANIMS, name
    # FireRed's 16x32 oam: shape 2 (tall) size 2 (16x32)
    assert rom[R(OAM_16x32):R(OAM_16x32) + 4] == bytes.fromhex("00800080"), \
        rom[R(OAM_16x32):R(OAM_16x32) + 4].hex()


def pal_entries(rom):
    return [struct.unpack_from("<IH", rom, R(PAL_TABLE) + 8 * i)
            for i in range(PAL_TABLE_ENTRIES)]


def build(rom, characters, reserved, targets=None):
    """Plan every write for `characters` (characters_manifest order).

    Returns (writes, word_patches, gfx_table_addr, gfx_ids, sources):
      writes        [(file offset, bytes)] -- all into 0xFF free space
      word_patches  [(file offset, old u32, new u32)] -- the id slots and the
                    three palette-table literals
      gfx_table_addr  ROM address of the u16[len(characters)] id table the
                    shim reads (0 = keep the stock sprite)
      gfx_ids       [u16] that table's contents
      sources       {name: "costume" | "sheet"}
    """
    check_engine(rom)
    have = sheets()
    names = [c["character"] for c in characters]
    pals = pal_entries(rom)
    used_tags = {t for _, t in pals}
    slots = _id_slots(rom)
    walk = _info(rom, *PLAYER_WALK)

    alloc = Allocator(free_pieces(rom, reserved, targets))
    writes, patches = [], []

    sheet_names = [n for c, n in zip(characters, names)
                   if not c.get("hidden") and n not in NATIVE_COSTUMES and n in have]
    assert len(sheet_names) <= len(slots), (len(sheet_names), len(slots))
    assert all(PAL_TAG_BASE + k not in used_tags for k in range(len(sheet_names)))

    # palette table copy: Unbound's entries, ours, terminator
    n = len(sheet_names)
    pal_table = bytearray((len(pals) + n + 1) * 8)
    for i, (p, tag) in enumerate(pals):
        struct.pack_into("<IHH", pal_table, i * 8, p, tag, 0)
    pal_table_off = alloc.alloc(len(pal_table))

    frame_at = {}            # frame bytes -> file offset (dedupe)
    ids, sources = {}, {}
    for k, name in enumerate(sheet_names):
        e = have[name]
        w, h = e["width"], e["height"]
        fb = w * h // 2
        gfx = (SHEETS / f"{e['stem']}.4bpp").read_bytes()
        assert len(gfx) == 18 * fb, (name, len(gfx))
        frame_off = []
        for f in range(18):
            fr = gfx[f * fb:(f + 1) * fb]
            if fr not in frame_at:
                frame_at[fr] = alloc.alloc(fb)
                writes.append((frame_at[fr], fr))
            frame_off.append(frame_at[fr])
        pal = (SHEETS / f"{e['stem']}.gbapal").read_bytes()
        assert len(pal) == 32, name
        pal_off = alloc.alloc(32)
        writes.append((pal_off, pal))
        tag = PAL_TAG_BASE + k
        struct.pack_into("<IHH", pal_table, (len(pals) + k) * 8, ROM_BASE + pal_off, tag, 0)

        images = bytearray()
        for src in FRAME_MAP:
            images += struct.pack("<IHH", ROM_BASE + frame_off[src], fb, 0)
        images_off = alloc.alloc(len(images))
        writes.append((images_off, bytes(images)))

        info = bytearray(walk)
        struct.pack_into("<HH", info, 2, tag, PAL_TAG_NONE)        # palette, reflection
        if (w, h) == (16, 32):
            struct.pack_into("<Hhh", info, 6, 256, 16, 32)
            struct.pack_into("<II", info, 0x10, OAM_16x32, SUBSPRITES_16x32)
        else:
            assert (w, h) == (32, 32), (name, w, h)
        struct.pack_into("<I", info, 0x1C, ROM_BASE + images_off)
        info_off = alloc.alloc(INFO_SIZE)
        writes.append((info_off, bytes(info)))

        gid = slots[k]
        slot = R(OW_TABLES[gid >> 8]) + (gid & 0xFF) * 4
        patches.append((slot, 0, ROM_BASE + info_off))
        ids[name], sources[name] = gid, "sheet"
    struct.pack_into("<IHH", pal_table, (len(pals) + n) * 8, 0, PAL_TAG_NONE, 0)
    writes.append((pal_table_off, bytes(pal_table)))
    for ref in PAL_TABLE_REFS:
        patches.append((R(ref), PAL_TABLE, ROM_BASE + pal_table_off))

    for c, name in zip(characters, names):
        if name in NATIVE_COSTUMES and not c.get("hidden"):
            ids[name], sources[name] = NATIVE_COSTUMES[name], "costume"
    gfx_ids = [ids.get(nm, 0) if not c.get("hidden") else 0
               for c, nm in zip(characters, names)]
    table = struct.pack(f"<{len(gfx_ids)}H", *gfx_ids)
    table_off = alloc.alloc(len(table))
    writes.append((table_off, table))
    return writes, patches, ROM_BASE + table_off, gfx_ids, sources


if __name__ == "__main__":
    rom = (ROOT / "rom" / "Pokemon Unbound (v2.1.1.1).gba").read_bytes()
    chars = json.loads(CHAR_MANIFEST.read_text())["characters"]
    writes, patches, table, gfx_ids, sources = build(rom, chars, [])
    total = sum(len(b) for _, b in writes)
    print(f"{sum(1 for s in sources.values() if s == 'sheet')} sheets, "
          f"{sum(1 for s in sources.values() if s == 'costume')} native costumes; "
          f"{total:,} B in {len(writes)} writes; id table @ {table:#x}")
    print(f"{len(chars) - sum(1 for g in gfx_ids if g)} characters keep the stock sprite")
