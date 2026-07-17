# Shared phase-1 intro drive for the live-test harnesses. Exec'd from a
# test's gdb python block (after `target remote`): drives a fresh save
# through Unbound's new-game intro with verified key presses and answers
# **No** at the Character Mode opt-in (the splice at the first-run gate,
# 0x1E6FF2D), then continues to the hijackable overworld.
#
# Replaces the old blind 170s x-masher: since the splice moved into the
# first-run intro path (2026-07-17), a blind A-mash answers Yes and can
# wedge nondeterministically in the number-entry validation loop. This
# drive is state-machine-driven off the script pointer instead (harness
# lesson v11-3c) and needs NO background masher for phase 1.
#
# Requires env MGBA_WID. Defines drive_intro_to_freeroam() -> bool.

import gdb as _gdb
import os as _os
import signal as _sig
import threading as _thr
import subprocess as _sub
import struct as _struct

_inf = _gdb.selected_inferior()
_WID = _os.environ.get("MGBA_WID", "")

def _rd(addr, n):
    return int.from_bytes(_inf.read_memory(addr, n).tobytes(), "little")

def _wr(addr, data):
    _inf.write_memory(addr, bytes(data))

def _run(sec):
    _thr.Timer(sec, lambda: _os.kill(_os.getpid(), _sig.SIGINT)).start()
    try:
        _gdb.execute("continue", to_string=True)
    except _gdb.error:
        pass

_KEYMASK = {"x": 1, "z": 2, "n": 4, "q": 8, "l": 0x10, "j": 0x20, "i": 0x40, "k": 0x80}

def _press(key):
    m = _KEYMASK[key]
    for attempt in range(3):
        _sub.run(f"xdotool keydown --window {_WID} {key}", shell=True)
        _run(0.25)
        if _rd(0x03003118, 2) & m:
            _run(0.25)
            _sub.run(f"xdotool keyup --window {_WID} {key}", shell=True)
            _run(0.5)
            return True
        _sub.run(f"xdotool keyup --window {_WID} {key}", shell=True)
        _sub.run(f"xdotool windowfocus --sync {_WID}", shell=True)
        _run(0.2)
    b = _struct.pack("<H", m)
    _wr(0x0300311A, b)
    _wr(0x0300311E, b)
    _wr(0x03003120, b)
    _run(0.8)
    return False

_BLOCK = _rd(0x09E6FF2E, 4)   # opt-in block address from the splice's call target

def _block_pos():
    vals = [_rd(0x03000EB8, 4)]
    depth = _rd(0x03000EB0, 1)
    for i in range(min(depth, 20)):
        vals.append(_rd(0x03000EBC + 4 * i, 4))
    for v in vals:
        if _BLOCK <= v < _BLOCK + 130:
            return v - _BLOCK
    return -1

def drive_intro_to_freeroam(max_intro_steps=150):
    """Fresh save -> intro -> answer No at the CM prompt -> free-roam."""
    entered = False
    for step in range(max_intro_steps):
        if _block_pos() >= 0:
            entered = True
            break
        _press("x")
    if not entered:
        print("  intro drive: never reached the CM block")
        return False
    # inside the block: No at the opt-in yesno (pos 13: cursor Yes -> Down -> A)
    for step in range(40):
        pos = _block_pos()
        if pos < 0:
            break
        if pos == 13:
            _press("k")
            _press("x")
        elif pos == 36:
            # number screen opened anyway (a Yes slipped through): cancel
            # via empty buffer + OK (Start jumps to OK; empty = 0xFFFF = No)
            _run(1.5)
            _press("q")
            _press("x")
        else:
            _press("x")
    # continue the intro (story cutscene) to the overworld
    for step in range(220):
        if _rd(0x03000F9C, 1) == 0 and _rd(0x030030F4, 4) == 0x080565B5:
            return True
        _press("x")
    print("  intro drive: never reached free-roam")
    return False
