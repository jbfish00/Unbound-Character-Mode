#!/bin/bash
# Organic intro-reach driver (see organic_intro.gdb): fresh save, blind
# x-masher (same pattern that reaches free-roam in the live-test harnesses),
# periodic F12 screenshots for visual evidence of the prompt.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
. "$HERE/headless_display.sh"
ROM="$ROOT/build/unbound-cm.gba"
LOG="$ROOT/build/organic_intro.log"

[ -f "$ROM" ] || { echo "patched ROM missing — run tools/build_patch.py first"; exit 1; }

rm -f "$ROOT/build/unbound-cm.sav" "$ROOT"/build/unbound-cm-*.png
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
(
    sleep 8
    i=0
    end=$((SECONDS + 240))
    while [ $SECONDS -lt $end ]; do
        i=$((i + 1))
        press x
        sleep 0.3
        if [ $((i % 12)) -eq 0 ]; then
            press F12   # screenshot -> build/unbound-cm-N.png
        fi
    done
) &
MASH_PID=$!

timeout 400 gdb-multiarch -batch -x "$HERE/organic_intro.gdb" >"$LOG" 2>&1

kill $MASH_PID $MGBA_PID 2>/dev/null
trap - EXIT

echo "--- log ---"
grep -av "^warning:" "$LOG" | grep -av "SIGINT\|^0x\|^$"
echo "-----------"
ls "$ROOT"/build/unbound-cm-*.png 2>/dev/null | head -5

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
