#!/bin/bash
# LIVE layer: START > Extras > Heal party / PC (QoL round 2 item 3, 2026-11-11; src/roster_display.c).
# From the free-roam checkpoint (no Pokemon yet: the Lua queues `givemon Pikachu` first), cm_exprate_menu_test.lua sets the lead to 1 HP + poison, opens START >
# Extras and picks a row:
#   heal (CM on: Roster, Exp. Rate, Heal party, PC -> DOWN DOWN A; CM off: Exp. Rate, Heal party, PC -> DOWN A):
#        the lead is at full HP with no status, the storage special did not run, the field is back
#   pc   (CM on: DOWN DOWN DOWN A): the storage special ran once, nothing was healed, B leaves, the field is back
#   CM_NO_EXTRAS=1 build (control): CM off opens the rate chooser at once (no Extras list); asked for the heal with
#        CM on (DOWN DOWN A on a 2-row list) it must FAIL (negative).
set -u
[ -z "${BASH_VERSION:-}" ] && exec bash "$0" "$@"
cd "$(dirname "$0")/../.." || exit 1
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
export CM_CHECKPOINT=${CM_CHECKPOINT:-/tmp/ub_ss_field.ss}
ROM=build/unbound-cm.gba
CTL=build/unbound-cm_noextras.gba
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA -- build it with 'sh tools/build_mgba.sh'"; exit 2; }
CM_NO_EXTRAS=1 python3 tools/build_patch.py >/dev/null || { echo "  FAIL control build"; exit 1; }
cp "$ROM" "$CTL"; cp build/character_mode.elf build/character_mode_noextras.elf
python3 tools/build_patch.py >/dev/null || { echo "  FAIL shipping build"; exit 1; }
if [ ! -f "$CM_CHECKPOINT" ] || [ "$ROM" -nt "$CM_CHECKPOINT" ]; then
    echo "making the free-roam checkpoint (~5 min)..."
    rm -f "$CM_CHECKPOINT"
    timeout 1500 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_field.lua "$ROM" > /tmp/ub_ex_checkpoint.log 2>&1
    [ -f "$CM_CHECKPOINT" ] || { echo "  FAIL no free-roam checkpoint"; exit 1; }
fi
symf() { printf '0x%s' "$(arm-none-eabi-nm "$1" | awk -v s="$2" '$3 == s {print $1}')"; }
EXPECT_CASES=6
pass=0; fail=0
ok() { echo "[PASS] $1"; pass=$((pass+1)); }
bad() { echo "[FAIL] $1"; fail=$((fail+1)); }
export MGBA_HEADLESS_DEBUGGER=1 CM_CHAR=10 GIVE_MON=1      # the checkpoint has no Pokemon: the Lua gives a Pikachu first
menu() {  # label rom elf mode extras_keys list_keys want_next want_rate want_extras checks
    log=/tmp/ub_ex_$1.log
    QUEUE_CB1=$(( $(symf $3 CharacterMode_QueueScriptCb1) | 1 )) EXTRAS_INPUT=$(symf $3 Extras_HandleInput) RATE_INPUT=$(symf $3 ExpRate_HandleInput) ROSTER_INPUT=$(symf $3 RosterMenu_HandleInput) \
    MODE=$4 START_RATE=0 EXTRAS_KEYS=$5 LIST_KEYS=$6 WANT_NEXT=$7 WANT_RATE=$8 WANT_EXTRAS=$9 CM_EXPECT_CHECKS=${10} SHOTS=build/extras_$1 \
        timeout 240 "$MGBA" --script tools/mgba_scripts/cm_exprate_menu_test.lua "$2" > "$log" 2>&1
    grep -aq "HARNESS RESULT: PASS" "$log"
}
E=build/character_mode.elf; EC=build/character_mode_noextras.elf
if menu heal_on $ROM $E on "DOWN,DOWN,A" "" heal 0 1 5; then ok "CM on: Extras > Heal party heals the lead"; else bad "heal CM on (/tmp/ub_ex_heal_on.log)"; fi
if menu heal_off $ROM $E off "DOWN,A" "" heal 0 1 5; then ok "CM off: Extras > Heal party heals the lead"; else bad "heal CM off (/tmp/ub_ex_heal_off.log)"; fi
if menu pc_on $ROM $E on "DOWN,DOWN,DOWN,A" "" pc 0 1 6; then ok "CM on: Extras > PC opens the storage system"; else bad "pc CM on (/tmp/ub_ex_pc_on.log)"; fi
if menu pc_off $ROM $E off "DOWN,DOWN,A" "" pc 0 1 6; then ok "CM off: Extras > PC opens the storage system"; else bad "pc CM off (/tmp/ub_ex_pc_off.log)"; fi
if menu ctl_off $CTL $EC off "" "DOWN,DOWN,A" rate 2 0 6; then ok "control (CM_NO_EXTRAS): CM off opens the rate chooser at once"; else bad "control (/tmp/ub_ex_ctl_off.log)"; fi
if menu NEG_heal $CTL $EC on "DOWN,DOWN,A" "" heal 0 1 5; then bad "NEGATIVE CONTROL: CM_NO_EXTRAS still healed"
else ok "negative control: CM_NO_EXTRAS asked for the heal fails (want FAIL)"; fi
echo "Extras live: $pass passed, $fail failed (want $EXPECT_CASES)"
[ "$fail" -eq 0 ] && [ $((pass+fail)) -eq "$EXPECT_CASES" ]
