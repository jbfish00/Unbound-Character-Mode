#!/usr/bin/env python3
"""Prove ROSTERS.md describes exactly what the BUILT ROM offers.

`emit_roster_docs.py` generates the docs from `rosters.bin`, so docs and build
agree by construction -- which means a bug in the generator would make them agree
with each other and still disagree with the game. This closes that loop by
reading the roster blob and the character count back out of
`build/unbound-cm.gba` at the addresses the injector actually wrote them to, and
re-deriving every doc row from those bytes.

Checks:
  1. the roster blob in the built ROM == rosters.bin (the docs' input is real)
  2. the in-ROM u16 character count == the manifest's count
  3. every character in ROSTERS.md exists in the manifest, and vice versa
  4. every Pokemon listed under a character is genuinely in that character's
     in-ROM roster (bases + injected family expansion)
  5. every final evolution the in-ROM roster reaches is actually listed
  6. the sprite pages mirror ROSTERS.md character for character, row for row
  7. the character counts in ROSTERS.md, ROSTERS_SPRITES.md and dist/README
     agree with the ROM

Exit 1 on any mismatch. Run after emit_roster_docs.py, on a built ROM.
"""
import importlib.util
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
BUILT = os.path.join(ROOT, "build", "unbound-cm.gba")
INJECT_FILE_OFF = 0x00B2B280          # keep in sync with tools/build_patch.py
REGION_RE = re.compile(r"^(Alolan|Galarian|Hisuian|Paldean)\s+")


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def parse_doc(text):
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^### (.+?) — ", line)
        if m:
            cur = m.group(1).strip()
            out[cur] = []
            continue
        m = re.match(r"^\| (.+?) \| (.*?) \|$", line)
        if m and cur and m.group(1) not in ("Pokémon", "---"):
            out[cur].append(m.group(1).strip())
    return out


