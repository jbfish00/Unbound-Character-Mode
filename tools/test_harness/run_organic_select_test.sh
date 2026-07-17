#!/bin/bash
# Full organic character-select driver (see organic_select.gdb): the gdb
# script drives every key press itself (verified presses), so no masher.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
. "$HERE/headless_display.sh"
ROM="$ROOT/build/unbound-cm.gba"
LOG="$ROOT/build/organic_select.log"

[ -f "$ROM" ] || { echo "patched ROM missing — run tools/build_patch.py first"; exit 1; }

rm -f "$ROOT/build/unbound-cm.sav" "$ROOT"/build/unbound-cm-*.png
pkill -f "mgba-qt -g .*unbound-cm\.gba" 2>/dev/null && sleep 1

mgba-qt -g -C audioSync=0 -C videoSync=0 -C fpsTarget=60 "$ROM" &
MGBA_PID=$!
trap 'kill $MGBA_PID 2>/dev/null; headless_display_stop' EXIT
sleep 5

WID=$(xdotool search --pid $MGBA_PID 2>/dev/null | tail -1)
[ -n "$WID" ] || { echo "mgba window not found"; exit 1; }
xdotool windowfocus --sync "$WID" 2>/dev/null
export MGBA_WID="$WID"

# background typer: when the gdb script touches .type_now (number screen up,
# core running uninterrupted for ~14s), type '1', OK, confirm with clean
# wall-clock timing — no gdb stops in between (the screen garbles sliced
# input). Repeats for validation-loop re-asks.
rm -f "$ROOT/build/.type_now"
press_hold() {
    xdotool keydown --window "$WID" "$1" 2>/dev/null
    sleep 0.12
    xdotool keyup --window "$WID" "$1" 2>/dev/null
}
(
    while true; do
        [ -f "$ROOT/build/.type_now" ] || { sleep 0.3; continue; }
        rm -f "$ROOT/build/.type_now"
        sleep 2.5                     # screen fade-in
        press_hold F12
        press_hold l;  sleep 0.5      # cursor '0' -> '1'
        press_hold x;  sleep 0.5      # type '1'
        press_hold F12
        press_hold q;  sleep 0.5      # Start -> OK
        press_hold x;  sleep 0.5      # confirm number
        press_hold F12
    done
) &
TYPER_PID=$!
trap 'kill $MGBA_PID $TYPER_PID 2>/dev/null; headless_display_stop' EXIT

timeout 700 gdb-multiarch -batch -x "$HERE/organic_select.gdb" >"$LOG" 2>&1
kill $TYPER_PID 2>/dev/null

kill $MGBA_PID 2>/dev/null
trap - EXIT

echo "--- log ---"
grep -av "^warning:" "$LOG" | grep -av "SIGINT\|^0x\|^$"
echo "-----------"
ls "$ROOT"/build/unbound-cm-*.png 2>/dev/null | tail -3

python3 - "$LOG" <<'EOF'
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
