#!/bin/bash
# LIVE layer (QoL A3, 2026-10-28): new games -- every game, existing saves too, since it is code -- get an instant HP
# bar (tools/build_patch.py instant_hp: CFRU's MoveBattleBar tail passes scale 0 / toAdd 255). From the free-roam
# checkpoint, cm_exp_share_party_test.lua runs its real wild battle (Pikachu L50 Tackle KOs a Magikarp L2; WANT_HPBAR
# leaves the wild HP alone so a full bar drains) and counts the frames MoveBattleBar(HEALTH_BAR) runs per bar update.
#   shipped                              -> instant (<= 4 frames an update)
#   CM_NO_INSTANTHP=1 build              -> animated (the discriminating control)
#   CM_NO_INSTANTHP, asked for instant   -> must FAIL (the negative control)
set -u
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
STATE=${CM_CHECKPOINT:-/tmp/ub_ss_field.ss}
ROM=build/unbound-cm.gba
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh'"; exit 2; }
CM_NO_INSTANTHP=1 python3 tools/build_patch.py >/dev/null || { echo "  FAIL control build"; exit 1; }
cp "$ROM" build/unbound-cm_nohp.gba
python3 tools/build_patch.py >/dev/null || { echo "  FAIL shipping build"; exit 1; }
if [ ! -f "$STATE" ]; then
    CM_CHECKPOINT="$STATE" timeout 900 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_field.lua "$ROM" \
        > /tmp/ub_exp_checkpoint.log 2>&1 || true
    [ -f "$STATE" ] || { echo "  FAIL no free-roam checkpoint"; exit 1; }
fi
QUEUE=$(( 0x$(arm-none-eabi-nm build/character_mode.elf | awk '/ CharacterMode_QueueScriptCb1$/{print $1}') | 1 ))
EXPECT_CASES=3
pass=0; fail=0
hp_case() {  # name rom WANT_HPBAR
    log=/tmp/ub_hp_$1.log
    MGBA_HEADLESS_DEBUGGER=1 QUEUE_CB1=$QUEUE EXPECT=share WANT_HPBAR=$3 CM_EXPECT_CHECKS=4 \
        timeout 120 "$MGBA" --script tools/mgba_scripts/cm_exp_share_party_test.lua -t "$STATE" "$2" > "$log" 2>&1
    grep -a "HP bar:" "$log" | sed 's/^/  /'
    grep -aq "EXPSHARE RESULT: PASS" "$log"
}
if hp_case shipped $ROM 1; then echo "[PASS] shipped: the HP bar snaps"; pass=$((pass+1))
else echo "[FAIL] instant HP bar (see /tmp/ub_hp_shipped.log)"; fail=$((fail+1)); fi
if hp_case nohp build/unbound-cm_nohp.gba 0; then echo "[PASS] CM_NO_INSTANTHP: the HP bar animates (control)"; pass=$((pass+1))
else echo "[FAIL] control (see /tmp/ub_hp_nohp.log)"; fail=$((fail+1)); fi
if hp_case nohp_as_instant build/unbound-cm_nohp.gba 1; then echo "[FAIL] NEGATIVE CONTROL: CM_NO_INSTANTHP passed 'instant'"; fail=$((fail+1))
else echo "[PASS] negative control: CM_NO_INSTANTHP fails 'instant' (want FAIL)"; pass=$((pass+1)); fi
echo "instant HP bar live: $pass passed, $fail failed (want $EXPECT_CASES)"
[ "$fail" -eq 0 ] && [ $((pass+fail)) -eq "$EXPECT_CASES" ]
