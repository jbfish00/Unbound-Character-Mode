#!/usr/bin/env python3
"""Negative test for verify_artifacts.py's [R] checks -- the roster display's
START menu row (2026-09-27).

Each case breaks a COPY of the built ROM in one way, points verify_artifacts.py
at it with CM_BUILT_ROM, and requires the matching [R] check to report FAIL BY
NAME (a tampered ROM also fails diff containment, so a bare exit code proves
nothing). Checks that must stay SILENT prove the tamper was precise -- a
checker that fails everything would "catch" every case.

⚠️ THE ROM IS NEVER MODIFIED IN PLACE.
"""
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from cm_tally import assert_cases      # noqa: E402
import build_patch as bp               # noqa: E402  (constants only)

VERIFY = os.path.join(HERE, "verify_artifacts.py")
BUILT = os.path.join(ROOT, "build", "unbound-cm.gba")
ELF = os.path.join(ROOT, "build", "character_mode.elf")
CM = os.path.join(ROOT, "tools", "character_mode")

CHECKS = {
    "entry": "and root slice re-derive from the manifest",
    "tile": "entries tile roots[] exactly",
    "name": "resolves to a non-empty name in the BUILT ROM",
    "late": "late probe: character #",
    "empty": "characters with zero roots in-ROM ==",
    "record": "START record 6 callback/label",
    "icon": "record 6 icon = build_patch's",
    "label": "its label reads 'Roster'",
    "sheet": "START icon sheet = stock 10 frames",
    "case6": "builder case 6 -> append",
    "varget": "the order loops' VarGet literal",
    "wrapper": "compiled wrapper carries",
    "callback": "compiled callback stops the handler's fade",
}


def run(path):
    env = dict(os.environ, CM_BUILT_ROM=path)
    env.pop("CM_EXPECT_CHECKS", None)
    env.pop("CM_EXPECT_CASES", None)
    p = subprocess.run([sys.executable, VERIFY], capture_output=True, text=True,
                       cwd=ROOT, env=env)
    return p.stdout + p.stderr


def _hit(out, key, marker):
    return any(line.strip().startswith(marker) and CHECKS[key] in line
               for line in out.splitlines())


EXPECT_CASES = 16


