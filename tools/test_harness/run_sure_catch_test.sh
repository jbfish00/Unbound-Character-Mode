#!/bin/bash
# LIVE layer: 100% catch for on-roster species (src/character_mode.c
# CharacterMode_CatchOddsStub; verify [S]). Headless mGBA + Lua: from the
# free-roam checkpoint, a battle script is queued through the build's own
# CharacterMode_QueueScriptCb1 (Pikachu L50 lead, 10 Poke Balls, wild Snorlax
# L30 at full HP, catch rate 25) and one ball is thrown through the real Cube.
# Red (1) has Snorlax on his roster, Leaf (2) does not: her ball is dodged by
# the existing catch gate before any odds exist. A copy with the compare
# restored must FAIL "sure" (the negative control).
set -u
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
STATE=${CM_CHECKPOINT:-/tmp/ub_ss_field.ss}
ROM=build/unbound-cm.gba
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh'"; exit 2; }
[ -f "$ROM" ] || { echo "build first: python3 tools/build_patch.py"; exit 1; }
if [ ! -f "$STATE" ]; then
    CM_CHECKPOINT="$STATE" timeout 900 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_field.lua "$ROM" \
        > /tmp/ub_sure_checkpoint.log 2>&1 || true
    [ -f "$STATE" ] || { echo "  FAIL no free-roam checkpoint"; exit 1; }
fi
QUEUE=$(( 0x$(arm-none-eabi-nm build/character_mode.elf | awk '/ CharacterMode_QueueScriptCb1$/{print $1}') | 1 ))
python3 - "$ROM" build/unbound-cm-nosure.gba <<'PY'
import sys
d = bytearray(open(sys.argv[1], "rb").read())
d[0x9C8D58:0x9C8D5C] = bytes.fromhex("fe2d63d9")   # the base ROM's cmp r5,#254 ; bls
open(sys.argv[2], "wb").write(d)
PY
fail=0
sure_case() {  # name rom CM_ON CM_CHAR SEED EXPECT
    log=/tmp/ub_sure_$1.log
    MGBA_HEADLESS_DEBUGGER=1 QUEUE_CB1=$QUEUE CM_EXPECT_CHECKS=3 CM_ON=$3 CM_CHAR=$4 SEED=$5 EXPECT=$6 \
        timeout 60 "$MGBA" --script tools/mgba_scripts/cm_sure_catch_test.lua -t "$STATE" "$2" > "$log" 2>&1
    grep -aq "SURE RESULT: PASS" "$log"
}
for seed in 1 2 3; do
    if sure_case red$seed "$ROM" 1 1 $seed sure; then echo "[PASS] on-roster Snorlax caught at full HP (Red, seed $seed)"
    else echo "[FAIL] sure catch, seed $seed (see /tmp/ub_sure_red$seed.log)"; fail=1; fi
done
if sure_case leaf "$ROM" 1 2 1 dodged; then echo "[PASS] off-roster (Leaf): the ball is dodged before any odds"
else echo "[FAIL] off-roster (see /tmp/ub_sure_leaf.log)"; fail=1; fi
if sure_case off "$ROM" 0 1 1 miss; then echo "[PASS] CM off: the ball's own odds, seed 1 breaks out"
else echo "[FAIL] CM off control (see /tmp/ub_sure_off.log)"; fail=1; fi
if sure_case nohook build/unbound-cm-nosure.gba 1 1 1 sure; then echo "[FAIL] NEGATIVE CONTROL: the no-hook ROM passed 'sure'"; fail=1
else echo "[PASS] sure catch NEGATIVE CONTROL (compare restored -> odds below 255)"; fi
exit $fail
