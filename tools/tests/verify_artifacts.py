#!/usr/bin/env python3
"""Independent static verification of the built Unbound Character Mode ROM.

rowe_parity.md §9 listed this as the third gap the parity table never carried:
Radical Red, Lazarus and Seaglass each have a verify_artifacts.py and Unbound
had none.  §9 called that "weaker rather than absent" -- the injector asserts
its preconditions at build time and 74 GDB checks run against the built ROM --
and it is right, but the two things it leaves uncovered are the two that have
actually bitten the sibling repos:

  * ⭐ DIFF CONTAINMENT.  build_patch.py counts changed bytes and prints the
    number; nothing checks WHERE they are.  A stray write outside the declared
    windows -- the failure mode that surfaced in Seaglass as "299 stray bytes"
    when an address was rebased and one verifier kept the old value -- would be
    invisible here.  This walks every differing byte between the base ROM and
    the built ROM and requires each to fall inside a declared region.
  * ⭐ The build asserting its own work.  build_patch.py's checks run inside the
    process that does the patching, on the bytes it just wrote.  This reads
    build/unbound-cm.gba back off disk with no shared state.

⚠️ Every address and every window is IMPORTED from tools/build_patch.py rather
than restated here.  Restating them is how Seaglass's verifier ended up
validating a stale CM_MUGSHOT_ADDR while the injector's log printed the right
one, and six checks then failed as "stray bytes" rather than as a stale
constant.  If build_patch rebases something, this file follows automatically.

Exit 1 on any mismatch.  Run after tools/build_patch.py.
"""
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
TOOLS = os.path.join(ROOT, "tools")
CM = os.path.join(TOOLS, "character_mode")
sys.path.insert(0, HERE)
sys.path.insert(0, TOOLS)

from cm_tally import assert_tally      # noqa: E402
import build_patch as bp               # noqa: E402  (constants only; no side effects)
import trade_hook                      # noqa: E402
import egg_hook                        # noqa: E402
import pc_hook                         # noqa: E402
import optin_script                    # noqa: E402

# CM_BUILT_ROM lets the negative test point this at a tampered COPY. The real
# build output is never written to by anything here.
BUILT = os.environ.get("CM_BUILT_ROM",
                       os.path.join(ROOT, "build", "unbound-cm.gba"))

# How many checks this layer must run. A deliberate LITERAL -- see
# tools/tests/cm_tally.py for why this must never be a derived expression.
EXPECT_CHECKS = 88   # +6: [L] the link-trade sweep (2026-09-30); +8: [G] the PC second guard (2026-09-29); +6: [F] the build fingerprints (2026-09-29); +17: [R] the roster display START row (2026-09-27)
                     # +21: the PC-exit sweep, 5 checks x 4 sites + the tail census (2026-09-10)

failures = []
checks_run = 0


def check(name, ok, detail=""):
    global checks_run
    checks_run += 1
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name,
                           (" -- %s" % detail) if detail and not ok else ""))
    if not ok:
        failures.append(name)


def _find_pc_tails(rom):
    """ROM addresses of the four PC-exit tails, located by CONTENT.

    ⚠️ The first version of this read the base out of site 0's own `goto`
    operand -- which made the "site 0 points at its tail" check SELF-REFERENTIAL
    and therefore unable to fail. Bending that operand moved the expectation
    with it, and the negative test caught it. (It was written that way to avoid
    replaying the injector's packing arithmetic, which is a real hazard: every
    offset in that block depends on the length of everything before it.)

    So locate them by the one thing neither the goto nor the rejoin can fake:
    the four-byte head every tail shares -- `special <storage>; waitstate` --
    inside the injection block. Four of them, evenly spaced, written in SITES
    order. That is independent of every operand under test.

    ⚠️ The head deliberately STOPS before the sweep special, even though
    including it would look tidier. Locating on the sweep too would make a
    tamper that bends the sweep MOVE the tail out from under its own check, so
    every site would fail the census instead of the one site failing the check
    that names the defect. The locator must not depend on anything it is
    helping to test.
    """
    head = (bytes([0x25]) + struct.pack("<H", pc_hook.SPECIAL_PC)
            + bytes([0x27]))
    lo, hi = bp.INJECT_FILE_OFF, bp.INJECT_FILE_OFF + bp.INJECT_BLOCK_LEN
    hits, i = [], lo - 1
    while True:
        i = bytes(rom).find(head, i + 1, hi)
        if i < 0:
            break
        hits.append(bp.ROM_BASE + i)
    return hits


