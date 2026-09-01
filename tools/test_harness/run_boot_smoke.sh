#!/bin/bash
# Boot smoke test for the patched ROM (see boot_smoke.gdb).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
. "$HERE/headless_display.sh"
ROM="$ROOT/build/unbound-cm.gba"
LOG="$ROOT/build/boot_smoke.log"

[ -f "$ROM" ] || { echo "patched ROM missing — run tools/build_patch.py first"; exit 1; }

pkill -f "mgba-qt -g .*unbound-cm\.gba" 2>/dev/null && sleep 1

mgba-qt -g -C audioSync=0 -C videoSync=0 -C fpsTarget=60 "$ROM" &
MGBA_PID=$!
trap 'kill $MGBA_PID 2>/dev/null; headless_display_stop' EXIT
sleep 5

timeout 90 gdb-multiarch -batch -x "$HERE/boot_smoke.gdb" >"$LOG" 2>&1

kill $MGBA_PID 2>/dev/null
trap - EXIT
# the trap is disarmed above, so the private Xvfb must be stopped explicitly.
# Leaving it running squats the ":90 + PID%8" display the next run may allocate,
# which surfaces there as "mgba window not found" -- a hang, not a leak.
headless_display_stop

echo "--- gdb output ---"
cat "$LOG"
echo "------------------"

# Tally assertion lives in assert_tally.py -- one copy, and it now
# checks the NUMBER of checks, not just that each agrees with itself.
# The literal below is deliberate: see rowe_parity.md §9 Finding 2.
python3 "$(dirname "$0")/assert_tally.py" --expect 4 "$LOG"
