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

# The display is sourced once above the case loop, so it is stopped once here.
headless_display_stop

exit $OVERALL
