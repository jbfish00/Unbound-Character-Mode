#!/bin/bash
# LIVE layer: QoL C11/C16 starter kit for every new game (2026-11-07). Each ROM gets its own fresh-new-game free-roam
# checkpoint (the kit is given inside NewGameInitData, so a checkpoint from another build would prove nothing), then
# cm_newgame_kit_test.lua queues checkitem 633 / 632 and reads the Running Shoes flag.
#   shipped                         -> granted
#   CM_NO_STARTKIT=1 build          -> none (the discriminating control)
#   that control asked for granted  -> must FAIL (the negative control)
set -u
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA"; exit 2; }
CM_NO_STARTKIT=1 python3 tools/build_patch.py > /tmp/ub_kit_ctl_build.log 2>&1 && cp build/unbound-cm.gba /tmp/ub_kit_ctl.gba \
  && python3 tools/build_patch.py > /tmp/ub_kit_build.log 2>&1 && cp build/unbound-cm.gba /tmp/ub_kit.gba || { echo "  FAIL builds"; exit 1; }
QUEUE=$(( 0x$(arm-none-eabi-nm build/character_mode.elf | awk '/ CharacterMode_QueueScriptCb1$/{print $1}') | 1 ))
for r in ub_kit ub_kit_ctl; do
    rm -f /tmp/${r}_field.ss
    CM_CHECKPOINT=/tmp/${r}_field.ss timeout 900 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_field.lua /tmp/$r.gba \
        > /tmp/${r}_ckpt.log 2>&1 || true
    [ -f /tmp/${r}_field.ss ] || { echo "  FAIL no free-roam checkpoint for $r"; exit 1; }
done
EXPECT_CASES=3; pass=0; fail=0
kcase() {  # rom expect checks
    log=/tmp/ub_kit_$1_$2.log
    QUEUE_CB1=$QUEUE EXPECT=$2 CM_EXPECT_CHECKS=$3 timeout 120 "$MGBA" --script tools/mgba_scripts/cm_newgame_kit_test.lua \
        -t /tmp/${1}_field.ss /tmp/$1.gba > "$log" 2>&1
    grep -aq "KIT RESULT: PASS" "$log"
}
if kcase ub_kit granted 4; then echo "[PASS] fresh new game: Running Shoes + Shiny + Oval Charm"; pass=$((pass+1))
else echo "[FAIL] starter kit (see /tmp/ub_kit_ub_kit_granted.log)"; fail=$((fail+1)); fi
if kcase ub_kit_ctl none 3; then echo "[PASS] CM_NO_STARTKIT build: no charms (control)"; pass=$((pass+1))
else echo "[FAIL] control (see /tmp/ub_kit_ub_kit_ctl_none.log)"; fail=$((fail+1)); fi
if kcase ub_kit_ctl granted 4; then echo "[FAIL] NEGATIVE CONTROL: the control build passed 'granted'"; fail=$((fail+1))
else echo "[PASS] negative control: the CM_NO_STARTKIT build fails 'granted' (want FAIL)"; pass=$((pass+1)); fi
echo "starter kit live: $pass passed, $fail failed (want $EXPECT_CASES)"
[ "$fail" -eq 0 ] && [ $((pass+fail)) -eq "$EXPECT_CASES" ]
