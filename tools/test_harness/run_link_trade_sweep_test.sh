#!/bin/bash
# LIVE e2e for the link-trade sweep (src/character_mode.c
# CharacterMode_LinkTradeSweepThenExpand; verify_artifacts [L]; rowe_parity.md
# §13.53). Headless Lua. The SHIPPED PC debug script builds [Pikachu,
# Hitmontop] with the case's character and opens the PC; the layer then runs the
# REAL CB2_SaveAndEndTrade from state 0 up to its hooked BL. FireRed has one
# ender for wired and wireless trades, so this covers the Union Room too.
#   swept (Pikachu ON, Hitmontop OFF) -> Hitmontop boxed
#   stays (both ON)                   -> nothing moves
#   off   (flag cleared once the PC opens) -> nothing moves
#   no-hook ROM                       -> the layer must FAIL
set -u
[ -z "${BASH_VERSION:-}" ] && exec bash "$0" "$@"
cd "$(dirname "$0")/../.." || exit 1
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
SCRIPT=tools/mgba_scripts/cm_link_trade_sweep_test.lua
ROM=build/unbound-cm.gba
NEG=build/unbound-cm-linksweep-neg.gba
export CM_CHECKPOINT=${CM_CHECKPOINT:-/tmp/ub_ss_field.ss}
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh', or set MGBA_HEADLESS"; exit 2; }
[ -f "$ROM" ] || { echo "build first: python3 tools/build_patch.py"; exit 1; }
if [ ! -f "$CM_CHECKPOINT" ] || [ "$ROM" -nt "$CM_CHECKPOINT" ]; then
    echo "making the free-roam checkpoint (drives the whole intro, ~5 min)..."
    rm -f "$CM_CHECKPOINT"
    timeout 1500 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_field.lua \
        "$ROM" > /tmp/ub_lts_checkpoint.log 2>&1
    [ -f "$CM_CHECKPOINT" ] || { echo "  FAIL checkpoint script produced no savestate"; exit 1; }
fi
# The negative control: the link-trade BL back to the base ROM's bytes.
python3 - <<'PY'
import sys
sys.path.insert(0, "tools")
import build_patch as bp
d = bytearray(open("build/unbound-cm.gba", "rb").read())
base = open("rom/Pokemon Unbound (v2.1.1.1).gba", "rb").read()
o = bp.LINK_TRADE_BL_FILE_OFF
assert d[o:o + 4] != base[o:o + 4], "link-trade sweep not in the shipped build"
d[o:o + 4] = base[o:o + 4]
open("build/unbound-cm-linksweep-neg.gba", "wb").write(bytes(d))
PY
eval "$(python3 - <<'PY'
import json, re, struct, subprocess, sys
sys.path.insert(0, "tools/character_mode")
import pc_hook
d = json.load(open("build/debug_addrs.json"))
nm = subprocess.run(["arm-none-eabi-nm", "build/character_mode.elf"], capture_output=True, text=True).stdout
sym = lambda n: int(re.search(rf"^([0-9a-f]+) T {n}$", nm, re.M).group(1), 16)
rom = open("build/unbound-cm.gba", "rb").read()
pss = struct.unpack_from("<I", rom, 0x15FD60 + 4 * pc_hook.SPECIAL_PC)[0] & ~1
print(f"export CM_SWEPT={d['pc_test_script_swept']:#x} CM_STAYS={d['pc_test_script_stays']:#x}")
print(f"export CM_QUEUE={sym('CharacterMode_QueueScriptCb1'):#x} CM_PSS_ADDR={pss:#x}")
print(f"export LINK_SHIM={sym('CharacterMode_LinkTradeSweepThenExpand'):#x}")
PY
)" || exit 1
export MGBA_HEADLESS_DEBUGGER=1
fail=0
run() {  # label script-var expect rom want(PASS|FAIL) shim [CM_OFF]
    log=/tmp/ub_lts_$1.log
    CM_SCRIPT=$2 EXPECT=$3 CM_EXPECT_CHECKS=6 CM_OFF=${7:-0} CM_SHIM_ADDR=$6 \
        CM_SHOT_PREFIX=/tmp/ub_lts_$1 \
        timeout 300 "$MGBA" --script "$SCRIPT" "$4" > "$log" 2>&1
    if grep -aq "HARNESS RESULT: $5" "$log"; then
        echo "  PASS link-trade sweep $1 (want $5)"
    else
        echo "  FAIL link-trade sweep $1 (want $5, see $log)"; grep -a "HARNESS" "$log" | tail -6; fail=1
    fi
}
run swept  "$CM_SWEPT" box1 "$ROM" PASS "$LINK_SHIM"
run stays  "$CM_STAYS" none "$ROM" PASS "$LINK_SHIM"
run off    "$CM_SWEPT" none "$ROM" PASS "$LINK_SHIM" 1
run noHook "$CM_SWEPT" box1 "$NEG" FAIL 0
grep -aq "HARNESS FAIL Hitmontop (off the roster) left the party" /tmp/ub_lts_noHook.log \
    || { echo "  FAIL the negative control failed for another reason (see /tmp/ub_lts_noHook.log)"; fail=1; }
exit $fail
