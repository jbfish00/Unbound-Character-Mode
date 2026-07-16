#!/bin/bash
# Live catch-gate test driver (see scroll_select_test.gdb). Phase-1 masher
# plays to free-roam, then the gdb script takes over ALL input (choreographed
# presses), so the masher is killed before the injection.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
. "$HERE/headless_display.sh"
ROM="$ROOT/build/unbound-cm.gba"
ELF="$ROOT/build/character_mode.elf"
LOG="$ROOT/build/scroll_select_test.log"

[ -f "$ROM" ] || { echo "patched ROM missing"; exit 1; }
[ -f "$ELF" ] || { echo "ELF missing"; exit 1; }

rm -f "$ROOT/build/unbound-cm.sav" "$ROOT"/build/unbound-cm-*.png
pkill -f "mgba-qt -g .*unbound-cm\.gba" 2>/dev/null && sleep 1

mgba-qt -g "$ROM" &
MGBA_PID=$!
MASH_PID=""
trap 'kill $MGBA_PID $MASH_PID 2>/dev/null; headless_display_stop' EXIT
sleep 5

WID=$(xdotool search --pid $MGBA_PID 2>/dev/null | tail -1)
[ -n "$WID" ] || { echo "mgba window not found"; exit 1; }
xdotool windowfocus --sync "$WID" 2>/dev/null
export MGBA_WID="$WID"

press() {
    xdotool keydown --window "$WID" "$1" 2>/dev/null
    sleep 0.1
    xdotool keyup --window "$WID" "$1" 2>/dev/null
}
(
    sleep 8
    end=$((SECONDS + 168))
    while [ $SECONDS -lt $end ]; do
        press x
        sleep 0.3
    done
) &
MASH_PID=$!

timeout 420 gdb-multiarch -batch -x "$HERE/scroll_select_test.gdb" "$ELF" >"$LOG" 2>&1

kill $MASH_PID $MGBA_PID 2>/dev/null
trap - EXIT

echo "--- log ---"
grep -av "^warning:" "$LOG" | grep -av "^0x\|SIGINT\|^$"
echo "-----------"
ls "$ROOT"/build/unbound-cm-*.png 2>/dev/null
