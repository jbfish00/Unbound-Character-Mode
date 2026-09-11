#!/usr/bin/env python3
"""Assemble the PC-exit sweep hook (withdraw-path enforcement).

THE GAP THIS CLOSES. Enforcement deliberately routes off-roster Pokemon INTO
the PC -- the catch gate, the gift routing, the activation sweep, the trade
hook and the egg-hatch hook all box what the roster does not allow. Nothing
then looked at the PC's own WITHDRAW, so a mon the catch gate had just boxed
could be taken straight back out and kept for the rest of the run. No exploit
was required: it is what happens if you open the PC and take the mon back.
../game_plans/rowe_parity.md §13.24 has the measurement; §13.26c has this RE.

⭐ THE FINDING THAT MADE THIS CHEAP, AND IT IS THE EGG HOOK AGAIN. The PC is
opened FROM A SCRIPT, and the special that opens it carries a `waitstate`, so
the script RESUMES after the storage UI closes:

    0x081A6A1A: 0F 00 <0x081A50BE>  loadword 0, "Pokemon Storage System opened."
              +6: 09 04              callstd MSGBOX_DEFAULT
    0x081A6A22: 25 3C 00             special 0x3C   <- opens the storage system
              +3: 27                 waitstate      <- returns here when it closes
              +4: 16 04 80 1B 00     setvar 0x8004, 0x001B
              +9: 25 7D 01           special 0x17D
             +12: 05 <0x081A6998>    goto (back to the PC main menu)

That is the SAME SHAPE as the egg-hatch tail this repo already splices
(egg_hook.py: `25 C2 00 27 6B 02`), so this hook is that technique pointed at a
different script, and it reuses the SAME sweep special (`0x1AF`, the dead
gSpecials slot the trade hook repointed at CharacterMode_SweepPartyToPC).

⭐⭐ FOUR SITES, AND THEY ARE NOT ALL THE SAME SHAPE. This is the most sites of
any of the four ports, and the two high-ROM ones have a DIFFERENT tail, so a
single hardcoded "nine replayable bytes" would have spliced across an
instruction boundary in two of the four:

    site 0  0x081A6A22  9 bytes  25 3C 00 27 16 04 80 1B 00   special;waitstate;setvar
    site 1  0x0874B478  9 bytes  25 3C 00 27 16 04 80 1B 00   (byte-identical head)
    site 2  0x09E7A330  5 bytes  25 3C 00 27 6B                special;waitstate;releaseall
    site 3  0x09E80B49  5 bytes  25 3C 00 27 6B                (byte-identical head)

Five bytes is exactly what a `goto` needs, and every one of those five is an
opcode already confirmed in THIS ROM by egg_hook.py (`25 xx xx`, `27`, `6B`) --
which is why the short form was chosen for sites 2 and 3 over the eight-byte
boundary that would also have fitted: it needs no new opcode decode to be
provably a clean boundary. ⚠️ §13.26c's "every one with at least 9 bytes of
splice room" is therefore WITHDRAWN for this game; it was true of the FireRed
donor pair and not of Unbound's own two.

✅ REACHABILITY, measured rather than assumed -- §13.26c left both high-ROM
sites flagged as "not confirmed reachable", and both are now confirmed:

- **site 2 is an ordinary PC object, placed in ~30 maps.** Its script entry
  `0x09E7A320` is the `script` field of a 24-byte object-event template in 30
  separate map data blocks (0x083B98D8, 0x08B51C44, 0x08B58F64, …). It shows
  the same "Pokemon Storage System opened." message as sites 0 and 1.
- **site 3 is option 0 of an in-game console menu.** The multichoice above it
  prompts *"What would you like to do?"* with *"Pokemon Storage"* (→ site 3),
  *"Heal Pokemon"* and a third entry; the `goto_if` at `0x09E80B35` is what
  reaches it. ⚠️ Unlike the other three it is **jumped to, not fallen into**,
  so it has no msgbox above it and is anchored on that `goto_if` operand
  instead of on a text pointer.

Neither is a link/Union-Room path: `special 0x3C` is the single-player storage
system, and site 2's referents are ordinary map object events.

HOW THE SPECIAL ID WAS FOUND (0x3C), and it was NOT guessed. The FireRed pair
has no `specials.inc` to count, so: scan all 444 `gSpecials` entries for a
handler inside the PSS code region 0x0808B000-0x08096000 -- bracketed by
`StorageGetCurrentBox` 0x0808B9F4 and `CompactPartySlots` 0x080937DC, both
named in the CFRU donor's BPRE.ld. Three entries qualify (0x3C, 0x84, 0x85) and
only 0x3C is ever followed by a `waitstate`. ✅ Confirmed by decoding the
dialogue immediately above sites 0, 1 and 2.

⚠️ WHAT THIS GIVES, AND WHAT IT DOES NOT. This is ROWE's `Cb2_ExitPSS`
semantics: UNDO ON EXIT, not prevention. The player may withdraw an off-roster
mon and carry it inside the PC UI; it is boxed again the moment the PC closes.
🔴 It does NOT give ROWE's SECOND guard, `IsRemovingLastAllowedPartyMon`. The
sweep's never-empty rule KEEPS an off-roster mon when the roster allows nothing
else, so "deposit your only on-roster mon, withdraw an off-roster one, exit"
still leaves the player holding it. That is a real RE job in a closed binary
and is deliberately NOT attempted here.

🔴 THE MISSION COST, which is why this one needed a user decision and the other
three did not: **all 193 offered characters lose at least one in-game trade**
here, because Unbound COMPLETES a trade whose incoming mon is off-roster (the
trade hook boxes it) where the Emerald pair refuses outright -- so the mon the
trade gave you can no longer be withdrawn and used. The user accepted that on
2026-09-10. `../game_plans/rowe_parity.md` §13.26b.

Facts checked IN THIS ROM before any overlay is applied:

- **Nothing references the interior of any spliced region.** An UNALIGNED u32
  scan of the whole ROM finds ZERO words pointing into bytes 1..n-1 of any of
  the four regions. Site 3's ENTRY has one referent, the menu's `goto_if`,
  which is correct and required -- it lands on the new `goto`. (⚠️ The scan MUST
  be unaligned: script pointers in this engine are not word-aligned, and an
  aligned-only scan reports a clean interior it never looked at.)
- **Every site's original bytes are asserted byte-for-byte** before anything is
  written, so a wrong ROM, or a re-run over an already-patched build, fails
  loudly instead of writing opcodes into the middle of something else.

Byte grammar (all opcodes confirmed in this ROM):
    25 <u16>        special
    27              waitstate
    6B              releaseall
    16 <u16> <u16>  setvar
    05 <u32>        goto
"""
import struct

