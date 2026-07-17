#!/bin/bash
# Live starter-grant test driver (see starter_test.gdb). Phase-1 masher
# plays to free-roam, then the gdb script queues the ROM-baked starter
# debug script and reads the party back.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
. "$HERE/headless_display.sh"
ROM="$ROOT/build/unbound-cm.gba"
ELF="$ROOT/build/character_mode.elf"
LOG="$ROOT/build/starter_test.log"

[ -f "$ROM" ] || { echo "patched ROM missing"; exit 1; }
[ -f "$ELF" ] || { echo "ELF missing"; exit 1; }

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
export MGBA_WID="$WID"

# phase 1 is driven entirely by the gdb script (intro_drive.py answers No
# at the CM prompt deterministically) — no background masher
MASH_PID=""

timeout 500 gdb-multiarch -batch -x "$HERE/starter_test.gdb" "$ELF" >"$LOG" 2>&1

kill $MASH_PID $MGBA_PID 2>/dev/null
trap - EXIT

echo "--- log ---"
grep -av "^warning:" "$LOG" | grep -av "^0x\|SIGINT\|^$"
echo "-----------"

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
