#!/bin/bash
# LIVE layer (QoL B9, 2026-11-08): the wild-intro roster hint in a real battle
# (CharacterMode_MarkedIntro; tools/mgba_scripts/cm_intro_hint_test.lua). Wild Snorlax,
# on Red's roster (1), off Leaf's (2).
#   shipped, Red          -> "destined for RED"
#   shipped, Leaf         -> "It is not on your roster."
#   shipped, CM off       -> vanilla
#   CM_NO_OFFROSTER, Leaf -> vanilla (the discriminating control)
#   CM_NO_OFFROSTER, Leaf, asked for the off-roster line -> must FAIL (negative control)
set -u
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
STATE=${CM_CHECKPOINT:-/tmp/ub_ss_field.ss}
ROM=build/unbound-cm.gba
CTRL=build/unbound-cm-nooffroster.gba
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh'"; exit 2; }
[ -f "$ROM" ] || { echo "build first: python3 tools/build_patch.py"; exit 1; }
CM_NO_OFFROSTER=1 python3 tools/build_patch.py >/dev/null 2>&1 || { echo "control build failed"; exit 1; }
cp "$ROM" "$CTRL"
CTRL_QUEUE=$(( 0x$(arm-none-eabi-nm build/character_mode.elf | awk '/ CharacterMode_QueueScriptCb1$/{print $1}') | 1 ))
python3 tools/build_patch.py >/dev/null 2>&1 || { echo "shipping build failed"; exit 1; }
QUEUE=$(( 0x$(arm-none-eabi-nm build/character_mode.elf | awk '/ CharacterMode_QueueScriptCb1$/{print $1}') | 1 ))
if [ ! -f "$STATE" ]; then
    CM_CHECKPOINT="$STATE" timeout 900 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_field.lua "$ROM" \
        > /tmp/ub_hint_checkpoint.log 2>&1 || true
    [ -f "$STATE" ] || { echo "  FAIL no free-roam checkpoint"; exit 1; }
fi
EXPECT_CASES=5
pass=0; fail=0
hint_case() {  # name rom queue CM_ON CM_CHAR EXPECT
    log=/tmp/ub_hint_$1.log
    MGBA_HEADLESS_DEBUGGER=1 QUEUE_CB1=$3 CM_EXPECT_CHECKS=2 CM_ON=$4 CM_CHAR=$5 EXPECT=$6 \
        timeout 150 "$MGBA" --script tools/mgba_scripts/cm_intro_hint_test.lua -t "$STATE" "$2" > "$log" 2>&1
    grep -a "HINT intro r0=" "$log" | sed 's/^/  /'
    grep -aq "HINT RESULT: PASS" "$log"
}
ok()  { echo "[PASS] $1"; pass=$((pass+1)); }
bad() { echo "[FAIL] $1"; fail=$((fail+1)); }
if hint_case red "$ROM" $QUEUE 1 1 marker; then ok "Red: on-roster Snorlax is 'destined for RED'"; else bad "Red marker (/tmp/ub_hint_red.log)"; fi
if hint_case leaf "$ROM" $QUEUE 1 2 offroster; then ok "Leaf: off-roster Snorlax says 'It is not on your roster.'"; else bad "Leaf off-roster line (/tmp/ub_hint_leaf.log)"; fi
if hint_case off "$ROM" $QUEUE 0 2 vanilla; then ok "CM off: vanilla intro"; else bad "CM off (/tmp/ub_hint_off.log)"; fi
if hint_case nooff "$CTRL" $CTRL_QUEUE 1 2 vanilla; then ok "CM_NO_OFFROSTER control: Leaf gets the vanilla intro"; else bad "control (/tmp/ub_hint_nooff.log)"; fi
if hint_case nooffneg "$CTRL" $CTRL_QUEUE 1 2 offroster; then bad "NEGATIVE CONTROL: CM_NO_OFFROSTER passed 'offroster'"
else ok "negative control: CM_NO_OFFROSTER fails 'offroster' (want FAIL)"; fi
echo "intro hint live: $pass passed, $fail failed (want $EXPECT_CASES)"
[ "$fail" -eq 0 ] && [ $((pass+fail)) -eq "$EXPECT_CASES" ]
