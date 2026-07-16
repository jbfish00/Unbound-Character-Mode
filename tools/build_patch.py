#!/usr/bin/env python3
"""Build the Character Mode patched ROM for Pokemon Unbound v2.1.1.1.

Pipeline (all addresses from docs/ROUTINE_MAP.md v8, double-confirmed):
  1. verify the source ROM against rom.sha1
  2. compile src/character_mode.c (arm-none-eabi-gcc, Thumb, -mlong-calls)
  3. lay out data blobs + code in the confirmed-free block at file 0x00B2B280
  4. link at the real injection address (src/unbound.ld pins engine symbols)
  5. splice data + code into a ROM copy
  6. apply the two hooks:
       a. bl retarget at 0x089C8CA6 (atkEF_handleballthrow's
          FlagGet(FLAG_NO_CATCHING) call -> CharacterMode_CatchFlagGet)
       b. 8-byte entry trampoline at 0x089C905C (GiveMonToPlayer ->
          CharacterMode_GiveMonToPlayer)
  7. self-verify: original-byte preconditions, free-space precondition,
     disassemble the patched sites back and check the expected shape
  8. write build/unbound-cm.gba (+ .sha1) and, if flips is present,
     build/unbound-cm.bps (this flips build only supports IPS/BPS)

Distribution is ALWAYS the patch, never the ROM.
"""
import hashlib
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

ROM_BASE = 0x08000000

# Injection block: confirmed 0xFF-free, 147 KiB @ file 0x00B2B280 (docs/FREE_SPACE.md)
INJECT_FILE_OFF = 0x00B2B280
INJECT_ROM_ADDR = ROM_BASE + INJECT_FILE_OFF
INJECT_BLOCK_LEN = 147 * 1024

