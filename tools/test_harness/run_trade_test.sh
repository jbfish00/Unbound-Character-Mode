#!/bin/bash
# Live trade-enforcement test driver (see trade_test.gdb). Runs both cases
# on separate fresh saves: swept (off-roster incoming mon swept to PC) and
# stays (on-roster incoming mon stays). Both characters are DERIVED at build
# time from the roster blob -- the old red/bruno pair BOTH gained Hitmontop in
# the 2026-07-25 roster audit, and the test silently stopped discriminating.
# Usage:
#   tools/test_harness/run_trade_test.sh [swept|stays]  (default: both)
# Bash-only (uses $SECONDS, and set -u makes a wrong shell fail silently in
# a background subshell -- that is exactly how a dead key-masher once looked
# like a stuck trade scene). Re-exec under bash if invoked as `sh <script>`.
[ -n "${BASH_VERSION:-}" ] || exec bash "$0" "$@"
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
. "$HERE/headless_display.sh"
ROM="$ROOT/build/unbound-cm.gba"
ELF="$ROOT/build/character_mode.elf"

[ -f "$ROM" ] || { echo "patched ROM missing — run tools/build_patch.py first"; exit 1; }
[ -f "$ELF" ] || { echo "ELF missing — run tools/build_patch.py first"; exit 1; }

CASES="${1:-swept stays}"
OVERALL=0

for CASE in $CASES; do
    LOG="$ROOT/build/trade_test_$CASE.log"
    echo "=== trade test case: $CASE ==="
    rm -f "$ROOT/build/unbound-cm.sav"
    pkill -f "mgba-qt -g .*unbound-cm\.gba" 2>/dev/null && sleep 1

    mgba-qt -g -C audioSync=0 -C videoSync=0 -C fpsTarget=60 "$ROM" &
    MGBA_PID=$!
    MASH_PID=""
    trap 'kill $MGBA_PID $MASH_PID 2>/dev/null; headless_display_stop' EXIT
    sleep 5

    WID=$(xdotool search --pid $MGBA_PID 2>/dev/null | tail -1)
    [ -n "$WID" ] || { echo "mgba window not found"; exit 1; }
    xdotool windowfocus --sync "$WID" 2>/dev/null

    press() {
        xdotool keydown --window "$WID" "$1" 2>/dev/null
        sleep 0.1
        xdotool keyup --window "$WID" "$1" 2>/dev/null
    }
    # phase 1 is driven by the gdb script (intro_drive.py answers No at the
    # CM prompt deterministically). The trade-scene masher (the scene has
    # press-A prompts) starts only when the gdb script touches .mash_now
    # after queueing the trade script, and stops on .trade_done.
    export MGBA_WID="$WID"
    rm -f "$ROOT/build/.trade_done" "$ROOT/build/.mash_now"
    (
        while [ ! -f "$ROOT/build/.mash_now" ]; do sleep 0.5; done
        end=$((SECONDS + 220))
        while [ $SECONDS -lt $end ] && [ ! -f "$ROOT/build/.trade_done" ]; do
            press x
            sleep 0.4
        done
    ) &
    MASH_PID=$!

    TRADE_CASE="$CASE" timeout 600 gdb-multiarch -batch -x "$HERE/trade_test.gdb" "$ELF" >"$LOG" 2>&1

    kill $MASH_PID $MGBA_PID 2>/dev/null
    trap - EXIT

    echo "--- log ($CASE) ---"
    grep -av "^warning:" "$LOG" | grep -av "^0x\|SIGINT\|^$"
    echo "-------------------"

    # Tally assertion lives in assert_tally.py -- one copy, and it now
    # checks the NUMBER of checks, not just that each agrees with itself.
    # The literal is deliberate: see rowe_parity.md §9 Finding 2.
    python3 "$(dirname "$0")/assert_tally.py" --expect 8 "$LOG" || OVERALL=1
done

# The display is sourced ONCE above the case loop, so it is stopped once here --
# not inside the loop, which would tear it down before the second case runs.
# Without this the trap disarm at the end of each case leaks the Xvfb, and the
# next suite to allocate the same ":90 + PID%8" number reports "mgba window not
# found" -- which reads as a hang rather than as a leaked display.
headless_display_stop

exit $OVERALL
