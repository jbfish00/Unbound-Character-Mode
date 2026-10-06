#!/bin/bash
# LIVE e2e for field moves (src/character_mode.c CharacterMode_FieldMoveCanLearn;
# verify_artifacts [H]). Headless Lua. With the mode on, any party mon can use
# a field move whose HM is in the bag (badges still required). The probe calls
# the real engine checks with a Magikarp that learns no HM.
#   on      (Brandon) -> every HM usable with the item, none without it
#   off               -> vanilla: nothing usable
#   nohook ROM, on    -> the layer must FAIL
# Lava Surf (cm_lava_surf_test.lua) jumps into the REAL magma script:
#   on + HM03 (Magikarp) -> surfs; on, no HM03 -> no; off + HM03 -> no;
#   off + Charmander -> surfs (the Fire search still works); on + Charmander,
#   no HM03 -> surfs (fallback); lava-only nohook ROM, on + HM03 -> must FAIL
set -u
[ -z "${BASH_VERSION:-}" ] && exec bash "$0" "$@"
cd "$(dirname "$0")/../.." || exit 1
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
SCRIPT=tools/mgba_scripts/cm_field_move_test.lua
ROM=build/unbound-cm.gba
NEG=build/unbound-cm-fieldmove-neg.gba
LAVA_NEG=build/unbound-cm-lava-neg.gba
LAVA_SCRIPT=tools/mgba_scripts/cm_lava_surf_test.lua
export CM_CHECKPOINT=${CM_CHECKPOINT:-/tmp/ub_ss_field.ss}
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh', or set MGBA_HEADLESS"; exit 2; }
[ -f "$ROM" ] || { echo "build first: python3 tools/build_patch.py"; exit 1; }
if [ ! -f "$CM_CHECKPOINT" ] || [ "$ROM" -nt "$CM_CHECKPOINT" ]; then
    echo "making the free-roam checkpoint (drives the whole intro, ~5 min)..."
    rm -f "$CM_CHECKPOINT"
    timeout 1500 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_field.lua \
        "$ROM" > /tmp/ub_fm_checkpoint.log 2>&1
    [ -f "$CM_CHECKPOINT" ] || { echo "  FAIL checkpoint script produced no savestate"; exit 1; }
fi
# The negative control: the three bls back to CanMonLearnTMTutor.
python3 - <<'PY'
import sys
sys.path.insert(0, "tools")
import build_patch as bp
d = bytearray(open("build/unbound-cm.gba", "rb").read())
base = open("rom/Pokemon Unbound (v2.1.1.1).gba", "rb").read()
for o, _ in bp.FIELD_MOVE_BL_SITES:
    assert d[o:o + 4] != base[o:o + 4], "field-move hook not in the shipped build at %#x" % o
    d[o:o + 4] = base[o:o + 4]
open("build/unbound-cm-fieldmove-neg.gba", "wb").write(bytes(d))
# The lava negative control: only the magma splice restored (the three bls
# stay hooked), so a failure there can only come from the splice.
d = bytearray(open("build/unbound-cm.gba", "rb").read())
o = bp.LAVA_SPLICE_FILE_OFF
assert d[o:o + 8] != base[o:o + 8] and base[o:o + 8] == bp.LAVA_SPLICE_ORIG
d[o:o + 8] = base[o:o + 8]
open("build/unbound-cm-lava-neg.gba", "wb").write(bytes(d))
PY
eval "$(python3 - <<'PY'
import json, re, subprocess
d = json.load(open("build/debug_addrs.json"))
nm = subprocess.run(["arm-none-eabi-nm", "build/character_mode.elf"], capture_output=True, text=True).stdout
sym = lambda n: int(re.search(rf"^([0-9a-f]+) T {n}$", nm, re.M).group(1), 16)
print(f"export CM_ON={d['field_test_script_on']:#x} CM_OFF={d['field_test_script_off']:#x}")
print(f"export CM_QUEUE={sym('CharacterMode_QueueScriptCb1'):#x}")
for k, v in d["lava_test_scripts"].items():
    print(f"export LAVA_{k.upper()}={v:#x}")
PY
)" || exit 1
export MGBA_HEADLESS_DEBUGGER=1
fail=0
run() {  # label script expect checks rom want(PASS|FAIL)
    log=/tmp/ub_fm_$1.log
    CM_SCRIPT=$2 EXPECT=$3 CM_EXPECT_CHECKS=$4 \
        timeout 300 "$MGBA" --script "$SCRIPT" "$5" > "$log" 2>&1
    if grep -aq "HARNESS RESULT: $6" "$log"; then
        echo "  PASS field moves $1 (want $6)"
    else
        echo "  FAIL field moves $1 (want $6, see $log)"; grep -a "HARNESS" "$log" | tail -6; fail=1
    fi
}
run on     "$CM_ON"  on  19 "$ROM" PASS
run off    "$CM_OFF" off 19 "$ROM" PASS
run nohook "$CM_ON"  on  19 "$NEG" FAIL
grep -aq "HARNESS FAIL Surf: the Magikarp can use it with the HM in the bag" /tmp/ub_fm_nohook.log \
    || { echo "  FAIL the negative control failed for another reason (see /tmp/ub_fm_nohook.log)"; fail=1; }
lava() {  # label script mode want_slot rom want(PASS|FAIL)
    log=/tmp/ub_lava_$1.log
    CM_SCRIPT=$2 CM_LAVA_MODE=$3 WANT_SLOT=$4 CM_EXPECT_CHECKS=2 \
        timeout 300 "$MGBA" --script "$LAVA_SCRIPT" "$5" > "$log" 2>&1
    if grep -aq "HARNESS RESULT: $6" "$log"; then
        echo "  PASS lava surf $1 (want $6)"
    else
        echo "  FAIL lava surf $1 (want $6, see $log)"; grep -a "HARNESS" "$log" | tail -4; fail=1
    fi
}
lava on_hm        "$LAVA_ON_HM"        1 0 "$ROM" PASS
lava on_nohm      "$LAVA_ON_NOHM"      0 6 "$ROM" PASS
lava off_hm       "$LAVA_OFF_HM"       1 6 "$ROM" PASS
lava off_fire     "$LAVA_OFF_FIRE"     2 0 "$ROM" PASS
lava on_fire_nohm "$LAVA_ON_FIRE_NOHM" 2 0 "$ROM" PASS
lava nohook       "$LAVA_ON_HM"        1 0 "$LAVA_NEG" FAIL
grep -aq "HARNESS FAIL the magma script offers to surf" /tmp/ub_lava_nohook.log \
    || { echo "  FAIL the lava negative control failed for another reason (see /tmp/ub_lava_nohook.log)"; fail=1; }
exit $fail
