#!/usr/bin/env python3
"""Build the Character Mode patched ROM for Pokemon Unbound v2.1.1.1.

Pipeline (all addresses from docs/ROUTINE_MAP.md v8, double-confirmed):
  1. verify the source ROM against rom.sha1
  2. compile src/character_mode.c (arm-none-eabi-gcc, Thumb, -mlong-calls)
  3. lay out data blobs + code in the confirmed-free block at file 0x00B2B280
  4. link at the real injection address (src/unbound.ld pins engine symbols)
  5. splice data + code into a ROM copy
  6. apply the hooks:
       a. bl retarget at 0x089C8CA6 (atkEF_handleballthrow's
          FlagGet(FLAG_NO_CATCHING) call -> CharacterMode_CatchFlagGet)
       b. 8-byte entry trampoline at 0x089C905C (GiveMonToPlayer ->
          CharacterMode_GiveMonToPlayer)
       c. bl retarget of the 4 real random-table-roll `bl CreateWildMon`
          call sites (TryGenerateWildMon primary+double, GenerateFishingWildMon
          primary+double) -> CharacterMode_CreateWildMon (10% chance to
          override the wild-roll species with a roster member;
          docs/ROUTINE_MAP.md v17 — raid/swarm/scripted/DexNav sites
          deliberately NOT hooked)
  7. self-verify: original-byte preconditions, free-space precondition,
     disassemble the patched sites back and check the expected shape
  8. write build/unbound-cm.gba (+ .sha1) and, if flips is present,
     build/unbound-cm.bps (this flips build only supports IPS/BPS)

Distribution is ALWAYS the patch, never the ROM.
"""
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ROM = os.path.join(ROOT, "rom", "Pokemon Unbound (v2.1.1.1).gba")
BUILD = os.path.join(ROOT, "build")
CM_DIR = os.path.join(HERE, "character_mode")

sys.path.insert(0, CM_DIR)
import optin_script
import egg_hook
import trade_hook

ROM_BASE = 0x08000000

# Injection block: confirmed 0xFF-free, 147 KiB @ file 0x00B2B280 (docs/FREE_SPACE.md)
INJECT_FILE_OFF = 0x00B2B280
INJECT_ROM_ADDR = ROM_BASE + INJECT_FILE_OFF
INJECT_BLOCK_LEN = 147 * 1024

# Phase 3 character sprites (2026-07-25). The 147 KB block above is nearly full
# and the sprite blobs are ~122 KB, so they live in the separate 344 KB 0xFF run
# at file 0x015FBC90. Additive: this never touches the engine's trainer-pic
# table, so locating that table is not a prerequisite and nothing the game
# already draws changes.
CM_SPRITE_PTRS_FILE_OFF  = 0x015FC000
CM_SPRITE_BLOBS_FILE_OFF = 0x015FC800

# Hook sites (docs/ROUTINE_MAP.md v8)
CATCH_BL_FILE_OFF = 0x9C8CA6          # bl call_via_r6 (FlagGet) inside atkEF_handleballthrow
CATCH_BL_ORIG = bytes.fromhex("00F0E6FE")
GMTP_FILE_OFF = 0x9C905C              # GiveMonToPlayer entry
GMTP_ORIG = bytes.fromhex("70B504001CF0CEFE")
# Starter grant: the givemon(0x79) handler's `bl ScriptGiveMon 0x080A011C`
# (docs/ROUTINE_MAP.md v9) — retargeted to CharacterMode_ScriptGiveMon so the
# first mon given while Character Mode is active becomes the character's
# roster[0] starter.
GIVEMON_BL_FILE_OFF = 0x6C030
GIVEMON_BL_ORIG = bytes.fromhex("34F074F8")
# The handler is ~11MB below the injection block — out of Thumb bl range
# (±4MB) — so the bl goes through an 8-byte near veneer placed in a
# separate confirmed-0xFF block: `ldr r3,[pc,#0]; bx r3; .word wrapper|1`.
# r3 carries ScriptGiveMon's unused1 arg, which CFRU itself documents as
# the hook-in arg ("don't use it for anything") — clobbering it is safe,
# and the wrapper forwards it unread.
GIVEMON_VENEER_FILE_OFF = 0x1B2940  # inside the 34KB 0xFF run @ 0x1B2938
# Character-select (v3): the reserved gSpecials[0x1B6] slot (script-
# unreachable stale entry, docs/ROUTINE_MAP.md v8.1) is repointed to the
# injected name-buffering special used by the number-entry select flow.
SPECIAL_1B6_FILE_OFF = 0x160438
SPECIAL_1B6_ORIG = bytes.fromhex("c1371508")  # stale 0x081537C1