def main():
    fails = []
    if not os.path.isfile(BUILT):
        print("no built ROM at %s -- run tools/build_patch.py first"
              % os.path.relpath(BUILT, ROOT))
        return 1
    with open(BUILT, "rb") as f:
        rom = f.read()

    docs = _load("emit_roster_docs")
    emit = _load("emit_characters")
    ms = docs.load_map_species()

    with open(os.path.join(HERE, "characters_manifest.json")) as f:
        manifest = json.load(f)["characters"]
    with open(os.path.join(HERE, "characters.bin"), "rb") as f:
        chars_bin = f.read()
    with open(os.path.join(HERE, "rosters.bin"), "rb") as f:
        staged = f.read()

    # The injector lays the block out as [characters][rosters][names][u16 count],
    # so both offsets follow from the artifact sizes -- no second hardcoded
    # address to drift out of sync.
    off_rosters = INJECT_FILE_OFF + len(chars_bin)
    in_rom = rom[off_rosters:off_rosters + len(staged)]
    if in_rom != staged:
        fails.append("the roster blob in the built ROM differs from rosters.bin "
                     "-- the docs were generated from data the ROM does not carry")

    n = len(manifest)
    with open(os.path.join(HERE, "names.bin"), "rb") as f:
        names_len = len(f.read())
    off_nameptrs = (INJECT_FILE_OFF + len(chars_bin) + len(staged)
                    + names_len + 3) & ~3
    off_count = off_nameptrs + n * 4
    # ...and the wild metadata follows the count, same derived-from-sizes rule
    # as everything else in this block (tools/build_patch.py layout).
    off_wild_meta = (off_count + 2 + 3) & ~3
    (rom_count,) = struct.unpack_from("<H", rom, off_count)
    if rom_count != n:
        fails.append("the ROM's own character count is %d, the manifest has %d"
                     % (rom_count, n))

    # CHAR_FLAG_HIDDEN (bit1 of flags, byte 11 of each 16-byte record), read
    # out of the BUILT ROM -- this is the byte CharacterMode_IsCharacterSelectable
    # actually tests, so checking it here closes the loop between the docs and
    # the gate rather than trusting the manifest that produced both.
    rom_chars = rom[INJECT_FILE_OFF:INJECT_FILE_OFF + len(chars_bin)]
    if rom_chars != chars_bin:
        fails.append("the character records in the built ROM differ from "
                     "characters.bin -- the ROM was not built from this data")
    rom_hidden = {manifest[i]["character"]
                  for i in range(min(n, len(rom_chars) // 16))
                  if rom_chars[16 * i + 11] & 0x2}
    man_hidden = {c["character"] for c in manifest if c.get("hidden")}
    if rom_hidden != man_hidden:
        fails.append("the ROM hides %s but the manifest hides %s"
                     % (sorted(rom_hidden), sorted(man_hidden)))
    drops = set(docs.load_unselectable())
    if rom_hidden != drops:
        fails.append("the ROM hides %d character(s), character_drops.json lists "
                     "%d (only in ROM: %s; only in drops: %s)"
                     % (len(rom_hidden), len(drops),
                        sorted(rom_hidden - drops), sorted(drops - rom_hidden)))
    selectable = {c["character"] for c in manifest} - rom_hidden

    const_id = ms.species_ids()
    id_const = {v: k for k, v in const_id.items()}
    id_name = {v: k for k, v in ms.name_to_id().items()}
    kids = docs.evolution_children(ms.DONOR, const_id)
    dex = docs.national_dex(ms.DONOR, const_id)
    canonical = {}
    for sid in sorted(dex):
        canonical.setdefault(dex[sid], sid)

    def rom_roster(rec):
        off, ids = rec["roster_offset"], []
        while True:
            (sid,) = struct.unpack_from("<H", in_rom, off)
            off += 2
            if sid == 0:
                break
            ids.append(sid)
        return ids

    def row_name(sid):
        plain = id_name.get(canonical.get(dex.get(sid, 0), sid)) \
            or id_name.get(sid) or "#%d" % sid
        region = docs.regional_form(id_const.get(sid, ""))
        return "%s %s" % (region, plain) if region else plain

    rom_names, rom_finals = {}, {}
    for rec in manifest:
        ids = rom_roster(rec)
        rom_names[rec["character"]] = {row_name(s) for s in ids} \
            | {id_name.get(s) for s in ids if id_name.get(s)}
        shown = set()
        for sid in ids:
            if kids.get(sid):
                continue
            num = dex.get(sid)
            if not num or num > docs.MAX_NATIONAL_DEX:
                continue
            const = id_const.get(sid, "")
            if not docs.regional_form(const):
                base = canonical.get(num, sid)
                if kids.get(base):
                    continue
                sid = base
            shown.add(row_name(sid))
        rom_finals[rec["character"]] = shown

    doc = parse_doc(read(os.path.join(ROOT, "ROSTERS.md")))

    for char in doc:
        if char not in rom_names:
            fails.append("%s: in ROSTERS.md but not in characters_manifest.json"
                         % char)
    # Selection gating IS injected, so the docs must list exactly the characters
    # the ROM will let the player choose: every selectable one present, and no
    # hidden one present. Both directions matter -- documenting a character the
    # select screen refuses is the same defect as omitting one it accepts.
    for char in selectable:
        if char not in doc:
            fails.append("%s: offered by the ROM but missing from ROSTERS.md" % char)
    for char in rom_hidden:
        if char in doc:
            fails.append("%s: hidden by the ROM but still listed in ROSTERS.md" % char)

    for char, listed in doc.items():
        if char not in rom_names:
            continue
        for mon in listed:
            if mon not in rom_names[char] \
                    and REGION_RE.sub("", mon) not in rom_names[char]:
                fails.append("%s: doc lists %s, which is not in its in-ROM roster"
                             % (char, mon))
        missing = rom_finals[char] - set(listed)
        if missing:
            fails.append("%s: in-ROM roster reaches %d final evolution(s) the doc "
                         "omits (%s)"
                         % (char, len(missing), ", ".join(sorted(missing)[:6])))

    sprite_chars, sprite_rows, missing_src = {}, 0, 0
    sdir = os.path.join(ROOT, "sprites")
    for path in sorted(os.listdir(sdir)):
        if not re.match(r"gen_\d+\.md$", path):
            continue
        cur = None
        for line in read(os.path.join(sdir, path)).splitlines():
            m = re.match(r"^### (.+?) — ", line)
            if m:
                cur = m.group(1).strip()
                sprite_chars[cur] = 0
                continue
            for cell in re.finditer(
                    r"<sub>([^<]+)</sub>(<br><sub><i>([^<]*)</i></sub>)?", line):
                if cur is None:
                    continue
                sprite_chars[cur] += 1
                sprite_rows += 1
                if not cell.group(3):
                    missing_src += 1
    for char in doc:
        if char not in sprite_chars:
            fails.append("%s: in ROSTERS.md but missing from the sprite pages" % char)
        elif sprite_chars[char] != len(doc[char]):
            fails.append("%s: sprite pages show %d Pokemon, ROSTERS.md lists %d"
                         % (char, sprite_chars[char], len(doc[char])))
    for char in sprite_chars:
        if char not in doc:
            fails.append("%s: on a sprite page but not in ROSTERS.md" % char)

    # ---- ENCOUNTERS.md (game_plans/legendary_encounters.md §3) ----
    # Recompute both pools from the BUILT ROM's roster blob plus the wild
    # metadata the picker reads, and require the doc to describe exactly that.
    enc_path = os.path.join(ROOT, "ENCOUNTERS.md")
    if not os.path.isfile(enc_path):
        fails.append("ENCOUNTERS.md missing -- run emit_encounter_tables.py")
    else:
        enc_text = read(enc_path)
        enc_chars = set(re.findall(r"^### (.+?) — ", enc_text, re.M))
        for char in selectable - enc_chars:
            fails.append("%s: selectable but missing from ENCOUNTERS.md" % char)
        for char in enc_chars - selectable:
            fails.append("%s: in ENCOUNTERS.md but not selectable" % char)

        with open(os.path.join(HERE, "wild_species_meta.bin"), "rb") as f:
            meta_blob = f.read()
        meta_in_rom = rom[off_wild_meta:off_wild_meta + len(meta_blob)] \
            if off_wild_meta else b""
        if off_wild_meta and meta_in_rom != meta_blob:
            fails.append("the wild-species metadata in the built ROM differs from "
                         "wild_species_meta.bin -- ENCOUNTERS.md describes "
                         "encounters the ROM cannot produce")

        n_legend = n_only_legend = n_empty = 0
        for rec in manifest:
            if rec["character"] in rom_hidden:
                continue
            legend, plain = set(), set()
            for sid in rom_roster(rec):
                if sid * 6 + 6 > len(meta_blob):
                    continue
                _lo, _hi, mflags, _pad, root = struct.unpack_from("<BBBBH", meta_blob, sid * 6)
                (legend if (mflags & 1) else plain).add(root)
            if legend:
                n_legend += 1
            if legend and not plain:
                n_only_legend += 1
            if not legend and not plain:
                n_empty += 1
        m = re.search(r"\*\*(\d+) of (\d+) have at least one legendary", enc_text)
        if not m:
            fails.append("ENCOUNTERS.md has no legendary-coverage line -- the "
                         "check that would catch drift cannot run")
        elif (int(m.group(1)), int(m.group(2))) != (n_legend, len(selectable)):
            fails.append("ENCOUNTERS.md says %s of %s have a legendary; the ROM's "
                         "own data says %d of %d"
                         % (m.group(1), m.group(2), n_legend, len(selectable)))
        # The catch-nothing failure mode must be reported accurately or not at
        # all -- this is the whole point of the doc.
        if n_empty and "NO wild pool at all" not in enc_text:
            fails.append("%d character(s) have an empty wild pool but "
                         "ENCOUNTERS.md does not say so" % n_empty)

    # The README's "## Character numbers" table is what a player reads to know
    # what to type at the prompt, so a wrong number there is a wrong answer at
    # the only moment the mode asks a question. Check the NUMBER, not just the
    # count: the numbers are non-contiguous (hidden records keep their slots),
    # which is exactly the shape that invites an off-by-one when regenerated.
    readme_nums = {}
    readme_txt = read(os.path.join(ROOT, "README.md"))
    if "## Character numbers" in readme_txt:
        sect = readme_txt[readme_txt.index("## Character numbers"):]
        sect = sect[:sect.index("## Credits")] if "## Credits" in sect else sect
        for num, name in re.findall(r"^\| \*\*(\d+)\*\* \| ([^|]+?) \|", sect,
                                    re.M):
            readme_nums[name.strip()] = int(num)
        expected = {c["character"]: i + 1 for i, c in enumerate(manifest)
                    if c["character"] not in rom_hidden}
        for char, want in sorted(expected.items()):
            got = readme_nums.get(char)
            if got is None:
                fails.append("%s: offered by the ROM but missing from the "
                             "README's number table" % char)
            elif got != want:
                fails.append("README lists %s as number %d; the ROM's table puts "
                             "it at %d" % (char, got, want))
        for char in sorted(set(readme_nums) - set(expected)):
            fails.append("%s: in the README's number table but the ROM does not "
                         "offer it" % char)
    else:
        fails.append("README.md has no '## Character numbers' section -- run "
                     "emit_readme_codes.py")

    for path, pat in (("ROSTERS.md", r"\*\*(\d+) characters"),
                      ("ROSTERS_SPRITES.md", r"\*\*(\d+) characters"),
                      (os.path.join("dist", "README.md"), r"pick one of (\d+) iconic"),
                      # The repo README carries the SAME sentence and was NOT
                      # checked -- it sat at 178 while the ROM shipped 208. The
                      # guard existed and was pointed one path entry away from
                      # the file that was wrong.
                      ("README.md", r"pick one of \*\*(\d+) iconic")):
        full = os.path.join(ROOT, path)
        if not os.path.isfile(full):
            print("   note: %s not built yet, skipping its count check" % path)
            continue
        m = re.search(pat, read(full))
        if not m:
            fails.append("no character count found in %s -- the check that would "
                         "catch drift cannot run" % path)
        elif int(m.group(1)) != len(doc):
            fails.append("%s says %s characters, ROSTERS.md lists %d"
                         % (path, m.group(1), len(doc)))

    print("built ROM:    %d-char roster blob read at file 0x%X, count u16 = %d%s"
          % (n, off_rosters, rom_count, "" if in_rom == staged else "  (MISMATCH)"))
    print("ROSTERS.md:   %d characters, %d Pokemon rows"
          % (len(doc), sum(len(v) for v in doc.values())))
    print("sprite pages: %d characters, %d cells, %d without a source line"
          % (len(sprite_chars), sprite_rows, missing_src))
    print("threshold:    %d characters hidden from the select screen by "
          "CHAR_FLAG_HIDDEN in the built ROM; %d selectable and documented"
          % (len(rom_hidden), len(selectable)))
    if os.path.isfile(enc_path):
        print("encounters:   %d characters, %d with a legendary pool, %d "
              "legendaries-only, %d with NO pool%s"
              % (len(enc_chars), n_legend, n_only_legend, n_empty,
                 "" if meta_in_rom == meta_blob else "  (META MISMATCH)"))
    if fails:
        print("\n%d MISMATCHES:" % len(fails))
        for f in fails[:25]:
            print("   " + f)
        if len(fails) > 25:
            print("   ... and %d more" % (len(fails) - 25))
        return 1
    print("\nOK: the documentation matches what the built ROM offers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