SPECIAL_PC = 0x003C
# The SAME dead gSpecials slot the trade hook and the egg hook already use,
# repointed by the injector at CharacterMode_SweepPartyToPC. Reusing it means
# this hook needs no new engine surface at all.
SPECIAL_SWEEP = 0x01AF
OPCODE_SPECIAL = 0x25
OPCODE_WAITSTATE = 0x27

# The message sites 0, 1 and 2 show. Asserted by the injector, so a moved
# script fails loudly instead of being spliced at the wrong address.
PC_TEXT_PTR = 0x081A50BE

# (rom_addr, file_off, original bytes, anchor, label)
#   anchor = (file_off, expected u32) -- the independent fact that proves this
#   is still the right script. For the three fall-through sites that is the
#   msgbox pointer above the splice; for site 3, which is JUMPED to, it is the
#   menu's own `goto_if` operand.
SITES = [
    (0x081A6A22, 0x001A6A22, bytes.fromhex("253c00271604801b00"),
     (0x001A6A1C, PC_TEXT_PTR), "PokeCenter PC (CFRU donor script)"),
    (0x0874B478, 0x0074B478, bytes.fromhex("253c00271604801b00"),
     (0x0074B472, PC_TEXT_PTR), "second PC script (Unbound content)"),
    (0x09E7A330, 0x01E7A330, bytes.fromhex("253c00276b"),
     (0x01E7A32A, PC_TEXT_PTR), "PC object event, referenced by ~30 maps"),
    (0x09E80B49, 0x01E80B49, bytes.fromhex("253c00276b"),
     (0x01E80B35, 0x09E80B49), "console menu, option 'Pokemon Storage'"),
]
# Kept for the checkers, which pin the primary site by name.
SPLICE_ROM_ADDR = SITES[0][0]
SPLICE_FILE_OFF = SITES[0][1]
SPLICE_ORIG = SITES[0][2]
SPACING = 0x20


def tail_addr(base, i, spacing=SPACING):
    return base + i * spacing


def build(tail_base_addr, spacing=SPACING):
    """Return (blob, patches, addrs).

    blob    -- one contiguous buffer holding all four replayed tails, each at
               `spacing` from the last, to be written at tail_base_addr.
    patches -- [(file_off, orig_bytes, new_bytes)] overlays.
    addrs   -- the ROM address of each tail, in SITES order.

    The sweep is a `special`, not a `callnative`: this repo routes every
    enforcement call through gSpecials[0x1AF] (see trade_hook / egg_hook), so
    there is nothing to resolve from a symbol table here and nothing to go
    stale.
    """
    blob = bytearray()
    patches, addrs = [], []
    for i, (rom_addr, file_off, orig, _anchor, _label) in enumerate(SITES):
        # Each site rejoins its OWN caller, immediately after the bytes this
        # tail replays. Derived from that site's own address and its own
        # original length rather than hardcoded, so two sites can never be
        # transposed.
        ret = rom_addr + len(orig)
        addr = tail_addr(tail_base_addr, i, spacing)
        # ORDER IS THE FEATURE: the sweep runs AFTER the waitstate, i.e. once
        # the storage UI has closed and the party is whatever the player left
        # it as. Run before it and the sweep would see the party as it was on
        # the way IN -- a silent no-op that still passes any "the sweep special
        # is present" check.
        tail = (orig[:4]                                        # special; waitstate
                + bytes([OPCODE_SPECIAL])
                + struct.pack("<H", SPECIAL_SWEEP)              # NEW: sweep to PC
                + orig[4:]                                      # rest of the replay
                + bytes([0x05]) + struct.pack("<I", ret))       # rejoin
        assert tail[:3] == bytes([OPCODE_SPECIAL]) + struct.pack("<H", SPECIAL_PC)
        assert tail[3] == OPCODE_WAITSTATE
        new = bytes([0x05]) + struct.pack("<I", addr)
        new += b"\x00" * (len(orig) - len(new))
        assert len(new) == len(orig), (
            "PC splice must be exactly %d bytes, got %d" % (len(orig), len(new)))
        assert len(tail) <= spacing, (len(tail), spacing)
        while len(blob) < i * spacing:
            blob.append(0xFF)
        blob += tail
        patches.append((file_off, orig, new))
        addrs.append(addr)
    return bytes(blob), patches, addrs


if __name__ == "__main__":
    blob, patches, addrs = build(0x08B33100)
    for i, a in enumerate(addrs):
        n = len(SITES[i][2]) + 8
        print("tail %d @%#010x: %d bytes: %s"
              % (i, a, n, blob[i * SPACING:i * SPACING + n].hex(" ")))
    for off, orig, new in patches:
        print("patch @%#010x: %s -> %s" % (off, orig.hex(" "), new.hex(" ")))
