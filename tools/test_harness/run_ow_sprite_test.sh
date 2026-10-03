#!/bin/bash
# LIVE overworld-sprite layer (2026-10-03, ../game_plans/overworld_sprites.md).
#
# For each character, a fresh game is driven through the intro with Character
# Mode turned on through the real opt-in block (mk_checkpoint_cm.lua), and the
# player is then read out of OBJ VRAM and the unfaded palette buffer while
# standing, walking and running in all four directions
# (cm_ow_sprite_test.lua). Expected art comes from the source sheets, not the
# build (tools/tests/ow_sprite_env.py).
#
#   Misty  (10)  16x32 sheet whose run frames are its walk frames (147 of 155 are)
#   Kris   (23)  16x32 sheet with real run frames
#   Lucas  (60)  32x32 sheet with real run frames (sideways running is the
#                case that showed RR a running player's back)
#   Leaf    (2)  Unbound's own costume set
# Plus CM OFF (a fresh game answered No: the player is not Misty), and a
# NEGATIVE CONTROL: a copy with the GetCustomGraphicsIdByState trampoline put
# back, with its OWN checkpoint (a savestate made on the shipped ROM would
# carry the sprite in VRAM and RAM), which must FAIL.
set -u
[ -z "${BASH_VERSION:-}" ] && exec bash "$0" "$@"
cd "$(dirname "$0")/../.." || exit 1

MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
ROM=build/unbound-cm.gba
NEG=build/unbound-cm-ow-neg.gba
TMP=${CM_OW_TMP:-/tmp/ub_ow}
EXPECT_ON=11
EXPECT_OFF=2
mkdir -p "$TMP"

[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh', or set MGBA_HEADLESS"; exit 2; }
[ -f "$ROM" ] || { echo "build first: python3 tools/build_patch.py"; exit 1; }

python3 - <<'EOF' || exit 1
import sys
sys.path.insert(0, "tools"); sys.path.insert(0, "tools/character_mode")
import build_patch as bp, unbound_ow_player as owp
d = bytearray(open("build/unbound-cm.gba", "rb").read())
o = bp.AVATAR_FN_FILE_OFF
assert d[o:o + 8] != owp.AVATAR_FN_ORIG, "shipped build has no avatar trampoline"
d[o:o + 8] = owp.AVATAR_FN_ORIG
open("build/unbound-cm-ow-neg.gba", "wb").write(bytes(d))
EOF

fail=0
checkpoint() {  # char rom out
    if [ ! -f "$3" ] || [ "$2" -nt "$3" ]; then
        rm -f "$3"
        CM_CHAR=$1 CM_CHECKPOINT=$3 timeout 600 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_cm.lua "$2" \
            > "$3.log" 2>&1
        [ -f "$3" ] || { echo "  FAIL checkpoint for char $1 on $2 (see $3.log)"; fail=1; return 1; }
    fi
}
run() {  # label char mode checks rom checkpoint want
    eval "$(python3 tools/tests/ow_sprite_env.py "$2" 2>/dev/null)" || { echo "  FAIL env for char $2"; fail=1; return; }
    local log=$TMP/$1.log
    MODE=$3 CM_EXPECT_CHECKS=$4 CM_CHECKPOINT=$6 CM_SHOTS=$TMP/$1 timeout 240 "$MGBA" \
        --script tools/mgba_scripts/cm_ow_sprite_test.lua "$5" > "$log" 2>&1
    if grep -aq "HARNESS RESULT: $7" "$log"; then
        echo "  PASS overworld sprite $1 (want $7)"
    else
        echo "  FAIL overworld sprite $1 (want $7, see $log)"; grep -a "HARNESS" "$log" | tail -6; fail=1
    fi
}

eval "$(python3 tools/tests/ow_sprite_env.py 10 2>/dev/null)"    # opt-in block addresses
for c in 10 23 60 2; do
    checkpoint $c "$ROM" "$TMP/cm$c.ss" && run "char$c" $c on $EXPECT_ON "$ROM" "$TMP/cm$c.ss" PASS
done
# CM off: the stock free-roam checkpoint (opt-in answered No)
OFF_SS=$TMP/field.ss
if [ ! -f "$OFF_SS" ] || [ "$ROM" -nt "$OFF_SS" ]; then
    CM_CHECKPOINT=$OFF_SS timeout 1500 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_field.lua "$ROM" \
        > "$OFF_SS.log" 2>&1
fi
if [ -f "$OFF_SS" ]; then run cm_off 10 off $EXPECT_OFF "$ROM" "$OFF_SS" PASS
else echo "  FAIL CM-off checkpoint (see $OFF_SS.log)"; fail=1; fi
checkpoint 10 "$NEG" "$TMP/neg10.ss" && \
    run NEGATIVE_CONTROL_no_avatar_hook 10 on $EXPECT_ON "$NEG" "$TMP/neg10.ss" FAIL
exit $fail
