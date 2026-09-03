#!/usr/bin/env python3
"""INVENTORY every routine in this ROM that writes gPlayerPartyCount.

⭐ WHY THIS EXISTS, and why it is an inventory rather than a grep.

The workspace's lesson #1 (CLAUDE.md, from Platinum): *a checker that greps the
files which ALREADY contain a hook cannot see a bypass in a file with no hook.*
Platinum's acquisition inventory enumerated `Party_AddPokemon*` repo-wide and
still could not see the link trade or the GTS, because a trade fills the slot
its partner vacated and adds nothing. The fix there was not "search more files"
but "choose a different PRIMITIVE to count".

For a GBA binary hack the primitive that cannot be dodged is the one every
acquisition must eventually touch: **the party count byte itself**. A routine
that hands the player a Pokemon has to increment gPlayerPartyCount, whatever
route it took to get there. So this enumerates every instruction in the ROM
that STORES through a pointer to that byte, and requires each one to carry a
verdict below. A new acquisition path is then a failing check rather than a
silent arrival.

✅ THE METHOD IS VALIDATED ON A KNOWN POSITIVE. Run against Seaglass, it
rediscovers both that game's enforcement choke point AND the give-core bypass
its own ROUTINE_MAP documents as "never BLs GiveMonToPlayer -> bypasses the
injected CM gate" -- a path a caller-of-GiveMonToPlayer scan cannot see, and
the exact shape of the Platinum miss.

⚠️ WHAT THIS DOES AND DOES NOT PROVE. It proves the SET of party-count writers
has not changed. It does NOT prove each one is correctly gated -- that is what
the verdicts record, and several are still UNVERIFIED (they are writers whose
containing routine has not been reverse-engineered here). An UNVERIFIED entry
is a "go look", not a clean bill of health. Recording an absence of
investigation as a negative result is a mistake this workspace has made at
least four times.

Detection: Thumb `ldr rX,[pc,#imm]` puts its literal at ((pc+4) & ~3) + imm*4,
so the loads of a given pool word are found exactly rather than by proximity;
then a store THROUGH that register within the following instructions is a
write. Conservative: it reports WRITE only when it can see the store.

Run:  python3 tools/tests/check_acquisition_paths.py   (0 = ok, 1 = changed)
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from cm_tally import assert_tally          # noqa: E402

GAME = "Pokémon Unbound v2.1.1.1"
ROM = os.path.join(ROOT, 'rom/Pokemon Unbound (v2.1.1.1).gba')
PARTY_COUNT = 0x02024029

# How many checks this layer must run. A deliberate LITERAL -- see cm_tally.py.
EXPECT_CHECKS = 4

# Measured, reachable, and covered by NO gate. A second one must fail check 4.
EXPECT_UNGATED = frozenset()

# ldr site -> (verdict, why). Every writer the scan finds must be listed here.
#   GATED      the project's enforcement covers this path
#   EXEMPT     deliberately not gated, with a reason
#   UNVERIFIED found by the scan, containing routine not yet identified
INVENTORY = {
    0x00040b6c: ("EXEMPT",
                 "DEAD CODE: the orphaned body of stock FireRed "
                 "GiveMonToPlayer. Its entry 0x08040B14 was overwritten "
                 "with a 4-byte thunk (ldr r1,[pc,#0]; bx r1) to "
                 "0x089C905D, the CFRU GiveMonToPlayer that carries the "
                 "GATED writer, so all 3 BL callers are redirected. No BL, "
                 "no branch and NO pointer of any kind reaches the orphan "
                 "in this ROM -- a cleaner negative than Radical Red's, "
                 "measured the same way"),
    0x00040c3e: ("EXEMPT",
                 "CalculatePlayerPartyCount (36 BL callers): "
                 "gPlayerPartyCount = 0, then ++ per slot whose "
                 "MON_DATA_SPECIES is non-zero. A RECOUNT of what the array "
                 "already holds -- it cannot introduce a mon. See the "
                 "LAUNDERING note in docs/PARTY_COUNT_WRITERS.md"),
    0x0004c232: ("EXEMPT",
                 "LoadPlayerParty: gPlayerPartyCount = "
                 "gSaveBlock1Ptr->[0x34], then copies 6 x 100 bytes back "
                 "from the save block. Restores the player's OWN saved "
                 "party (link/facility swap-back); everything it restores "
                 "was gated when first acquired -- same reasoning as the "
                 "existing party-restore EXEMPT"),
    0x00054aee: ("EXEMPT",
                 "new-game init (entry 0x08054A60 thunked to 0x089A2FD1, "
                 "which re-enters the original body at +0x09): "
                 "gPlayerPartyCount = 0 amid the init BL run. Zeroing "
                 "removes, never adds"),
    0x0008ecc0: ("EXEMPT",
                 "gPlayerPartyCount = CalculatePlayerPartyCount() -- "
                 "literally `bl 0x08040C3C; ldr r1,=count; strb r0,[r1]`. A "
                 "recount after a storage-screen exit"),
    0x0008edf4: ("EXEMPT",
                 "gPlayerPartyCount = CalculatePlayerPartyCount(); "
                 "byte-identical to the site at 0x0008ECC0, the other arm "
                 "of the same screen"),
    0x0012092a: ("NOT-A-WRITER",
                 "FALSE POSITIVE -- not a writer. `ldr r0,=count; ldrb "
                 "r0,[r0]; cmp r4,r0; bcc` is a LOOP BOUND READ. The "
                 "detector's window walked past the loop's unconditional "
                 "branch into the literal pool at 0x08120938 and decoded "
                 "the word 0x020370C2 as `strb r2,[r0,#3]`. See the "
                 "DETECTOR DEFECT note in docs/PARTY_COUNT_WRITERS.md"),
    0x0082f442: ("NOT-A-WRITER",
                 "FALSE POSITIVE -- not a writer. r3 is loaded with "
                 "&gPlayerPartyCount and used only by `ldrb r5,[r3,#0]`, "
                 "then CLOBBERED by `movs r3,r4` at 0x0882F45A. The "
                 "detector kept scanning and matched `strb r2,[r3,#1]` at "
                 "0x0882F472, which stores through the new r3. Same "
                 "detector defect as 0x0012092A"),
    0x008a42b2: ("EXEMPT",
                 "DEPOSIT arm of the party <-> 6-slot EWRAM store at "
                 "0x0203C000 (count byte + 6 x 80-byte records): copies "
                 "gPlayerParty[i] out to the store, compacts the party, "
                 "clears slot 5, then store-count++ and "
                 "gPlayerPartyCount--. A DECREMENT: a mon leaves the party"),
    0x008a4324: ("EXEMPT",
                 "WITHDRAW arm of the same store: party-full check, memcpy "
                 "80 bytes from the store into gPlayerParty[count], expand, "
                 "compact the store, store-count-- and gPlayerPartyCount++. "
                 "This one INCREMENTS, but the store's only filler is the "
                 "deposit arm above, which draws from the party -- so "
                 "nothing enters that the party gate did not already pass. "
                 "NOTE: off-roster mons are PC-routed to gPokemonStoragePtr "
                 "0x03005010 (docs/ROUTINE_MAP.md:221), a DIFFERENT "
                 "structure, so they cannot appear in this store. Highest "
                 "residual risk of the EXEMPT sites; worth one live check"),
    0x008a4db0: ("EXEMPT",
                 "party removal/compaction: shifts slots down over the "
                 "removed one, zeroes the tail with `stmia r6!`, then "
                 "gPlayerPartyCount--. A DECREMENT"),
    0x008aaef2: ("EXEMPT",
                 "gPlayerPartyCount-- (`ldrb r3,[r2]; subs r3,#1; strb "
                 "r3,[r2]`) on the failure/removal arm of the routine that "
                 "also contains 0x008AAF12"),
    0x008aaf12: ("EXEMPT",
                 "RESOLVED 2026-09-02. The containing function's entry is "
                 "0x088AAE24 -- FOUR instructions are hoisted above its "
                 "push, which is why a nearest-push scan lands 8 bytes late "
                 "at 0x088AAE2C. It has NO BL callers and no aligned "
                 "pointer because it is a SCRIPT CALLNATIVE: the only "
                 "reference is the unaligned u32 inside `23 <ptr>` at "
                 "0x088AA4CD, followed by `compare VAR_RESULT,1/2/3` "
                 "branches that match the 1..5 codes the function returns. "
                 "One script site, in a Deoxys form/meteor scene (the "
                 "adjacent text decodes as '...act to the meteor.' and "
                 "'...changed form!'). It is a DEPOSIT/WITHDRAW TOGGLE over "
                 "an 80-byte EWRAM buffer at 0x0203D700, the same shape as "
                 "the 0x0203C000 store at 0x008A42B2/0x008A4324: one arm "
                 "copies the selected party mon out and does count-- "
                 "(0x088AAEF2, returns 1), the other copies it back into "
                 "gPlayerParty[count], clears the buffer and does count++ "
                 "(0x088AAF76, returns 4). EXEMPT for the same reason as "
                 "that store: the buffer's ONLY filler is the deposit arm, "
                 "which draws from the party, so nothing enters that the "
                 "party gate did not already pass. Residual caveat, same as "
                 "the sibling: this is only true while no other path can "
                 "write that buffer."),
    0x008bf8fc: ("EXEMPT",
                 "recount, party or enemy party selected by r9&1 (r5 = "
                 "0x02024284 or 0x0202402C): count = 0, then ++ per slot "
                 "with a non-zero species. 8 BL callers. Adds nothing"),
    0x008d14ac: ("EXEMPT",
                 "Unbound's own relocated LoadPlayerParty: copies 6 x 100 "
                 "bytes back, then gPlayerPartyCount = "
                 "gSaveBlock1Ptr->[0x34]. Same verdict and reasoning as the "
                 "stock copy at 0x0004C232"),
    0x009c90c6: ("GATED",
                 "inside GiveMonToPlayer 0x089C905C -- the entry trampoline hooks this function, so every BL caller is gated by construction (docs/ROUTINE_MAP.md:270)"),
    0x009e8664: ("EXEMPT",
                 "the same 124-byte routine as Radical Red's 0x0109B5C8 "
                 "(party slots 0-2 -> 3-5, then recount), relocated: only "
                 "12 of 124 bytes differ and all 12 are pool words. "
                 "Confirmed by comparing the opcode stream, not by "
                 "arithmetic"),
}

WINDOW = 60          # instructions to follow after the ldr


def thumb(b, i):
    return struct.unpack_from("<H", b, i)[0]


def writers(b):
    """{ldr file offset: pool offset} for every store through gPlayerPartyCount."""
    pools = []
    p = struct.pack("<I", PARTY_COUNT)
    i = b.find(p)
    while i >= 0:
        if i % 4 == 0:
            pools.append(i)
        i = b.find(p, i + 1)

    found = {}
    for pool in pools:
        for i in range(max(0, pool - 1024), pool, 2):
            w = thumb(b, i)
            if (w & 0xF800) != 0x4800:            # ldr rX,[pc,#imm8]
                continue
            rX, imm = (w >> 8) & 7, w & 0xFF
            if (((i + 4) & ~3) + imm * 4) != pool:
                continue
            for k in range(i + 2, min(i + 2 + WINDOW * 2, len(b) - 1), 2):
                v = thumb(b, k)
                if (v & 0xF800) == 0x7000 and ((v >> 3) & 7) == rX:
                    found[i] = pool; break        # strb rY,[rX,#imm]
                if (v & 0xFE00) == 0x5400 and ((v >> 3) & 7) == rX:
                    found[i] = pool; break        # strb rY,[rX,rZ]
                if (v & 0xF800) == 0x6000 and ((v >> 3) & 7) == rX:
                    found[i] = pool; break        # str  rY,[rX,#imm]
                if (v & 0xF800) == 0x4800 and ((v >> 8) & 7) == rX:
                    break                         # rX reloaded: not ours
                if (v & 0xFF00) in (0x4700, 0xBD00):
                    break                         # bx / pop {..,pc}
    return found


failures = []
checks_run = 0


def check(name, ok, detail=""):
    global checks_run
    checks_run += 1
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name,
                           (" -- " + detail) if detail and not ok else ""))
    if not ok:
        failures.append(name)


def main():
    if not os.path.isfile(ROM):
        print("base ROM not found: %s" % os.path.relpath(ROM, ROOT))
        return 1
    with open(ROM, "rb") as f:
        b = f.read()

    found = writers(b)
    rom_addr = {off: 0x08000000 + off for off in found}

    print("%s -- gPlayerPartyCount %#010x" % (GAME, PARTY_COUNT))
    print("  %d writer site(s) found, %d inventoried\n"
          % (len(found), len(INVENTORY)))

    # 1. nothing new arrived
    new = sorted(set(found) - set(INVENTORY))
    check("every party-count writer in the ROM is inventoried",
          not new,
          ", ".join("%#010x" % rom_addr[o] for o in new)
          + " -- a routine that writes the party count and is not on the list "
            "is a possible ungated acquisition path; identify it, then add it "
            "with a verdict")

    # 2. nothing inventoried vanished (the inventory is not describing a
    #    ROM that no longer exists)
    gone = sorted(set(INVENTORY) - set(found))
    check("every inventoried writer is still present in the ROM",
          not gone,
          ", ".join("%#010x" % (0x08000000 + o) for o in gone))

    # 3. the enforcement choke point is actually among the writers -- an
    #    inventory that lists no GATED path would be describing a ROM with no
    #    enforcement at all, and would still pass checks 1 and 2.
    gated = [o for o in INVENTORY if INVENTORY[o][0] == "GATED" and o in found]
    check("at least one GATED writer is present (the enforcement point)",
          bool(gated), "no GATED writer found among %d" % len(found))

    # 4. no NEW ungated acquisition path. UNGATED means measured, reachable and
    #    NOT covered by any gate -- a known hole, pinned here so that finding a
    #    SECOND one fails the suite instead of arriving silently. Pinning it
    #    rather than failing on its existence is deliberate: the suite must stay
    #    green while a recorded, understood hole waits on a design decision,
    #    or it becomes a red checker nobody runs.
    ungated = frozenset(o for o in INVENTORY if INVENTORY[o][0] == "UNGATED")
    check("the set of UNGATED acquisition paths is exactly the known one",
          ungated == EXPECT_UNGATED,
          "new: %s | disappeared: %s"
          % (", ".join("%#010x" % (0x08000000 + o)
                       for o in sorted(ungated - EXPECT_UNGATED)) or "none",
             ", ".join("%#010x" % (0x08000000 + o)
                       for o in sorted(EXPECT_UNGATED - ungated)) or "none"))
    if ungated:
        print("  🔴 %d UNGATED path(s) -- reachable and covered by no gate:"
              % len(ungated))
        for o in sorted(ungated):
            print("       %#010x" % (0x08000000 + o))

    unver = sorted(o for o in INVENTORY if INVENTORY[o][0] == "UNVERIFIED")
    print("\n  verdicts: %d GATED, %d EXEMPT, %d NOT-A-WRITER, %d UNGATED, "
          "%d UNVERIFIED"
          % (sum(1 for v in INVENTORY.values() if v[0] == "GATED"),
             sum(1 for v in INVENTORY.values() if v[0] == "EXEMPT"),
             sum(1 for v in INVENTORY.values() if v[0] == "NOT-A-WRITER"),
             len(ungated), len(unver)))
    print("  NOT-A-WRITER: the scan reports these, and reverse engineering "
          "showed they are\n    reads, not stores. They stay listed on "
          "purpose -- the detector is deliberately\n    conservative, so "
          "dropping them would make check 2 fail. See\n    "
          "docs/PARTY_COUNT_WRITERS.md for the detector defect that "
          "produces them.")
    if unver:
        print("  ⚠️ UNVERIFIED means the containing routine has not been "
              "identified here. It is a 'go look', not a clean bill of health:")
        for o in unver:
            print("       %#010x" % (0x08000000 + o))

    if assert_tally(checks_run, EXPECT_CHECKS, "check_acquisition_paths"):
        return 1
    print("\n%s" % ("ALL PASS" if not failures
                     else "FAILURES: " + ", ".join(failures)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
