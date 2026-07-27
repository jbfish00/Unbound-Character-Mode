#!/usr/bin/env python3
"""Regenerate README.md's "## Character numbers" section from the injected data.

Unbound selects a character by NUMBER (CFRU's ChooseNumberScreen, special 0x0B3),
not by a typed name-code like the Radical Red sibling, so the table a player needs
is the numbered one. It lived only in dist/CHARACTERS.md, which is built into the
distribution zip -- someone reading the repo on GitHub had no list at all and no
way to know what to type at the prompt.

Everything comes from emit_character_list.load_rows(), i.e. from characters.bin /
rosters.bin -- the same bytes the ROM enforces, and the same call dist/CHARACTERS.md
uses, so the two tables cannot disagree. Hidden characters (CHAR_FLAG_HIDDEN, flags
bit1) are omitted from both: the select screen re-asks on their numbers, so listing
one would document a number that does not work.

Run after emit_characters.py (and after emit_character_list.py, though order between
those two does not matter):
    python3 tools/character_mode/emit_readme_codes.py
"""
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
README = os.path.join(ROOT, "README.md")

sys.path.insert(0, HERE)
from emit_character_list import load_rows

SECTION_START = "## Character numbers"
SECTION_END = "## Credits"


def main():
    rows, n_hidden = load_rows()
    total = len(rows) + n_hidden

    by_gen = defaultdict(list)
    for r in rows:
        by_gen[r["generation"]].append(r)
    gens = sorted(by_gen, key=int)

    out = [SECTION_START, "",
           "Enter this number at the Character Mode prompt during a new game.",
           "The same list, with roster sizes, ships in the patch as",
           "[`dist/CHARACTERS.md`](dist/CHARACTERS.md).", ""]
    if n_hidden:
        out += ["Numbers are not contiguous: %d of the %d records are hidden because"
                % (n_hidden, total),
                "fewer than six of their Pokémon fully evolve in this game's dex, and",
                "the select screen re-asks on those numbers. The gaps are deliberate --",
                "character ids are save data, so the hidden records keep their slots and",
                "nothing is renumbered.", ""]
    for gen in gens:
        out += ["### Generation %s" % gen, "",
                "| # | Character | Role | Starter Pokemon |",
                "|---|---|---|---|"]
        for r in by_gen[gen]:
            out.append("| **%d** | %s | %s | %s |"
                       % (r["number"], r["name"], r["category"], r["starter"]))
        out.append("")

    text = open(README, encoding="utf-8").read()
    if SECTION_START in text:
        start = text.index(SECTION_START)
        end = text.index(SECTION_END)
        text = text[:start] + "\n".join(out) + "\n" + text[end:]
    else:
        # First run: park the section immediately above Credits.
        end = text.index(SECTION_END)
        text = text[:end] + "\n".join(out) + "\n" + text[end:]

    # The prose counts are generated too. Rewriting only the table is how the
    # sibling repo's intro sentence sat at "199 characters" through two rebuilds.
    text, n1 = re.subn(r"pick one of \*\*\d+ iconic Pokémon",
                       "pick one of **%d iconic Pokémon" % len(rows), text, count=1)
    text, n2 = re.subn(r"The character table holds \d+ records; \d+ are hidden",
                       "The character table holds %d records; %d are hidden"
                       % (total, n_hidden), text, count=1)
    for ok, what in ((n1, "intro character-count sentence"),
                     (n2, "'table holds N records' sentence")):
        if not ok:
            print("  !! could not find the %s in README.md -- check it by hand" % what)

    open(README, "w", encoding="utf-8").write(text)
    print("rewrote README.md's character-number tables: %d selectable characters "
          "across generations %s (%d hidden below the threshold, omitted)"
          % (len(rows), ", ".join(gens), n_hidden))


if __name__ == "__main__":
    main()
