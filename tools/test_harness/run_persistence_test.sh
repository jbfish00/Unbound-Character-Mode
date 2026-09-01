#!/bin/bash
# Flag-persistence driver: phase A saves in-game (hijacked TrySavingData)
# with Character Mode state set; phase B reboots the emulator on the same
# .sav and verifies the state survived. See persistence_test.gdb /
# persistence_load.gdb.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
. "$HERE/headless_display.sh"
ROM="$ROOT/build/unbound-cm.gba"
ELF="$ROOT/build/character_mode.elf"
SAV="$ROOT/build/unbound-cm.sav"
LOGA="$ROOT/build/persistence_a.log"
LOGB="$ROOT/build/persistence_b.log"

[ -f "$ROM" ] || { echo "patched ROM missing — run tools/build_patch.py first"; exit 1; }
[ -f "$ELF" ] || { echo "ELF missing"; exit 1; }

rm -f "$SAV"
pkill -f "mgba-qt -g .*unbound-cm\.gba" 2>/dev/null && sleep 1

launch() {
    mgba-qt -g -C audioSync=0 -C videoSync=0 -C fpsTarget=60 "$ROM" &
    MGBA_PID=$!
    sleep 5
    WID=$(xdotool search --pid $MGBA_PID 2>/dev/null | tail -1)
    [ -n "$WID" ] || { echo "mgba window not found"; exit 1; }
    xdotool windowfocus --sync "$WID" 2>/dev/null
    export MGBA_WID="$WID"
}

# ---- phase A: fresh save -> free-roam -> set state -> in-game save ----
launch
trap 'kill $MGBA_PID 2>/dev/null; headless_display_stop' EXIT
timeout 500 gdb-multiarch -batch -x "$HERE/persistence_test.gdb" "$ELF" >"$LOGA" 2>&1
kill $MGBA_PID 2>/dev/null   # SIGTERM: mgba flushes the .sav on clean exit
sleep 3

echo "--- phase A ---"
grep -av "^warning:" "$LOGA" | grep -av "SIGINT\|^0x\|^$"
[ -s "$SAV" ] || { echo "FAIL: no .sav written"; headless_display_stop; exit 1; }
echo ".sav present: $(stat -c%s "$SAV") bytes"

# ---- phase B: reboot on the saved file -> CONTINUE -> verify ----
launch
trap 'kill $MGBA_PID 2>/dev/null; headless_display_stop' EXIT
timeout 200 gdb-multiarch -batch -x "$HERE/persistence_load.gdb" >"$LOGB" 2>&1
kill $MGBA_PID 2>/dev/null
trap - EXIT
headless_display_stop

echo "--- phase B ---"
grep -av "^warning:" "$LOGB" | grep -av "SIGINT\|^0x\|^$"

# Tally assertion lives in assert_tally.py -- one copy, and it now
# checks the NUMBER of checks, not just that each agrees with itself.
# The literal is deliberate: see rowe_parity.md §9 Finding 2.
python3 "$(dirname "$0")/assert_tally.py" --expect 9 "$LOGA" "$LOGB"
