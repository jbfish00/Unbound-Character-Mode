#!/bin/bash
# Live wild-encounter roster-override test driver (see wild_encounter_test.gdb).
# Reaches real free-roam via the shared intro drive, enables Character Mode as
# Red through the real handlers, then hijack-calls the LIVE TryGenerateWildMon
# (the actual grass/cave/surf/rock-smash generator, containing our hooked bl)
# many times and observes the 10% roster override firing on the real path
# without ever picking a legendary. A single mgba instance is used (no retry:
# a second attempt would attach to an already-hijacked CPU).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
. "$HERE/headless_display.sh"
ROM="$ROOT/build/unbound-cm.gba"
ELF="$ROOT/build/character_mode.elf"
LOG="$ROOT/build/wild_encounter_test.log"

[ -f "$ROM" ] || { echo "patched ROM missing — run tools/build_patch.py first"; exit 1; }
[ -f "$ELF" ] || { echo "ELF missing — run tools/build_patch.py first"; exit 1; }

rm -f "$ROOT/build/unbound-cm.sav"
pkill -f "mgba-qt -g .*unbound-cm\.gba" 2>/dev/null && sleep 1

mgba-qt -g -C audioSync=0 -C videoSync=0 -C fpsTarget=60 "$ROM" &
MGBA_PID=$!
trap 'kill $MGBA_PID 2>/dev/null; headless_display_stop' EXIT
sleep 5

WID=$(xdotool search --pid $MGBA_PID 2>/dev/null | tail -1)
[ -n "$WID" ] || { echo "mgba window not found"; exit 1; }
xdotool windowfocus --sync "$WID" 2>/dev/null
export MGBA_WID="$WID"

timeout 500 gdb-multiarch -batch -x "$HERE/wild_encounter_test.gdb" "$ELF" >"$LOG" 2>&1

kill $MGBA_PID 2>/dev/null
trap - EXIT
# the trap is disarmed above, so the private Xvfb must be stopped explicitly.
# Leaving it running squats the ":90 + PID%8" display the next run may allocate,
# which surfaces there as "mgba window not found" -- a hang, not a leak.
headless_display_stop

echo "--- log ---"
grep -aE "^phase1|^W[0-9]|^info:|TESTS DONE" "$LOG"
echo "-----------"

# Tally assertion lives in assert_tally.py -- one copy, and it now
# checks the NUMBER of checks, not just that each agrees with itself.
# The literal below is deliberate: see rowe_parity.md §9 Finding 2.
python3 "$(dirname "$0")/assert_tally.py" --expect 12 "$LOG"
