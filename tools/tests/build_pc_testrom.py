#!/usr/bin/env python3
"""Build the NEGATIVE-CONTROL ROM for the live PC-exit e2e (never shipped).

../game_plans/rowe_parity.md §13.33 item 1. The positive cases run against the
real build/unbound-cm.gba -- the debug scripts that set the fixture up are baked
into it by tools/build_patch.py, and the PC access script they fall into is the
shipped one. So unlike the sibling ports there is no positive test ROM to build.

What IS needed is the control: the same run with the hook ABSENT. Without it the
layer proves the sweep works when something calls it and says nothing about
whether CLOSING THE PC calls it -- which is the entire claim. This reverts ALL
FOUR PC splices to their stock tails, so the debug script still falls into the
PC access script, the storage system still opens and closes, and nothing sweeps.

⚠️ All four, not just the one the layer walks: reverting one would leave a build
that still differs from "the hook is absent" in a way nothing here would notice.

Usage: python3 tools/tests/build_pc_testrom.py
Writes build/unbound-cm-pcnohook.gba. Never distributed.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "build" / "unbound-cm.gba"
OUT = ROOT / "build" / "unbound-cm-pcnohook.gba"


def main():
    sys.path.insert(0, str(ROOT / "tools" / "character_mode"))
    import pc_hook

    d = bytearray(SRC.read_bytes())
    for rom_addr, off, orig, _anchor, label in pc_hook.SITES:
        cur = bytes(d[off:off + len(orig)])
        # Refuse to build from an unhooked ROM: the control would then be
        # identical to the positive ROM and would "fail" for no reason at all.
        assert cur[0] == 0x05, (
            "the PC splice at %#x (%s) is NOT in this build (%s) -- run "
            "tools/build_patch.py first" % (rom_addr, label, cur.hex(" ")))
        d[off:off + len(orig)] = orig
    OUT.write_bytes(bytes(d))
    print("NEGATIVE CONTROL: %s -- all %d PC splices reverted to their stock "
          "tails; the hook is absent here. Never distributed."
          % (OUT.name, len(pc_hook.SITES)))


if __name__ == "__main__":
    main()
