#!/bin/bash
# LIVE layer: Mart evolution items (QoL A1, 2026-10-24; verify [M]). From the
# free-roam checkpoint a queued script sets the mode + character and runs a real
# `pokemart` list; SetShopItemsForSale's list is read at a breakpoint and the Buy
# menu photographed. The Mart is the first list in the ROM that lacks an item the
# character's roster needs (derived, as is the expected list).
#   CM on, that character        -> stock + the missing items
#   CM off                       -> the stock
#   the BL restored (copy), CM on -> the stock (the discriminating control), and
#                                    asking it for the merged list must FAIL
set -u
cd "$(dirname "$0")/../.."
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
STATE=${CM_CHECKPOINT:-/tmp/ub_ss_field.ss}
ROM=build/unbound-cm.gba
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh'"; exit 2; }
[ -f "$ROM" ] || { echo "build first: python3 tools/build_patch.py"; exit 1; }
if [ ! -f "$STATE" ]; then
    CM_CHECKPOINT="$STATE" timeout 900 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_field.lua "$ROM" \
        > /tmp/ub_mart_checkpoint.log 2>&1 || true
    [ -f "$STATE" ] || { echo "  FAIL no free-roam checkpoint"; exit 1; }
fi
QUEUE=$(( 0x$(arm-none-eabi-nm build/character_mode.elf | awk '/ CharacterMode_QueueScriptCb1$/{print $1}') | 1 ))
read -r CHAR MART STOCK MERGED < <(python3 - <<'PY'
import json, os, sys
sys.path.insert(0, "tools")
import build_patch as bp
rom = open(bp.ROM, "rb").read()
man = json.load(open(os.path.join(bp.CM_DIR, "characters_manifest.json")))
sets = bp.mart_need_sets(rom, open(os.path.join(bp.CM_DIR, "rosters.bin"), "rb").read(), man)
marts = bp.find_marts(rom)
for c, st in enumerate(sets):
    for mp, stock in marts.items():
        miss = [x for x in st if x not in stock]
        if miss:
            print(c + 1, "%x" % mp, ",".join(map(str, stock)), ",".join(map(str, stock + miss)))
            raise SystemExit
PY
)
echo "character $CHAR, mart 0x$MART: stock $STOCK"
python3 - "$ROM" /tmp/ub_nomart.gba <<'PY'
import sys
sys.path.insert(0, "tools")
import build_patch as bp
d = bytearray(open(sys.argv[1], "rb").read())
s = bp.MART_SITE_FILE_OFF
d[s:s + 4] = bp.thumb_bl(bp.ROM_BASE + s, bp.CREATE_POKEMART_MENU)   # the base ROM's BL CreatePokemartMenu
open(sys.argv[2], "wb").write(d)
PY
EXPECT_CASES=4
pass=0; fail=0
mart_case() {  # name rom char want
    log=/tmp/ub_mart_$1.log
    MGBA_HEADLESS_DEBUGGER=1 QUEUE_CB1=$QUEUE MART=$MART CHAR=$3 WANT_LIST=$4 SHOT=/tmp/ub_mart_$1.png CM_EXPECT_CHECKS=2 \
        timeout 120 "$MGBA" --script tools/mgba_scripts/cm_mart_test.lua -t "$STATE" "$2" > "$log" 2>&1
    grep -aq "MART RESULT: PASS" "$log"
}
if mart_case on "$ROM" $CHAR "$MERGED"; then echo "[PASS] CM on (character $CHAR): stock + the roster's evolution items"; pass=$((pass+1))
else echo "[FAIL] CM on (see /tmp/ub_mart_on.log)"; fail=$((fail+1)); fi
if mart_case off "$ROM" 0 "$STOCK"; then echo "[PASS] CM off: the stock"; pass=$((pass+1))
else echo "[FAIL] CM off (see /tmp/ub_mart_off.log)"; fail=$((fail+1)); fi
if mart_case nohook /tmp/ub_nomart.gba $CHAR "$STOCK"; then echo "[PASS] BL restored, CM on: the stock (control)"; pass=$((pass+1))
else echo "[FAIL] control (see /tmp/ub_mart_nohook.log)"; fail=$((fail+1)); fi
if mart_case nohook_as_on /tmp/ub_nomart.gba $CHAR "$MERGED"; then echo "[FAIL] NEGATIVE CONTROL: the BL-restored ROM passed 'merged'"; fail=$((fail+1))
else echo "[PASS] negative control: the BL-restored ROM fails 'merged' (want FAIL)"; pass=$((pass+1)); fi
echo "Mart evolution items live: $pass passed, $fail failed (want $EXPECT_CASES)"
[ "$fail" -eq 0 ] && [ $((pass+fail)) -eq "$EXPECT_CASES" ]
