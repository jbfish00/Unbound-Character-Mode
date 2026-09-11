#!/bin/bash
# LIVE PC-exit test driver (see pc_exit_test.gdb).
# ../game_plans/rowe_parity.md §13.33 item 1: the PC-exit hook shipped in all
# four GBA games on STATIC evidence alone. Seaglass got the first live layer on
# 2026-09-10, Radical Red and Lazarus followed, and this is the port to the one
# repo with no Lua harness -- here it is GDB over the mGBA stub.
#
# Three runs: swept (off-roster mon boxed when the PC closes), stays (on-roster
# mon kept -- the discriminating control), and nohook, which runs the identical
# script against a ROM with all four PC splices reverted and MUST FAIL. Without
# that third run the layer proves the sweep works when something calls it and
# says nothing about whether CLOSING THE PC calls it.
#
# Both characters are DERIVED at build time from the roster blob, exactly as the
# trade test's are, and for the same reason: a hardcoded pair silently stopped
# discriminating once a roster audit moved a species.
#
# Usage: tools/test_harness/run_pc_exit_test.sh [swept|stays|nohook]
#
# ⚠️ Bash-only ($SECONDS, and set -u makes a wrong shell fail silently in a
# background subshell -- that is exactly how a dead key-masher once looked like
# a stuck scene). Re-exec under bash if invoked as `sh <script>`.
[ -n "${BASH_VERSION:-}" ] || exec bash "$0" "$@"
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
. "$HERE/headless_display.sh"
ELF="$ROOT/build/character_mode.elf"

[ -f "$ROOT/build/unbound-cm.gba" ] || { echo "patched ROM missing — run tools/build_patch.py first"; exit 1; }
[ -f "$ELF" ] || { echo "ELF missing — run tools/build_patch.py first"; exit 1; }

python3 "$ROOT/tools/tests/build_pc_testrom.py" || exit 1

CASES="${1:-swept stays nohook}"
OVERALL=0

for CASE in $CASES; do
    LOG="$ROOT/build/pc_exit_test_$CASE.log"
    echo "=== PC-exit test case: $CASE ==="
    # nohook runs the SWEPT fixture against the unhooked ROM: same script, same
    # character, same expectations -- and every roster assertion must fail.
    if [ "$CASE" = nohook ]; then
        ROM="$ROOT/build/unbound-cm-pcnohook.gba"; GDBCASE=swept
    else
        ROM="$ROOT/build/unbound-cm.gba"; GDBCASE="$CASE"
    fi
    rm -f "$ROOT/build/unbound-cm.sav" "$ROOT/build/unbound-cm-pcnohook.sav"
    pkill -f "mgba-qt -g .*unbound-cm.*\.gba" 2>/dev/null && sleep 1

    mgba-qt -g -C audioSync=0 -C videoSync=0 -C fpsTarget=60 "$ROM" &
    MGBA_PID=$!
    MASH_PID=""
    trap 'kill $MGBA_PID $MASH_PID 2>/dev/null; headless_display_stop' EXIT
    sleep 5

    WID=$(xdotool search --pid $MGBA_PID 2>/dev/null | tail -1)
    [ -n "$WID" ] || { echo "mgba window not found"; exit 1; }
    xdotool windowfocus --sync "$WID" 2>/dev/null

    # ⚠️ A LONGER hold than the trade test's 0.1 s. The gdb stub samples
    # heldKeysRaw only at the instants it halts, and this menu closes on the
    # FIRST press, so a short blip is easy to miss entirely -- which reads as a
    # dead masher on a run that plainly had one.
    press() {
        xdotool keydown --window "$WID" "$1" 2>/dev/null
        sleep 0.25
        xdotool keyup --window "$WID" "$1" 2>/dev/null
    }
    export MGBA_WID="$WID"
    rm -f "$ROOT/build/.pc_done" "$ROOT/build/.mash_now"
    # ⚠️ z, NOT x. mGBA's default keymap is A=x, B=z, and this masher must press
    # B: B backs out of the storage system, where A would dive INTO a box and
    # the run would sit there until the poll gives up.
    (
        while [ ! -f "$ROOT/build/.mash_now" ]; do sleep 0.5; done
        end=$((SECONDS + 220))
        while [ $SECONDS -lt $end ] && [ ! -f "$ROOT/build/.pc_done" ]; do
            press z
            sleep 0.15
        done
    ) &
    MASH_PID=$!

    PC_CASE="$GDBCASE" timeout 600 gdb-multiarch -batch -x "$HERE/pc_exit_test.gdb" "$ELF" >"$LOG" 2>&1

    kill $MASH_PID $MGBA_PID 2>/dev/null
    trap - EXIT

    echo "--- log ($CASE) ---"
    grep -av "^warning:" "$LOG" | grep -av "^0x\|SIGINT\|^$"
    echo "-------------------"

    if [ "$CASE" = nohook ]; then
        # ⭐ THE NEGATIVE CONTROL, and it must fail for the RIGHT reason: the
        # mon stays in the party because nothing swept it. Requiring merely
        # "the tally failed" would also be satisfied by a crash, a dead masher
        # or a missing ROM, none of which say anything about the hook.
        if grep -aq "T5 off-roster Hitmontop out of party (want 1): 0" "$LOG" \
           && grep -aq "T6 Hitmontop delivered to PC storage (want 1): 0" "$LOG" \
           && grep -aq "T2b the PC held the script open with no input (want 1): 1" "$LOG"; then
            echo "[PASS] PC exit NEGATIVE CONTROL (hook absent -> the mon is NOT swept)"
        else
            echo "[FAIL] negative control did not fail, or failed for another reason"
            OVERALL=1
        fi
    else
        python3 "$HERE/assert_tally.py" --expect 10 "$LOG" || OVERALL=1
    fi
done

headless_display_stop
exit $OVERALL
