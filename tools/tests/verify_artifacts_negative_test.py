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
    return subprocess.run([sys.executable, VERIFY], env=env,
                          capture_output=True, text=True).returncode


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
    case("control: the untouched copy still passes", 0)

    shutil.rmtree(tmp, ignore_errors=True)
    if fails:
        print("\nFAILURES: " + ", ".join(fails))
        return 1
    print("\nverify_artifacts negative test: %d/%d PASS" % (passes, passes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
