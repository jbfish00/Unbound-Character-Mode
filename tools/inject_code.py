#!/usr/bin/env python3
"""Compile a freestanding C file and splice it into ROM free space at a fixed address.

Adapted from CFRU's scripts/insert.py mechanism (github.com/Skeli789/Complete-Fire-Red-Upgrade)
— same core idea (pin code to a known address via a linker script, compile,
extract the raw .text bytes, splice into the ROM) — but CFRU targets one
fixed reserved offset in a mostly-empty vanilla ROM; we're scavenging
specific free-space blocks in an already-dense hack (see docs/FREE_SPACE.md),
so the target address is a parameter, not a constant.

This handles the MECHANICAL part of Phase 1's "hello world" injection test
and Phase 4's real enforcement-logic injection: compile -> link at a fixed
address -> extract raw bytes -> splice into a ROM copy. It does NOT decide
what to inject where — that needs a real hook site (still pending Phase 1)
so the injected code actually gets called.

Usage:
  python3 tools/inject_code.py <source.c> <rom.gba> <target_rom_address_hex> \\
      [--out patched.gba] [--extern-syms syms.json]

--extern-syms: optional JSON {symbol_name: hex_address} for resolving this
  file's `extern` declarations (e.g. gCharacterTable -> its injected address)
  when they're already known, instead of leaving them unresolved.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

GCC = "arm-none-eabi-gcc"
LD = "arm-none-eabi-ld"
OBJCOPY = "arm-none-eabi-objcopy"
NM = "arm-none-eabi-nm"

CFLAGS = ["-mthumb", "-mcpu=arm7tdmi", "-mtune=arm7tdmi", "-O2",
          "-ffreestanding", "-fno-builtin", "-fno-pic", "-Wall"]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("COMMAND FAILED:", " ".join(cmd))
        print(r.stdout)
        print(r.stderr)
        sys.exit(1)
    return r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("rom")
    ap.add_argument("target_addr", help="hex ROM address to link/splice this code at, e.g. 0x081FE6C64 -- must be inside a confirmed free-space block")
    ap.add_argument("--out", default=None)
    ap.add_argument("--extern-syms", default=None, help="JSON file: {symbol: hex_address} for resolving externs")
    args = ap.parse_args()

    target = int(args.target_addr, 0)
    out_rom = args.out or (os.path.splitext(args.rom)[0] + "_patched.gba")

    with tempfile.TemporaryDirectory() as tmp:
        obj = os.path.join(tmp, "code.o")
        run([GCC, "-c", *CFLAGS, args.source, "-o", obj])

        ld_script_lines = [
            "SECTIONS", "{",
            f"  . = 0x{target:08X};",
            "  .text : { *(.text*) }",
            "  .rodata : { *(.rodata*) }",
            "  .data : { *(.data*) }",
            "  /DISCARD/ : { *(.comment) *(.ARM.attributes) }",
            "}",
        ]
        if args.extern_syms:
            with open(args.extern_syms) as f:
                syms = json.load(f)
            defines = "\n".join(f"{name} = 0x{int(addr, 0):08X};" for name, addr in syms.items())
            ld_script_lines = [defines] + ld_script_lines

        ld_script = os.path.join(tmp, "link.ld")
        with open(ld_script, "w") as f:
            f.write("\n".join(ld_script_lines))

        linked = os.path.join(tmp, "linked.elf")
        link_cmd = [LD, "-T", ld_script, obj, "-o", linked]
        r = subprocess.run(link_cmd, capture_output=True, text=True)
        if r.returncode != 0:
            undefined = [l for l in r.stderr.splitlines() if "undefined reference" in l]
            if undefined:
                print(f"Link has {len(undefined)} unresolved extern(s) (expected until Phase 1 provides real addresses):")
                for u in undefined[:20]:
                    print(" ", u.strip())
                print("\nPass --extern-syms with a JSON address map to resolve them, or ignore for a dry-run size/layout check.")
            else:
                print(r.stdout, r.stderr)
            sys.exit(1)

        raw = os.path.join(tmp, "raw.bin")
        run([OBJCOPY, "-O", "binary", linked, raw])

        with open(raw, "rb") as f:
            payload = f.read()

        print(f"Compiled+linked payload: {len(payload)} bytes, targeting ROM address 0x{target:08X}")

        with open(args.rom, "rb") as f:
            rom = bytearray(f.read())

        file_off = target - 0x08000000
        if file_off < 0 or file_off + len(payload) > len(rom):
            print("ERROR: target address is outside the ROM's address range")
            sys.exit(1)

        region = rom[file_off:file_off + len(payload)]
        if any(b != 0xFF for b in region):
            print(f"WARNING: target region at file offset 0x{file_off:X} is NOT all 0xFF "
                  f"({sum(1 for b in region if b != 0xFF)}/{len(region)} non-FF bytes) — "
                  "this does not look like confirmed free space. Re-check docs/FREE_SPACE.md before proceeding.")
            sys.exit(1)

        rom[file_off:file_off + len(payload)] = payload
        with open(out_rom, "wb") as f:
            f.write(rom)

        print(f"Wrote {out_rom} with payload spliced in at file offset 0x{file_off:X}")
        print("NOTE: this only places the code — nothing calls it yet. A hook (branch")
        print("instruction) at a confirmed call site is still needed for it to execute.")


if __name__ == "__main__":
    main()
