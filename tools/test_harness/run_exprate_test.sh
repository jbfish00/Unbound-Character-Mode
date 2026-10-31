#!/bin/bash
# LIVE layer: EXP rate (2026-10-30, src/exp_rate.c; ../game_plans/EXP_RATE_PLAN.md).
# Battle: from the free-roam checkpoint (CM off: the rate works in every save), cm_exp_share_party_test.lua runs the
# same KO (Pikachu L5 lead Tackles a wild Magikarp at 1 HP, Caterpie L5 benched through Unbound's native party-wide
# share) at every rate. The x1 run's gains give the others: award * N / 2 (N = 2 3 4 6 1 for var 0..4), never 0.
#   CM_NO_EXPRATE=1 build at rate 2 -> the x1 gains (the control); asked for the x2 gains it must FAIL (negative).
# Menu: cm_exprate_menu_test.lua drives START > Extras (record 6) > Exp. Rate with CM off and on, and the Roster and
# B paths of the Extras list; on a copy with the builder's case-6 byte put back to "skip" the CM-off run must FAIL.
set -u
[ -z "${BASH_VERSION:-}" ] && exec bash "$0" "$@"
cd "$(dirname "$0")/../.." || exit 1
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
export CM_CHECKPOINT=${CM_CHECKPOINT:-/tmp/ub_ss_field.ss}
ROM=build/unbound-cm.gba
CTL=build/unbound-cm_noexprate.gba
NEG=build/unbound-cm_exprate_no_row.gba
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh'"; exit 2; }
CM_NO_EXPRATE=1 python3 tools/build_patch.py >/dev/null || { echo "  FAIL control build"; exit 1; }
cp "$ROM" "$CTL"
python3 tools/build_patch.py >/dev/null || { echo "  FAIL shipping build"; exit 1; }
python3 - <<'EOF' || exit 1
import sys
sys.path.insert(0, "tools")
import build_patch as bp
d = bytearray(open("build/unbound-cm.gba", "rb").read())
assert d[bp.START_CASE6_OFF] == bp.START_CASE6_APPEND, "shipped build does not append row 6"
d[bp.START_CASE6_OFF] = bp.START_CASE6_ORIG
open("build/unbound-cm_exprate_no_row.gba", "wb").write(bytes(d))
EOF
# The checkpoint embeds RAM that points into the injected code: remake it whenever the ROM is newer.
if [ ! -f "$CM_CHECKPOINT" ] || [ "$ROM" -nt "$CM_CHECKPOINT" ]; then
    echo "making the free-roam checkpoint (~5 min)..."
    rm -f "$CM_CHECKPOINT"
    timeout 1500 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_field.lua "$ROM" > /tmp/ub_er_checkpoint.log 2>&1
    [ -f "$CM_CHECKPOINT" ] || { echo "  FAIL no free-roam checkpoint"; exit 1; }
fi
sym() { printf '0x%s' "$(arm-none-eabi-nm build/character_mode.elf | awk -v s="$1" '$3 == s {print $1}')"; }
QUEUE=$(( $(sym CharacterMode_QueueScriptCb1) | 1 ))
EXPECT_CASES=14
pass=0; fail=0
ok() { echo "[PASS] $1"; pass=$((pass+1)); }
bad() { echo "[FAIL] $1"; fail=$((fail+1)); }

