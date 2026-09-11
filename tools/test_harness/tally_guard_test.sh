#!/bin/bash
# Proves assert_tally.py's guards actually fail (rowe_parity.md §9 Finding 2).
#
# Every runner here used to carry its own inline copy of the tally logic, and
# every copy failed a self-inconsistent check line while never checking HOW MANY
# check lines there were. "40 of 74 checks prints 40/40 passed and exits 0" was
# the measured hole. assert_tally.py closes it; this breaks it on purpose.
#
# The control is the case that matters: a guard that rejected everything would
# pass all the negative cases and look correct.
set -u
cd "$(dirname "$0")" || exit 1
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
printf 'a (want 1): 1\nb (want 2): 2\nc (want 3): 3\n' > "$T/ok.log"
printf 'a (want 1): 1\nb (want 2): 9\n'                > "$T/bad.log"
printf 'no check lines at all\n'                       > "$T/dead.log"

fail=0; pass=0
c() { # <label> <want-exit> <args...>
    local label=$1 want=$2; shift 2
    python3 assert_tally.py "$@" >/dev/null 2>&1
    local got=$?
    if [ "$got" = "$want" ]; then printf '  ok    %-44s exit=%s\n' "$label" "$got"; pass=$((pass+1))
    else printf '  FAIL  %-44s got %s want %s\n' "$label" "$got" "$want"; fail=1; fi
}

echo "assert_tally guard negative test"
c "control: right count, all passing"  0 --expect 3 "$T/ok.log"
c "too few checks ran"                 1 --expect 5 "$T/ok.log"
c "too many checks ran"                1 --expect 2 "$T/ok.log"
c "zero checks is never a pass"        2 --expect 3 "$T/dead.log"
c "a failing check still fails"        1 --expect 2 "$T/bad.log"
c "control: two logs are summed (3+3)"  0 --expect 6 "$T/ok.log" "$T/ok.log"
# The override is how the guard gets broken from outside; prove it really
# overrides, by making a run that would otherwise FAIL pass, and vice versa.
CM_EXPECT_CHECKS=3 c "override rescues a wrong literal"   0 --expect 999 "$T/ok.log"
CM_EXPECT_CHECKS=999 c "override can also break a good one" 1 --expect 3 "$T/ok.log"

# Every runner must declare a count -- a runner that forgets is the hole
# reopening. Checked here so it cannot be reintroduced silently.
missing=""
for f in run_*.sh; do
    grep -q "assert_tally.py" "$f" || continue
    # Either an inline literal, or a variable the runner assigns a literal to
    # (run_gate_test.sh needs a count PER CASE, because its cases assert
    # different numbers). What must never pass is a runner that declares no
    # count at all -- that is the hole reopening.
    grep -qE -- "--expect [0-9]|EXPECT=[0-9]" "$f" || missing="$missing $f"
done
if [ -z "$missing" ]; then
    printf '  ok    %-44s\n' "every runner declares an expected count"; pass=$((pass+1))
else
    printf '  FAIL  runners with no --expect:%s\n' "$missing"; fail=1
fi

# ⭐ And every printed check must be COUNTABLE by that tally, which is the
# guard's own blind spot: assert_tally.py finds checks by matching a literal
# "(want", so a line worded "(key bits seen, want 1)" prints, can fail, and is
# invisible to the count. trade_test.gdb printed NINE T-lines against an
# --expect of 8 for as long as that wording existed, and the two agreed with
# each other the whole time. check_countable_checks.py makes it an error.
cc() { # <label> <want-exit> <dir>
    local label=$1 want=$2 dir=$3
    python3 check_countable_checks.py "$dir" >/dev/null 2>&1
    local got=$?
    if [ "$got" = "$want" ]; then printf '  ok    %-44s exit=%s\n' "$label" "$got"; pass=$((pass+1))
    else printf '  FAIL  %-44s got %s want %s\n' "$label" "$got" "$want"; fail=1; fi
}
G="$T/gdb"; mkdir -p "$G"
printf 'print(f"T0 a thing (want 1): {x}")\n' > "$G/good.gdb"
cc "control: a countable check passes"       0 "$G"
printf 'print(f"T1 b (some prose, want 1): {y}")\n' > "$G/bad.gdb"
cc "an uncountable check fails"              1 "$G"
rm -f "$G/bad.gdb"
cc "control: removing it passes again"       0 "$G"
# ⚠️ And an empty scan is never a pass -- pointed at the wrong directory this
# would otherwise report "0 uncountable" and exit 0, which is the same shape of
# vacuous green the tally guard itself exists to stop.
cc "an empty scan is never a pass"           1 "$T"
cc "the real layers are all countable"       0 "."

[ $fail -eq 0 ] && echo "tally guard test: $pass/$pass PASS" || echo "tally guard test: FAILURES"
exit $fail
