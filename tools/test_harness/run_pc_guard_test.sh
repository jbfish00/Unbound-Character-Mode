#!/bin/bash
# LIVE e2e for the PC second guard (ROWE's IsRemovingLastAllowedPartyMon;
# src/character_mode.c CM_PSSLastMonGuard; verify_artifacts [G]). Headless Lua.
# The SHIPPED build's PC debug script (build_patch.py pc_debug_script) gives
# Pikachu + Hitmontop with the mode off, turns it on for the case's character
# and opens the real storage system; the layer deposits Pikachu. ⭐ With an
# alive Hitmontop beside it VANILLA ALLOWS that deposit, so only the guard can
# refuse it.
#   swept (Pikachu ON, Hitmontop OFF) -> refused
#   stays (both ON)                   -> deposited (another on-roster mon remains)
#   off   (flag cleared once the PC opens) -> deposited
#   noguard ROM                       -> the layer must FAIL on the deposit
set -u
[ -z "${BASH_VERSION:-}" ] && exec bash "$0" "$@"
cd "$(dirname "$0")/../.." || exit 1
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
SCRIPT=tools/mgba_scripts/cm_pc_guard_test.lua
ROM=build/unbound-cm.gba
NEG=build/unbound-cm-pcguard-neg.gba
export CM_CHECKPOINT=${CM_CHECKPOINT:-/tmp/ub_ss_field.ss}
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh', or set MGBA_HEADLESS"; exit 2; }
[ -f "$ROM" ] || { echo "build first: python3 tools/build_patch.py"; exit 1; }
if [ ! -f "$CM_CHECKPOINT" ] || [ "$ROM" -nt "$CM_CHECKPOINT" ]; then
    echo "making the free-roam checkpoint (drives the whole intro, ~5 min)..."
    rm -f "$CM_CHECKPOINT"
    timeout 1500 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_field.lua \
        "$ROM" > /tmp/ub_pcg_checkpoint.log 2>&1
    [ -f "$CM_CHECKPOINT" ] || { echo "  FAIL checkpoint script produced no savestate"; exit 1; }
fi
# The negative control: the guard's BLs, tail and trampoline back to base bytes.
python3 - <<'PY'
import sys
sys.path.insert(0, "tools")
import build_patch as bp
d = bytearray(open("build/unbound-cm.gba", "rb").read())
base = open("rom/Pokemon Unbound (v2.1.1.1).gba", "rb").read()
regs = [(o, 4) for o in bp.PSS_GUARD_BL_FILE_OFFS + (bp.PSS_CANSHIFT_BL_FILE_OFF,
                                                      bp.PSS_CANSHIFT_TAIL_FILE_OFF)]
regs.append((bp.PSS_GUARD_TRAMPOLINE_FILE_OFF, 8))
for o, n in regs:
    assert d[o:o + n] != base[o:o + n], "guard not in the shipped build at %#x" % o
    d[o:o + n] = base[o:o + n]
open("build/unbound-cm-pcguard-neg.gba", "wb").write(bytes(d))
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
print(f"export CM_QUEUE={sym('CharacterMode_QueueScriptCb1'):#x} CM_GUARD_ADDR={sym('CM_PSSLastMonGuard'):#x} CM_PSS_ADDR={pss:#x}")
PY
)" || exit 1
export MGBA_HEADLESS_DEBUGGER=1
fail=0
run() {  # label script-var expect checks rom want(PASS|FAIL) [CM_OFF]
    log=/tmp/ub_pcg_$1.log
    CM_SCRIPT=$2 EXPECT=$3 CM_EXPECT_CHECKS=$4 CM_OFF=${7:-0} CM_SHOT_PREFIX=/tmp/ub_pcg_$1 \
        timeout 300 "$MGBA" --script "$SCRIPT" "$5" > "$log" 2>&1
    if grep -aq "HARNESS RESULT: $6" "$log"; then
        echo "  PASS PC guard $1 (want $6)"
    else
        echo "  FAIL PC guard $1 (want $6, see $log)"; grep -a "HARNESS" "$log" | tail -6; fail=1
    fi
}
run swept   "$CM_SWEPT" refused   4 "$ROM" PASS
run stays   "$CM_STAYS" deposited 3 "$ROM" PASS
run off     "$CM_SWEPT" deposited 3 "$ROM" PASS 1
run noguard "$CM_SWEPT" refused   ""  "$NEG" FAIL
grep -aq "HARNESS FAIL slot 0 (the last on-roster mon) is still in the party" /tmp/ub_pcg_noguard.log \
    || { echo "  FAIL the negative control failed for another reason (see /tmp/ub_pcg_noguard.log)"; fail=1; }
exit $fail
