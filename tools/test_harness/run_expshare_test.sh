#!/bin/bash
# LIVE layer: the party-wide Exp. Share with Character Mode OFF (user ruling
# 2026-10-21). Native in Unbound: the new-game init script (0x09E70DB0) runs an
# unconditional `setflag 0x9F2`, and the exp award shares with the whole party
# while FlagGet(0x9F2) is set (verify [X] pins both). Nothing in this repo
# changes it; this layer proves it on the shipped ROM.
#
# From the free-roam checkpoint (mk_checkpoint_field.lua: a FRESH new game with
# the Character Mode opt-in answered No), cm_exp_share_party_test.lua queues
# Pikachu L50 + Caterpie L5 benched and a wild Magikarp; the Caterpie never
# battles, so any Exp. it gains is the share.
#   shipped            -> share (the bench gains Exp.)
#   flag 0x9F2 cleared -> none  (the discriminating control)
#   flag 0x9F2 cleared, asked for "share" -> must FAIL (the negative control)
set -u
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
STATE=${CM_CHECKPOINT:-/tmp/ub_ss_field.ss}
ROM=build/unbound-cm.gba
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh'"; exit 2; }
[ -f "$ROM" ] || { echo "build first: python3 tools/build_patch.py"; exit 1; }
if [ ! -f "$STATE" ]; then
    CM_CHECKPOINT="$STATE" timeout 900 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_field.lua "$ROM" \
        > /tmp/ub_exp_checkpoint.log 2>&1 || true
    [ -f "$STATE" ] || { echo "  FAIL no free-roam checkpoint"; exit 1; }
fi
QUEUE=$(( 0x$(arm-none-eabi-nm build/character_mode.elf | awk '/ CharacterMode_QueueScriptCb1$/{print $1}') | 1 ))
EXPECT_CASES=3
pass=0; fail=0
exp_case() {  # name EXPECT CLEAR_FLAG
    log=/tmp/ub_exp_$1.log
    QUEUE_CB1=$QUEUE EXPECT=$2 CLEAR_FLAG=$3 CM_EXPECT_CHECKS=3 \
        timeout 120 "$MGBA" --script tools/mgba_scripts/cm_exp_share_party_test.lua -t "$STATE" "$ROM" > "$log" 2>&1
    grep -aq "EXPSHARE RESULT: PASS" "$log"
}
if exp_case shipped share ""; then echo "[PASS] CM off, fresh new game: the benched mon gains Exp. (party-wide share)"; pass=$((pass+1))
else echo "[FAIL] CM-off share (see /tmp/ub_exp_shipped.log)"; fail=$((fail+1)); fi
if exp_case cleared none 9F2; then echo "[PASS] flag 0x9F2 cleared: the benched mon gains nothing (control)"; pass=$((pass+1))
else echo "[FAIL] 0x9F2 control (see /tmp/ub_exp_cleared.log)"; fail=$((fail+1)); fi
if exp_case cleared_as_share share 9F2; then echo "[FAIL] NEGATIVE CONTROL: 0x9F2 cleared still passed 'share'"; fail=$((fail+1))
else echo "[PASS] negative control: with 0x9F2 cleared, 'share' fails (want FAIL)"; pass=$((pass+1)); fi
echo "CM-off Exp. Share live: $pass passed, $fail failed (want $EXPECT_CASES)"
[ "$fail" -eq 0 ] && [ $((pass+fail)) -eq "$EXPECT_CASES" ]
