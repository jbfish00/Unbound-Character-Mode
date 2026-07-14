#!/bin/bash
# Automated intro playthrough: boots the patched ROM from a fresh save and
# mashes through the new-game intro with xdotool (XTEST -> focused window)
# while intro_probe.gdb watches EWRAM for the Character Mode opt-in flag.
#
# Key bindings read from ~/.config/mgba/config.ini [gba.input.QT_K]:
#   A=x  B=z  Start=q  Up=i  Down=k  Left=j  Right=l
# Mash pattern: A every ~0.35s answers msgboxes/yesno(Yes)/multichoice(first
# entry); a periodic Start handles the title screen and jumps name entry to
# OK. The opt-in prompt defaults to Yes, so an A-mash run should set flag
# 0x18F8 + var 0x51FC=1 if (and only if) the spliced script actually runs.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
ROM="$ROOT/build/unbound-cm.gba"
LOG="$ROOT/build/intro_playthrough.log"

[ -f "$ROM" ] || { echo "patched ROM missing — run tools/build_patch.py first"; exit 1; }
command -v xdotool >/dev/null || { echo "xdotool missing"; exit 1; }

rm -f "$ROOT/build/unbound-cm.sav"   # fresh save: main menu starts on NEW GAME
pkill -f "mgba-qt -g .*unbound-cm\.gba" 2>/dev/null && sleep 1

mgba-qt -g "$ROM" &
MGBA_PID=$!
MASH_PID=""
trap 'kill $MGBA_PID $MASH_PID 2>/dev/null' EXIT
sleep 5

WID=$(xdotool search --pid $MGBA_PID 2>/dev/null | tail -1)
[ -n "$WID" ] || { echo "mgba window not found"; exit 1; }
# no EWMH WM on this display: windowactivate fails, but XSendEvent with an
# explicit --window works focus-free (verified by keytest.gdb reading
# gMain.heldKeysRaw = 0x0001 while held). windowfocus as belt-and-braces.
xdotool windowfocus --sync "$WID" 2>/dev/null

# key masher (starts pressing ~8s after the probe's first `continue` unpauses
# the core). IMPORTANT: presses must be HELD ~0.1s — the GBA polls input once
# per frame (16.7ms), and xdotool's default down+up (~1ms apart) falls
# between polls and is never seen by the game.
press() {
    xdotool keydown --window "$WID" "$1" 2>/dev/null
    sleep 0.1
    xdotool keyup --window "$WID" "$1" 2>/dev/null
}
rm -f "$ROOT"/build/unbound-cm-*.png   # stale mGBA F12 screenshots
# hold a d-pad direction for a walk burst
walk() {
    xdotool keydown --window "$WID" "$1" 2>/dev/null
    sleep "$2"
    xdotool keyup --window "$WID" "$1" 2>/dev/null
}
(
    sleep 8
    # Unbound's opening is a scripted cutscene chain, then free-roam rooms
    # that need actual walking to reach the next trigger (the difficulty +
    # enhancement prompts come after the bedroom). Mix A-mashing (advances
    # dialogue/answers Yes) with directional sweeps (south-biased: exits).
    dirs=(k k j l k i k k j l k k)   # k=down j=left l=right i=up
    for i in $(seq 1 500); do
        press x
        sleep 0.25
        press x
        sleep 0.25
        press x
        sleep 0.25
        d=${dirs[$((i % 12))]}
        walk "$d" 0.9
        if [ $((i % 20)) -eq 0 ]; then
            press q
            sleep 0.25
        fi
        if [ $((i % 30)) -eq 0 ]; then
            press F12  # mGBA-native screenshot -> build/unbound-cm-N.png
        fi
    done
) &
MASH_PID=$!

timeout 800 gdb-multiarch -batch -x "$HERE/intro_probe.gdb" >"$LOG" 2>&1

kill $MASH_PID $MGBA_PID 2>/dev/null
trap - EXIT

echo "--- probe log ---"
grep -v "^warning:" "$LOG"
echo "-----------------"

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