# Hook sites (docs/ROUTINE_MAP.md v8)
CATCH_BL_FILE_OFF = 0x9C8CA6          # bl call_via_r6 (FlagGet) inside atkEF_handleballthrow
CATCH_BL_ORIG = bytes.fromhex("00F0E6FE")
GMTP_FILE_OFF = 0x9C905C              # GiveMonToPlayer entry
GMTP_ORIG = bytes.fromhex("70B504001CF0CEFE")
# CFRU scrolling-multichoice list getters (docs/ROUTINE_MAP.md v8.1) —
# trampolined so set index 32 serves the 156 character names
SCROLL_SIZE_FILE_OFF = 0x1EB48B8      # GetSizeOfMultiList
SCROLL_SIZE_ORIG = bytes.fromhex("044b1a881f2a00d9")
SCROLL_LIST_FILE_OFF = 0x1EB48D4      # GetScrollingMultiList
SCROLL_LIST_ORIG = bytes.fromhex("044b1b881f2b00d9")
# gScrollingSets (0x09FB196C, 32 entries x 8) is ALSO read by Unbound-custom
# code with an unclamped Var8000 index, so the table is relocated into
# injection space with the character list appended as entry 32, and every
# pool word referencing the old table is repointed to the relocation.
SCROLLSETS_FILE_OFF = 0x1FB196C
SCROLLSETS_COUNT = 32
SCROLLSETS_ADDR = 0x09FB196C
SCROLLSETS_POOL_REFS = (0x1EB48D0, 0x1EB48EC, 0x1EB7C6C, 0x1EB80B4, 0x1ED4FD8)


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
    run(["arm-none-eabi-gcc", "-c", "-g", "-mthumb", "-mcpu=arm7tdmi", "-mtune=arm7tdmi",
         "-O2", "-ffreestanding", "-fno-builtin", "-mlong-calls", "-Wall", "-Wextra",
         "-Werror", "-o", obj, os.path.join(ROOT, "src", "character_mode.c")])

    # 3. layout: [characters.bin][rosters.bin][names.bin][u16 count][pad][code]
    with open(os.path.join(CM_DIR, "characters.bin"), "rb") as f:
        characters = f.read()
    with open(os.path.join(CM_DIR, "rosters.bin"), "rb") as f:
        rosters = f.read()
    with open(os.path.join(CM_DIR, "names.bin"), "rb") as f:
        names = f.read()
    n_chars = len(characters) // 16

    off_characters = 0
    off_rosters = off_characters + len(characters)
    off_names = off_rosters + len(rosters)
    off_nameptrs = (off_names + len(names) + 3) & ~3
    off_scrollsets = off_nameptrs + n_chars * 4
    off_count = off_scrollsets + (SCROLLSETS_COUNT + 1) * 8
    off_code = (off_count + 2 + 3) & ~3

    addr = lambda off: INJECT_ROM_ADDR + off

    # per-character name pointer array (for the scrolling character list):
    # record layout characters.bin: nameOffset u32 at +0 of each 16B record
    nameptrs = b"".join(
        struct.pack("<I", addr(off_names) + struct.unpack_from("<I", characters, 16 * i)[0])
        for i in range(n_chars))

    # relocated gScrollingSets: the 32 original entries + ours as entry 32
    scrollsets = rom[SCROLLSETS_FILE_OFF:SCROLLSETS_FILE_OFF + SCROLLSETS_COUNT * 8]
    scrollsets += struct.pack("<IB3x", addr(off_nameptrs), n_chars)

    # 4. link (unbound.ld as an input script augments the default one)
    elf = os.path.join(BUILD, "character_mode.elf")
    run(["arm-none-eabi-ld",
         f"-Ttext={addr(off_code):#x}",
         "--defsym", f"gCharacterTable={addr(off_characters):#x}",
         "--defsym", f"gCharacterRosters={addr(off_rosters):#x}",
         "--defsym", f"gCharacterNames={addr(off_names):#x}",
         "--defsym", f"gCharacterNamePtrs={addr(off_nameptrs):#x}",
         "--defsym", f"gCharacterScrollSets={addr(off_scrollsets):#x}",
         "--defsym", f"gCharacterCount={addr(off_count):#x}",
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
    print(f"CharacterMode_CatchFlagGet   @ {catch_hook:#010x}")
    print(f"CharacterMode_GiveMonToPlayer@ {gmtp_hook:#010x}")

    # opt-in prompt script block, appended after the code
    off_optin = (off_code + len(code) + 3) & ~3
    optin_blob, optin_splice = optin_script.build(addr(off_optin), n_chars)
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
    assert rom[SCROLL_SIZE_FILE_OFF:SCROLL_SIZE_FILE_OFF + 8] == SCROLL_SIZE_ORIG, \
        "GetSizeOfMultiList entry bytes changed — wrong ROM?"
    assert rom[SCROLL_LIST_FILE_OFF:SCROLL_LIST_FILE_OFF + 8] == SCROLL_LIST_ORIG, \
        "GetScrollingMultiList entry bytes changed — wrong ROM?"

    # 5. splice data + code
    rom[INJECT_FILE_OFF + off_characters:INJECT_FILE_OFF + off_characters + len(characters)] = characters
    rom[INJECT_FILE_OFF + off_rosters:INJECT_FILE_OFF + off_rosters + len(rosters)] = rosters
    rom[INJECT_FILE_OFF + off_names:INJECT_FILE_OFF + off_names + len(names)] = names
    rom[INJECT_FILE_OFF + off_nameptrs:INJECT_FILE_OFF + off_nameptrs + len(nameptrs)] = nameptrs
    rom[INJECT_FILE_OFF + off_scrollsets:INJECT_FILE_OFF + off_scrollsets + len(scrollsets)] = scrollsets
    rom[INJECT_FILE_OFF + off_count:INJECT_FILE_OFF + off_count + 2] = struct.pack("<H", n_chars)
    rom[INJECT_FILE_OFF + off_code:INJECT_FILE_OFF + off_code + len(code)] = code
    rom[INJECT_FILE_OFF + off_optin:INJECT_FILE_OFF + off_optin + len(optin_blob)] = optin_blob

    # 6a. bl retarget (thumb bit must NOT be in a bl target address)
    bl = thumb_bl(ROM_BASE + CATCH_BL_FILE_OFF, catch_hook & ~1)
    rom[CATCH_BL_FILE_OFF:CATCH_BL_FILE_OFF + 4] = bl
    print(f"catch hook: bl @{ROM_BASE + CATCH_BL_FILE_OFF:#x} -> {catch_hook & ~1:#x}  bytes={bl.hex()}")

    # 6b. entry trampoline: ldr r1,[pc,#0]; bx r1; .word hook|1
    tramp = struct.pack("<HHI", 0x4900, 0x4708, gmtp_hook | 1)
    rom[GMTP_FILE_OFF:GMTP_FILE_OFF + 8] = tramp
    print(f"gift hook: trampoline @{ROM_BASE + GMTP_FILE_OFF:#x} -> {gmtp_hook | 1:#x}  bytes={tramp.hex()}")

    # 6c. opt-in prompt splice (call <block>; nop nop nop)
    rom[optin_script.SPLICE_FILE_OFF:
        optin_script.SPLICE_FILE_OFF + len(optin_splice)] = optin_splice
    print(f"opt-in splice @{ROM_BASE + optin_script.SPLICE_FILE_OFF:#x}  bytes={optin_splice.hex()}")

    # 6d'. repoint every pool reference of the old gScrollingSets to the
    # relocated+extended copy (entry 32 = the character list)
    for ref in SCROLLSETS_POOL_REFS:
        got = struct.unpack_from("<I", rom, ref)[0]
        assert got == SCROLLSETS_ADDR, \
            f"pool ref at {ref:#x} is {got:#x}, expected gScrollingSets — wrong ROM?"
        rom[ref:ref + 4] = struct.pack("<I", addr(off_scrollsets))
    print(f"gScrollingSets relocated -> {addr(off_scrollsets):#010x} "
          f"({SCROLLSETS_COUNT}+1 sets, {len(SCROLLSETS_POOL_REFS)} pool refs repointed)")

    # 6d. scrolling-multichoice getter trampolines (character-select list)
    scroll_size_hook = syms["CharacterMode_GetSizeOfMultiList"]
    scroll_list_hook = syms["CharacterMode_GetScrollingMultiList"]
    for site, hook, name in ((SCROLL_SIZE_FILE_OFF, scroll_size_hook, "GetSizeOfMultiList"),
                             (SCROLL_LIST_FILE_OFF, scroll_list_hook, "GetScrollingMultiList")):
        tr = struct.pack("<HHI", 0x4900, 0x4708, hook | 1)
        rom[site:site + 8] = tr
        print(f"scroll hook: {name} trampoline @{ROM_BASE + site:#x} -> {hook | 1:#x}")

    # 7b. disassemble both patched sites back and check shape
    verify_disasm(bytes(rom[CATCH_BL_FILE_OFF:CATCH_BL_FILE_OFF + 4]),
                  ROM_BASE + CATCH_BL_FILE_OFF, ["bl"])
    verify_disasm(bytes(rom[GMTP_FILE_OFF:GMTP_FILE_OFF + 4]),
                  ROM_BASE + GMTP_FILE_OFF, ["ldr", "bx"])
    verify_disasm(bytes(rom[SCROLL_SIZE_FILE_OFF:SCROLL_SIZE_FILE_OFF + 4]),
                  ROM_BASE + SCROLL_SIZE_FILE_OFF, ["ldr", "bx"])
    verify_disasm(bytes(rom[SCROLL_LIST_FILE_OFF:SCROLL_LIST_FILE_OFF + 4]),
                  ROM_BASE + SCROLL_LIST_FILE_OFF, ["ldr", "bx"])

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
          f"(data+code {total_len}, hooks 12)")

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
