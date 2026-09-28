#!/bin/bash
# LIVE roster-display e2e: the START menu Roster row (2026-09-27).
#
# The first headless mgba + Lua layer in this repo (the GDB layers are
# unchanged). Unbound's START menu is a graphical icon bar built from a
# 12-record table; the Roster row takes dead record 6 ("Costume Box"), shown
# only while Character Mode is on (src/roster_display.c). This runs
# tools/mgba_scripts/cm_roster_menu_test.lua from a free-roam checkpoint that
# tools/mgba_scripts/mk_checkpoint_field.lua makes from a fresh game.
#
# Three runs, and the third is the point: on a test-only copy with the builder's
# case-6 byte put back to "skip", the roster run must FAIL -- or the layer only
# proves the screen works when something calls it.
# Misty (char 10) is deliberately not #1: a per-character test on the first
# record cannot catch an indexing error. Rows come from the manifest.
set -u
[ -z "${BASH_VERSION:-}" ] && exec bash "$0" "$@"
cd "$(dirname "$0")/../.." || exit 1

MGBA=../Seaglass-Character-Mode/tools/mgba_src/build/mgba-headless
SCRIPT=tools/mgba_scripts/cm_roster_menu_test.lua
ROM=build/unbound-cm.gba
NEG=build/unbound-cm-roster-neg.gba
export CM_CHECKPOINT=${CM_CHECKPOINT:-/tmp/ub_ss_field.ss}
EXPECT=14          # cm_roster_menu_test.lua, MODE=roster (MODE=off runs 2)

[ -x "$MGBA" ] || { echo "SKIP: mgba-headless not found at $MGBA"; exit 0; }
[ -f "$ROM" ] || { echo "build first: python3 tools/build_patch.py"; exit 1; }

# The checkpoint embeds RAM that points into the injected code, so remake it
# whenever the ROM is newer than it.
if [ ! -f "$CM_CHECKPOINT" ] || [ "$ROM" -nt "$CM_CHECKPOINT" ]; then
    echo "making the free-roam checkpoint (drives the whole intro, ~5 min)..."
    rm -f "$CM_CHECKPOINT"
    timeout 1500 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_field.lua \
        "$ROM" > /tmp/ub_roster_checkpoint.log 2>&1
    [ -f "$CM_CHECKPOINT" ] || { echo "  FAIL checkpoint script produced no savestate"; exit 1; }
fi

python3 - <<'EOF'
import sys
sys.path.insert(0, "tools")
import build_patch as bp
d = bytearray(open("build/unbound-cm.gba", "rb").read())
assert d[bp.START_CASE6_OFF] == bp.START_CASE6_APPEND, "shipped build does not append row 6"
d[bp.START_CASE6_OFF] = bp.START_CASE6_ORIG
open("build/unbound-cm-roster-neg.gba", "wb").write(bytes(d))
EOF

eval "$(python3 tools/tests/roster_menu_env.py 10)" || exit 1
export MGBA_HEADLESS_DEBUGGER=1 CM_CHAR=10

fail=0
run() {  # label mode checks rom want(PASS|FAIL)
    log=/tmp/ub_roster_$1.log
    MODE=$2 CM_EXPECT_CHECKS=$3 timeout 240 "$MGBA" --script "$SCRIPT" "$4" > "$log" 2>&1
    if grep -aq "HARNESS RESULT: $5" "$log"; then
        echo "  PASS roster e2e $1 (want $5)"
    else
        echo "  FAIL roster e2e $1 (want $5, see $log)"; grep -a "HARNESS" "$log" | tail -6; fail=1
    fi
}
run roster roster "$EXPECT" "$ROM" PASS
run off    off    2         "$ROM" PASS
run NEGATIVE_CONTROL_case6_skipped roster "$EXPECT" "$NEG" FAIL
exit $fail
