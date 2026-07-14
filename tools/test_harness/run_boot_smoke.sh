#!/bin/bash
# Boot smoke test for the patched ROM (see boot_smoke.gdb).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
ROM="$ROOT/build/unbound-cm.gba"
LOG="$ROOT/build/boot_smoke.log"

[ -f "$ROM" ] || { echo "patched ROM missing — run tools/build_patch.py first"; exit 1; }

pkill -f "mgba-qt -g .*unbound-cm\.gba" 2>/dev/null && sleep 1

mgba-qt -g "$ROM" &
MGBA_PID=$!
trap 'kill $MGBA_PID 2>/dev/null' EXIT
sleep 5

timeout 90 gdb-multiarch -batch -x "$HERE/boot_smoke.gdb" >"$LOG" 2>&1

kill $MGBA_PID 2>/dev/null
trap - EXIT

echo "--- gdb output ---"
cat "$LOG"
echo "------------------"

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
