#!/usr/bin/env python3
"""Assert a GDB test layer's check tally.

Usage: assert_tally.py --expect N <log> [<log> ...]

Every runner in this directory used to carry its own copy of this logic inline.
All the copies agreed on one thing and were silent about another: they failed
when a `(want N): M` line disagreed with itself, and they failed when NO check
lines were found at all -- but nothing compared the NUMBER of checks against
what the layer was supposed to run.

rowe_parity.md §9 Finding 2: "40 of 74 checks prints '40/40 passed' and exits
0." That is the hole. A check that silently stops firing -- a breakpoint that
no longer resolves, a gdb script that dies half way, a case list that shrank --
reduces what the layer proves without changing its exit status, and the tally
line moves in lockstep so it never looks wrong.

`expect` is a deliberate LITERAL passed by each runner, never a count derived
from the log being checked. A number derived from the thing it is meant to be
pinning cannot fail. Bump it in the same commit that changes the checks.
CM_EXPECT_CHECKS overrides it, for the negative test.

Exit codes are the ones the inline copies used, so callers do not change:
  0  every check passed and the tally is what was expected
  1  a check failed, or the tally is not what was expected
  2  no check lines at all (the gdb session probably died)
"""
import os
import re
import sys


def main():
    argv = sys.argv[1:]
    if len(argv) < 3 or argv[0] != "--expect":
        print("usage: assert_tally.py --expect N <log> [<log> ...]")
        return 1
    expect = int(os.environ.get("CM_EXPECT_CHECKS", argv[1]))
    logs = argv[2:]

    fails = checks = 0
    for log in logs:
        for line in open(log, errors="replace"):
            m = re.search(r"\(want (\d+)(?:=[a-z]+)?\): (\d+)", line)
            if m:
                checks += 1
                if m.group(1) != m.group(2):
                    print("FAIL: %s" % line.strip())
                    fails += 1

    if checks == 0:
        print("NO CHECKS RAN - gdb session failed?")
        return 2

    print("%d/%d checks passed" % (checks - fails, checks))

    if checks != expect:
        print("TALLY MISMATCH: ran %d checks, expected %d. Either a check "
              "stopped running (silently reducing what this layer proves) or "
              "one was added and the runner's expected count was not bumped "
              "with it." % (checks, expect))
        return 1
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
