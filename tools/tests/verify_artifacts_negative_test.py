#!/usr/bin/env python3
"""Negative test for tools/tests/verify_artifacts.py.

A checker nobody has broken on purpose is not a checker. This tampers a COPY of
the built ROM -- never the build output itself -- and requires a non-zero exit
for each case, with a control at each end so that a verifier which rejected
everything could not pass by looking strict.

The cases target the things this layer exists to catch, one each:

  1. control                     -- the real ROM passes
  2. a byte changed OUTSIDE every declared window (the diff-containment check;
     this is the one that caught the undeclared opt-in splice on its first run)
  3. a hook reverted to its original bytes  (the patch silently not applied)
  4. a deliberately-UNHOOKED CreateWildMon reacher touched (silent scope creep
     into scripted/raid/swarm/DexNav encounters)
  5. a marker slot with its 0xFF terminator overwritten
  6. control again -- the untouched copy still passes, proving the harness is
     restoring what it thinks it is
"""
import os
import shutil
import subprocess
import sys
import os as _os
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from cm_tally import assert_cases
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "character_mode"))
import build_patch as bp                                    # noqa: E402

BUILT = os.path.join(ROOT, "build", "unbound-cm.gba")
VERIFY = os.path.join(HERE, "verify_artifacts.py")


def run(path):
    env = dict(os.environ, CM_BUILT_ROM=path)
    # ⚠️ Strip the tally overrides: subprocess inherits the environment, so
    # running this negative test with CM_EXPECT_CHECKS set pinned the CHILD
    # to that number and broke the CONTROL case for a reason unrelated to
    # any tamper. A control an inherited variable can break is not a control.
    env.pop("CM_EXPECT_CHECKS", None)
    env.pop("CM_EXPECT_CASES", None)
    return subprocess.run([sys.executable, VERIFY], env=env,
                          capture_output=True, text=True).returncode


# How many tamper cases this negative test must run. A deliberate
# LITERAL -- see cm_tally.assert_cases.
EXPECT_CASES = 22