def main():
    if not os.path.isfile(BUILT):
        print("no built ROM at %s -- run tools/build_patch.py first"
              % os.path.relpath(BUILT, ROOT))
        return 1
    with open(bp.ROM, "rb") as f:
        orig = f.read()
    with open(BUILT, "rb") as f:
        rom = f.read()

    manifest = json.load(open(os.path.join(CM, "characters_manifest.json")))
    chars = manifest["characters"] if isinstance(manifest, dict) else manifest
    n_chars = len(chars)

    check("built ROM is the same size as the base ROM",
          len(rom) == len(orig), "%d vs %d" % (len(rom), len(orig)))

    # ---- the declared write windows, all imported ------------------------
    windows = []   # (name, file_off, length)

    def win(name, off, ln):
        windows.append((name, off, ln))

    win("injection block", bp.INJECT_FILE_OFF, bp.INJECT_BLOCK_LEN)
    # roster display: record 6 (callback, label, icon gfx + frame = 11 B),
    # the builder's case-6 byte, and the order loops' VarGet literal
    win("START record 6", bp.START_RECORD6_OFF, 11)
    win("START builder case-6 byte", bp.START_CASE6_OFF, 1)
    win("START VarGet literal", bp.START_VARGET_LIT, 4)
    # PC second guard: the trampoline over CheckHeap, two BLs, CanShiftMon's tail
    win("PC guard trampoline (CheckHeap)", bp.PSS_GUARD_TRAMPOLINE_FILE_OFF, 8)
    for _o in bp.PSS_GUARD_BL_FILE_OFFS + (bp.PSS_CANSHIFT_BL_FILE_OFF,):
        win("PC guard BL %#x" % _o, _o, 4)
    win("CanShiftMon tail", bp.PSS_CANSHIFT_TAIL_FILE_OFF, 4)
    # link-trade sweep: the CheckHeap+8 trampoline and one BL
    win("link-trade trampoline (CheckHeap+8)", bp.LINK_TRADE_TRAMPOLINE_FILE_OFF, 8)
    win("link-trade BL", bp.LINK_TRADE_BL_FILE_OFF, 4)
    win("catch bl", bp.CATCH_BL_FILE_OFF, 4)
    win("GiveMonToPlayer trampoline", bp.GMTP_FILE_OFF, 8)
    win("givemon bl", bp.GIVEMON_BL_FILE_OFF, 4)
    win("givemon veneer", bp.GIVEMON_VENEER_FILE_OFF, 8)
    win("gSpecials[0x1B6]", bp.SPECIAL_1B6_FILE_OFF, 4)
    win("marker pool word", bp.CM_MARKER_POOL_FILE_OFF, 4)
    win("marker strings", bp.CM_MARKER_FILE_OFF, n_chars * bp.CM_MARKER_STRIDE)
    win("trade special sweep", trade_hook.SPECIAL_SWEEP_FILE_OFF, 4)
    win("trade inline site", trade_hook.INLINE_SITE_OFF,
        len(trade_hook.INLINE_ORIG))
    # SUB_SITES is a {description: file_offset} dict; iterating it bare yields
    # the descriptions, which is how this first tried to treat a string as an
    # address.
    for label, off in sorted(trade_hook.SUB_SITES.items()):
        win("trade sub site (%s)" % label, off, len(trade_hook.SUB_TAIL_ORIG))
    win("egg splice", egg_hook.SPLICE_FILE_OFF, len(egg_hook.SPLICE_ORIG))
    # PC-exit sweep: four overlays (the tails live inside the injection block,
    # which is already a declared window).
    for _i, (_pr, _pf, _po, _anchor, _plabel) in enumerate(pc_hook.SITES):
        win("PC splice %d (%s)" % (_i, _plabel), _pf, len(_po))
    # ⚠️ The opt-in splice. Omitting it is what this checker caught on its first
    # run -- 9 stray bytes at 0x1e6ff2d, which is the entire organic-reach
    # mechanism (the checkflag gate every first-run new game passes through).
    # A window list assembled by reading the injector's constants misses any
    # site whose offset lives in a helper module, which is precisely the shape
    # of hole diff containment exists to catch.
    win("opt-in splice", optin_script.SPLICE_FILE_OFF,
        len(optin_script.SPLICE_ORIG)
        if hasattr(optin_script, "SPLICE_ORIG") else 9)
    for name, (off, _o) in bp.WILD_CALL_SITES.items():
        win("wild call site %s" % name, off, 4)

    # The sprite and marker blobs live in a separate 0xFF run; cover the whole
    # span they occupy rather than restating each blob's length.
    spr_lo = min(bp.CM_SPRITE_PTRS_FILE_OFF, bp.CM_SPRITE_BLOBS_FILE_OFF)
    spr_len = os.path.getsize(os.path.join(CM, "cm_sprite_blobs.bin"))
    spr_ptr_len = os.path.getsize(os.path.join(CM, "cm_sprite_offsets.bin"))
    win("sprite pointer table", bp.CM_SPRITE_PTRS_FILE_OFF, spr_ptr_len)
    win("sprite blobs", bp.CM_SPRITE_BLOBS_FILE_OFF, spr_len)

    # faster stat-change battle messages: two 15-byte battle-script windows
    # reordered in place (same length, so nothing downstream moves).
    for _label, _a, _t in bp.CM_BATTLE_MSG_SITES:
        win("battle message %s" % _label, _a - 0x08000000, 15)

    check("no two declared windows overlap",
          all(not (a[1] < b[1] + b[2] and b[1] < a[1] + a[2])
              for i, a in enumerate(windows) for b in windows[i + 1:]))

    # ---- 1. diff containment --------------------------------------------
    covered = bytearray(len(rom))
    for _name, off, ln in windows:
        covered[off:off + ln] = b"\x01" * ln
    stray = [i for i in range(min(len(rom), len(orig)))
             if rom[i] != orig[i] and not covered[i]]
    check("every changed byte is inside a declared window",
          not stray,
          "%d stray byte(s), first at file %#x" % (len(stray), stray[0])
          if stray else "")

    changed = sum(1 for a, b in zip(orig, rom) if a != b)
    check("the build changed something at all", changed > 0, str(changed))

    # ---- 1c. activation party sweep --------------------------------------
    # The opt-in block's confirm arm must be: setflag FLAG_CHARACTER_MODE, then
    # a callnative into the injected code, then the "enabled" msgbox. Decoded
    # POSITIONALLY -- the sweep returns immediately unless the mode is active,
    # so it has to come AFTER the setflag; an edit that moved it before would
    # leave it a permanent no-op rather than failing anywhere else.
    #
    # Anchored on the WHOLE shape, not on `29 <flag>` alone: that three-byte
    # pattern occurs six times in the injected code as incidental compiled
    # bytes, and matching it by itself reports "the block sets the flag six
    # times".
    _blk = bp.INJECT_FILE_OFF
    _end = _blk + bp.INJECT_BLOCK_LEN
    _setflag = bytes([0x29]) + struct.pack("<H", optin_script.FLAG_CHARACTER_MODE)
    _hits = []
    _i = _blk - 1
    while True:
        _i = bytes(rom).find(_setflag, _i + 1, _end)
        if _i < 0:
            break
        _a = _i + 3
        if (rom[_a] == 0x23 and rom[_a + 5] == 0x0F and rom[_a + 6] == 0x00
                and rom[_a + 11:_a + 13] == bytes([0x09, 0x04])):
            _hits.append(_a)
    check("exactly one `setflag; callnative; loadword; callstd 4` arm in the "
          "opt-in block", len(_hits) == 1, str(len(_hits)))
    if len(_hits) == 1:
        _sw = struct.unpack_from("<I", rom, _hits[0] + 1)[0]
        check("the sweep callnative is a Thumb pointer", (_sw & 1) == 1,
              f"{_sw:#010x}")
        check("...into the injected code block",
              _blk <= (_sw & ~1) - bp.ROM_BASE < _end, f"{_sw:#010x}")

    # ---- 1b. faster stat-change battle messages --------------------------
    # Pinned in BOTH directions on purpose. Checking only the built bytes would
    # pass just as happily if the base ROM had always been in the new order,
    # which would mean the injector was doing nothing.
    for _label, _a, _t in bp.CM_BATTLE_MSG_SITES:
        _o = _a - 0x08000000
        _play = bytes([0x45, 0x02, 0x01]) + struct.pack("<I", bp.CM_ANIM_ARGS)
        _prnt = bytes([0x13]) + struct.pack("<I", _t)
        _vanilla = _play + _prnt + bytes([0x12]) + struct.pack("<H", 0x0040)
        _fast = _prnt + _play + bytes([0x12]) + struct.pack("<H", 0x0020)
        check("base ROM '%s' still has the vanilla order + wait 64" % _label,
              bytes(orig[_o:_o + 15]) == _vanilla,
              bytes(orig[_o:_o + 15]).hex())
        check("built ROM '%s' prints first, then animates, wait 32" % _label,
              bytes(rom[_o:_o + 15]) == _fast,
              bytes(rom[_o:_o + 15]).hex())

    # ---- 2. the injection block really was free before -------------------
    blk = orig[bp.INJECT_FILE_OFF:bp.INJECT_FILE_OFF + bp.INJECT_BLOCK_LEN]
    check("the injection block was 0xFF in the base ROM",
          all(b == 0xFF for b in blk),
          "%d non-0xFF bytes" % sum(1 for b in blk if b != 0xFF))
    for label, off, ln in (("sprite pointer table", bp.CM_SPRITE_PTRS_FILE_OFF, spr_ptr_len),
                           ("sprite blobs", bp.CM_SPRITE_BLOBS_FILE_OFF, spr_len),
                           ("marker strings", bp.CM_MARKER_FILE_OFF,
                            n_chars * bp.CM_MARKER_STRIDE)):
        seg = orig[off:off + ln]
        check("the %s region was 0xFF in the base ROM" % label,
              all(b == 0xFF for b in seg),
              "%d non-0xFF" % sum(1 for b in seg if b != 0xFF))

    # ---- 3. the emitted data actually shipped ---------------------------
    inj = rom[bp.INJECT_FILE_OFF:bp.INJECT_FILE_OFF + bp.INJECT_BLOCK_LEN]
    for name in ("characters.bin", "rosters.bin", "names.bin",
                 "wild_species_meta.bin"):
        path = os.path.join(CM, name)
        if not os.path.isfile(path):
            check("%s present" % name, False, "missing")
            continue
        with open(path, "rb") as f:
            blob = f.read()
        # Searched rather than read at a recomputed offset: duplicating
        # build_patch's layout arithmetic here would be one more thing that can
        # silently disagree with it.
        check("%s appears verbatim in the injection block" % name,
              blob and blob in inj, "%d bytes" % len(blob))

    # ---- 4. the hook sites hold something, and point into our code ------
    def bl_target(off):
        """Decode a Thumb BL pair at a file offset to its target ROM address."""
        hi, lo = struct.unpack_from("<HH", rom, off)
        if (hi & 0xF800) != 0xF000 or (lo & 0xF800) != 0xF800:
            return None
        off11h, off11l = hi & 0x7FF, lo & 0x7FF
        disp = (off11h << 12) | (off11l << 1)
        if disp & (1 << 22):
            disp -= 1 << 23
        return bp.ROM_BASE + off + 4 + disp

    inj_lo = bp.ROM_BASE + bp.INJECT_FILE_OFF
    inj_hi = inj_lo + bp.INJECT_BLOCK_LEN

    check("the catch hook no longer holds its original bytes",
          rom[bp.CATCH_BL_FILE_OFF:bp.CATCH_BL_FILE_OFF + 4] != bp.CATCH_BL_ORIG)
    t = bl_target(bp.CATCH_BL_FILE_OFF)
    check("the catch hook branches into the injection block",
          t is not None and inj_lo <= t < inj_hi,
          hex(t) if t else "not a BL pair")

    check("the GiveMonToPlayer entry no longer holds its original bytes",
          rom[bp.GMTP_FILE_OFF:bp.GMTP_FILE_OFF + 8] != bp.GMTP_ORIG)
    check("gSpecials[0x1B6] was repointed",
          rom[bp.SPECIAL_1B6_FILE_OFF:bp.SPECIAL_1B6_FILE_OFF + 4]
          != bp.SPECIAL_1B6_ORIG)

    bad_wild = []
    for name, (off, origbytes) in sorted(bp.WILD_CALL_SITES.items()):
        if rom[off:off + 4] == origbytes:
            bad_wild.append(name + " (unpatched)")
            continue
        tt = bl_target(off)
        if tt is None or not (inj_lo <= tt < inj_hi):
            bad_wild.append(name + " -> " + (hex(tt) if tt else "not a BL"))
    check("all %d wild call sites retarget into the injection block"
          % len(bp.WILD_CALL_SITES), not bad_wild, ", ".join(bad_wild))

    # ⚠️ The deliberately UNHOOKED CreateWildMon reachers must stay unhooked:
    # scripted, raid, swarm and DexNav encounters are out of scope by spec, and
    # a future retarget that swept them up would be a silent scope change.
    check("the marker pool word was repointed away from the original wrapper",
          struct.unpack_from("<I", rom, bp.CM_MARKER_POOL_FILE_OFF)[0]
          != bp.CM_MARKER_ORIG_TARGET)

    # ---- 5. marker strings: one terminated slot per character -----------
    mk = rom[bp.CM_MARKER_FILE_OFF:
             bp.CM_MARKER_FILE_OFF + n_chars * bp.CM_MARKER_STRIDE]
    unterminated = [i for i in range(n_chars)
                    if 0xFF not in mk[i * bp.CM_MARKER_STRIDE:
                                      (i + 1) * bp.CM_MARKER_STRIDE]]
    check("every marker slot is 0xFF-terminated",
          not unterminated, "%d unterminated" % len(unterminated))

    # ---- 6. counts derived, never restated ------------------------------
    # The hardcoded-character-count trap has fired seven times in this
    # workspace and never once presented as a count error.
    # The hardcoded-character-count trap has fired seven times in this
    # workspace and has never once presented as a count error -- it surfaces as
    # "stray bytes", a "size mismatch", or a shim trusting an out-of-range
    # index. So derive the count from the ROM's own bytes.
    #
    # ⚠️ Deliberately NOT by locating the u16 count field. Doing that means
    # replicating build_patch's layout and alignment arithmetic, and a first
    # attempt that assumed the count sat immediately after names.bin read
    # padding and then a neighbouring table -- two different wrong answers. The
    # record COUNT of characters.bin as it sits in the ROM is the same fact,
    # self-locating, and needs no layout knowledge.
    REC = 16                      # record layout: 16 B/character (build_patch)
    cbin = open(os.path.join(CM, "characters.bin"), "rb").read()
    check("characters.bin in the ROM holds one record per manifest entry",
          len(cbin) == n_chars * REC and cbin in inj,
          "%d bytes = %d records, manifest lists %d"
          % (len(cbin), len(cbin) // REC, n_chars))

    # ⚠️ Scope check. build_patch.py documents five CreateWildMon reachers that
    # are deliberately NOT hooked -- scripted (setwildbattle), raid, swarm and
    # two DexNav sites -- because the spec says a roster override replaces a
    # random TABLE ROLL and nothing else. Nothing checked that they stayed
    # unhooked, so a future retarget that swept them up would silently widen
    # the feature. These are the addresses from build_patch's own comment.
    # ⚠️ These are ROM addresses and must be converted to FILE offsets. The
    # first version indexed the ROM with the raw 0x08A14EAC and, because a
    # slice past the end of a bytes object is simply empty, compared b"" to b""
    # and PASSED without testing anything. A check that cannot fail is the
    # exact defect this session's tally guards exist to stop, and it slipped
    # into a brand-new checker anyway -- it was the negative test that caught
    # it, not review.
    UNHOOKED = {"CreateScriptedWildMon": 0x08A14A4A,
                "sp117_CreateRaidMon": 0x08A14C3A,
                "TryGenerateSwarmMon": 0x08A14EAC,
                "DexNav a": 0x089D7B48, "DexNav b": 0x089D863E}
    touched, unreadable = [], []
    for nm, addr in sorted(UNHOOKED.items()):
        off = addr - bp.ROM_BASE
        if not (0 <= off and off + 4 <= len(rom)):
            unreadable.append("%s (%#x out of range)" % (nm, addr))
        elif rom[off:off + 4] != orig[off:off + 4]:
            touched.append(nm)
    check("every deliberately-unhooked call site is readable",
          not unreadable, ", ".join(unreadable))
    check("the scripted/raid/swarm/DexNav call sites are still unhooked",
          not touched, ", ".join(touched))

    # ---- the PC-exit sweep (game_plans/rowe_parity.md §13.24/§13.26c) ----
    # Pinned in BOTH directions and for ALL FOUR sites: checking only one would
    # leave the other three free to be unhooked or to point at the wrong tail.
    # ⚠️ This game has the most sites AND two different tail shapes, so nothing
    # here may assume a fixed replay length.
    _pc_tails = _find_pc_tails(rom)
    check("exactly %d PC-exit tails in the injection block, evenly spaced"
          % len(pc_hook.SITES),
          len(_pc_tails) == len(pc_hook.SITES)
          and all(_pc_tails[_k] == _pc_tails[0] + _k * pc_hook.SPACING
                  for _k in range(len(_pc_tails))),
          "found %d at %s" % (len(_pc_tails), [hex(_a) for _a in _pc_tails]))
    if len(_pc_tails) != len(pc_hook.SITES):
        # Without the tails there is nothing to decode; fail the rest by name
        # rather than indexing off the end of the list.
        _pc_tails = [0] * len(pc_hook.SITES)
    for _i, (_pr, _pf, _po, (_aoff, _aval), _plabel) in enumerate(pc_hook.SITES):
        _n = len(_po)
        check("[PC%d] base ROM still holds the stock PC script tail" % _i,
              orig[_pf:_pf + _n] == _po,
              "%s != %s" % (orig[_pf:_pf + _n].hex(), _po.hex()))
        _site = rom[_pf:_pf + _n]
        _want = _pc_tails[_i]
        check("[PC%d] PC script tail overlaid with `goto <PC tail>`" % _i,
              _site[0] == 0x05
              and struct.unpack_from("<I", _site, 1)[0] == _want,
              _site.hex())
        # ⚠️ Guarded: when the census above has already failed there is no
        # valid tail address, and an unguarded negative slice raised
        # IndexError here -- a checker that CRASHES reports nothing by name,
        # which is exactly what the negative test is trying to read.
        _toff = _want - bp.ROM_BASE
        _pt = (bytes(rom[_toff:_toff + _n + 8])
               if 0 <= _toff <= len(rom) - (_n + 8) else b"")
        _pt = _pt + b"\x00" * (_n + 8 - len(_pt))
        # ORDERING IS LOAD-BEARING: the sweep must run AFTER the waitstate.
        # Before it the storage UI has not opened, so the sweep would see the
        # party the player walked IN with -- a silent no-op that still passes
        # any "the sweep special is present" check.
        check("[PC%d] PC tail replays the storage special and its waitstate, "
              "then sweeps" % _i,
              _pt[0] == 0x25
              and struct.unpack_from("<H", _pt, 1)[0] == pc_hook.SPECIAL_PC
              and _pt[3] == 0x27
              and _pt[4] == 0x25
              and struct.unpack_from("<H", _pt, 5)[0] == pc_hook.SPECIAL_SWEEP,
              _pt.hex())
        # ⭐ The goto must rejoin THIS site's own caller. A tail that rejoined
        # another site's would be perfectly well-formed -- right special, right
        # waitstate, right sweep -- and would silently send the player into the
        # wrong script on exit. With four sites this is the tamper that matters.
        check("[PC%d] and its goto rejoins its OWN caller" % _i,
              _pt[_n + 3] == 0x05
              and struct.unpack_from("<I", _pt, _n + 4)[0] == _pr + _n,
              _pt.hex())
        check("[PC%d] the hooked script is still the PC access script" % _i,
              struct.unpack_from("<I", rom, _aoff)[0] == _aval,
              "%#x != %#x" % (struct.unpack_from("<I", rom, _aoff)[0], _aval))


    # ---- [R] roster display: a START menu row (2026-09-27) ---------------
    # Every check reads the BUILT ROM; expected values come from the manifest,
    # the base ROM or the linked ELF -- never from the .bin it was built from.
    import re
    import subprocess
    _elf = os.path.join(ROOT, "build", "character_mode.elf")
    _nm = subprocess.run(["arm-none-eabi-nm", _elf], check=True,
                         capture_output=True, text=True).stdout
    _sym = {m.group(3): int(m.group(1), 16)
            for m in re.finditer(r"^([0-9a-f]+) ([TtAaDdRr]) (\w+)$", _nm, re.M)}
    _rm = json.load(open(os.path.join(CM, "roster_roots_manifest.json")))
    _rr_file = open(os.path.join(CM, "roster_roots.bin"), "rb").read()
    _rr_off = _sym["gRosterRoots"] - 0x08000000
    check("[R] roster roots in-ROM == roster_roots.bin (at gRosterRoots)",
          rom[_rr_off:_rr_off + len(_rr_file)] == _rr_file)
    _blob = rom[_rr_off:_rr_off + len(_rr_file)]
    _esz = _rm["entry_size_bytes"]
    _roff = n_chars * _esz
    check("[R] roots[] offset re-derived from the character count == manifest",
          _roff == _rm["roots_offset_bytes"])
    check("[R] roster_roots.bin size == entry table + one u16 per root",
          len(_rr_file) == _roff + _rm["total_roots"] * 2)
    _names = struct.unpack_from("<I", orig, 0x144)[0] - 0x08000000   # CFRU slot
    _bad_e, _bad_n, _cur = [], [], 0
    for _ci, _c in enumerate(chars):
        _want = list(dict.fromkeys(_c["roster_species_ids"]))
        _f, _n = struct.unpack_from("<HH", _blob, _ci * _esz)
        if (_f, _n) != (_cur, len(_want)):
            _bad_e.append((_c["character"], _f, _n))
        _lo = _roff + _f * 2
        _got = (list(struct.unpack_from("<%dH" % _n, _blob, _lo))
                if _n and _lo + _n * 2 <= len(_blob) else ([] if not _n else None))
        if _got != _want:
            _bad_e.append((_c["character"], "roots differ"))
        for _sp in (_got or []):
            if rom[_names + _sp * 11] in (0x00, 0xFF):
                _bad_n.append((_c["character"], _sp))
        _cur += len(_want)
    check("[R] every character's (first,count) and root slice re-derive from the manifest",
          not _bad_e, str(_bad_e[:3]))
    _t, _gap = 0, []
    for _ci in range(n_chars):
        _f, _n = struct.unpack_from("<HH", _blob, _ci * _esz)
        if _f != _t:
            _gap.append(_ci)
        _t += _n
    check("[R] entries tile roots[] exactly, no gap and no overlap",
          not _gap and _t == _rm["total_roots"], "%d %s" % (_t, _gap[:3]))
    check("[R] every root resolves to a non-empty name in the BUILT ROM's gSpeciesNames",
          not _bad_n, str(_bad_n[:5]))
    _late = n_chars - 1
    _lf, _lc = struct.unpack_from("<HH", _blob, _late * _esz)
    _lw = list(dict.fromkeys(chars[_late]["roster_species_ids"]))
    check("[R] late probe: character #%d reads back its own roots" % (_late + 1),
          _lc == len(_lw) and (not _lc or list(struct.unpack_from(
              "<%dH" % _lc, _blob, _roff + _lf * 2)) == _lw))
    _empty = [c["character"] for ci, c in enumerate(chars)
              if struct.unpack_from("<HH", _blob, ci * _esz)[1] == 0]
    check("[R] characters with zero roots in-ROM == the emitter's list",
          _empty == _rm["empty_roster"], str(_empty))
    check("[R] every zero-root character is hidden (the wrapper also hides the row)",
          all(chars[ci].get("hidden") for ci in range(n_chars)
              if struct.unpack_from("<HH", _blob, ci * _esz)[1] == 0))
    # START record 6: callback + label from the ELF, icon from build_patch,
    # the rest of the record (var, flags) untouched.
    _r6 = rom[bp.START_RECORD6_OFF:bp.START_RECORD6_OFF + 16]
    _cb, _tx, _g = struct.unpack_from("<IIH", _r6, 0)
    check("[R] START record 6 callback/label -> CM_StartMenuRosterCallback / gCMRosterMenuText",
          _cb == _sym.get("CM_StartMenuRosterCallback", -2) | 1 and _tx == _sym.get("gCMRosterMenuText", -1),
          "%#x %#x" % (_cb, _tx))
    check("[R] record 6 icon = build_patch's (gfx, frame); var and flags untouched",
          _g == bp.ROSTER_ICON_GFX and _r6[10] == bp.ROSTER_ICON_FRAME
          and _r6[11:16] == bp.START_RECORD6_ORIG[11:16]
          and orig[bp.START_RECORD6_OFF:bp.START_RECORD6_OFF + 16] == bp.START_RECORD6_ORIG)
    _lbl = rom[_tx - 0x08000000:_tx - 0x08000000 + 8] if 0x08000000 <= _tx < 0x0A000000 else b""
    check("[R] its label reads 'Roster'",
          _lbl[:7] == bytes([0xCC, 0xE3, 0xE7, 0xE8, 0xD9, 0xE6, 0xFF]), _lbl.hex())
    check("[R] builder case 6 -> append (the rest of the jump table untouched)",
          rom[bp.START_CASE6_OFF] == bp.START_CASE6_APPEND
          and orig[bp.START_CASE6_OFF] == bp.START_CASE6_ORIG
          and rom[bp.START_CASE6_OFF - 6:bp.START_CASE6_OFF] == orig[bp.START_CASE6_OFF - 6:bp.START_CASE6_OFF]
          and rom[bp.START_CASE6_OFF + 1:bp.START_CASE6_OFF + 3] == orig[bp.START_CASE6_OFF + 1:bp.START_CASE6_OFF + 3])
    # the byte's target must still be the unconditional append path
    _tgt = 0x08A0BA80 + bp.START_CASE6_APPEND * 2 - 0x08000000
    check("[R] case 6's target is the append path (lsls r0,r4,#24; lsrs; ldr r3,[sp]; bl)",
          rom[_tgt:_tgt + 6] == bytes.fromhex("2006000e009b"), rom[_tgt:_tgt + 6].hex())
    _wrap = _sym.get("CM_StartMenuVarGet", -2) | 1
    _lits = [i for i in range(0, len(rom) - 3, 4) if struct.unpack_from("<I", rom, i)[0] == _wrap]
    check("[R] the order loops' VarGet literal -> CM_StartMenuVarGet, and nothing else points at it",
          struct.unpack_from("<I", orig, bp.START_VARGET_LIT)[0] == bp.START_VARGET_ORIG
          and _lits == [bp.START_VARGET_LIT], str([hex(a) for a in _lits]))
    # the compiled wrapper carries its gate: record 6's var, the CM flag,
    # VarGet, and the roots blob it checks for an empty roster
    _wo = (_wrap & ~1) - 0x08000000
    _wl = {struct.unpack_from("<I", rom, i)[0] for i in range(_wo & ~3, (_wo & ~3) + 0x80, 4)}
    check("[R] compiled wrapper carries 0x5040, flag 0x18F8, var 0x51FC, VarGet and gRosterRoots",
          {0x5040, 0x18F8, 0x51FC, bp.START_VARGET_ORIG, _sym["gRosterRoots"]} <= _wl)
    # scan the callback's whole extent (to the next symbol): CM_RosterOpen is
    # inlined into it, so its literal pool is well past a fixed window
    _co = (_sym["CM_StartMenuRosterCallback"] & ~1) - 0x08000000
    _next = min(v - 0x08000000 for v in _sym.values() if v - 0x08000000 > _co)
    _cl = {struct.unpack_from("<I", rom, i)[0] for i in range(_co & ~3, _next & ~3, 4)}
    check("[R] compiled callback stops the handler's fade and closes via Unbound's own routine",
          {0x08070A85, 0x08A0BD35} <= _cl, str(sorted(hex(x) for x in _cl if x > 0x08000000)[:8]))

    sha = os.path.join(ROOT, "build", "unbound-cm.gba.sha1")
    check("the build recorded its own sha1", os.path.isfile(sha))

    # ---- [F] compiled constants, read back out of the built ROM ----------
    # (2026-09-29) Every other section checks an emitted .bin, a patched range
    # or source TEXT. None reads what the COMPILER baked in -- the gap that let
    # Seaglass ship a stale WILDPOOL_STRIDE and Lazarus a stale TOBIAS_CHAR_ID
    # behind green suites. Both units export a fingerprint in
    # .rodata.cm_fingerprint; found by magic inside the injection block.
    # ⚠️ _fp*-prefixed locals: a bare name can shadow a counter the summary reads.
    _fp_blk = bytes(rom[bp.INJECT_FILE_OFF:bp.INJECT_FILE_OFF + bp.INJECT_BLOCK_LEN])
    _fp = {}
    for _fp_name, _fp_magic, _fp_words in (("character_mode.c", 0x4D435346, 4),
                                           ("roster_display.c", 0x4D435352, 3)):
        _fp_n = _fp_blk.count(struct.pack("<I", _fp_magic))
        check(f"[F] {_fp_name}: exactly one build fingerprint in the injection block "
              f"({_fp_n} found)", _fp_n == 1)
        if _fp_n == 1:
            _fp[_fp_name] = struct.unpack_from(
                "<%dI" % _fp_words, _fp_blk, _fp_blk.find(struct.pack("<I", _fp_magic)))
    if "character_mode.c" in _fp:
        _, _fp_mstride, _fp_wcount, _fp_wsize = _fp["character_mode.c"]
        _fp_mk = open(os.path.join(CM, "marker_strings.bin"), "rb").read()
        _fp_wm = open(os.path.join(CM, "wild_species_meta.bin"), "rb").read()
        check(f"[F] compiled MARKER_STRIDE={_fp_mstride} == the injector's "
              f"{bp.CM_MARKER_STRIDE}, and x{n_chars} == marker_strings.bin ({len(_fp_mk)} B)",
              _fp_mstride == bp.CM_MARKER_STRIDE and _fp_mstride * n_chars == len(_fp_mk))
        check(f"[F] compiled WILD_META_COUNT={_fp_wcount} x compiled "
              f"sizeof(WildSpeciesMetaBin)={_fp_wsize} == wild_species_meta.bin "
              f"({len(_fp_wm)} B) -- a stale count reads past the table or refuses real species",
              _fp_wcount * _fp_wsize == len(_fp_wm))
    if "roster_display.c" in _fp:
        _, _fp_nchars, _fp_roff = _fp["roster_display.c"]
        check(f"[F] roster_display compiled NUM_CHARACTERS={_fp_nchars} == manifest {n_chars}",
              _fp_nchars == n_chars)
        check(f"[F] roster_display compiled ROSTER_ROOTS_OFF={_fp_roff} == manifest "
              f"{_rm['roots_offset_bytes']} == {n_chars} x {_rm['entry_size_bytes']}",
              _fp_roff == _rm["roots_offset_bytes"] == n_chars * _rm["entry_size_bytes"])

    # ---- [G] PC second guard (ROWE's IsRemovingLastAllowedPartyMon) ------
    import re as _re
    import subprocess as _sp

    def _bl(buf, off):
        hw1, hw2 = struct.unpack_from("<HH", buf, off)
        if (hw1 & 0xF800) != 0xF000 or (hw2 & 0xF800) != 0xF800:
            return None
        d = ((hw1 & 0x7FF) << 12) | ((hw2 & 0x7FF) << 1)
        if d & 0x400000:
            d -= 0x800000
        return 0x08000000 + off + 4 + d
    _t = bp.PSS_GUARD_TRAMPOLINE_FILE_OFF
    _count = bp.PSS_COUNT_ALIVE_EXCEPT
    _sites = bp.PSS_GUARD_BL_FILE_OFFS + (bp.PSS_CANSHIFT_BL_FILE_OFF,)
    _c = bp.PSS_CANSHIFT_TAIL_FILE_OFF
    check("[G] base: CheckHeap is vanilla, and nothing calls it or points at it",
          bytes(orig[_t:_t + 8]) == bytes.fromhex("30b508480468051c")
          and not any(_bl(orig, o) == 0x08000000 + _t
                      for o in range(0, len(orig) - 4, 2)
                      if (orig[o + 1] & 0xF8) == 0xF0)
          and struct.pack("<I", 0x08000000 + _t + 1) not in orig
          and struct.pack("<I", 0x08000000 + _t) not in orig)
    _w = struct.unpack_from("<I", orig, 0x15FD60 + 4 * 0x85)[0] & ~1
    check("[G] base: special 0x85's wrapper calls CountPartyAliveNonEggMonsExcept",
          any(_bl(orig, _w - 0x08000000 + k) == _count for k in range(0, 12, 2)))
    check("[G] base: both guard sites call the count routine",
          all(_bl(orig, x) == _count for x in _sites))
    check("[G] built: both guard sites call the CheckHeap trampoline",
          all(_bl(rom, x) == 0x08000000 + _t for x in _sites))
    _nm = _sp.run(["arm-none-eabi-nm", os.path.join(ROOT, "build", "character_mode.elf")],
                  check=True, capture_output=True, text=True).stdout
    _guard = int(_re.search(r"^([0-9a-f]+) T CM_PSSLastMonGuard$", _nm, _re.M).group(1), 16)
    check("[G] trampoline is ldr r3,[pc]; bx r3 -> CM_PSSLastMonGuard",
          bytes(rom[_t:_t + 8]) == struct.pack("<HHI", 0x4B00, 0x4718, _guard | 1))
    check("[G] CanShiftMon tail: lsls; cmp -> b <epilogue 0x0809399A>; nop",
          bytes(orig[_c:_c + 4]) == bytes.fromhex("00060028")
          and bytes(rom[_c:_c + 4]) == struct.pack("<HH", 0xE01E, 0x46C0))
    _g0 = (_guard & ~1) - 0x08000000
    _gcode = bytes(rom[_g0:_g0 + 0x200])
    _glits = {struct.unpack_from("<I", _gcode, k)[0] for k in range(0, len(_gcode) - 3, 4)}
    check("[G] compiled guard (read from the ROM) carries 0x0809395A and gStorage 0x020397B0",
          {0x0809395A, 0x020397B0} <= _glits)
    # Exhaustive: after the patch, the ONLY direct caller of the count routine
    # is special 0x85's wrapper -- no storage-system path skips the guard.
    _left = [o for o in range(0, len(rom) - 4, 2)
             if (rom[o + 1] & 0xF8) == 0xF0 and _bl(rom, o) == _count]
    check("[G] built: the only remaining BL to the count routine is special 0x85's wrapper",
          len(_left) == 1 and 0x08000000 + _left[0] - (_w & ~1) < 16,
          str([hex(0x08000000 + o) for o in _left]))
    # ---- [L] link-trade sweep (rowe_parity.md §13.53, 2026-09-30) ----------
    _ls, _lt = bp.LINK_TRADE_BL_FILE_OFF, bp.LINK_TRADE_TRAMPOLINE_FILE_OFF
    _sep = bp.STRING_EXPAND_PLACEHOLDERS
    _case0 = struct.unpack_from("<I", orig, 0x053EB4)[0]   # CB2_SaveAndEndTrade's table, entry 0
    _c0 = _case0 - 0x08000000
    check("[L] base: CB2_SaveAndEndTrade's state 0 loads \"Communication standby\" "
          "and branches to the BL at the site, which calls StringExpandPlaceholders",
          _case0 == 0x0805404C
          and struct.unpack_from("<I", orig, ((_c0 + 14 + 4) & ~3) + 8)[0] == 0x0841E325
          and bytes(orig[_c0 + 16:_c0 + 18]) == bytes.fromhex("45e0")
          and _bl(orig, _ls) == _sep)
    _ptrs = [o for o in range(0, len(orig) - 3, 4)
             if struct.unpack_from("<I", orig, o)[0] == 0x08053E8D]
    check("[L] base: CB2_SaveAndEndTrade has one pointer to it (CB2_TryLinkTradeEvolution's "
          "pool, 0x080537F8) and no BL callers",
          _ptrs == [0x0537F8]
          and not any(_bl(orig, o) == 0x08053E8C for o in range(0, len(orig) - 4, 2)
                      if (orig[o + 1] & 0xF8) == 0xF0))
    check("[L] base: CheckHeap+8 is vanilla, and nothing calls it or points at it",
          bytes(orig[_lt:_lt + 8]) == bp.LINK_TRADE_DEAD_BYTES
          and not any(_bl(orig, o) == 0x08000000 + _lt
                      for o in range(0, len(orig) - 4, 2)
                      if (orig[o + 1] & 0xF8) == 0xF0)
          and struct.pack("<I", 0x08000000 + _lt + 1) not in orig)
    check("[L] built: the site calls the CheckHeap+8 trampoline",
          _bl(rom, _ls) == 0x08000000 + _lt)
    _lshim = int(_re.search(r"^([0-9a-f]+) T CharacterMode_LinkTradeSweepThenExpand$",
                            _nm, _re.M).group(1), 16)
    _sweep = int(_re.search(r"^([0-9a-f]+) T CharacterMode_SweepPartyToPC$",
                            _nm, _re.M).group(1), 16)
    check("[L] trampoline is ldr r3,[pc]; bx r3 -> CharacterMode_LinkTradeSweepThenExpand",
          bytes(rom[_lt:_lt + 8]) == struct.pack("<HHI", 0x4B00, 0x4718, _lshim | 1))
    _l0 = (_lshim & ~1) - 0x08000000
    _lcode = bytes(rom[_l0:_l0 + 0x24])
    check("[L] compiled link shim (read from the ROM) BLs CharacterMode_SweepPartyToPC "
          "and carries StringExpandPlaceholders",
          any(_bl(rom, _l0 + k) == (_sweep & ~1) for k in range(0, 0x20, 2))
          and (_sep | 1) in {struct.unpack_from("<I", _lcode, k)[0]
                             for k in range(0, len(_lcode) - 3, 4)})

    if assert_tally(checks_run, EXPECT_CHECKS, "verify_artifacts"):
        return 1
    print("\n%s -- %d checks ran"
          % ("ALL PASS" if not failures else "FAILURES: " + ", ".join(failures),
             checks_run))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
