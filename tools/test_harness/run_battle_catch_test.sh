#!/bin/bash
# Live catch-gate test driver (see battle_catch_test.gdb). Phase-1 masher
# plays to free-roam, then the gdb script takes over ALL input (choreographed
# presses), so the masher is killed before the injection.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
# the gdb side DERIVES its wild species from character 1's own injected roster
export CM_MANIFEST="$ROOT/tools/character_mode/characters_manifest.json"

. "$HERE/headless_display.sh"
ROM="$ROOT/build/unbound-cm.gba"
ELF="$ROOT/build/character_mode.elf"
LOG="$ROOT/build/battle_catch_test.log"

[ -f "$ROM" ] || { echo "patched ROM missing"; exit 1; }
[ -f "$ELF" ] || { echo "ELF missing"; exit 1; }

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
export MGBA_WID="$WID"

# phase 1 is driven entirely by the gdb script (intro_drive.py answers No
# at the CM prompt deterministically) — no background masher
MASH_PID=""

timeout 520 gdb-multiarch -batch -x "$HERE/battle_catch_test.gdb" "$ELF" >"$LOG" 2>&1

kill $MASH_PID $MGBA_PID 2>/dev/null
trap - EXIT
# the trap is disarmed above, so the private Xvfb must be stopped explicitly.
# Leaving it running squats the ":90 + PID%8" display the next run may allocate,
# which surfaces there as "mgba window not found" -- a hang, not a leak.
headless_display_stop

echo "--- log ---"
grep -av "^warning:" "$LOG" | grep -av "^0x\|SIGINT\|^$"
echo "-----------"
ls "$ROOT"/build/unbound-cm-*.png 2>/dev/null

# The verdict used to be `ls` -- i.e. this suite structurally could not fail.
# It guards the CATCH GATE, the core enforcement feature, and a gdb session that
# died before printing a single check still exited 0 as long as a screenshot
# existed. Same assertion phase every other runner here uses, including the
# checks==0 guard that turns "the harness never ran" into a failure rather than
# a pass.
python3 - "$LOG" <<'PYEOF'
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
PYEOF