def main():
    if not os.path.isfile(BUILT):
        print("SKIP: no built ROM -- run tools/build_patch.py first")
        return 0
    fails, passes = [], 0
    tmp = tempfile.mkdtemp()
    copy = os.path.join(tmp, "tampered.gba")

    def case(label, want, mutate=None):
        nonlocal passes
        shutil.copyfile(BUILT, copy)
        if mutate:
            with open(copy, "r+b") as f:
                mutate(f)
        got = run(copy)
        ok = (got == 0) == (want == 0)
        print("  %-5s %-52s exit=%d" % ("ok" if ok else "FAIL", label, got))
        if ok:
            passes += 1
        else:
            fails.append(label)

    def flip(off):
        def m(f):
            f.seek(off)
            b = f.read(1)[0]
            f.seek(off)
            f.write(bytes([b ^ 0xFF]))
        return m

    def revert(off, orig):
        def m(f):
            f.seek(off)
            f.write(orig)
        return m

    print("verify_artifacts negative test")
    case("control: the real build passes", 0)
    # Somewhere far from every declared window: the base ROM's own code.
    case("a byte changed outside every window fails", 1, flip(0x00300000))
    case("the catch hook reverted to original fails", 1,
         revert(bp.CATCH_BL_FILE_OFF, bp.CATCH_BL_ORIG))
    # Touching a site the spec says must stay untouched.
    # ROM address -> file offset; see the note in verify_artifacts.py.
    case("touching the swarm call site fails", 1, flip(0x08A14EAC - bp.ROM_BASE))
    # Overwrite a whole marker slot with non-0xFF so it loses its terminator.
    def wipe_marker(f):
        f.seek(bp.CM_MARKER_FILE_OFF)
        f.write(b"\x41" * bp.CM_MARKER_STRIDE)
    case("an unterminated marker slot fails", 1, wipe_marker)
    # PC second guard ([G]). Each tamper hits one thing [G] owns.
    def guard_site_reverted(f):
        o = bp.PSS_GUARD_BL_FILE_OFFS[0]
        f.seek(o)
        f.write(bp.thumb_bl(bp.ROM_BASE + o, bp.PSS_COUNT_ALIVE_EXCEPT))
    case("the deposit site left calling the vanilla count fails", 1, guard_site_reverted)
    case("CanShiftMon's tail reverted fails", 1,
         revert(bp.PSS_CANSHIFT_TAIL_FILE_OFF, bytes.fromhex("00060028")))
    def guard_tramp_bent(f):
        f.seek(bp.PSS_GUARD_TRAMPOLINE_FILE_OFF + 4)
        v = int.from_bytes(f.read(4), "little")
        f.seek(bp.PSS_GUARD_TRAMPOLINE_FILE_OFF + 4)
        f.write((v + 4).to_bytes(4, "little"))
    case("the guard trampoline aimed 4 bytes off fails", 1, guard_tramp_bent)
    # Link-trade sweep ([L]). Each tamper stays inside a declared window, so only
    # [L] can catch it.
    def link_site_reverted(f):
        o = bp.LINK_TRADE_BL_FILE_OFF
        f.seek(o)
        f.write(bp.thumb_bl(bp.ROM_BASE + o, bp.STRING_EXPAND_PLACEHOLDERS))
    case("the link-trade site left calling vanilla fails", 1, link_site_reverted)
    def link_site_to_guard(f):
        o = bp.LINK_TRADE_BL_FILE_OFF
        f.seek(o)
        f.write(bp.thumb_bl(bp.ROM_BASE + o, bp.ROM_BASE + bp.PSS_GUARD_TRAMPOLINE_FILE_OFF))
    case("the link-trade site aimed at the guard's trampoline fails", 1, link_site_to_guard)
    def link_tramp_bent(f):
        f.seek(bp.LINK_TRADE_TRAMPOLINE_FILE_OFF + 4)
        v = int.from_bytes(f.read(4), "little")
        f.seek(bp.LINK_TRADE_TRAMPOLINE_FILE_OFF + 4)
        f.write((v + 4).to_bytes(4, "little"))
    case("the link-trade trampoline aimed 4 bytes off fails", 1, link_tramp_bent)
    # Overworld sprite ([O], 2026-10-03). Each tamper stays inside a declared
    # window, so only [O] can catch it. Misty (10) has a sheet.
    import subprocess as _sp
    import re as _re
    sys.path.insert(0, os.path.join(ROOT, "tools", "character_mode"))
    import unbound_ow_player as owp
    _nm = _sp.run(["arm-none-eabi-nm", os.path.join(ROOT, "build", "character_mode.elf")],
                  check=True, capture_output=True, text=True).stdout
    _gtab = int(_re.search(r"^([0-9a-f]+) A gCharacterOwGfx$", _nm, _re.M).group(1), 16) - bp.ROM_BASE
    with open(BUILT, "rb") as _f:
        _b = _f.read()
    _gid = int.from_bytes(_b[_gtab + 18:_gtab + 20], "little")
    _info = int.from_bytes(_b[owp.R(owp.OW_TABLES[_gid >> 8]) + (_gid & 0xFF) * 4:][:4], "little")
    _imgs = int.from_bytes(_b[owp.R(_info) + 0x1C:][:4], "little")
    _frame3 = int.from_bytes(_b[owp.R(_imgs) + 8 * 3:][:4], "little") - bp.ROM_BASE
    case("the avatar trampoline reverted fails", 1,
         revert(bp.AVATAR_FN_FILE_OFF, owp.AVATAR_FN_ORIG))
    case("a pixel of Misty's walk frame changed fails", 1, flip(_frame3 + 40))
    case("Misty's id zeroed in the id table fails", 1, revert(_gtab + 18, b"\x00\x00"))
    case("one palette-table reader left on the base table fails", 1,
         revert(owp.R(owp.PAL_TABLE_REFS[1]), owp.PAL_TABLE.to_bytes(4, "little")))
    # Field moves ([H], 2026-10-04). Each tamper stays inside a declared window.
    _fh = int(_re.search(r"^([0-9a-f]+) T CharacterMode_FieldMoveCanLearn$", _nm, _re.M).group(1), 16)
    def field_site_reverted(f):
        o = bp.FIELD_MOVE_BL_SITES[1][0]          # Fly
        f.seek(o)
        f.write(bp.thumb_bl(bp.ROM_BASE + o, bp.CAN_MON_LEARN_TM_TUTOR))
    case("the Fly site left calling CanMonLearnTMTutor fails", 1, field_site_reverted)
    def field_site_bent(f):
        o = bp.FIELD_MOVE_BL_SITES[0][0]          # PartyHasMonWithFieldMovePotential
        f.seek(o)
        f.write(bp.thumb_bl(bp.ROM_BASE + o, (_fh & ~1) + 4))
    case("the overworld site aimed 4 bytes into the hook fails", 1, field_site_bent)
    def field_hook_pool_bent(f):
        o = (_fh & ~1) - bp.ROM_BASE
        f.seek(o)
        code = f.read(0x80)
        k = next(k for k in range(0, 0x7D, 4)
                 if int.from_bytes(code[k:k + 4], "little") == bp.CAN_MON_LEARN_TM_TUTOR | 1)
        f.seek(o + k)
        f.write((bp.CAN_MON_LEARN_TM_TUTOR + 5).to_bytes(4, "little"))
    case("the hook's fallback literal bent fails", 1, field_hook_pool_bent)
    # Lava Surf ([H], 2026-10-05)
    case("the magma script's Fire search left in place fails", 1,
         revert(bp.LAVA_SPLICE_FILE_OFF, bp.LAVA_SPLICE_ORIG))
    def lava_tail_at(f):
        f.seek(bp.LAVA_SPLICE_FILE_OFF + 1)
        return int.from_bytes(f.read(4), "little") - bp.ROM_BASE
    def lava_rejoin_bent(f):
        t = lava_tail_at(f)
        f.seek(t + 17)                            # the first goto's operand
        f.write((bp.LAVA_REJOIN_ROM_ADDR + 5).to_bytes(4, "little"))
    case("the lava tail rejoining 5 bytes late fails", 1, lava_rejoin_bent)
    _lsetup = int(_re.search(r"^([0-9a-f]+) T CharacterMode_LavaSurfSetup$", _nm, _re.M).group(1), 16)
    def lava_callasm_wrong(f):
        t = lava_tail_at(f)
        f.seek(t + 1)
        f.write((_lsetup | 1).to_bytes(4, "little"))
    case("the lava tail calling the test setup instead fails", 1, lava_callasm_wrong)
    case("control: the untouched copy still passes", 0)

    shutil.rmtree(tmp, ignore_errors=True)
    if fails:
        print("\nFAILURES: " + ", ".join(fails))
        return 1
    print("\nverify_artifacts negative test: %d/%d PASS" % (passes, passes))
    if assert_cases(passes + len(fails), EXPECT_CASES, 'verify_artifacts'):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
