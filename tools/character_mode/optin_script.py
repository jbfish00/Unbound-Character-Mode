#!/usr/bin/env python3
"""Assemble the Character Mode opt-in prompt script (Phase 4 menu hook).

Splice site v2 (2026-07-17, organic-reach fix): the original v1 splice at
0x1E70003 (the "view game enhancement options?" prompt) turned out to be
UNREACHABLE on a first-run new game — the intro questionnaire sets temp
flag 0x0001 at its start (setflag @0x1E6FBE6), and a checkflag right before
the enhancement region skips past it whenever that flag is set (i.e. on
every fresh playthrough; the enhancement region only runs on settings-NPC /
New-Game-Plus re-entry, where the temp flag has since been cleared).
Proven live: breadcrumbed mashed intro never set the breadcrumb at the old
site; screenshots show questionnaire -> story cutscene directly.

New splice site: the checkflag gate itself (file 0x1E6FF2D, 9 bytes):
    original: 2B 01 00             checkflag 0x0001
              06 01 9D 01 E7 09    goto_if TRUE -> 0x09E7019D (first-run skip)
    patched:  04 <u32 block>       call  <our block in free space>
              00 00 00 00          nops
Both paths cross this gate, so the block runs exactly once in the intro
(right after difficulty is chosen) AND on any re-entry it replays the
original checkflag+goto_if semantics byte-for-byte: after the prompt the
block does `checkflag 0x0001; goto_if TRUE -> 0x09E7019D; return`.
(When the goto_if fires inside the called block, the call frame's return
slot leaks until the script ends — harmless, the context stack is reset
per script run.) The enhancement-options region itself is left untouched:
Character Mode is deliberately NOT offered on mid-game re-entry, so a
player's mode state can't be toggled after new game.

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

SPLICE_FILE_OFF = 0x1E6FF2D
SPLICE_ORIG = bytes.fromhex("2B0100" "06019D01E709")  # checkflag 1; goto_if TRUE -> 0x09E7019D
FIRSTRUN_SKIP_PTR = 0x09E7019D

FLAG_CHARACTER_MODE = 0x18F8
VAR_CHARACTER_ID = 0x51FC
VAR_RESULT = 0x800D
# Breadcrumb: set the moment the spliced block runs, BEFORE any prompt.
# Proves organic reach of the splice in blind/mashed playthroughs even when
# the prompt ends up answered No. 0x51FA is audited-unused (ROUTINE_MAP
# v8.2); EWRAM shadow 0x0203B768.
VAR_REACHED_BREADCRUMB = 0x51FA
BREADCRUMB_VALUE = 0xCA11

PROMPT_TEXT = "Would you like to enable Character\nMode and pick your character?"
NUMBER_TEXT = "Enter your character's number\n(1-{count}, listed in the patch notes)."
CONFIRM_TEXT = "Play as {NAME}?"
ENABLED_TEXT = "Character Mode has been enabled\nfor your chosen character!"
# Shown when the entered number names a character below the playability
# threshold (CHAR_FLAG_HIDDEN). Two lines: FRLG's msgbox shows two at a time.
HIDDEN_TEXT = "{NAME} is not available\nin this game."

# v3 select flow: CFRU ChooseNumberScreen special -> number in 0x800D
# (0xFFFF on empty/cancel); our special 0x1B6 buffers the chosen name.
SPECIAL_CHOOSE_NUMBER = 0x0B3
SPECIAL_BUFFER_NAME = 0x1B6

# ScrCmd_callnative discards the C return value, so CharacterMode_
# CheckSelectableNative hands its verdict back through this var (1 = may be
# chosen, 0 = out of range or hidden). 0x800C is outside givemon's own
# 0x8000-0x800B override channel and is read by nothing else in the project.
VAR_SELECTABLE = 0x800C

NEWLINE = 0xFE  # in-msgbox line break
STR_VAR_1 = b"\xFD\x02"  # {STR_VAR_1} placeholder


def encode_msg(text, charmap):
    parts = []
    for chunk in text.split("{NAME}"):
        lines = [encode_text(line, charmap)[:-1] for line in chunk.split("\n")]
        parts.append(bytes([NEWLINE]).join(lines))
    return STR_VAR_1.join(parts) + b"\xFF"


def label_offsets(show_mugshot=True, hide_mugshot=True, check_selectable=True,
                  sweep=True):
    """Byte offsets of the block's labels and of the points where the script
    PARKS waiting on the player.

    The live harness used to hardcode these (CONFIRM_POS = 90, block bound
    140). Every optional feature added to the block -- the mugshot callnatives,
    now the threshold gate -- shifts everything after it, and a stale literal
    here does not fail as "the offset moved": the driver simply never sees the
    state it is waiting for and the suite reports a scene that never completed.
    Derive them instead."""
    mug = 5 if (show_mugshot and hide_mugshot) else 0
    sel = 16 if check_selectable else 0
    selbr = 16 if check_selectable else 0
    # The activation party sweep is one callnative (5 bytes) emitted right
    # after the setflag, so it shifts everything from ENABLED_MSGBOX onward and
    # nothing before it.
    swp = 5 if sweep else 0
    o = {
        "OPTIN_YESNO": 13,      # parked in the opt-in yes/no
        "NUMTEXT_MSGBOX": 32,   # parked in the "enter your number" msgbox
        "NUMBER_SCREEN": 36,    # parked on the waitstate, number screen up
        "PICK": 24,
        # First byte of the threshold gate (the callnative), i.e. the point
        # just past the range checks. Fixed, because everything before it is
        # unconditional. A test can `goto` here with VAR_RESULT preset to run
        # the REAL shipped gate without driving the number screen.
        "GATE": 69 if check_selectable else -1,
        "NO": 112 + 2 * mug + sel + swp,
        "REPLAY": 120 + 2 * mug + sel + swp,
        "HIDDEN": 130 + 2 * mug + sel + swp,
        "TEXT": 130 + 2 * mug + sel + selbr + swp,
    }
    # Parked in "Play as {NAME}?" -- just past its callstd. Only the SHOW
    # callnative precedes it (hide runs after the yesno returns), so this
    # carries one mug, not two.
    o["CONFIRM_YESNO"] = 85 + mug + sel
    # parked in the "mode enabled" msgbox -- past both callnatives
    o["ENABLED_MSGBOX"] = 107 + 2 * mug + sel + swp
    # parked in the "not available" msgbox of the rejection branch
    o["HIDDEN_MSGBOX"] = o["HIDDEN"] + 11 if sel else -1
    return o


def build(block_rom_addr, char_count, show_mugshot=None, hide_mugshot=None,
          check_selectable=None, sweep_party=None):
    """Return (block_blob, splice_bytes) for a block placed at block_rom_addr.

    v2 flow: yesno -> scrolling character list (all char_count names via the
    magic set index) -> picked index+1 becomes VAR_CHARACTER_ID; cancel
    (0xFFFF, >= char_count) or No answer clears mode state. Either way the
    displaced enhancement prompt is replayed so the original flow continues.
    """
    charmap = load_charmap(CHARMAP_PATH)
    # the charmap file escapes the apostrophe ('\'' = B4), which load_charmap's
    # simple regex misses — add it directly
    charmap["'"] = 0xB4
    prompt = encode_msg(PROMPT_TEXT, charmap)
    numtext = encode_msg(NUMBER_TEXT.replace("{count}", str(char_count)), charmap)
    confirm = encode_msg(CONFIRM_TEXT, charmap)
    enabled = encode_msg(ENABLED_TEXT, charmap)
    hiddentext = encode_msg(HIDDEN_TEXT, charmap)

    # The two mugshot callnatives are 5 bytes each (0x23 + u32) and are only
    # emitted when the caller supplies their addresses, so the fixed label
    # offsets below shift with them. Every OFF_* is still asserted against the
    # real emitted length — a drift shows up as an assertion, not as a script
    # that runs off into the text.
    mug = 5 if (show_mugshot and hide_mugshot) else 0
    # The threshold gate is likewise optional and likewise shifts every label
    # after it: callnative (5) + compare_var_to_value (5) + goto_if (6), plus a
    # 16-byte rejection branch after the `return`.
    sel = 16 if check_selectable else 0

    # fixed-size body, so label offsets are static (+5: breadcrumb setvar).
    # Shared with the live harness via label_offsets() so the two cannot drift.
    _off = label_offsets(show_mugshot, hide_mugshot, check_selectable,
                         sweep_party)
    OFF_PICK = _off["PICK"]        # the number-entry loop head
    OFF_NO = _off["NO"]            # No/cancel branch (clears mode state, falls into replay)
    OFF_REPLAY = _off["REPLAY"]    # replay of the displaced checkflag+goto_if gate
    OFF_HIDDEN = _off["HIDDEN"]    # "not available" branch (right after the `return`)
    OFF_TEXT = _off["TEXT"]        # first text byte
    p_prompt = block_rom_addr + OFF_TEXT
    p_numtext = p_prompt + len(prompt)
    p_confirm = p_numtext + len(numtext)
    p_enabled = p_confirm + len(confirm)
    p_hiddentext = p_enabled + len(enabled)
    p_pick = block_rom_addr + OFF_PICK
    p_no = block_rom_addr + OFF_NO
    p_replay = block_rom_addr + OFF_REPLAY
    p_hidden = block_rom_addr + OFF_HIDDEN

    body = bytearray()
    body += bytes([0x16]) + struct.pack("<HH", VAR_REACHED_BREADCRUMB,
                                        BREADCRUMB_VALUE)              # breadcrumb: splice reached
    body += bytes([0x0F, 0x00]) + struct.pack("<I", p_prompt)          # loadword 0, prompt
    body += bytes([0x09, 0x05])                                        # callstd MSGBOX_YESNO
    body += bytes([0x21]) + struct.pack("<HH", VAR_RESULT, 1)          # compare 0x800D, 1
    body += bytes([0x06, 0x05]) + struct.pack("<I", p_no)              # goto_if NE -> no
    # pick: number-entry loop
    assert len(body) == OFF_PICK, f"OFF_PICK drifted: {len(body)}"
    body += bytes([0x0F, 0x00]) + struct.pack("<I", p_numtext)         # loadword 0, numtext
    body += bytes([0x09, 0x04])                                        # callstd MSGBOX_DEFAULT
    body += bytes([0x25]) + struct.pack("<H", SPECIAL_CHOOSE_NUMBER)   # ChooseNumberScreen
    body += bytes([0x27])                                              # waitstate
    body += bytes([0x21]) + struct.pack("<HH", VAR_RESULT, 0xFFFF)     # empty/cancelled?
    body += bytes([0x06, 0x01]) + struct.pack("<I", p_no)              # goto_if == -> no
    body += bytes([0x21]) + struct.pack("<HH", VAR_RESULT, 1)          # < 1 ?
    body += bytes([0x06, 0x00]) + struct.pack("<I", p_pick)            # goto_if < -> pick
    body += bytes([0x21]) + struct.pack("<HH", VAR_RESULT, char_count + 1)  # > count ?
    body += bytes([0x06, 0x04]) + struct.pack("<I", p_pick)            # goto_if >= -> pick
    if sel:
        # Threshold gate. It runs AFTER the range checks (so the id handed to
        # the native is always 1..count) and BEFORE the copyvar that commits it
        # to VAR_CHARACTER_ID -- a rejected pick must leave no trace, and must
        # not have shown a mugshot for a character the player cannot have.
        assert len(body) == _off["GATE"], \
            f"GATE drifted: {len(body)} != {_off['GATE']}"
        body += bytes([0x23]) + struct.pack("<I", check_selectable)    # callnative check
        body += bytes([0x21]) + struct.pack("<HH", VAR_SELECTABLE, 1)  # selectable?
        body += bytes([0x06, 0x05]) + struct.pack("<I", p_hidden)      # goto_if NE -> hidden
    body += bytes([0x19]) + struct.pack("<HH", VAR_CHARACTER_ID, VAR_RESULT)  # copyvar
    # (ids are 1-based and the player enters 1..count: no +1 adjustment)
    body += bytes([0x25]) + struct.pack("<H", SPECIAL_BUFFER_NAME)     # name -> gStringVar1
    if mug:
        body += bytes([0x23]) + struct.pack("<I", show_mugshot)        # callnative show mugshot
    body += bytes([0x0F, 0x00]) + struct.pack("<I", p_confirm)         # loadword 0, confirm
    body += bytes([0x09, 0x05])                                        # callstd MSGBOX_YESNO
    # The live driver waits for exactly this position to sample the mugshot.
    assert len(body) == _off["CONFIRM_YESNO"], \
        f"CONFIRM_YESNO drifted: {len(body)} != {_off['CONFIRM_YESNO']}"
    if mug:
        # After the yes/no returns, so it runs on BOTH answers — a No sends
        # the script back to p_pick, which would otherwise leave the mugshot
        # up over the number-entry screen.
        body += bytes([0x23]) + struct.pack("<I", hide_mugshot)        # callnative hide mugshot
    body += bytes([0x21]) + struct.pack("<HH", VAR_RESULT, 1)          # confirmed?
    body += bytes([0x06, 0x05]) + struct.pack("<I", p_pick)            # goto_if NE -> pick
    body += bytes([0x29]) + struct.pack("<H", FLAG_CHARACTER_MODE)     # setflag
    if sweep_party:
        # Reconcile whatever the player already has. On the intro path the
        # party is empty and this is a no-op; it earns its place on the
        # settings-NPC / New-Game-Plus re-entry, where the mode can be turned
        # on with a party already in hand. AFTER the setflag on purpose: the
        # sweep returns immediately unless the mode is active.
        body += bytes([0x23]) + struct.pack("<I", sweep_party)         # callnative sweep
    body += bytes([0x0F, 0x00]) + struct.pack("<I", p_enabled)         # loadword 0, enabled
    body += bytes([0x09, 0x04])                                        # callstd MSGBOX_DEFAULT
    assert len(body) == _off["ENABLED_MSGBOX"], \
        f"ENABLED_MSGBOX drifted: {len(body)} != {_off['ENABLED_MSGBOX']}"
    body += bytes([0x05]) + struct.pack("<I", p_replay)                # goto replay (MUST
    # skip the No branch — a fall-through here once cleared the flag right
    # after setting it; caught live by tools/test_harness/live_script_test)
    assert len(body) == OFF_NO, f"OFF_NO drifted: {len(body)}"
    # No/cancel branch: actively clear mode state so if the intro flow is
    # re-entered (difficulty menu Back loop), the LAST answer wins
    body += bytes([0x2A]) + struct.pack("<H", FLAG_CHARACTER_MODE)     # clearflag
    body += bytes([0x16]) + struct.pack("<HH", VAR_CHARACTER_ID, 0)    # setvar id, 0
    assert len(body) == OFF_REPLAY, f"OFF_REPLAY drifted: {len(body)}"
    body += bytes([0x2B]) + struct.pack("<H", 0x0001)                  # replay: checkflag 1
    body += bytes([0x06, 0x01]) + struct.pack("<I", FIRSTRUN_SKIP_PTR) # goto_if TRUE -> skip
    body += bytes([0x03])                                              # return (re-entry path)
    if sel:
        # Rejection branch: name the character the player actually typed (the
        # id is still in VAR_RESULT and still in range, so the buffer special
        # resolves it), say it is unavailable, and go back to the number entry.
        assert len(body) == OFF_HIDDEN, f"OFF_HIDDEN drifted: {len(body)}"
        body += bytes([0x25]) + struct.pack("<H", SPECIAL_BUFFER_NAME) # name -> gStringVar1
        body += bytes([0x0F, 0x00]) + struct.pack("<I", p_hiddentext)  # loadword 0, hiddentext
        body += bytes([0x09, 0x04])                                    # callstd MSGBOX_DEFAULT
        assert len(body) == _off["HIDDEN_MSGBOX"], \
            f"HIDDEN_MSGBOX drifted: {len(body)} != {_off['HIDDEN_MSGBOX']}"
        body += bytes([0x05]) + struct.pack("<I", p_pick)              # goto pick (re-ask)
    assert len(body) == OFF_TEXT, f"OFF_TEXT drifted: {len(body)}"
    body += prompt + numtext + confirm + enabled
    if sel:
        body += hiddentext

    splice = bytes([0x04]) + struct.pack("<I", block_rom_addr) + b"\x00\x00\x00\x00"
    assert len(splice) == len(SPLICE_ORIG)
    return bytes(body), splice


if __name__ == "__main__":
    blob, splice = build(0x08B2B280, 178, 0x08B2B001, 0x08B2B101, 0x08B2B201)
    print(f"block: {len(blob)} bytes; splice: {splice.hex(' ')}")
