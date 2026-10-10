#!/usr/bin/env python3
"""Negative test for verify_artifacts.py [S] -- 100% catch for on-roster
species (2026-10-09). Ported from the Lazarus/Seaglass tests of the same name.

Each case breaks a COPY of the built ROM in one way and requires the matching
[S] check to report FAIL BY NAME (any tamper also fails the BPS round-trip, so a
bare non-zero exit would prove nothing); the other built-ROM [S] checks must
stay PASS.

  1. control                                   -- every check passes
  2. the odds compare restored                 -- the hook is gone
  3. the BL aimed one halfword into the stub   -- skips its push {lr}
  4. the stub's compare made `cmp r5,#255`      -- off-by-one: 255 would shake
  5. CM_CatchOdds reads gBattlerAttacker        -- the wrong battler's species
  6. control again                              -- nothing left behind

THE ROM IS NEVER MODIFIED IN PLACE.
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cm_tally import assert_cases  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
VERIFY = os.path.join(HERE, "verify_artifacts.py")
BUILT = os.path.join(ROOT, "build", "unbound-cm.gba")

CHECKS = {
    "site": "[S] built: the odds compare is a BL to CharacterMode_CatchOddsStub",
    "stub": "returns to 0x089C8D5C when it is above 254",
    "fn": "CharacterMode_CatchOdds reads gBankTarget, gBattlerPartyIndexes",
}
SITE = 0x9C8D58


def _child_env():
    env = dict(os.environ)
    env.pop("CM_EXPECT_CHECKS", None)
    env.pop("CM_EXPECT_CASES", None)
    return env


def run(rom_path):
    env = _child_env()
    env["CM_BUILT_ROM"] = rom_path
    p = subprocess.run([sys.executable, VERIFY], capture_output=True, text=True,
                       cwd=ROOT, env=env)
    return p.returncode, p.stdout + p.stderr


def _hit(out, key, marker):
    return any(line.strip().startswith("[%s]" % marker) and CHECKS[key] in line
               for line in out.splitlines())


# A deliberate LITERAL -- see cm_tally.assert_cases.
EXPECT_CASES = 6


def _syms():
    out = subprocess.run(["arm-none-eabi-nm", os.path.join(ROOT, "build", "character_mode.elf")],
                         check=True, capture_output=True, text=True).stdout
    return {l.split()[2]: int(l.split()[0], 16) for l in out.splitlines()
            if len(l.split()) == 3}


def main():
    if not os.path.isfile(BUILT):
        print("SKIP: no built ROM -- run the injector first")
        return 0
    good = bytearray(open(BUILT, "rb").read())
    syms = _syms()
    stub = (syms["CharacterMode_CatchOddsStub"] & ~1) - 0x08000000
    fn = (syms["CharacterMode_CatchOdds"] & ~1) - 0x08000000
    tgt = fn + bytes(good[fn:stub]).find((0x02023D6C).to_bytes(4, "little"))
    assert tgt > fn, "gBankTarget literal not found in CM_CatchOdds"
    fails, passes = [], 0

    with tempfile.TemporaryDirectory() as tmp:

        def case(name, mutate, want_fail):
            nonlocal passes
            data = bytearray(good)
            if mutate is not None:
                mutate(data)
                if data == good:
                    fails.append(name)
                    print("  [MISS] %s -- TAMPER CHANGED NOTHING" % name)
                    return
            rom = os.path.join(tmp, "tampered.gba")
            open(rom, "wb").write(bytes(data))
            _rc, out = run(rom)
            if want_fail is None:
                ok = all(_hit(out, k, "PASS") for k in CHECKS)
                detail = "every [S] built check passes"
            else:
                ok = _hit(out, want_fail, "FAIL")
                detail = "%r reported FAIL" % CHECKS[want_fail]
                for k in CHECKS:
                    if k != want_fail and not _hit(out, k, "PASS"):
                        ok = False
                        detail += "; but %r did not PASS" % CHECKS[k]
            print("  [%s] %s -- %s" % ("PASS" if ok else "MISS", name, detail))
            if ok:
                passes += 1
            else:
                fails.append(name)

        print("negative test: verify_artifacts [S], 100% roster catch")
        case("1 control -- the real build", None, None)

        def restore(d):
            d[SITE:SITE + 4] = bytes.fromhex("fe2d63d9")
        case("2 the odds compare restored", restore, "site")

        def off_by_one(d):
            # re-encode the BL at the site to stub + 2
            a = 0x08000000 + SITE
            off = (stub + 0x08000000 + 2) - (a + 4)
            imm = (off >> 1) & 0x3FFFFF
            d[SITE:SITE + 4] = ((0xF000 | (imm >> 11)) | ((0xF800 | (imm & 0x7FF)) << 16)).to_bytes(4, "little")
        case("3 the BL aimed one halfword into the stub", off_by_one, "site")

        def cmp255(d):
            i = stub + bytes(d[stub:stub + 20]).find(bytes.fromhex("fe2d"))
            d[i] = 0xFF
        case("4 the stub's compare made cmp r5,#255", cmp255, "stub")

        def attacker(d):
            d[tgt:tgt + 4] = (0x02023D6B).to_bytes(4, "little")
        case("5 CM_CatchOdds reads another battler byte", attacker, "fn")

        case("6 control again -- nothing left behind", None, None)

    total = passes + len(fails)
    if fails:
        print("RESULT: %d/%d -- MISSED: %s" % (passes, total, ", ".join(fails)))
        return 1
    print("RESULT: %d/%d ALL PASS" % (passes, total))
    return assert_cases(total, EXPECT_CASES, "sure_catch_negative_test")


if __name__ == "__main__":
    sys.exit(main())
