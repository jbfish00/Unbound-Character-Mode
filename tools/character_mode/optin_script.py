#!/usr/bin/env python3
"""Assemble the Character Mode opt-in prompt script (Phase 4 menu hook, v1).

Splices into Unbound's new-game "enhancement options" flow, whose grammar was
fully decoded in docs/ROUTINE_MAP.md (opcodes cross-validated against the
dispatch table at 0x0815F9B4; the Yes/No answer lands in VAR_RESULT 0x800D).

Splice site (file 0x1E70003, the start of the enhancement-options prompt):
    original: 0F 00 5C 06 F1 09  loadword 0, 0x09F1065C   ("...enhancement
              09 05              callstd 5 (MSGBOX_YESNO)   options?")
    patched:  04 <u32 block>     call  <our block in free space>
              00 00 00           nop nop nop
Our block asks the Character Mode question first, then REPLAYS the exact
loadword+callstd pair it displaced and returns, so the original compare at
0x1E7000B still reads 0x800D from the enhancement prompt — the surrounding
flow is byte-for-byte unaffected in behavior.

v1 limitation (deliberate): answering Yes enables Character Mode as Red
(character id 1). The full 156-character select menu is a later phase; this
gets a playable, testable opt-in wired end to end first.

Byte grammar used (all confirmed in this ROM, same idiom as the randomizer
prompts at 0x1E7002C-0x1E70052):
    0F 00 <u32>        loadword 0, text
    09 05 / 09 04      callstd MSGBOX_YESNO / MSGBOX_DEFAULT
    21 <u16> <u16>     compare_var_to_value
    06 05 <u32>        goto_if NE
    29 <u16>           setflag
    16 <u16> <u16>     setvar
    03                 return
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emit_characters import CHARMAP_PATH, load_charmap, encode_text

SPLICE_FILE_OFF = 0x1E70003
SPLICE_ORIG = bytes.fromhex("0F005C06F1090905")
ENHANCEMENT_PROMPT_PTR = 0x09F1065C

FLAG_CHARACTER_MODE = 0x18F8
VAR_CHARACTER_ID = 0x51FC
VAR_RESULT = 0x800D

PROMPT_TEXT = "Would you like to enable Character\nMode and play as Red of Kanto?"
ENABLED_TEXT = "Character Mode is now enabled!\nOnly Red's team may join you."

NEWLINE = 0xFE  # in-msgbox line break


def encode_msg(text, charmap):
    lines = [encode_text(line, charmap)[:-1] for line in text.split("\n")]
    return bytes([NEWLINE]).join(lines) + b"\xFF"


def build(block_rom_addr):
    """Return (block_blob, splice_bytes) for a block placed at block_rom_addr."""
    charmap = load_charmap(CHARMAP_PATH)
    # the charmap file escapes the apostrophe ('\'' = B4), which load_charmap's
    # simple regex misses — add it directly
    charmap["'"] = 0xB4
    prompt = encode_msg(PROMPT_TEXT, charmap)
    enabled = encode_msg(ENABLED_TEXT, charmap)

    # fixed-size body, so label offsets are static
    OFF_NO = 35      # the No branch (clears mode state, then replays)
    OFF_TEXT = 52    # first text byte (right after the `return`)
    p_prompt = block_rom_addr + OFF_TEXT
    p_enabled = p_prompt + len(prompt)
    p_no = block_rom_addr + OFF_NO

    body = bytearray()
    body += bytes([0x0F, 0x00]) + struct.pack("<I", p_prompt)          # loadword 0, prompt
    body += bytes([0x09, 0x05])                                        # callstd MSGBOX_YESNO
    body += bytes([0x21]) + struct.pack("<HH", VAR_RESULT, 1)          # compare 0x800D, 1
    body += bytes([0x06, 0x05]) + struct.pack("<I", p_no)              # goto_if NE -> no
    body += bytes([0x29]) + struct.pack("<H", FLAG_CHARACTER_MODE)     # setflag
    body += bytes([0x16]) + struct.pack("<HH", VAR_CHARACTER_ID, 1)    # setvar id, 1 (Red)
    body += bytes([0x0F, 0x00]) + struct.pack("<I", p_enabled)         # loadword 0, enabled
    body += bytes([0x09, 0x04])                                        # callstd MSGBOX_DEFAULT
    assert len(body) == OFF_NO, f"OFF_NO drifted: {len(body)}"
    # No branch: actively clear mode state so if the intro flow is re-entered
    # (difficulty menu Back loop), the LAST answer wins
    body += bytes([0x2A]) + struct.pack("<H", FLAG_CHARACTER_MODE)     # clearflag
    body += bytes([0x16]) + struct.pack("<HH", VAR_CHARACTER_ID, 0)    # setvar id, 0
    body += bytes([0x0F, 0x00]) + struct.pack("<I", ENHANCEMENT_PROMPT_PTR)  # replay original
    body += bytes([0x09, 0x05])
    body += bytes([0x03])                                              # return
    assert len(body) == OFF_TEXT, f"OFF_TEXT drifted: {len(body)}"
    body += prompt + enabled

    splice = bytes([0x04]) + struct.pack("<I", block_rom_addr) + b"\x00\x00\x00"
    assert len(splice) == len(SPLICE_ORIG)
    return bytes(body), splice


if __name__ == "__main__":
    blob, splice = build(0x08B2B280)
    print(f"block: {len(blob)} bytes; splice: {splice.hex(' ')}")
