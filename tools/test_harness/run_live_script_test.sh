#!/bin/bash
# Live opt-in script test (see live_script_test.gdb). Fresh save, masher
# A-mashes through the opening cutscene into free-roam, then keeps answering
# whatever msgboxes appear after the gdb hijack queues the difficulty script.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
ROM="$ROOT/build/unbound-cm.gba"
ELF="$ROOT/build/character_mode.elf"
LOG="$ROOT/build/live_script_test.log"

[ -f "$ROM" ] || { echo "patched ROM missing — run tools/build_patch.py first"; exit 1; }
[ -f "$ELF" ] || { echo "ELF missing — run tools/build_patch.py first"; exit 1; }

rm -f "$ROOT/build/unbound-cm.sav"
pkill -f "mgba-qt -g .*unbound-cm\.gba" 2>/dev/null && sleep 1

mgba-qt -g "$ROM" &
MGBA_PID=$!
MASH_PID=""
trap 'kill $MGBA_PID $MASH_PID 2>/dev/null' EXIT
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
    while true; do
        press x
        sleep 0.3
    done
) &
MASH_PID=$!

timeout 500 gdb-multiarch -batch -x "$HERE/live_script_test.gdb" "$ELF" >"$LOG" 2>&1

kill $MASH_PID $MGBA_PID 2>/dev/null
trap - EXIT

echo "--- log ---"
grep -v "^warning:" "$LOG"
echo "-----------"

python3 - "$LOG" <<'EOF'
import re, sys
fails = 0
checks = 0
for line in open(sys.argv[1]):
    m = re.search(r"\(want (\d+)(?:=[a-z]+)?\): (\d+)", line)
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
