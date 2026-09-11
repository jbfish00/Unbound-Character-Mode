#!/usr/bin/env python3
"""INVENTORY every ChoosePartyMon call site in this ROM, and decode what the
NPCs behind them GIVE.

⭐ WHY THIS EXISTS. `rowe_parity.md` §13.28 measured a class of NPC that wants
a species SHOWN rather than traded, and reported the raw counts 5/5/2/0 across
the four ports as the mission cost of the PC-withdraw fix -- while stating
plainly that NOBODY HAD DECODED WHAT ANY OF THEM GIVE, so the count was an
upper bound and not a loss. §13.37 decoded them. The answer is that the count
matters to nothing: nine of the fourteen gates hand over an item that only
works on the very species the character cannot own, four more give something
a shop sells, and the last two gate on a species that has to be CAUGHT, which
the catch gate already refuses.

⚠️ THE PRIMITIVE, AND WHY IT IS NOT THE DIALOGUE WALK. `check_gift_eggs.py`
finds its sites by decoding forward from a dialogue anchor. That walk is the
right primitive for `giveegg`, and it is the WRONG one here: measured on these
four ROMs it reaches 26 of 76 ChoosePartyMon sites in this game
(20/43, 26/76, 3/19 and 2/11 across the four). The count §13.28 published was
the walk-reachable subset, so it was never a count of the class. This file
scans for the call site itself -- `special <ChoosePartyMon>` immediately
followed by `waitstate`, which every real site has -- and pins the whole set.

⚠️ WHAT THIS DOES AND DOES NOT PROVE. It proves the set of ChoosePartyMon call
sites has not changed and that the decoded gates still compare the recorded
species and still hand over the recorded items. It does NOT claim every site
in SITES has been decoded: the ones that have are in GATES, and the rest are
pinned by address only. A species test that lives in native code (Radical
Red's `special 0x78`, its gender-swap `callasm`, Unbound's Deoxys and Rotom
callasms, Seaglass's `special 0x224`) is in GATES with an EMPTY species tuple
-- it is there because the DIALOGUE was decoded, and no compare scan can see
it.

⚠️ Three false-positive constants worth pinning, all of which decode as a
plausible species right after a ChoosePartyMon:
  255  PARTY_NOTHING_CHOSEN in the Emerald pair (decodes as Torchic)
  412  SPECIES_EGG in the FireRed pair (decodes as Bad Egg)
  a small value in a BP facility is the PRICE IN BP, not a species -- five
  Unbound sites compare 16, 25 or 27, which decode as Pidgey, Pikachu and
  Sandshrew.

Run:  python3 tools/tests/check_species_gates.py   (0 = ok, 1 = changed)
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from cm_tally import assert_tally          # noqa: E402

GAME = 'Pokémon Unbound v2.1.1.1'
ROM = os.path.join(ROOT, 'rom/Pokemon Unbound (v2.1.1.1).gba')
ROM_BASE = 0x08000000
CHARMAP = os.path.join(ROOT, "tools/charmap.txt")

# special id of ChoosePartyMon in this engine family, MEASURED against this
# ROM's own scripts -- the two families do not agree.
CHOOSE_SPECIAL = 0x9f
WAITSTATE = 0x27

# (address of the NAME of id 0, stride) for this ROM's own tables. Measured
# per ROM: all four item tables sit at different addresses and the strides are
# 44 / 44 / 80 / 84. NEVER copy one of these from a sibling port.
ITEM_TABLE = (0x08876200, 44)
SPECIES_TABLE = (0x0966a98c, 11)
# (id, name) pairs read out of those two tables when this file was written.
# ⚠️ At least one probe is deliberately FAR from the base: a wrong STRIDE is
# invisible at id 1 and shows up only at a high index. That is not
# hypothetical -- an early version of this work carried a sibling's stride for
# Seaglass, read ids 1-4 correctly, and decoded item 51 as mojibake.
# Species id 386 is pinned in the FireRed pair on purpose: it is Volbeat, not
# the national-dex 386, which is the trap `CHARACTER_ROSTER_PLAN.md` records.
ITEM_PROBES = ((1, 'Master Ball'), (299, 'TM11'))
SPECIES_PROBES = ((1, 'Bulbasaur'), (386, 'Volbeat'))

# Every ChoosePartyMon call site in the ROM. A site being here is not a claim
# that anyone has looked at it; GATES holds the ones that were decoded.
SITES = (
    0x0816b282,
    0x0816d8b8,
    0x0816e370,
    0x0816ffb0,
    0x081a8cbd,
    0x0879422c,
    0x087a82d3,
    0x088aa2c2,
    0x088aa485,
    0x088aa4c5,
    0x088aa9d1,
    0x088aaa11,
    0x088c0ff1,
    0x088c1006,
    0x088c101b,
    0x088c1030,
    0x088c1045,
    0x088c105a,
    0x088c1151,
    0x088c9801,
    0x088c9816,
    0x088c982b,
    0x088c9840,
    0x088c9855,
    0x088c986a,
    0x09e52b72,
    0x09e56c2e,
    0x09e57739,
    0x09e57952,
    0x09e607fd,
    0x09e6119f,
    0x09e6238c,
    0x09e623d3,
    0x09e63112,
    0x09e63191,
    0x09e64868,
    0x09e67b44,
    0x09e68c86,
    0x09e69879,
    0x09e69a5d,
    0x09e6a61c,
    0x09e6a780,
    0x09e6a890,
    0x09e6a92d,
    0x09e6b2e9,
    0x09e7b1cc,
    0x09e7b2e8,
    0x09e7cdc9,
    0x09e81e9f,
    0x09e821fe,
    0x09e8569c,
    0x09e8e266,
    0x09e8e35b,
    0x09e8e409,
    0x09e8e901,
    0x09e8eaed,
    0x09e8eb95,
    0x09e94580,
    0x09e9587b,
    0x09e95b99,
    0x09e95c96,
    0x09e9baf7,
    0x09ea180d,
    0x09ea1942,
    0x09ea1a13,
    0x09ea1b80,
    0x09ea1c50,
    0x09ea1fe0,
    0x09ea20b4,
    0x09ea2142,
    0x09ea2289,
    0x09ea23c6,
    0x09ea5dad,
    0x09eb02a7,
    0x09eb0723,
    0x09eb086a,
)

# address -> (label, gate species ids, ((give address, item id, qty), ...),
#             verdict, what it actually gives)
#   SPECIES_LOCKED      the reward only works on the species that opens the
#                       gate, so a character who cannot keep that species
#                       loses nothing of value
#   ELSEWHERE           the reward is generic but obtainable another way in
#                       this same ROM (measured, with the other source named)
#   CATCH_ONLY          the reward is generic and has no other source, but
#                       the gate needs a species the catch gate already
#                       refuses. ⚠️ Whether an in-game trade or a computed
#                       gift egg could still deliver that species into the PC
#                       is NOT established here -- so this verdict bounds the
#                       cost, it does not prove it is zero
GATES = {
 0x0816ffb0: (
  'Magikarp size judge',
  (),
  ((0x0817003c, 6, 1),),
  'ELSEWHERE',
  'rewards seen in the window between this site and the next call site:'
  ' Net Ball x1'),
 0x0879422c: (
  'Hoopa -- MASTER BALL (low-ROM copy)',
  (828, 829),
  ((0x08794269, 1, 1),),
  'ELSEWHERE',
  'rewards seen in the window between this site and the next call site:'
  ' Master Ball x1'),
 0x087a82d3: (
  'Happiny -- Oval Stone',
  (493,),
  ((0x087a8307, 102, 1),),
  'SPECIES_LOCKED',
  'rewards seen in the window between this site and the next call site:'
  ' Oval Stone x1'),
 0x088aa2c2: (
  'Deoxys meteorite (native test, callasm 0x088AB3CD)',
  (),
  (),
  'SPECIES_LOCKED',
  'no give-item in its window'),
 0x088aa485: (
  'Kyurem FUSION -- "There is no Kyurem in the party!", "Multiple'
  ' fusions are not allowed!"; NOT dialogue-reachable. Labelled Deoxys'
  ' at first by PROXIMITY to the meteorite script, which is exactly the'
  ' mistake the PC-hook work already recorded: the discriminator is the'
  ' text, not the neighbourhood',
  (),
  (),
  'SPECIES_LOCKED',
  'no give-item in its window'),
 0x088aa4c5: (
  'Kyurem separation, the same NPC -- NOT dialogue-reachable',
  (),
  (),
  'SPECIES_LOCKED',
  'no give-item in its window'),
 0x088aa9d1: (
  'Rotom appliance (native test) -- NOT dialogue-reachable',
  (),
  (),
  'SPECIES_LOCKED',
  'no give-item in its window'),
 0x088aaa11: (
  'Rotom appliance, second site -- NOT dialogue-reachable',
  (),
  (),
  'SPECIES_LOCKED',
  'no give-item in its window'),
 0x088c0ff1: (
  'one of six identical per-slot stubs; the species in the window'
  ' belong to a neighbouring table',
  (252, 609, 610, 611, 612, 613),
  (),
  'NOT_A_GATE',
  'no give-item in its window'),
 0x088c1006: (
  'per-slot stub',
  (252, 609, 610, 611, 612, 613),
  (),
  'NOT_A_GATE',
  'no give-item in its window'),
 0x088c101b: (
  'per-slot stub',
  (252, 609, 610, 611, 612, 613),
  (),
  'NOT_A_GATE',
  'no give-item in its window'),
 0x088c1030: (
  'per-slot stub',
  (252, 609, 610, 611, 612, 613, 618),
  (),
  'NOT_A_GATE',
  'no give-item in its window'),
 0x088c1045: (
  'per-slot stub',
  (252, 609, 610, 611, 612, 613, 618, 619),
  (),
  'NOT_A_GATE',
  'no give-item in its window'),
 0x088c105a: (
  'per-slot stub',
  (252, 609, 610, 611, 612, 613, 618, 619, 620, 958),
  (),
  'NOT_A_GATE',
  'no give-item in its window'),
 0x088c1151: (
  'per-slot stub family, second group',
  (618, 619, 620, 958, 1043, 1044, 1045),
  (),
  'NOT_A_GATE',
  'no give-item in its window'),
 0x09e57739: (
  'Basculin -- EVIOLITE',
  (),
  ((0x09e57772, 495, 1), (0x09e57844, 105, 1)),
  'UNIQUE',
  'rewards seen in the window between this site and the next call site:'
  ' Eviolite x1, Ice Stone x1'),
 0x09e607fd: (
  'Alolan Sandshrew / Sandslash -- Ice Stone, and a Moon Stone in the'
  ' same window',
  (1023, 1024),
  ((0x09e6083c, 105, 1), (0x09e6089f, 94, 1)),
  'UNIQUE',
  'rewards seen in the window between this site and the next call site:'
  ' Ice Stone x1, Moon Stone x1'),
 0x09e63112: (
  'the floating-Pokemon NPC, first site',
  (174, 478, 479, 1086),
  (),
  'UNIQUE',
  'no give-item in its window'),
 0x09e63191: (
  'the floating-Pokemon NPC -- "I\'ll give you the item, Air Balloon!"',
  (174, 478, 479, 1086),
  ((0x09e631cc, 564, 1),),
  'UNIQUE',
  'rewards seen in the window between this site and the next call site:'
  ' Air Balloon x1'),
 0x09e68c86: (
  'Oddish scientist -- CONSUMES thirty Oddish, gives Dream Mist',
  (),
  ((0x09e68dd7, 89, 1),),
  'UNIQUE',
  'rewards seen in the window between this site and the next call site:'
  ' Dream Mist x1'),
 0x09e69879: (
  'Hoopa -- MASTER BALL (high-ROM copy)',
  (828, 829),
  ((0x09e698ba, 1, 1), (0x09e69960, 263, 1), (0x09e699c0, 84, 3)),
  'ELSEWHERE',
  'rewards seen in the window between this site and the next call site:'
  ' Master Ball x1, Good Rod x1, Max Repel x3'),
 0x09e6a780: (
  'Happiny -- Oval Stone (second site)',
  (493,),
  (),
  'SPECIES_LOCKED',
  'no give-item in its window'),
 0x09e6a890: (
  'Happiny -- Oval Stone / Everstone (third site)',
  (493,),
  ((0x09e6a8cb, 102, 1),),
  'SPECIES_LOCKED',
  'rewards seen in the window between this site and the next call site:'
  ' Oval Stone x1'),
 0x09e6b2e9: (
  'Butterfree named in flavour text only',
  (),
  (),
  'NOT_A_GATE',
  'no give-item in its window'),
 0x09e7b1cc: (
  'Furfrou trimmer',
  (),
  (),
  'SPECIES_LOCKED',
  'no give-item in its window'),
 0x09e7b2e8: (
  'Furfrou trimmer, second site',
  (),
  (),
  'SPECIES_LOCKED',
  'no give-item in its window'),
 0x09e821fe: (
  'Sneasel -- Luck Incense',
  (215,),
  ((0x09e82233, 252, 1),),
  'ELSEWHERE',
  'rewards seen in the window between this site and the next call site:'
  ' Luck Incense x1'),
 0x09e8569c: (
  'Mr. Sun -- Solrock / Solgaleo, TM11',
  (349, 1008),
  ((0x09e856dc, 299, 1),),
  'UNIQUE',
  'rewards seen in the window between this site and the next call site:'
  ' TM11 x1'),
 0x09e8e901: (
  'Pumpkaboo size judge -- 5 Dusk Balls and a Bottle Cap',
  (),
  ((0x09e8e995, 60, 5), (0x09e8e9e2, 616, 1)),
  'ELSEWHERE',
  'rewards seen in the window between this site and the next call site:'
  ' Dusk Ball x5, Bottle Cap x1'),
 0x09e8eaed: (
  'Pichu -- DESTINY KNOT',
  (172, 1100),
  ((0x09e8eb22, 239, 1),),
  'UNIQUE',
  'rewards seen in the window between this site and the next call site:'
  ' Destiny Knot x1'),
 0x09e8eb95: (
  'Pichu -- a gift Pichu (givepokemon 1100 L50 @Light Ball, 0x09E8EC25)',
  (172, 1100),
  (),
  'SPECIES_LOCKED',
  'no give-item in its window'),
 0x09eb02a7: (
  'Zygardia / Zygfried -- moves and ability',
  (826, 837),
  (),
  'SPECIES_LOCKED',
  'no give-item in its window'),
 0x09eb0723: (
  'Zygardia -- disassemble the construct',
  (),
  (),
  'SPECIES_LOCKED',
  'no give-item in its window'),
 0x09eb086a: (
  'Zygardia -- form change',
  (826, 837),
  (),
  'SPECIES_LOCKED',
  'no give-item in its window'),
}

EXPECT_CHECKS = 7

failures = []
checks_run = 0


def check(name, ok, detail=""):
    global checks_run
    checks_run += 1
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name,
                           (" -- " + detail) if detail and not ok else ""))
    if not ok:
        failures.append(name)


def charmap():
    import re
    table = {}
    pat = re.compile(r"^'(.)'\s*=\s*([0-9A-Fa-f]{2})\s*$")
    for line in open(CHARMAP, encoding="utf-8"):
        m = pat.match(line.rstrip("\n"))
        if m:
            table[int(m.group(2), 16)] = m.group(1)
    table[0x00] = " "
    return table


def name_at(b, cm, addr, limit):
    out = []
    for i in range(limit):
        c = b[addr - ROM_BASE + i]
        if c == 0xFF:
            break
        out.append(cm.get(c, "."))
    return "".join(out).strip()


def item_name(b, cm, n):
    base, stride = ITEM_TABLE
    return name_at(b, cm, base + n * stride, min(stride, 14))


def species_name(b, cm, n):
    base, stride = SPECIES_TABLE
    return name_at(b, cm, base + n * stride, min(stride, 12))


def scan_sites(b):
    """Every `special ChoosePartyMon; waitstate` in the ROM."""
    found = []
    pat = bytes((0x25, CHOOSE_SPECIAL, 0x00))
    i = b.find(pat)
    while i >= 0:
        if i + 3 < len(b) and b[i + 3] == WAITSTATE:
            found.append(ROM_BASE + i)
        i = b.find(pat, i + 1)
    return found


def compares(b, addr, span=0x140):
    """Every compare-var-to-value operand in the window after a site."""
    out = []
    o = addr - ROM_BASE
    for i in range(o, min(len(b) - 5, o + span)):
        if b[i] == 0x21:
            var = struct.unpack_from("<H", b, i + 1)[0]
            if var in (0x8000, 0x8004, 0x8005, 0x8006, 0x800D):
                out.append(struct.unpack_from("<H", b, i + 3)[0])
    return out


def main():
    if not os.path.isfile(ROM):
        print("base ROM not found: %s" % os.path.relpath(ROM, ROOT))
        return 1
    with open(ROM, "rb") as f:
        b = f.read()
    cm = charmap()

    found = scan_sites(b)
    print("%s -- %d ChoosePartyMon (special %#04x) call site(s), "
          "%d inventoried, %d decoded\n"
          % (GAME, len(found), CHOOSE_SPECIAL, len(SITES), len(GATES)))

    # A scanner that resolves nothing finds nothing, and an empty result
    # satisfies every set comparison below. Zero is never a pass.
    check("the scan reached at least one call site", bool(found),
          "no site at all -- the special id or the ROM is wrong, not the data")

    new = sorted(set(found) - set(SITES))
    check("every ChoosePartyMon call site in the ROM is inventoried",
          not new,
          ", ".join("%#010x" % a for a in new)
          + " -- a way to hand a Pokemon to an NPC that nobody has looked at")

    gone = sorted(set(SITES) - set(found))
    check("every inventoried call site is still present in the ROM",
          not gone, ", ".join("%#010x" % a for a in gone))

    bad = []
    for addr, (_label, ids, _rew, _v, _why) in sorted(GATES.items()):
        seen = compares(b, addr)
        missing = [i for i in ids if i not in seen]
        if missing:
            bad.append("%#010x wants %s" % (addr, missing))
    check("every decoded gate still compares its recorded species",
          not bad, "; ".join(bad))

    bad = []
    for addr, (_label, _ids, rew, _v, _why) in sorted(GATES.items()):
        for give, item, qty in rew:
            o = give - ROM_BASE
            ok = (b[o:o + 3] == bytes((0x1A, 0x00, 0x80))
                  and struct.unpack_from("<H", b, o + 3)[0] == item
                  and b[o + 5:o + 8] == bytes((0x1A, 0x01, 0x80))
                  and struct.unpack_from("<H", b, o + 8)[0] == qty
                  and b[o + 10:o + 12] == bytes((0x09, 0x00)))
            if not ok:
                bad.append("%#010x is no longer `give item %d x%d`"
                           % (give, item, qty))
    check("every recorded reward still gives that item, at that address",
          not bad, "; ".join(bad))

    # The two name tables are the reason a reward can be READ at all. If one
    # moves, every verdict above describes the wrong item or the wrong
    # species, and every set check above still passes. The probes are
    # deliberately not empty in any port: a check over GATES alone would be
    # vacuous in the game whose only gate is tested in native code and gives
    # no item.
    bad = ["%d reads %r, recorded %r" % (n, item_name(b, cm, n), want)
           for n, want in ITEM_PROBES if item_name(b, cm, n) != want]
    check("the item-name table still reads what this file recorded",
          ITEM_PROBES and not bad, "; ".join(bad) or "no probe is pinned")

    bad = ["%d reads %r, recorded %r" % (n, species_name(b, cm, n), want)
           for n, want in SPECIES_PROBES if species_name(b, cm, n) != want]
    check("the species-name table still reads what this file recorded",
          SPECIES_PROBES and not bad, "; ".join(bad) or "no probe is pinned")

    counts = {}
    for _l, _i, _r, verdict, _w in GATES.values():
        counts[verdict] = counts.get(verdict, 0) + 1
    if counts:
        print("\n  verdicts: " + ", ".join("%d %s" % (counts[k], k)
                                           for k in sorted(counts)))
    for addr in sorted(GATES):
        label, ids, rew, verdict, why = GATES[addr]
        print("\n  %#010x  %s" % (addr, verdict))
        print("     %s" % label)
        if ids:
            print("     gate: %s" % ", ".join(
                "%d %s" % (i, species_name(b, cm, i)) for i in ids[:8])
                + (" (+%d more)" % (len(ids) - 8) if len(ids) > 8 else ""))
        else:
            print("     gate: tested in NATIVE code -- no script operand")
        for give, item, qty in rew:
            print("     gives: %#010x item %d x%d  %s"
                  % (give, item, qty, item_name(b, cm, item)))
        print("     %s" % why)

    if assert_tally(checks_run, EXPECT_CHECKS, "check_species_gates"):
        return 1
    print("\n%s" % ("ALL PASS" if not failures
                     else "FAILURES: " + ", ".join(failures)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
