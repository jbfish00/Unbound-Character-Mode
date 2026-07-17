#!/usr/bin/env python3
"""Assemble the in-game-trade sweep hook (trade-path enforcement).

RE summary (docs/ROUTINE_MAP.md, 2026-07-17 trade session):

Unbound's in-game trades (the Borrius Trade Quest) run through the vanilla
FireRed trade natives, which CFRU never repointed:
    special 0xFC = GetInGameTradeSpeciesInfo  0x08053A9D
    special 0x9F = ChoosePartyMon             0x080BF8FD
    special 0xFF = GetTradeSpecies            0x08053D2D
    special 0xFD = CreateInGameTradePokemon   0x08053D69
    special 0xFE = DoInGameTradeScene         0x08054441
sIngameTrades survives at vanilla 0x0826CF8C, 9 entries overwritten in
place with Unbound's own pairs (received species u16 @+12, requested
u16 @+0x38).

Every trade in the ROM executes through exactly THREE `special 0xFD;
special 0xFE; waitstate` junctions (exhaustive byte scan — all other
25FD00/25FE00 hits are Thumb-code false positives):
    1. 0x1E945A6  high-ROM shared subroutine 0x1E9459C (32 call sites)
    2. 0x1A8CE3   low-ROM shared subroutine 0x1A8CD9 (4 call sites)
    3. 0x16E3A8   inline junction in a low-ROM script (fall-through only)

The trade scene writes the incoming mon into the traded-away party slot
BEFORE its waitstate completes, so the enforcement hook goes right after
the waitstate: each junction's tail is overlaid with a `goto` into a tiny
injected tail script that replays the displaced instructions and inserts
`special 0x1AF` — a dead gSpecials slot (script-unreachable, stale
0x0815D835) repointed by build_patch.py to CharacterMode_SweepPartyToPC.
Off-roster non-egg party members are sent to the PC (never emptying the
party); with Character Mode off the special is a no-op.

Byte grammar (all opcodes confirmed in this ROM):
    19 <u16> <u16>   copyvar dst, src
    25 <u16>         special
    27               waitstate
    05 <u32>         goto
    0F 00 <u32>      loadword 0, ptr
    6A / 5A / 03     lock / faceplayer / return
"""
import struct

SPECIAL_SWEEP = 0x1AF
SPECIAL_SWEEP_FILE_OFF = 0x15FD60 + 4 * SPECIAL_SWEEP  # gSpecials[0x1AF]
SPECIAL_SWEEP_ORIG = bytes.fromhex("35D81508")          # stale 0x0815D835

# Shared-subroutine junctions: overlay `25 FE 00 27 6A 5A 03` (7 bytes:
# special 0xFE; waitstate; lock; faceplayer; return) with a 5-byte goto
# into the shared tail + 2 unreachable nops.
SUB_TAIL_ORIG = bytes.fromhex("25FE00276A5A03")
SUB_SITES = {
    "high sub (0x1E9459C, 32 callers)": 0x1E945A9,
    "low sub (0x1A8CD9, 4 callers)": 0x1A8CE6,
}

# Inline junction: overlay `25 FE 00 27 0F` (special 0xFE; waitstate; first
# byte of the follow-up loadword) with a 5-byte goto; the tail replays the
# full loadword and resumes at the callstd that follows it.
INLINE_SITE_OFF = 0x16E3AB
INLINE_ORIG = bytes.fromhex("25FE00270F004A5B1A080904")  # through callstd 4
INLINE_LOADWORD = bytes.fromhex("0F004A5B1A08")          # loadword 0, 0x081A5B4A
INLINE_RESUME = 0x0816E3B5                               # the callstd 4


def build(tail_rom_addr):
    """Return (blob, patches): the tail-script blob to place at tail_rom_addr
    and a list of (file_off, orig_bytes, new_bytes) overlay patches."""
    # shared tail: special 0xFE; waitstate; special sweep; lock; faceplayer; return
    sub_tail = (bytes([0x25]) + struct.pack("<H", 0xFE)
                + bytes([0x27])
                + bytes([0x25]) + struct.pack("<H", SPECIAL_SWEEP)
                + bytes([0x6A, 0x5A, 0x03]))
    # inline tail: special 0xFE; waitstate; special sweep; <replay loadword>; goto resume
    inline_tail = (bytes([0x25]) + struct.pack("<H", 0xFE)
                   + bytes([0x27])
                   + bytes([0x25]) + struct.pack("<H", SPECIAL_SWEEP)
                   + INLINE_LOADWORD
                   + bytes([0x05]) + struct.pack("<I", INLINE_RESUME))
    blob = sub_tail + inline_tail
    p_sub_tail = tail_rom_addr
    p_inline_tail = tail_rom_addr + len(sub_tail)

    patches = []
    for label, off in SUB_SITES.items():
        new = bytes([0x05]) + struct.pack("<I", p_sub_tail) + b"\x00\x00"
        assert len(new) == len(SUB_TAIL_ORIG)
        patches.append((label, off, SUB_TAIL_ORIG, new))
    inline_new = bytes([0x05]) + struct.pack("<I", p_inline_tail)
    patches.append(("inline junction (0x16E398)", INLINE_SITE_OFF,
                    INLINE_ORIG[:5], inline_new))
    return blob, patches


if __name__ == "__main__":
    blob, patches = build(0x08B2B280)
    print(f"tail blob: {len(blob)} bytes: {blob.hex(' ')}")
    for label, off, orig, new in patches:
        print(f"  {label}: @0x{off:06X}  {orig.hex()} -> {new.hex()}")
