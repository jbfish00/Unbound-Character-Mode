#!/bin/bash
# LIVE layer: move best-version crit +2 (2026-11-24, tools/build_patch.py CRIT_SITE). The EXP-share battle (a wild
# Magikarp at 1 HP) with the lead's move 1 forced; a breakpoint right after the crit routine's move-stage computation
# (0x089CE4D0) reads r6 = the move's crit stage. Slash (163, in the crit list): 2 on the shipping stub, 1 on the
# CM_NO_CRITPLUS2 build (Unbound's own flag bit); Tackle (33): 0; and the control asked for 2 must FAIL.
set -u
[ -z "${BASH_VERSION:-}" ] && exec bash "$0" "$@"
cd "$(dirname "$0")/../.." || exit 1
MGBA="${MGBA_HEADLESS:-tools/mgba_src/build/mgba-headless}"
export CM_CHECKPOINT=${CM_CHECKPOINT:-/tmp/ub_ss_field.ss}
ROM=build/unbound-cm.gba
CTL=build/unbound-cm_nocrit.gba
[ -x "$MGBA" ] || { echo "no headless mGBA at $MGBA"; exit 2; }
CM_NO_CRITPLUS2=1 python3 tools/build_patch.py >/dev/null || { echo "  FAIL control build"; exit 1; }
cp "$ROM" "$CTL"
python3 tools/build_patch.py >/dev/null || { echo "  FAIL shipping build"; exit 1; }
if [ ! -f "$CM_CHECKPOINT" ] || [ "$ROM" -nt "$CM_CHECKPOINT" ]; then
    echo "making the free-roam checkpoint (~5 min)..."
    rm -f "$CM_CHECKPOINT"
    timeout 1500 "$MGBA" --script tools/mgba_scripts/mk_checkpoint_field.lua "$ROM" > /tmp/ub_cr_checkpoint.log 2>&1
    [ -f "$CM_CHECKPOINT" ] || { echo "  FAIL no free-roam checkpoint"; exit 1; }
fi
sym() { printf '0x%s' "$(arm-none-eabi-nm build/character_mode.elf | awk -v s="$1" '$3 == s {print $1}')"; }
QUEUE=$(( $(sym CharacterMode_QueueScriptCb1) | 1 ))
EXPECT_CASES=4
pass=0; fail=0
ok() { echo "[PASS] $1"; pass=$((pass+1)); }
bad() { echo "[FAIL] $1"; fail=$((fail+1)); }
battle() {  # label rom move want
    log=/tmp/ub_cr_$1.log
    env MGBA_HEADLESS_DEBUGGER=1 QUEUE_CB1=$QUEUE EXPECT=share LEAD_LV=5 CM_EXPECT_CHECKS=4 FORCE_MOVE=$3 WANT_CRIT=$4 CRIT_BP=0x089CE4D0 \
        timeout 120 "$MGBA" --script tools/mgba_scripts/cm_exp_share_party_test.lua -t "$CM_CHECKPOINT" "$2" > "$log" 2>&1
    grep -ao "CRIT move [0-9]* stage [0-9]*" "$log" | sort -u | tr '\n' ' ' | sed "s/^/  $1: /"; echo
    grep -aq "EXPSHARE RESULT: PASS" "$log"
}
if battle slash $ROM 163 2; then ok "Slash: crit stage 2"; else bad "Slash (/tmp/ub_cr_slash.log)"; fi
if battle slash_ctl $CTL 163 1; then ok "control: Slash keeps Unbound's 1"; else bad "control (/tmp/ub_cr_slash_ctl.log)"; fi
if battle tackle $ROM 33 0; then ok "Tackle: 0"; else bad "Tackle (/tmp/ub_cr_tackle.log)"; fi
if battle neg $CTL 163 2; then bad "NEGATIVE CONTROL: nocrit still gave Slash 2"; else ok "negative control: nocrit asked for 2 fails (want FAIL)"; fi
echo "crit +2 live: $pass passed, $fail failed (want $EXPECT_CASES)"
[ "$fail" -eq 0 ] && [ $((pass+fail)) -eq "$EXPECT_CASES" ]