def main():
    if not os.path.isfile(BUILT):
        print("SKIP: no built ROM -- run tools/build_patch.py first")
        return 0
    good = bytearray(open(BUILT, "rb").read())
    nm = subprocess.run(["arm-none-eabi-nm", ELF], check=True,
                        capture_output=True, text=True).stdout
    sym = {m.group(3): int(m.group(1), 16)
           for m in re.finditer(r"^([0-9a-f]+) ([TtAa]) (\w+)$", nm, re.M)}
    roots = sym["gRosterRoots"] - 0x08000000
    man = json.load(open(os.path.join(CM, "characters_manifest.json")))["characters"]
    rm = json.load(open(os.path.join(CM, "roster_roots_manifest.json")))
    esz = rm["entry_size_bytes"]
    roots_start = roots + len(man) * esz
    names = struct.unpack_from("<I", good, 0x144)[0] - 0x08000000
    late = len(man) - 1
    big = max(ci for ci in range(len(man))
              if struct.unpack_from("<HH", good, roots + ci * esz)[1] >= 4)

    def fc(d, ci):
        return struct.unpack_from("<HH", d, roots + ci * esz)

    fails, passes = [], 0
    with tempfile.TemporaryDirectory() as tmp:
        rom = os.path.join(tmp, "tampered.gba")
        # verify_artifacts also reads build/unbound-cm.gba.sha1's existence;
        # keep it where the real one is.
        shutil.copy(BUILT + ".sha1", rom + ".sha1") if os.path.exists(BUILT + ".sha1") else None

        def case(name, mutate, want_fail, also_pass=()):
            nonlocal passes
            data = bytearray(good)
            if mutate is not None:
                mutate(data)
                if data == good:
                    fails.append("%s: TAMPER CHANGED NOTHING" % name)
                    print("  [MISS] %s -- TAMPER CHANGED NOTHING" % name)
                    return
            open(rom, "wb").write(bytes(data))
            out = run(rom)
            if want_fail is None:
                ok = all(_hit(out, k, "[PASS]") for k in CHECKS)
                detail = "every [R] check passes"
            else:
                ok = _hit(out, want_fail, "[FAIL]")
                detail = "%r reported FAIL" % CHECKS[want_fail]
                for k in also_pass:
                    if not _hit(out, k, "[PASS]"):
                        ok = False
                        detail += "; but %r did not PASS" % CHECKS[k]
            print("  [%s] %s -- %s" % ("PASS" if ok else "MISS", name, detail))
            if ok:
                passes += 1
            else:
                fails.append(name)

        print("negative test: verify_artifacts [R] roster display START row")
        case("1 control -- the real build", None, None)

        def blank_name(d):
            f, _c = fc(d, big)
            sp, = struct.unpack_from("<H", d, roots_start + f * 2)
            d[names + sp * 11] = 0xFF
        case("2 a root's species name blanked in the built ROM", blank_name, "name",
             also_pass=("entry",))

        def bend_first(d):
            f, c = fc(d, big)
            struct.pack_into("<HH", d, roots + big * esz, f + 1, c)
        case("3 a first_root bent into another character's roots (real names)",
             bend_first, "entry", also_pass=("name",))

        def bend_last(d):
            f, c = fc(d, late)
            struct.pack_into("<HH", d, roots + late * esz, f, c + 1)
        case("4 the last character's count bent -- roots no longer tile", bend_last, "tile")

        def bend_late(d):
            f, _c = fc(d, late)
            cur, = struct.unpack_from("<H", d, roots_start + f * 2)
            struct.pack_into("<H", d, roots_start + f * 2, 25 if cur != 25 else 26)
        case("5 the LATE probe's own roots bent", bend_late, "late")

        def zero_count(d):
            f, _c = fc(d, big)
            struct.pack_into("<HH", d, roots + big * esz, f, 0)
        case("6 a count zeroed -- an empty roster appears", zero_count, "empty")

        def mission_cb(d):
            struct.pack_into("<I", d, bp.START_RECORD6_OFF, 0x0801D769)   # the Mission Log callback
        case("7 record 6's callback put back to the stock one", mission_cb, "record",
             also_pass=("icon", "case6", "varget"))

        def bend_icon(d):
            d[bp.START_RECORD6_OFF + 10] ^= 0x01
        case("8 record 6's icon frame bent", bend_icon, "icon", also_pass=("record", "label"))

        def bend_label(d):
            t = struct.unpack_from("<I", d, bp.START_RECORD6_OFF + 4)[0] - 0x08000000
            d[t] ^= 0x01
        case("9 the 'Roster' label bent", bend_label, "label", also_pass=("record", "icon"))

        def case6_skip(d):
            d[bp.START_CASE6_OFF] = bp.START_CASE6_ORIG
        case("10 builder case 6 back to skip (the row would never show)", case6_skip, "case6",
             also_pass=("record", "varget"))

        def varget_stock(d):
            struct.pack_into("<I", d, bp.START_VARGET_LIT, bp.START_VARGET_ORIG)
        case("11 the order loops' literal back to plain VarGet (row shown with CM off)",
             varget_stock, "varget", also_pass=("case6", "record"))

        def wrong_row(d):
            w = (sym["CM_StartMenuVarGet"] & ~1) - 0x08000000
            for i in range(w & ~3, (w & ~3) + 0x80, 4):
                if struct.unpack_from("<I", d, i)[0] == 0x5040:
                    struct.pack_into("<I", d, i, 0x503F)             # gates Mission Log instead
        case("12 the wrapper gates the WRONG row (0x503F)", wrong_row, "wrapper",
             also_pass=("varget", "record"))

        def no_fade_reset(d):
            c = (sym["CM_StartMenuRosterCallback"] & ~1) - 0x08000000
            for i in range(c & ~3, (c & ~3) + 0x200, 4):
                if struct.unpack_from("<I", d, i)[0] == 0x08070A85:
                    struct.pack_into("<I", d, i, 0x08070589)         # BeginNormalPaletteFade: a no-op here
        case("13 the callback no longer stops the fade (the black-screen bug)", no_fade_reset,
             "callback", also_pass=("record", "wrapper"))

        def stock_sheet(d):
            struct.pack_into("<IH", d, bp.START_ICON_SHEET_OFF,
                             struct.unpack_from("<I", bp.START_ICON_SHEET_ORIG)[0], 0x1400)
        case("14 the icon sheet struct put back to the stock sheet (frame 10 is past its end)",
             stock_sheet, "sheet", also_pass=("icon", "record"))

        def bend_pixel(d):
            # The sheet is a store-only LZ77 stream: data byte k sits at
            # 4 + k + k // 8 + 1. Bend one byte inside frame 10.
            k = 0x1400 + 0x50
            d[bp.START_ICON_FILE_OFF + 4 + k + k // 8 + 1] ^= 0x11
        case("15 one byte of the Roster icon bent", bend_pixel, "sheet",
             also_pass=("icon", "record"))

        case("16 control again -- nothing left behind", None, None)

    total = passes + len(fails)
    if fails:
        print("RESULT: %d/%d -- MISSED: %s" % (passes, total, ", ".join(fails)))
        return 1
    print("RESULT: %d/%d ALL PASS" % (passes, total))
    return assert_cases(total, EXPECT_CASES, "roster_display_negative_test")


if __name__ == "__main__":
    sys.exit(main())
