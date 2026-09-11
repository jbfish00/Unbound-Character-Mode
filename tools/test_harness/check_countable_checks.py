#!/usr/bin/env python3
"""Every printed check must be COUNTABLE by assert_tally.py.

assert_tally.py pins the NUMBER of checks a layer runs, so a check that stops
firing cannot silently reduce what the layer proves. That guard has one blind
spot of its own: it finds check lines by matching a LITERAL `"(want"`, so a line
worded `"(key bits seen, want 1): 1"` is not a check as far as the tally is
concerned -- it prints, it is read by a human, it can fail, and it is invisible
to the count.

That was not hypothetical. trade_test.gdb printed NINE `T<n> ... (want N)` lines
and its runner declared `--expect 8`, and the two agreed with each other for as
long as the wording existed. The tally was not wrong; it was measuring eight of
the nine checks and saying so in a way nobody could tell from a green run.

So this scans the layers themselves rather than their output: any `print(...)`
that mentions `want` must carry assert_tally's anchor, `(want N):`. Put the
prose BEFORE the opening parenthesis, not inside it.

Usage: check_countable_checks.py <dir> [<dir> ...]
Exit 0 = every printed check is countable, 1 = at least one is not.
"""
import pathlib
import re
import sys

# The same anchor assert_tally.py uses, minus the trailing value -- in the
# source the value is an f-string expression, not a literal digit.
ANCHOR = re.compile(r"\(want \d+(?:=[a-z]+)?\): ")


def main():
    dirs = sys.argv[1:]
    if not dirs:
        print("usage: check_countable_checks.py <dir> [<dir> ...]")
        return 1
    bad = []
    scanned = 0
    for d in dirs:
        for f in sorted(pathlib.Path(d).glob("*.gdb")):
            for i, line in enumerate(f.read_text(errors="replace").splitlines(), 1):
                if "want" not in line or "print(" not in line:
                    continue
                scanned += 1
                if not ANCHOR.search(line):
                    bad.append((f, i, line.strip()))
    if not scanned:
        print("NO CHECK LINES FOUND - wrong directory?")
        return 1
    for f, i, line in bad:
        print("UNCOUNTABLE %s:%d  %s" % (f, i, line[:100]))
        print("            -> assert_tally.py matches a literal '(want', so this "
              "line never enters its own layer's tally.")
    print("%d printed checks scanned, %d uncountable" % (scanned, len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