# Wild-encounter roster override (docs/ROUTINE_MAP.md v17): CreateWildMon's
# real body (0x08A14838, behind the low-ROM veneer at 0x080829FC) is left
# 100% untouched; instead ONLY the 4 real table-roll `bl CreateWildMon` call
# sites inside the compiled wild_encounter.c unit are retargeted to
# CharacterMode_CreateWildMon. They are near calls (well within Thumb bl's
# ±4MB range of the 0x00B2B280 injection block), so no veneer is needed.
#
# Per-site attribution (docs/ROUTINE_MAP.md v17): every `bl` to 0x08A14838
# in the whole ROM was located (9 near callers + 2 low-ROM veneer callers +
# 1 function pointer) and each was decoded by argument shape + surrounding
# calls against the CFRU donor's wild_encounter.c source. Of the 9 near
# callers, exactly these 4 are genuine random-table rolls; the other
# CreateWildMon reachers are deliberately EXCLUDED:
#   - 0x8A14A4A  CreateScriptedWildMon (setwildbattle; r2=0, r3=firstMon) —
#                a SCRIPTED encounter, spec says never touch it.
#   - 0x8A14C3A  sp117_CreateRaidMon (r2=0, r3=1, FlagSet raid/hidden-ability
#                flags, species+level from two globals) — raid, not a roll.
#   - 0x8A14EAC  TryGenerateSwarmMon (guarded by Random()%100 < SWARM_CHANCE)
#                — swarm, matches the RadicalRed sibling's own exclusion.
#   - 0x89D7B48 / 0x89D863E  DexNav (FindHeaderIndexWithLetter for r2) — not
#                a table roll.
#   - 0x8082B52 / 0x8082B8E  DEAD low-ROM vanilla TryGenerateWildMon /
#                GenerateFishingWildMon copies: their entry points were
#                overwritten with veneers pointing at the live high-ROM
#                versions below, so this old code is unreachable.
#   - function pointer at 0x09EC354C -> the veneer (0x080829FD), a direct
#                pointer call that bypasses these call sites entirely and so
#                never sees the override — correct (not a random roll).
# All four kept sites cover the required set: grass/cave, surf, and rock
# smash all funnel through the single high-ROM TryGenerateWildMon
# (0x08A14EC4, called by Standard/RockSmash/SweetScent/StartRandom
# encounter entries), whose two CreateWildMon calls are the primary +
# double-battle sites; both fishing-rod tiers funnel through
# GenerateFishingWildMon (inlined into FishingWildEncounter 0x08A15BE8).
WILD_CALL_SITES = {
    "trygenwild_primary_0x8a14fe6": (0xA14FE6, bytes.fromhex("fff727fc")),
    "trygenwild_double_0x8a150c4":  (0xA150C4, bytes.fromhex("fff7b8fb")),
    "fishing_primary_0x8a15c20":    (0xA15C20, bytes.fromhex("fef70afe")),
    "fishing_double_0x8a15c54":     (0xA15C54, bytes.fromhex("fef7f0fd")),
}


def sha1(data):
    return hashlib.sha1(data).hexdigest()


def run(cmd, **kw):
    print("  $", " ".join(cmd))
    subprocess.run(cmd, check=True, **kw)


def thumb_bl(from_addr, to_addr):
    """Encode a Thumb-1 BL instruction pair at from_addr targeting to_addr."""
    offset = to_addr - (from_addr + 4)
    assert -0x400000 <= offset < 0x400000, f"BL out of range: {offset:#x}"
    imm = (offset >> 1) & 0x3FFFFF
    hi = 0xF000 | ((imm >> 11) & 0x7FF)
    lo = 0xF800 | (imm & 0x7FF)
    return struct.pack("<HH", hi, lo)


