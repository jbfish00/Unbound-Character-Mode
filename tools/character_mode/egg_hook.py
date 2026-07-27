#!/usr/bin/env python3
"""Assemble the egg-hatch sweep hook (hatch-path enforcement).

THE GAP THIS CLOSES. Eggs are deliberately exempt from both the gift routing
and the party sweep, so an egg event can never block progress -- but nothing
looked at what an egg HATCHED INTO. A scripted gift egg of an off-roster
species therefore hatched into a permanent off-roster party member, the one
enforcement hole reachable in ordinary play. (Breeding cannot reach it: only
on-roster parents can be kept, and a roster stores whole evolution families, so
their offspring is on-roster by construction. Gift eggs are the way in.)

RE summary (2026-07-26):

Hatching is SCRIPT-DRIVEN, which is what makes this cheap. The overworld step
handler at 0x0806D704 calls `ShouldEggHatch` (0x080463B8, the CFRU donor's own
address, one caller in the whole ROM) and on a true result runs a script:

    0806d704: bl   ShouldEggHatch
    0806d70a: cmp  r0, #0
    0806d70c: beq  <no hatch>
    0806d70e: movs r0, #13
    0806d710: bl   0x08054E90
    0806d714: ldr  r0, [pc, #4]      @ 0x081BF546
    0806d716: bl   ScriptContext1_SetupScript

The script at 0x081BF546 decodes to:

    081bf546: 69                 lock-ish (replayed byte-for-byte, unexamined)
    081bf547: 0F 00 <0x081BFB5A> loadword 0, "...hatched!" text
    081bf54d: 09 04              callstd MSGBOX_DEFAULT
    081bf54f: 25 C2 00           special 0xC2   <- performs the hatch
    081bf552: 27                 waitstate
    081bf553: 6B                 release-ish (replayed byte-for-byte)
    081bf554: 02                 end

So the tail from `special 0xC2` is overlaid with a `goto` into an injected tail
that replays those four commands and then runs **special 0x1AF** -- the same
dead gSpecials slot repointed to CharacterMode_SweepPartyToPC that the trade
hook uses. The sweep runs AFTER the hatch's waitstate, so it sees the finished
Pokemon rather than the egg, and the egg exemption inside the sweep no longer
applies to it. With Character Mode off the special is a no-op, and the sweep
never empties the party.

Two facts that made this safe, both checked rather than assumed:

- **Nothing references the interior of the script.** 0x081BF546 (the entry) has
  exactly two referents -- the caller's literal pool at 0x0806D71C and a second
  table at 0x089FFE3C, i.e. a second code path that runs the SAME script, so one
  hook covers both. 0x081BF54F/52/53/54 have zero referents, so overlaying them
  cannot land mid-jump.
- **Six bytes are available** (`25 c2 00 27 6b 02`) and a `goto` needs five, so
  the displaced code is replayed rather than shortened. The sixth byte is
  padding that is never executed.

Byte grammar (all opcodes confirmed in this ROM):
    25 <u16>   special
    27         waitstate
    05 <u32>   goto
    02         end
"""
import struct

# file offset == rom address - 0x08000000 in this region
SPLICE_ROM_ADDR = 0x081BF54F
SPLICE_FILE_OFF = 0x001BF54F
SPLICE_ORIG = bytes.fromhex("25c200276b02")   # special 0xC2; waitstate; 6B; end
SPECIAL_HATCH = 0x00C2
SPECIAL_SWEEP = 0x01AF
OPCODE_RELEASE = 0x6B


def build(tail_rom_addr):
    """Return (blob, patches): the tail-script blob to place at tail_rom_addr
    and a list of (file_off, orig_bytes, new_bytes) overlay patches."""
    tail = (bytes([0x25]) + struct.pack("<H", SPECIAL_HATCH)   # replay: the hatch
            + bytes([0x27])                                     # replay: waitstate
            + bytes([OPCODE_RELEASE])                           # replay: release-ish
            + bytes([0x25]) + struct.pack("<H", SPECIAL_SWEEP)  # NEW: sweep to PC
            + bytes([0x02]))                                    # replay: end

    new = bytes([0x05]) + struct.pack("<I", tail_rom_addr) + b"\x00"
    assert len(new) == len(SPLICE_ORIG), (
        "egg splice must be exactly %d bytes, got %d"
        % (len(SPLICE_ORIG), len(new)))
    return tail, [(SPLICE_FILE_OFF, SPLICE_ORIG, new)]


if __name__ == "__main__":
    blob, patches = build(0x08B33000)
    print("tail: %d bytes: %s" % (len(blob), blob.hex(" ")))
    for off, orig, new in patches:
        print("patch @%#010x: %s -> %s" % (off, orig.hex(" "), new.hex(" ")))
