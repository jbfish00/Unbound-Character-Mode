#!/bin/bash
# Live driver for the playability-threshold gate (see gate_test.gdb).
# Runs BOTH cases by default -- the "shown" control is what stops "the script
# did not reach the confirm prompt" from passing when the gate rejects
# everything. Pass a case name to run just one: hidden | shown
[ -n "${BASH_VERSION:-}" ] || exec bash "$0" "$@"
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
export CM_MANIFEST="$ROOT/tools/character_mode/characters_manifest.json"

. "$HERE/headless_display.sh"
ROM="$ROOT/build/unbound-cm.gba"
ELF="$ROOT/build/character_mode.elf"

[ -f "$ROM" ] || { echo "patched ROM missing — run tools/build_patch.py first"; headless_display_stop; exit 1; }
[ -f "$ELF" ] || { echo "ELF missing"; headless_display_stop; exit 1; }

CASES="${1:-hidden shown}"
OVERALL=0

for CASE in $CASES; do
    LOG="$ROOT/build/gate_test_$CASE.log"
    echo "=== threshold gate case: $CASE ==="
    rm -f "$ROOT/build/unbound-cm.sav"
    pkill -f "mgba-qt -g .*unbound-cm\.gba" 2>/dev/null && sleep 1

    mgba-qt -g -C audioSync=0 -C videoSync=0 -C fpsTarget=60 "$ROM" &
    MGBA_PID=$!
    trap 'kill $MGBA_PID 2>/dev/null; headless_display_stop' EXIT
    sleep 5

    WID=$(xdotool search --pid $MGBA_PID 2>/dev/null | tail -1)
    [ -n "$WID" ] || { echo "mgba window not found"; kill $MGBA_PID 2>/dev/null; headless_display_stop; exit 1; }
    xdotool windowfocus --sync "$WID" 2>/dev/null
    export MGBA_WID="$WID"

    TEST_CASE="$CASE" timeout 600 gdb-multiarch -batch -x "$HERE/gate_test.gdb" "$ELF" >"$LOG" 2>&1
    kill $MGBA_PID 2>/dev/null
    trap - EXIT

    echo "--- log ($CASE) ---"
    grep -av "^warning:" "$LOG" | grep -av "^0x\|SIGINT\|^$"
    echo "-------------------"

    # Tally assertion lives in assert_tally.py -- one copy, and it now checks
    # the NUMBER of checks, not just that each agrees with itself.
    # ⚠️ PER CASE, not one number for the runner. This loop runs each case with
    # its own log and the cases do not run the same number of checks (hidden
    # asserts one more than shown). A single literal here reported a tally
    # mismatch on the case that was fine, and measuring the runner by tailing
    # its output for the last "N/N passed" line silently sampled only the last
    # case. A runner that loops needs a count per iteration.
    case "$CASE" in
        hidden) EXPECT=8 ;;
        shown)  EXPECT=7 ;;
        *) echo "no expected check count declared for case '$CASE' -- add one"
           OVERALL=1; continue ;;
    esac
    python3 "$(dirname "$0")/assert_tally.py" --expect "$EXPECT" "$LOG" || OVERALL=1
done

# The display is sourced once above the case loop, so it is stopped once here.
headless_display_stop

exit $OVERALL
