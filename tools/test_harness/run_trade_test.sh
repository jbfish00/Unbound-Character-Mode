#!/bin/bash
# Live trade-enforcement test driver (see trade_test.gdb). Runs both cases
# on separate fresh saves: red (off-roster incoming mon swept to PC) and
# bruno (on-roster incoming mon stays). Usage:
#   tools/test_harness/run_trade_test.sh [red|bruno]   (default: both)
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
. "$HERE/headless_display.sh"
ROM="$ROOT/build/unbound-cm.gba"
ELF="$ROOT/build/character_mode.elf"

[ -f "$ROM" ] || { echo "patched ROM missing — run tools/build_patch.py first"; exit 1; }
[ -f "$ELF" ] || { echo "ELF missing — run tools/build_patch.py first"; exit 1; }

CASES="${1:-red bruno}"
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

    python3 - "$LOG" <<'EOF' || OVERALL=1
import re, sys
fails = 0
checks = 0
for line in open(sys.argv[1], errors="replace"):
    m = re.search(r"\(want (\d+)\): (\d+)", line)
    if m:
        checks += 1
        if m.group(1) != m.group(2):
            print(f"FAIL: {line.strip()}")
            fails += 1
if checks == 0:
    print("NO CHECKS RAN — gdb session failed?")
    sys.exit(2)
print(f"{checks - fails}/{checks} checks passed")
sys.exit(1 if fails else 0)
EOF
done

exit $OVERALL
