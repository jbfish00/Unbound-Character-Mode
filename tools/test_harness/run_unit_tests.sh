#!/bin/bash
# Run the GDB unit tests against the patched ROM in a live mgba-qt instance.
# Usage: tools/test_harness/run_unit_tests.sh
# Requires: mgba-qt (with GDB stub), gdb-multiarch, an X display.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
. "$HERE/headless_display.sh"
ROM="$ROOT/build/unbound-cm.gba"
ELF="$ROOT/build/character_mode.elf"
LOG="$ROOT/build/unit_tests.log"

[ -f "$ROM" ] || { echo "patched ROM missing — run tools/build_patch.py first"; exit 1; }
[ -f "$ELF" ] || { echo "ELF missing — run tools/build_patch.py first"; exit 1; }

# stale instance cleanup — scoped to OUR test ROM only, so a personal
# mgba-qt session is never touched
pkill -f "mgba-qt -g .*unbound-cm\.gba" 2>/dev/null && sleep 1

mgba-qt -g -C audioSync=0 -C videoSync=0 -C fpsTarget=60 "$ROM" &
MGBA_PID=$!
trap 'kill $MGBA_PID 2>/dev/null; headless_display_stop' EXIT
sleep 5   # let the stub open port 2345

# timeout guard: a wedged stub session must never hang the harness (v1 of
# this harness hung for hours on a gdb dummy-frame call — never again)
timeout 120 gdb-multiarch -batch -x "$HERE/unit_tests.gdb" "$ELF" >"$LOG" 2>&1
GDB_RC=$?
if ! grep -q "TESTS DONE" "$LOG"; then
    echo "first gdb attempt didn't finish; retrying once..."
    sleep 3
    timeout 120 gdb-multiarch -batch -x "$HERE/unit_tests.gdb" "$ELF" >"$LOG" 2>&1
    GDB_RC=$?
fi

kill $MGBA_PID 2>/dev/null
trap - EXIT

echo "--- gdb output ---"
cat "$LOG"
echo "------------------"

# assert every (want N) line printed exactly N
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
