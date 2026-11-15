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
CM_OLD_HPBAR=1 python3 tools/build_patch.py >/dev/null || { echo "  FAIL old-patch build"; exit 1; }   # 2026-11-14 control
cp "$ROM" build/unbound-cm_oldhp.gba
python3 tools/build_patch.py >/dev/null || { echo "  FAIL shipping build"; exit 1; }
if [ ! -f "$STATE" ]; then
    CM_CHECKPOINT="$STATE" timeout 900 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_field.lua "$ROM" \
        > /tmp/ub_exp_checkpoint.log 2>&1 || true
    [ -f "$STATE" ] || { echo "  FAIL no free-roam checkpoint"; exit 1; }
fi
QUEUE=$(( 0x$(arm-none-eabi-nm build/character_mode.elf | awk '/ CharacterMode_QueueScriptCb1$/{print $1}') | 1 ))
EXPECT_CASES=6
pass=0; fail=0
hp_case() {  # name rom WANT_HPBAR [WANT_FULL]
    log=/tmp/ub_hp_$1.log
    MGBA_HEADLESS_DEBUGGER=1 QUEUE_CB1=$QUEUE EXPECT=share WANT_HPBAR=$3 WANT_FULL=${4:-} CM_EXPECT_CHECKS=$([ -n "${4:-}" ] && echo 6 || echo 4) \
        timeout 120 "$MGBA" --script tools/mgba_scripts/cm_exp_share_party_test.lua -t "$STATE" "$2" > "$log" 2>&1
    grep -a "HP bar\|full-HP" "$log" | sed 's/^/  /'
    grep -aq "EXPSHARE RESULT: PASS" "$log"
}
if hp_case shipped $ROM 1; then echo "[PASS] shipped: the HP bar snaps"; pass=$((pass+1))
else echo "[FAIL] instant HP bar (see /tmp/ub_hp_shipped.log)"; fail=$((fail+1)); fi
if hp_case nohp build/unbound-cm_nohp.gba 0; then echo "[PASS] CM_NO_INSTANTHP: the HP bar animates (control)"; pass=$((pass+1))
else echo "[FAIL] control (see /tmp/ub_hp_nohp.log)"; fail=$((fail+1)); fi
if hp_case nohp_as_instant build/unbound-cm_nohp.gba 1; then echo "[FAIL] NEGATIVE CONTROL: CM_NO_INSTANTHP passed 'instant'"; fail=$((fail+1))
else echo "[PASS] negative control: CM_NO_INSTANTHP fails 'instant' (want FAIL)"; pass=$((pass+1)); fi
# 2026-11-14 (user: bars low and red at battle start): every full-HP bar is drawn 48/48, incl. the L2 Magikarp
if hp_case full $ROM 1 1; then echo "[PASS] shipped: full-HP bars are drawn full"; pass=$((pass+1))
else echo "[FAIL] full bars (see /tmp/ub_hp_full.log)"; fail=$((fail+1)); fi
if hp_case oldhp build/unbound-cm_oldhp.gba 1 0; then echo "[PASS] CM_OLD_HPBAR: the 10-28 patch draws a short bar (control)"; pass=$((pass+1))
else echo "[FAIL] old-patch control (see /tmp/ub_hp_oldhp.log)"; fail=$((fail+1)); fi
if hp_case nohp_full build/unbound-cm_nohp.gba 0 1; then echo "[PASS] CM_NO_INSTANTHP: vanilla bars are drawn full"; pass=$((pass+1))
else echo "[FAIL] vanilla full bars (see /tmp/ub_hp_nohp_full.log)"; fail=$((fail+1)); fi
echo "instant HP bar live: $pass passed, $fail failed (want $EXPECT_CASES)"
[ "$fail" -eq 0 ] && [ $((pass+fail)) -eq "$EXPECT_CASES" ]