battle() {  # label rom rate [WANT_GAIN0 WANT_GAIN1]
    log=/tmp/ub_er_$1.log
    n=3; [ -n "${4:-}" ] && n=5
    env QUEUE_CB1=$QUEUE EXPECT=share RATE=$3 LEAD_LV=5 CM_EXPECT_CHECKS=$n ${4:+WANT_GAIN0=$4} ${5:+WANT_GAIN1=$5} \
        timeout 120 "$MGBA" --script tools/mgba_scripts/cm_exp_share_party_test.lua -t "$CM_CHECKPOINT" "$2" > "$log" 2>&1
    grep -ao "GAINS [0-9-]* [0-9-]*" "$log" | head -1 | sed "s/^/  $1: /"
    grep -aq "EXPSHARE RESULT: PASS" "$log"
}
if battle x1 $ROM 0; then ok "x1 baseline"; else bad "x1 baseline (/tmp/ub_er_x1.log)"; fi
G0=$(grep -ao "GAINS [0-9]* [0-9]*" /tmp/ub_er_x1.log | head -1 | cut -d' ' -f2)
G1=$(grep -ao "GAINS [0-9]* [0-9]*" /tmp/ub_er_x1.log | head -1 | cut -d' ' -f3)
[ -n "$G0" ] && [ "$G0" -ge 2 ] && [ -n "$G1" ] && [ "$G1" -ge 2 ] || { echo "no usable x1 gains ($G0 $G1)"; exit 1; }
want() { python3 -I -c "g=$1*$2//2; print(g if g else 1)"; }
for rn in "2 4 x2" "4 1 x0_5" "3 6 x3" "1 3 x1_5"; do
    set -- $rn
    if battle $3 $ROM $1 $(want $G0 $2) $(want $G1 $2); then ok "$3"; else bad "$3 (/tmp/ub_er_$3.log)"; fi
done
if battle ctl $CTL 2 $G0 $G1; then ok "control: CM_NO_EXPRATE at rate 2 gains the x1 amounts"; else bad "control (/tmp/ub_er_ctl.log)"; fi
if battle neg $CTL 2 $(want $G0 4) $(want $G1 4); then bad "NEGATIVE CONTROL: CM_NO_EXPRATE still gained x2"
else ok "negative control: CM_NO_EXPRATE fails the x2 amounts (want FAIL)"; fi

export EXTRAS_INPUT=$(sym Extras_HandleInput) RATE_INPUT=$(sym ExpRate_HandleInput) ROSTER_INPUT=$(sym RosterMenu_HandleInput)
export MGBA_HEADLESS_DEBUGGER=1 CM_CHAR=10
menu() {  # label rom mode start_rate extras_keys list_keys want_next want_rate checks
    log=/tmp/ub_er_ui_$1.log
    MODE=$3 START_RATE=$4 EXTRAS_KEYS=$5 LIST_KEYS=$6 WANT_NEXT=$7 WANT_RATE=$8 CM_EXPECT_CHECKS=$9 SHOTS=build/exprate_$1 \
        timeout 240 "$MGBA" --script tools/mgba_scripts/cm_exprate_menu_test.lua "$2" > "$log" 2>&1
    grep -aq "HARNESS RESULT: PASS" "$log"
}
if menu off_down2 $ROM off 0 "" "DOWN,DOWN,A" rate 2 5; then ok "CM off: Extras opens the chooser, x1 DOWN DOWN A -> x2"
else bad "CM off chooser (/tmp/ub_er_ui_off_down2.log)"; fi
if menu on_up $ROM on 0 "DOWN,A" "UP,A" rate 4 6; then ok "CM on: Extras > Exp. Rate, x1 UP A -> x0.5"
else bad "CM on chooser (/tmp/ub_er_ui_on_up.log)"; fi
if menu on_keep $ROM on 3 "DOWN,A" "A" rate 3 6; then ok "CM on: the cursor starts on the current rate (x3, A keeps 3)"
else bad "CM on preselect (/tmp/ub_er_ui_on_keep.log)"; fi
if menu on_cancel $ROM on 3 "DOWN,A" "UP,B" rate 3 6; then ok "CM on: B in the chooser keeps the rate"
else bad "CM on cancel (/tmp/ub_er_ui_on_cancel.log)"; fi
if menu on_roster $ROM on 0 "A" "" roster 0 5; then ok "CM on: Extras > Roster opens the roster screen"
else bad "CM on roster (/tmp/ub_er_ui_on_roster.log)"; fi
if menu on_b $ROM on 0 "B" "" field 0 5; then ok "CM on: B in Extras gives the field back"
else bad "CM on Extras B (/tmp/ub_er_ui_on_b.log)"; fi
if menu NEG_no_row $NEG off 0 "" "DOWN,DOWN,A" rate 2 5; then bad "NEGATIVE CONTROL: case 6 skipped still passed"
else ok "negative control: no Extras row fails the CM-off run (want FAIL)"; fi
echo "EXP rate live: $pass passed, $fail failed (want $EXPECT_CASES)"
[ "$fail" -eq 0 ] && [ $((pass+fail)) -eq "$EXPECT_CASES" ]
