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
import optin_script                    # noqa: E402

# CM_BUILT_ROM lets the negative test point this at a tampered COPY. The real
# build output is never written to by anything here.
BUILT = os.environ.get("CM_BUILT_ROM",
                       os.path.join(ROOT, "build", "unbound-cm.gba"))

# How many checks this layer must run. A deliberate LITERAL -- see
# tools/tests/cm_tally.py for why this must never be a derived expression.
EXPECT_CHECKS = 30   # +3: the activation party sweep (2026-09-02)

failures = []
checks_run = 0


def check(name, ok, detail=""):
    global checks_run
    checks_run += 1
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name,
                           (" -- %s" % detail) if detail and not ok else ""))
    if not ok:
        failures.append(name)


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

    sha = os.path.join(ROOT, "build", "unbound-cm.gba.sha1")
    check("the build recorded its own sha1", os.path.isfile(sha))

    if assert_tally(checks_run, EXPECT_CHECKS, "verify_artifacts"):
        return 1
    print("\n%s -- %d checks ran"
          % ("ALL PASS" if not failures else "FAILURES: " + ", ".join(failures),
             checks_run))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