def main():
    os.makedirs(BUILD, exist_ok=True)

    # 1. source ROM checksum
    with open(ROM, "rb") as f:
        rom = bytearray(f.read())
    with open(os.path.join(ROOT, "rom.sha1")) as f:
        want = f.read().split()[0]
    got = sha1(rom)
    assert got == want, f"ROM sha1 mismatch: {got} != {want}"
    print(f"ROM verified: {got}")

    # 2. compile
    obj = os.path.join(BUILD, "character_mode.o")
    # The wild-override picker collects one entry per DISTINCT non-legendary
    # family root on the roster, into a fixed-size stack array. Compute the real
    # worst case from the emitted data (same rule the shim applies: skip
    # out-of-range and legendary-flagged species, dedupe by familyRoot) and size
    # the array from it, rather than trusting a literal that silently truncates.
    _meta = open(os.path.join(CM_DIR, "wild_species_meta.bin"), "rb").read()
    _meta_count = len(_meta) // 6
    with open(os.path.join(CM_DIR, "characters_manifest.json")) as _f:
        _cm = json.load(_f)["characters"]
    _worst = 0
    for _c in _cm:
        _roots = set()
        for _sp in (_c.get("roster_species_ids") or []):
            if _sp >= _meta_count:
                continue
            _lmin, _lmax, _flags, _pad, _root = struct.unpack_from("<BBBBH", _meta, _sp * 6)
            if _flags & 1:
                continue
            _roots.add(_root)
        _worst = max(_worst, len(_roots))
    max_wild_roots = _worst + 16          # margin for roster growth
    assert max_wild_roots <= 160, (
        f"MAX_WILD_FAMILY_ROOTS {max_wild_roots} is too much stack for the "
        f"wild picker -- switch it to a static buffer instead of growing it")
    print(f"wild picker: worst-case family roots = {_worst} -> cap {max_wild_roots}")

    # Threshold-gate self-test fixtures, DERIVED. Hardcoding either id is the
    # trap this project has hit repeatedly: after a roster change a literal
    # index silently names a different character, and the check then passes for
    # the wrong reason rather than failing as a stale fixture.
    _hidden_ids = [_i + 1 for _i, _c in enumerate(_cm) if _c.get("hidden")]
    _shown_ids = [_i + 1 for _i, _c in enumerate(_cm) if not _c.get("hidden")]
    assert _shown_ids, "every character is hidden -- nothing would be selectable"
    test_hidden_id = _hidden_ids[0] if _hidden_ids else 0
    test_shown_id = _shown_ids[0]
    print(f"threshold gate: {len(_hidden_ids)} of {len(_cm)} hidden; self-test uses "
          f"hidden id {test_hidden_id or '(none)'}, selectable id {test_shown_id}")

    # Legendary-encounter self-test fixtures, also DERIVED. Split each roster
    # into legendary / non-legendary families using the SAME wild_species_meta
    # legendary bit the picker reads, so the test and the feature can never
    # disagree about what counts as a legendary.
    def _split(rec):
        legend, plain = set(), set()
        for _sp in (rec.get("roster_species_ids") or []):
            if _sp >= _meta_count:
                continue
            _lmin, _lmax, _flags, _pad, _root = struct.unpack_from("<BBBBH", _meta, _sp * 6)
            (legend if (_flags & 1) else plain).add(_root)
        return legend, plain

    test_legend_id = test_nolegend_id = test_alllegend_id = 0
    for _i, _c in enumerate(_cm):
        _legend, _plain = _split(_c)
        if _legend and _plain and not test_legend_id:
            test_legend_id = _i + 1                 # both kinds: once-each applies
        if not _legend and _plain and not test_nolegend_id:
            test_nolegend_id = _i + 1               # no legendary: must be unaffected
        if _legend and not _plain and not test_alllegend_id:
            test_alllegend_id = _i + 1              # §1.2 exemption (Cogita/Tobias)
    assert test_legend_id and test_nolegend_id, (
        "cannot derive legendary-encounter fixtures: need one character with both "
        "legendary and non-legendary families, and one with neither")
    _n_with_legend = sum(1 for _c in _cm if _split(_c)[0])
    print(f"legendary encounters: {_n_with_legend} of {len(_cm)} characters have one; "
          f"self-test uses mixed id {test_legend_id}, no-legendary id {test_nolegend_id}, "
          f"all-legendary id {test_alllegend_id or '(none)'}")

    run(["arm-none-eabi-gcc", "-c", "-g", "-mthumb", "-mcpu=arm7tdmi", "-mtune=arm7tdmi",
         "-O2", "-ffreestanding", "-fno-builtin", "-mlong-calls", "-Wall", "-Wextra",
         f"-DMAX_WILD_FAMILY_ROOTS={max_wild_roots}",
         f"-DTEST_HIDDEN_ID={test_hidden_id}", f"-DTEST_SHOWN_ID={test_shown_id}",
         f"-DTEST_LEGEND_CHAR_ID={test_legend_id}",
         f"-DTEST_NOLEGEND_CHAR_ID={test_nolegend_id}",
         f"-DTEST_ALLLEGEND_CHAR_ID={test_alllegend_id}",
         "-Werror", "-o", obj, os.path.join(ROOT, "src", "character_mode.c")])

    # 3. layout: [characters.bin][rosters.bin][names.bin][u16 count][pad]
    #            [wild_species_meta.bin][pad][code]
    with open(os.path.join(CM_DIR, "characters.bin"), "rb") as f:
        characters = f.read()
    with open(os.path.join(CM_DIR, "rosters.bin"), "rb") as f:
        rosters = f.read()
    with open(os.path.join(CM_DIR, "names.bin"), "rb") as f:
        names = f.read()
    with open(os.path.join(CM_DIR, "wild_species_meta.bin"), "rb") as f:
        wild_meta = f.read()
    # needed to derive the live trade test's discriminating character pair by
    # roster content rather than by hardcoded index -- see trade_debug_script
    with open(os.path.join(CM_DIR, "characters_manifest.json")) as f:
        manifest = json.load(f)
    n_chars = len(characters) // 16
    assert n_chars == len(manifest["characters"]), \
        ("characters.bin holds %d records but the manifest lists %d -- re-run "
         "emit_characters.py" % (n_chars, len(manifest["characters"])))

    def _expanded(rec):
        off, ids = rec["roster_offset"], set()
        while True:
            (sid,) = struct.unpack_from("<H", rosters, off)
            off += 2
            if sid == 0:
                return ids
            ids.add(sid)


    off_characters = 0
    off_rosters = off_characters + len(characters)
    off_names = off_rosters + len(rosters)
    off_nameptrs = (off_names + len(names) + 3) & ~3
    off_count = off_nameptrs + n_chars * 4
    off_wild_meta = (off_count + 2 + 3) & ~3
    off_code = (off_wild_meta + len(wild_meta) + 3) & ~3

    addr = lambda off: INJECT_ROM_ADDR + off

    # per-character name pointer array (for the scrolling character list):
    # record layout characters.bin: nameOffset u32 at +0 of each 16B record
    nameptrs = b"".join(
        struct.pack("<I", addr(off_names) + struct.unpack_from("<I", characters, 16 * i)[0])
        for i in range(n_chars))

    # 4. link (unbound.ld as an input script augments the default one)
    elf = os.path.join(BUILD, "character_mode.elf")
    run(["arm-none-eabi-ld",
         f"-Ttext={addr(off_code):#x}",
         "--defsym", f"gCharacterTable={addr(off_characters):#x}",
         "--defsym", f"gCharacterRosters={addr(off_rosters):#x}",
         "--defsym", f"gCharacterNames={addr(off_names):#x}",
         "--defsym", f"gCharacterNamePtrs={addr(off_nameptrs):#x}",
         "--defsym", f"gCharacterCount={addr(off_count):#x}",
         "--defsym", f"gWildSpeciesMeta={addr(off_wild_meta):#x}",
         # The sprite pointer table lives in the SEPARATE free run (see
         # CM_SPRITE_PTRS_FILE_OFF), not in this injection block, so its
         # address is a fixed constant rather than an offset into `addr`.
         "--defsym", f"gCharacterSpritePtrs={ROM_BASE + CM_SPRITE_PTRS_FILE_OFF:#x}",
         "-o", elf, obj, os.path.join(ROOT, "src", "unbound.ld")])
    code_bin = os.path.join(BUILD, "character_mode.bin")
    run(["arm-none-eabi-objcopy", "-O", "binary", "--only-section=.text",
         "--only-section=.rodata", elf, code_bin])
    with open(code_bin, "rb") as f:
        code = f.read()

    # symbol addresses out of the linked ELF
    nm = subprocess.run(["arm-none-eabi-nm", elf], check=True,
                        capture_output=True, text=True).stdout
    syms = {}
    for line in nm.splitlines():
        parts = line.split()
        if len(parts) == 3:
            syms[parts[2]] = int(parts[0], 16)
    catch_hook = syms["CharacterMode_CatchFlagGet"]
    gmtp_hook = syms["CharacterMode_GiveMonToPlayer"]
    sgm_hook = syms["CharacterMode_ScriptGiveMon"]
    wild_hook = syms["CharacterMode_CreateWildMon"]
    print(f"CharacterMode_CatchFlagGet   @ {catch_hook:#010x}")
    print(f"CharacterMode_GiveMonToPlayer@ {gmtp_hook:#010x}")
    print(f"CharacterMode_ScriptGiveMon  @ {sgm_hook:#010x}")
    print(f"CharacterMode_CreateWildMon  @ {wild_hook:#010x}")

    # opt-in prompt script block, appended after the code
    off_optin = (off_code + len(code) + 3) & ~3
    show_mugshot = syms["CharacterMode_ShowMugshot"] | 1
    hide_mugshot = syms["CharacterMode_HideMugshot"] | 1
    check_selectable = syms["CharacterMode_CheckSelectableNative"] | 1
    print(f"CharacterMode_ShowMugshot    @ {show_mugshot:#010x}")
    print(f"CharacterMode_HideMugshot    @ {hide_mugshot:#010x}")
    print(f"CharacterMode_CheckSelectable@ {check_selectable:#010x}")
    optin_blob, optin_splice = optin_script.build(addr(off_optin), n_chars,
                                                  show_mugshot, hide_mugshot,
                                                  check_selectable)
    print(f"opt-in script block          @ {addr(off_optin):#010x} ({len(optin_blob)} bytes)")

    total_len = off_optin + len(optin_blob)
    assert total_len <= INJECT_BLOCK_LEN, "injection block overflow"

    # 7a. preconditions BEFORE writing anything
    span = rom[INJECT_FILE_OFF:INJECT_FILE_OFF + total_len]
    assert all(b == 0xFF for b in span), "injection target not 0xFF-free!"
    assert rom[CATCH_BL_FILE_OFF:CATCH_BL_FILE_OFF + 4] == CATCH_BL_ORIG, \
        "catch-hook site bytes changed — wrong ROM?"
    assert rom[GMTP_FILE_OFF:GMTP_FILE_OFF + 8] == GMTP_ORIG, \
        "GiveMonToPlayer entry bytes changed — wrong ROM?"
    assert rom[optin_script.SPLICE_FILE_OFF:
               optin_script.SPLICE_FILE_OFF + len(optin_script.SPLICE_ORIG)] \
        == optin_script.SPLICE_ORIG, \
        "opt-in splice site bytes changed — wrong ROM?"
    assert rom[SPECIAL_1B6_FILE_OFF:SPECIAL_1B6_FILE_OFF + 4] == SPECIAL_1B6_ORIG, \
        "gSpecials[0x1B6] bytes changed — wrong ROM?"
    assert rom[GIVEMON_BL_FILE_OFF:GIVEMON_BL_FILE_OFF + 4] == GIVEMON_BL_ORIG, \
        "givemon-handler bl site bytes changed — wrong ROM?"
    assert all(b == 0xFF for b in
               rom[GIVEMON_VENEER_FILE_OFF:GIVEMON_VENEER_FILE_OFF + 8]), \
        "givemon veneer target not 0xFF-free!"
    assert rom[trade_hook.SPECIAL_SWEEP_FILE_OFF:
               trade_hook.SPECIAL_SWEEP_FILE_OFF + 4] == trade_hook.SPECIAL_SWEEP_ORIG, \
        "gSpecials[0x1AF] bytes changed — wrong ROM?"
    for label, off in trade_hook.SUB_SITES.items():
        assert rom[off:off + len(trade_hook.SUB_TAIL_ORIG)] == trade_hook.SUB_TAIL_ORIG, \
            f"trade junction bytes changed at {label} — wrong ROM?"
    assert rom[trade_hook.INLINE_SITE_OFF:
               trade_hook.INLINE_SITE_OFF + len(trade_hook.INLINE_ORIG)] == trade_hook.INLINE_ORIG, \
        "inline trade junction bytes changed — wrong ROM?"
    assert rom[egg_hook.SPLICE_FILE_OFF:
               egg_hook.SPLICE_FILE_OFF + len(egg_hook.SPLICE_ORIG)] == egg_hook.SPLICE_ORIG, \
        "egg-hatch script bytes changed — wrong ROM?"
    for label, (off, orig) in WILD_CALL_SITES.items():
        assert rom[off:off + 4] == orig, \
            f"wild-encounter call site bytes changed at {label} — wrong ROM?"

    # 5. splice data + code
    rom[INJECT_FILE_OFF + off_characters:INJECT_FILE_OFF + off_characters + len(characters)] = characters
    rom[INJECT_FILE_OFF + off_rosters:INJECT_FILE_OFF + off_rosters + len(rosters)] = rosters
    rom[INJECT_FILE_OFF + off_names:INJECT_FILE_OFF + off_names + len(names)] = names
    rom[INJECT_FILE_OFF + off_nameptrs:INJECT_FILE_OFF + off_nameptrs + len(nameptrs)] = nameptrs
    rom[INJECT_FILE_OFF + off_count:INJECT_FILE_OFF + off_count + 2] = struct.pack("<H", n_chars)
    rom[INJECT_FILE_OFF + off_wild_meta:INJECT_FILE_OFF + off_wild_meta + len(wild_meta)] = wild_meta
    rom[INJECT_FILE_OFF + off_code:INJECT_FILE_OFF + off_code + len(code)] = code
    rom[INJECT_FILE_OFF + off_optin:INJECT_FILE_OFF + off_optin + len(optin_blob)] = optin_blob

    # 5b. character sprites (separate free run)
    spr_b = os.path.join(CM_DIR, "cm_sprite_blobs.bin")
    spr_o = os.path.join(CM_DIR, "cm_sprite_offsets.bin")
    if os.path.isfile(spr_b) and os.path.isfile(spr_o):
        with open(spr_b, "rb") as f: sblobs = f.read()
        with open(spr_o, "rb") as f: soffs = f.read()
        assert len(soffs) == n_chars * 8, (len(soffs), n_chars)
        blobs_addr = ROM_BASE + CM_SPRITE_BLOBS_FILE_OFF
        sptrs = bytearray()
        wired = 0
        for i in range(n_chars):
            g, pl = struct.unpack_from("<II", soffs, i * 8)
            if g == 0xFFFFFFFF:
                sptrs += struct.pack("<II", 0, 0)
            else:
                sptrs += struct.pack("<II", blobs_addr + g, blobs_addr + pl)
                wired += 1
        for off, data, what in ((CM_SPRITE_BLOBS_FILE_OFF, sblobs, "sprite blobs"),
                                (CM_SPRITE_PTRS_FILE_OFF, bytes(sptrs), "sprite pointers")):
            assert all(b == 0xFF for b in rom[off:off + len(data)]), \
                f"{what}: target not 0xFF @ {off:#x}"
            rom[off:off + len(data)] = data
        print(f"character sprites: {wired}/{n_chars} wired, {len(sblobs):,} B "
              f"@ {blobs_addr:#x}, table @ {ROM_BASE + CM_SPRITE_PTRS_FILE_OFF:#x}")

    # 6a. bl retarget (thumb bit must NOT be in a bl target address)
    bl = thumb_bl(ROM_BASE + CATCH_BL_FILE_OFF, catch_hook & ~1)
    rom[CATCH_BL_FILE_OFF:CATCH_BL_FILE_OFF + 4] = bl
    print(f"catch hook: bl @{ROM_BASE + CATCH_BL_FILE_OFF:#x} -> {catch_hook & ~1:#x}  bytes={bl.hex()}")

    # 6a'. starter grant: bl -> near veneer -> far wrapper
    veneer = struct.pack("<HHI", 0x4B00, 0x4718, sgm_hook | 1)  # ldr r3,[pc,#0]; bx r3
    rom[GIVEMON_VENEER_FILE_OFF:GIVEMON_VENEER_FILE_OFF + 8] = veneer
    bl2 = thumb_bl(ROM_BASE + GIVEMON_BL_FILE_OFF, ROM_BASE + GIVEMON_VENEER_FILE_OFF)
    rom[GIVEMON_BL_FILE_OFF:GIVEMON_BL_FILE_OFF + 4] = bl2
    print(f"starter hook: bl @{ROM_BASE + GIVEMON_BL_FILE_OFF:#x} -> veneer "
          f"@{ROM_BASE + GIVEMON_VENEER_FILE_OFF:#x} -> {sgm_hook | 1:#010x}  "
          f"bl={bl2.hex()} veneer={veneer.hex()}")

    # 6b. entry trampoline: ldr r1,[pc,#0]; bx r1; .word hook|1
    tramp = struct.pack("<HHI", 0x4900, 0x4708, gmtp_hook | 1)
    rom[GMTP_FILE_OFF:GMTP_FILE_OFF + 8] = tramp
    print(f"gift hook: trampoline @{ROM_BASE + GMTP_FILE_OFF:#x} -> {gmtp_hook | 1:#x}  bytes={tramp.hex()}")

    # 6c. opt-in prompt splice (call <block>; nop nop nop)
    rom[optin_script.SPLICE_FILE_OFF:
        optin_script.SPLICE_FILE_OFF + len(optin_splice)] = optin_splice
    print(f"opt-in splice @{ROM_BASE + optin_script.SPLICE_FILE_OFF:#x}  bytes={optin_splice.hex()}")

    # 6c'. test-harness debug scripts, baked into ROM so live tests never
    # stage bytecode in volatile EWRAM. Two wild-battle setups: enable
    # Character Mode as Red, grant Pikachu L30 + 10 Master Balls, force a
    # wild battle vs Mewtwo (block case) / Charizard (catch case).
    def battle_debug_script(species):
        s = bytearray()
        for v in range(0x8000, 0x8008):
            s += bytes([0x16]) + struct.pack("<HH", v, 0)
        s += bytes([0x29]) + struct.pack("<H", 0x18F8)
        s += bytes([0x16]) + struct.pack("<HH", 0x51FC, 1)
        s += bytes([0x44]) + struct.pack("<HH", 1, 10)
        s += bytes([0x79]) + struct.pack("<HBH", 25, 30, 0) + b"\x00" * 9
        s += bytes([0xB6]) + struct.pack("<HBH", species, 30, 0)
        s += bytes([0xB7, 0x27, 0x02])
        return bytes(s)

    # starter-grant live test: enable Character Mode as Red on an empty
    # party, then run the exact shape of Unbound's own starter scripts
    # (givemon Larvitar). The wrapper must deliver Pikachu (Red roster[0]).
    # A second Larvitar give must pass through untouched and get PC-routed
    # by the gift rule (party stays at 1).
    def starter_debug_script():
        s = bytearray()
        for v in range(0x8000, 0x8008):
            s += bytes([0x16]) + struct.pack("<HH", v, 0)
        s += bytes([0x29]) + struct.pack("<H", 0x18F8)          # setflag CM
        s += bytes([0x16]) + struct.pack("<HH", 0x51FC, 1)      # Red
        s += bytes([0x79]) + struct.pack("<HBH", 246, 5, 0) + b"\x00" * 9   # Larvitar -> Pikachu
        s += bytes([0x79]) + struct.pack("<HBH", 246, 5, 0) + b"\x00" * 9   # Larvitar -> PC
        s += bytes([0x02])
        return bytes(s)

    # in-game trade sweep live test: party is set up with Character Mode OFF
    # (Pikachu + Lickitung — no starter substitution, no gift PC-routing),
    # then mode is enabled for char_id and trade 2 (The Top the Hitmontop
    # for Lickitung) is executed through the real patched shared junction.
    #
    # The two characters are DERIVED from the roster blob, not hardcoded. They
    # used to be Red (1, off-roster) and Bruno (6, on-roster); the 2026-07-25
    # roster audit put the Tyrogue line on Red, so Hitmontop became on-roster for
    # BOTH and the test silently stopped discriminating anything. Pikachu must
    # also be on-roster for each, because the script grants one to set the party
    # up -- otherwise the shim PC-routes it and the fixture collapses.
    def trade_debug_script(char_id):
        s = bytearray()
        s += bytes([0x2A]) + struct.pack("<H", 0x18F8)               # clearflag CM
        for v in range(0x8000, 0x8008):
            s += bytes([0x16]) + struct.pack("<HH", v, 0)
        s += bytes([0x79]) + struct.pack("<HBH", 25, 20, 0) + b"\x00" * 9   # Pikachu
        s += bytes([0x79]) + struct.pack("<HBH", 108, 20, 0) + b"\x00" * 9  # Lickitung
        s += bytes([0x29]) + struct.pack("<H", 0x18F8)               # setflag CM
        s += bytes([0x16]) + struct.pack("<HH", 0x51FC, char_id)
        s += bytes([0x16]) + struct.pack("<HH", 0x8008, 2)           # trade index 2
        s += bytes([0x16]) + struct.pack("<HH", 0x800A, 1)           # party slot 1
        s += bytes([0x04]) + struct.pack("<I", 0x09E9459C)           # patched junction
        s += bytes([0x02])
        return bytes(s)

    off_dbg_block = (off_optin + len(optin_blob) + 3) & ~3
    # The blocked-catch case needs a species genuinely OFF character 1's roster.
    # It was Mewtwo (150) until the 2026-07-25 audit, whose wave 5 explicitly kept
    # Mewtwo for Red (Pokemon Origins). Derived from the roster blob so it cannot
    # go stale again; Sandshrew's whole family is absent from Red's roster.
    blocked_species = None
    for cand in (27, 63, 74, 95, 109, 88, 100, 104, 108, 106):
        if cand not in _expanded(manifest["characters"][0]):
            blocked_species = cand
            break
    assert blocked_species, "no off-roster species left for the catch-block test"
    print(f"battle-catch blocked species (derived): {blocked_species}")
    dbg_block = battle_debug_script(blocked_species)
    off_dbg_catch = off_dbg_block + len(dbg_block)
    dbg_catch = battle_debug_script(6)
    off_dbg_starter = off_dbg_catch + len(dbg_catch)
    dbg_starter = starter_debug_script()
    off_trade_tails = off_dbg_starter + len(dbg_starter)
    trade_blob, trade_patches = trade_hook.build(addr(off_trade_tails))
    TRADE_SPECIES, SETUP_SPECIES = 237, 25     # Hitmontop traded in, Pikachu granted

    def _pick(wants_trade_species):
        for i, rec in enumerate(manifest["characters"]):
            ids = _expanded(rec)
            if SETUP_SPECIES not in ids:
                continue
            if (TRADE_SPECIES in ids) == wants_trade_species:
                return i + 1, rec["character"]
        raise SystemExit("no character can serve as the trade fixture "
                         "(wants_trade_species=%r) -- re-pick by hand"
                         % wants_trade_species)

    swept_id, swept_name = _pick(False)   # Hitmontop off-roster -> swept to PC
    stays_id, stays_name = _pick(True)    # Hitmontop on-roster  -> stays in party
    print(f"trade fixtures (derived): swept={swept_name} (id {swept_id}), "
          f"stays={stays_name} (id {stays_id})")
    off_dbg_trade_swept = off_trade_tails + len(trade_blob)
    dbg_trade_swept = trade_debug_script(swept_id)
    off_dbg_trade_stays = off_dbg_trade_swept + len(dbg_trade_swept)
    dbg_trade_stays = trade_debug_script(stays_id)

    # Threshold-gate live test. The number screen (sp0B3) is a naming screen in
    # number mode and is hostile to automation -- it drops and reorders
    # synthetic presses, so driving it to a two-digit id is unreliable. Instead
    # these preset VAR_RESULT and `goto` straight into the REAL gate bytes in
    # the REAL opt-in block, so the shipped callnative, compare and branch all
    # execute; only the player's typing is replaced.
    gate_off = optin_script.label_offsets()["GATE"]
    gate_addr = addr(off_optin) + gate_off

    def gate_debug_script(char_id):
        s = bytearray()
        s += bytes([0x16]) + struct.pack("<HH", 0x800D, char_id)  # setvar VAR_RESULT
        s += bytes([0x05]) + struct.pack("<I", gate_addr)         # goto the gate
        return bytes(s)

    hidden_ids = [i + 1 for i, c in enumerate(manifest["characters"]) if c.get("hidden")]
    shown_ids = [i + 1 for i, c in enumerate(manifest["characters"]) if not c.get("hidden")]
    gate_hidden_id = hidden_ids[0] if hidden_ids else 0
    gate_shown_id = shown_ids[0]
    off_dbg_gate_hidden = off_dbg_trade_stays + len(dbg_trade_stays)
    dbg_gate_hidden = gate_debug_script(gate_hidden_id)
    off_dbg_gate_shown = off_dbg_gate_hidden + len(dbg_gate_hidden)
    dbg_gate_shown = gate_debug_script(gate_shown_id)
    print(f"gate fixtures (derived): hidden id {gate_hidden_id}, shown id "
          f"{gate_shown_id}; gate @ {gate_addr:#010x} (block+{gate_off})")

    off_egg_tail = off_dbg_gate_shown + len(dbg_gate_shown)
    egg_blob, egg_patches = egg_hook.build(addr(off_egg_tail))

    total_len = off_egg_tail + len(egg_blob)
    assert total_len <= INJECT_BLOCK_LEN, "injection block overflow (debug scripts)"
    span2 = rom[INJECT_FILE_OFF + off_dbg_block:INJECT_FILE_OFF + total_len]
    assert all(b == 0xFF for b in span2), "debug-script target not 0xFF-free!"
    rom[INJECT_FILE_OFF + off_dbg_block:INJECT_FILE_OFF + off_dbg_block + len(dbg_block)] = dbg_block
    rom[INJECT_FILE_OFF + off_dbg_catch:INJECT_FILE_OFF + off_dbg_catch + len(dbg_catch)] = dbg_catch
    rom[INJECT_FILE_OFF + off_dbg_starter:INJECT_FILE_OFF + off_dbg_starter + len(dbg_starter)] = dbg_starter
    rom[INJECT_FILE_OFF + off_trade_tails:INJECT_FILE_OFF + off_trade_tails + len(trade_blob)] = trade_blob
    rom[INJECT_FILE_OFF + off_dbg_trade_swept:INJECT_FILE_OFF + off_dbg_trade_swept + len(dbg_trade_swept)] = dbg_trade_swept
    rom[INJECT_FILE_OFF + off_dbg_trade_stays:INJECT_FILE_OFF + off_dbg_trade_stays + len(dbg_trade_stays)] = dbg_trade_stays
    rom[INJECT_FILE_OFF + off_dbg_gate_hidden:INJECT_FILE_OFF + off_dbg_gate_hidden + len(dbg_gate_hidden)] = dbg_gate_hidden
    rom[INJECT_FILE_OFF + off_dbg_gate_shown:INJECT_FILE_OFF + off_dbg_gate_shown + len(dbg_gate_shown)] = dbg_gate_shown
    rom[INJECT_FILE_OFF + off_egg_tail:INJECT_FILE_OFF + off_egg_tail + len(egg_blob)] = egg_blob
    # json is imported at module scope (a second local import here made json
    # function-local, so the manifest load above raised UnboundLocalError)
    with open(os.path.join(BUILD, "debug_addrs.json"), "w") as f:
        json.dump({"battle_block_script": addr(off_dbg_block),
                   "battle_catch_script": addr(off_dbg_catch),
                   "starter_test_script": addr(off_dbg_starter),
                   "trade_test_script_swept": addr(off_dbg_trade_swept),
                   "trade_test_script_stays": addr(off_dbg_trade_stays),
                   "gate_test_script_hidden": addr(off_dbg_gate_hidden),
                   "gate_test_script_shown": addr(off_dbg_gate_shown),
                   "gate_hidden_id": gate_hidden_id,
                   "gate_shown_id": gate_shown_id,
                   "optin_block": addr(off_optin),
                   "optin_offsets": optin_script.label_offsets(),
                   "trade_test_swept_char": swept_name,
                   "trade_test_stays_char": stays_name}, f)
    print(f"debug scripts: block @ {addr(off_dbg_block):#010x}, catch @ {addr(off_dbg_catch):#010x}, "
          f"starter @ {addr(off_dbg_starter):#010x}")
    print(f"trade tails @ {addr(off_trade_tails):#010x}, trade tests red/bruno @ "
          f"{addr(off_dbg_trade_swept):#010x}/{addr(off_dbg_trade_stays):#010x}")

    # 6c''. trade-junction overlays + sweep special (gSpecials[0x1AF])
    sweep_fn = syms["CharacterMode_SweepPartyToPC"]
    rom[trade_hook.SPECIAL_SWEEP_FILE_OFF:trade_hook.SPECIAL_SWEEP_FILE_OFF + 4] = \
        struct.pack("<I", sweep_fn | 1)
    print(f"gSpecials[0x1AF] -> CharacterMode_SweepPartyToPC {sweep_fn | 1:#010x}")
    for label, off, orig, new in trade_patches:
        assert rom[off:off + len(orig)] == orig  # rechecked against pre-write state above
        rom[off:off + len(new)] = new
        print(f"trade hook: {label} @{ROM_BASE + off:#x}  {orig.hex()} -> {new.hex()}")

    # egg-hatch overlay: an off-roster GIFT egg used to hatch into a permanent
    # off-roster party member, because eggs are exempt from the gift routing AND
    # from the sweep, and nothing ever looked at what they became. Hatching is
    # script-driven, so the same sweep special the trade hook uses is appended to
    # the hatch script's tail -- after its waitstate, so it sees the finished
    # Pokemon rather than the egg.
    for off, orig, new in egg_patches:
        assert rom[off:off + len(orig)] == orig  # rechecked against pre-write state above
        rom[off:off + len(new)] = new
        print(f"egg hook: hatch script @{ROM_BASE + off:#x}  {orig.hex()} -> {new.hex()}")
    print(f"egg hatch tail @ {addr(off_egg_tail):#010x} ({len(egg_blob)} bytes)")

    # Decode the egg hook back out of the PATCHED image, the same way the bl
    # hooks are round-trip verified. A script overlay that merely "looks right"
    # in the source is exactly the class of thing that has shipped broken here
    # before (the opt-in Yes path once fell through into the No branch and
    # cleared the flag it had just set; only a live run caught it).
    _egg_site = rom[egg_hook.SPLICE_FILE_OFF:egg_hook.SPLICE_FILE_OFF + 6]
    assert _egg_site[0] == 0x05, "egg splice is not a goto"
    _egg_dest = struct.unpack_from("<I", _egg_site, 1)[0]
    assert _egg_dest == addr(off_egg_tail), (
        "egg splice targets %#010x, tail is at %#010x" % (_egg_dest, addr(off_egg_tail)))
    _tail = rom[INJECT_FILE_OFF + off_egg_tail:
                INJECT_FILE_OFF + off_egg_tail + len(egg_blob)]
    assert _tail == egg_blob, "egg tail in the image differs from what was assembled"
    # ...and it must still perform the hatch, wait for it, and only THEN sweep:
    # sweeping before the waitstate would see an egg, not a Pokemon.
    assert _tail[0] == 0x25 and struct.unpack_from("<H", _tail, 1)[0] == egg_hook.SPECIAL_HATCH, \
        "egg tail does not replay the hatch special first"
    assert _tail[3] == 0x27, "egg tail does not waitstate after the hatch"
    assert _tail[5] == 0x25 and struct.unpack_from("<H", _tail, 6)[0] == egg_hook.SPECIAL_SWEEP, \
        "egg tail does not run the sweep special after the hatch"
    assert _tail[8] == 0x02, "egg tail does not end"
    print("  verified egg hook: goto -> [special %#x; waitstate; %#04x; special %#x; end]"
          % (egg_hook.SPECIAL_HATCH, egg_hook.OPCODE_RELEASE, egg_hook.SPECIAL_SWEEP))

    # 6d. character-select: wire the name-buffering special into slot 0x1B6
    buf_special = syms["CharacterMode_BufferNameSpecial"]
    rom[SPECIAL_1B6_FILE_OFF:SPECIAL_1B6_FILE_OFF + 4] = struct.pack("<I", buf_special | 1)
    print(f"gSpecials[0x1B6] -> CharacterMode_BufferNameSpecial {buf_special | 1:#010x}")

    # 6e. wild-encounter roster override: retarget all 7 real call sites
    for label, (off, orig) in WILD_CALL_SITES.items():
        bl_wild = thumb_bl(ROM_BASE + off, wild_hook & ~1)
        rom[off:off + 4] = bl_wild
        print(f"wild hook: {label} bl @{ROM_BASE + off:#x}  {orig.hex()} -> {bl_wild.hex()}")

    # 7b. disassemble both patched sites back and check shape
    verify_disasm(bytes(rom[CATCH_BL_FILE_OFF:CATCH_BL_FILE_OFF + 4]),
                  ROM_BASE + CATCH_BL_FILE_OFF, ["bl"])
    verify_disasm(bytes(rom[GMTP_FILE_OFF:GMTP_FILE_OFF + 4]),
                  ROM_BASE + GMTP_FILE_OFF, ["ldr", "bx"])
    verify_disasm(bytes(rom[GIVEMON_BL_FILE_OFF:GIVEMON_BL_FILE_OFF + 4]),
                  ROM_BASE + GIVEMON_BL_FILE_OFF, ["bl"])
    verify_disasm(bytes(rom[GIVEMON_VENEER_FILE_OFF:GIVEMON_VENEER_FILE_OFF + 4]),
                  ROM_BASE + GIVEMON_VENEER_FILE_OFF, ["ldr", "bx"])
    for label, (off, _orig) in WILD_CALL_SITES.items():
        verify_disasm(bytes(rom[off:off + 4]), ROM_BASE + off, ["bl"])

    # 8. outputs
    out = os.path.join(BUILD, "unbound-cm.gba")
    with open(out, "wb") as f:
        f.write(rom)
    out_sha = sha1(rom)
    with open(out + ".sha1", "w") as f:
        f.write(f"{out_sha}  unbound-cm.gba\n")

    # changed-byte accounting
    with open(ROM, "rb") as f:
        orig = f.read()
    changed = sum(1 for a, b in zip(orig, rom) if a != b)
    print(f"\nwrote {out}")
    print(f"  sha1 {out_sha}")
    print(f"  changed bytes: {changed} "
          f"(data+code {total_len}, hooks 12 + specials 8 + trade overlays 19 "
          f"+ wild-encounter call sites {4 * len(WILD_CALL_SITES)})")

    flips = os.path.join(HERE, "bin", "flips")
    if os.path.exists(flips):
        bps = os.path.join(BUILD, "unbound-cm.bps")
        run([flips, "--create", "--bps-delta", ROM, out, bps])
        assert os.path.exists(bps), "flips reported success but wrote no patch"
        print(f"  patch: {bps}")


def verify_disasm(raw, vma, expect_mnemonics):
    """Round-trip the patched bytes through objdump and check mnemonics."""
    tmp = os.path.join(BUILD, "_verify.bin")
    with open(tmp, "wb") as f:
        f.write(raw)
    out = subprocess.run(
        ["arm-none-eabi-objdump", "-D", "-b", "binary", "-m", "armv4t",
         "-M", "force-thumb", f"--adjust-vma={vma:#x}", tmp],
        check=True, capture_output=True, text=True).stdout
    lines = [l for l in out.splitlines() if ":\t" in l]
    for want, line in zip(expect_mnemonics, lines):
        assert f"\t{want}" in line, f"patched site mismatch: wanted {want} in {line!r}"
    print(f"  verified disasm @{vma:#x}:")
    for line in lines[:len(expect_mnemonics)]:
        print(f"    {line.strip()}")
    os.remove(tmp)


if __name__ == "__main__":
    main()
