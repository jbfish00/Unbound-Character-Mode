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
 0x088aa2c2: (
  'Deoxys meteorite -- "bring the Deoxys in your party closer to the'
  ' meteorite?"; native test, callasm 0x088AB3CD',
  (),
  (),
  'SPECIES_LOCKED',
  'a Deoxys form change. Two more sites of the same NPC (0x088AA485,'
  ' 0x088AA4C5) are NOT reachable from any dialogue anchor -- see the'
  ' coverage note below.'),
 0x09e68c86: (
  'Oddish scientist -- "Which Oddish will you give me?"; CONSUMES the'
  ' mon, counting into var 0x5029 up to 30',
  (43,),
  ((0x09e68dd7, 89, 1),),
  'CATCH_ONLY',
  'one Dream Mist, which is generic and has no other confirmed scripted'
  ' source. THIRTY Oddish have to be handed over, each of them caught,'
  ' and the catch gate already refuses an off-roster catch -- so this is'
  ' the upper bound of what the PC hook costs here, and reaching it'
  ' would take thirty deliveries of a species the game will not let the'
  ' character keep.'),
 0x09e8569c: (
  'Mr. Sun -- "Oh Mr. Sun, Sun, Mr. Golden Sun, please shine down on'
  ' me"',
  (349, 1008),
  ((0x09e856dc, 299, 1),),
  'CATCH_ONLY',
  'TM11, which is generic, sold in no mart (33 mart tables scanned) and'
  ' given by no other script in this ROM -- the single most valuable'
  ' species-gate reward found in any of the four games, and the one real'
  ' item this class can cost a character. The gate still needs a Solrock'
  ' or Solgaleo, which the catch gate refuses.'),
 0x09e8eb95: (
  'Pichu girl -- "Can I see it?"',
  (172, 1100),
  (),
  'SPECIES_LOCKED',
  'a GIFT POKEMON: givepokemon species 1100 (Pichu) at level 50 holding'
  ' item 202 (Light Ball) at 0x09E8EC25. Only a character who already'
  ' has Pichu on-roster can open the gate, which is exactly the'
  ' character who could keep the gift.'),
 0x09eb02a7: (
  'Zygardia / Zygfried -- "Which Zygarde\'s Ability should I change?"',
  (826, 837),
  (),
  'SPECIES_LOCKED',
  'special moves and an ability change for a Zygarde.'),
 0x09eb086a: (
  'Zygardia -- "Would you like to change the form of your Zygarde?"',
  (826, 837),
  (),
  'SPECIES_LOCKED',
  'a Zygarde form change. A third site of the same NPC (0x09EB0723, the'
  ' disassembler) tests the construct natively.'),
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
