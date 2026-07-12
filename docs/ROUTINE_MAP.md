# Routine Map — Pokemon Unbound (v2.1.1.1).gba

The project's substitute for a public symbol table. Every finding is tagged:
- **CONFIRMED** — address verified by trace/patch-and-observe (code located and behavior proven).
- **STRING ANCHOR** — a data string is located and its content strongly implies which subsystem/dialogue it belongs to; the *code* that reads/displays it (the actual routine we need) is not yet located. Next step for these is Ghidra XREF analysis (find what code references the string's address) or an mGBA read-watchpoint on the string bytes.
- **LIKELY** — inferred from CFRU/pret source shape, not yet verified against this binary at all.
- **UNKNOWN** — not yet investigated.

All offsets below are **file offsets** into `rom/Pokemon Unbound (v2.1.1.1).gba` (pinned to `rom.sha1`). GBA ROM is memory-mapped at `0x08000000`, so the in-emulator/Ghidra address = file offset + `0x08000000` (e.g. file offset `0x3FD7A2` → ROM address `0x083FD7A2`).

Text was located with `tools/search_gametext.py` (Gen3-charmap string search, reusing ROWE's `charmap.txt`) and read with `tools/decode_gametext.py`. The charmap was sanity-checked against known vanilla strings (`TRAINER`, `POKéMON`, `SAVE` all decoded correctly) before trusting any hit.

## Catch mechanic — STRING ANCHOR (strong lead)

File offset `0x3FD790`–`0x3FD8xx` decodes to the full vanilla catch-sequence string bank, contiguous and in the expected order:
```
Gotcha! [X] was caught!
Gotcha! [X] was caught! (variant, different trailing control codes — likely the "+ new Pokédex entry" flow)
Give a nickname to the captured [X]?
[X] was sent to [Y]'s PC. / someone's / Bill's
[X]'s data was added to the Pokédex!
It is raining. / A sandstorm is raging. (weather-affects-catch-rate flavor lines, same bank)
The Box is full! You can't catch any more!
```
This is byte-for-byte the standard FRLG/CFRU catch message bank (not reworded), which is a good sign for risk #1 in the plan (Unbound's catch subsystem may not have diverged much from a CFRU-shape compile, at least at the message layer). **Next step**: once Ghidra analysis completes, find XREFs to `0x083FD7A2` ("Gotcha!") and `0x083FD86x` ("Box is full") — those functions are the real catch-success/catch-overflow handlers we need to hook for the "off-roster catch fails" enforcement.

## Mystery Gift — STRING ANCHOR (strong lead)

File offset `0x1A6317`–`0x1A6385` decodes to Mystery Gift explanation dialogue ("...you must know about the MYSTERY GIFT... From now on, you should be receiving MYSTERY GIFTS!... Once you save your game, you can access the MYSTERY GIFT... Thank you for accessing the MYSTERY GIFT System..."). Corroborated by Phase-1's earlier debug-string find: the ROM retains original GameFreak assert strings naming `mevent.c` and `mevent_server.c` (Mystery Event/Gift source files in the pret/pokefirered decomp) — those files are the known real implementation this dialogue belongs to. **Next step**: XREF from these string addresses once Ghidra is done, cross-reference against pokefirered's `mevent.c`/`mevent_server.c` structure for the species-assignment call site.

## Trade sequence — STRING ANCHOR (strong lead, corrected from earlier pass)

Earlier pass mischaracterized this as link-trade dialogue — a wider read proved it wrong. File offset `~0x1F8590`–`0x1F85BBA`+ is **Unbound's actual "Borrius Trade Quest" NPC in-game trade table** — a self-contained sidequest with real, named, Unbound-specific trade pairs:
```
"It looks like there are still residents of Borrius that are willing to trade.
 Trade with all of them, and then I'll give you a nice reward."
...
Alolan Sandshrew  <->  Quacker the Ducklett
Onix              <->  Roly-Poly the Electrode
Lickitung         <->  Top the Hitmontop
Manectric         <->  Squirry the Pachirisu
Amoonguss         <->  Shiinotic  (two-way, both directions listed)
... (table continues past what's been read so far)
```
"Borrius" is Unbound's custom region name, confirming this is genuinely Unbound-authored content, not a leftover vanilla string. This is a much better hook-point candidate than the original guess — it's a clean, self-contained table of species-for-species swaps, exactly the shape of code the plan needs to find (something that reads an incoming species and assigns an outgoing one). **Next step**: XREF from these string addresses (once Ghidra is done) to find the actual trade-handler function; also read further past `0x1F85BBA` to capture the rest of the trade table (this dump was truncated mid-table).

## Starter selection — RULED OUT (was a weak lead; now identified as something else)

File offset `0x75CB20` ("Go ahead, choose a Pokémon.") is **NOT starter selection** — wider context read (`0x75CA80`+) shows it's part of a mid-story escape sequence: "...If we each take one, we can use them to attack the guard and escape! Here, take this Poké Ball I picked up. [X] received a Poké Ball from [Y]! [Go ahead, choose a Pokémon.]" This is a scripted cutscene (an ally hands you a spare Poké Ball during an escape), not the game's opening starter pick. Do not use this as the starter-selection hook.

Still potentially useful as a **generic gift-item/gift-Pokémon message lead**: "[X] received a [Y] from [Z]!" reads like shared vanilla-shape infrastructure (the standard FRLG "received an item/Pokémon from" message format), which could be the same underlying print routine used across many gift scenarios, not just this one cutscene. Not yet pointer-searched — worth trying once the true string start is pinned down (this one also needs the careful backward-scan-to-real-boundary treatment other leads required).

Real starter-selection dialogue is still **UNKNOWN** — not yet found by any technique. Candidate search terms tried and failed: generic "starter" substring (too many false positives, see below).

False leads ruled out during this search (recorded so they aren't re-tried): plain `"starter"` substring-matched unrelated dialogue about "starters" (ferry/ocean traffic flavor text) — too generic a search term. `"was caught"` substring-matched a battle move effect message ("was caught in a sticky web!" — String Shot/Sticky Web) as well as the real catch text — needs the fuller surrounding-context check every time, not just a raw hit count.

## Pointer-reference technique (no Ghidra needed for this class of finding)

Discovered a technique that works without waiting for Ghidra: GBA code and data reference strings via plain 4-byte little-endian pointers (`file_offset + 0x08000000`) — this is true both for data tables *and* for ARM/Thumb literal pools and compiled script bytecode, since none of those embed the address as a relative/encoded value. `tools/find_pointer_refs.py` searches the raw ROM bytes for a given string's pointer value directly. Important nuance learned the hard way: the pointer always targets the **true start** of the enclosing string, not wherever a keyword search happened to match mid-sentence — back up to the preceding `0xFF` terminator first (with caution: `0xFF` also appears in non-text binary/script data, so a long backtrack distance is a red flag that the heuristic wandered into non-text bytes, not a real string boundary; short, plausible backtracks like the mystery-gift case below are trustworthy, the trade-table case's 3.7 KB backtrack was not and needs a different approach).

Results:
- **Catch message ("Gotcha!") — table fully bounded, real code now inspected via Ghidra (upgraded twice this session).** File offset `0x3FD7A2`'s pointer is referenced at `0x3FE338`, inside a table now fully bounded by scanning outward for the full run of valid `0x08xxxxxx`-range pointers: starts at `0x3FDF3C`, ends (exclusive) at `0x3FE514` — **374 entries**, a size right in line with pret's known `gBattleStringsTable`. Searching for pointer references to the table's *base* (`0x3FDF3C`) found **26 hits**, densely clustered in file offsets `0xCEFEC`–`0xD8494` (~57 KB), plus 3 outliers.
  - Ghidra's full-ROM auto-analysis (headless, `-analysisTimeoutPerFile 3600`) ran for the full hour and **timed out** before reaching this region — its own `getReferencesTo()` found zero refs here, confirming the timeout genuinely left large parts of the ROM unanalyzed, not just slow. Full auto-analysis is not a reliable way to reach specific regions of a ROM this size in one pass.
  - Worked around it with a **targeted-disassembly script** (`tools/ghidra_scripts/InspectRegions.java`) that force-disassembles small windows around known addresses directly, using the FlatProgramAPI — much faster than a full re-analysis for a handful of known sites. Caught and fixed a real pitfall: the default `disassemble()` call decodes in **ARM mode**, producing plausible-looking but wrong 32-bit instructions ("adcs r8,r0,#0x4000001" nonsense) for what's actually **Thumb (16-bit)** GBA code — had to explicitly set the `TMode` context register to 1 before disassembling. Also had to `clearListing()` first to undo the bad ARM-mode analysis from the first attempt.
  - With Thumb mode forced, 4 of the 26 sites (`0x080CF068`, `0x080CF328`, `0x080CF3F0`, `0x080CFE50`) show real, sensible code, and 2 more (`0x080CFB28`, `0x080D8494`) turned out to be thunks (`b <target>`) pointing elsewhere, not inspected further yet.
  - **Ran Ghidra's Decompiler on the 4 real functions — this REVISES the earlier hypothesis, not just refines it.** The decompiled C shows a `get-a-value → validate via a lookup function → branch` pattern, e.g. (from `FUN_080cf328`):
    ```c
    uVar3 = FUN_0803fbe8();          // get some 16-bit value (a candidate id?)
    uVar3 = uVar3 & 0xffff;
    iVar4 = func_0x080441b8(uVar3);   // validate/look up that id
    if (iVar4 != 0) {                 // valid: print a fixed message, bump a per-slot counter, done
        FUN_080d77f4(*(ptr)(table_base + offset));
        ...
    } else {                          // invalid: build a message with the id embedded via a TEXT PLACEHOLDER
        *buf = 0xFD;      // Gen3 CHAR_DYNAMIC control code
        buf[1] = 2;        // placeholder-kind byte
        buf[2] = (char)uVar3; buf[3] = (char)(uVar3 >> 8);   // the id itself, LE
        buf[4] = 0xFF;
        StringExpandPlaceholders_equivalent(); print_equivalent();
        ...
    }
    ```
    This is a **validate-a-candidate-and-report-if-invalid** shape, not a generic "print battle message N" dispatcher. Given this sits right next to code the Species Randomizer plausibly needs (validate a randomly-picked species id, report if it's not a legal candidate), **these 4 functions more likely belong to the Species Randomizer's own internals than to the catch-message system** — even though the STRING CONTENT identification of the 374-entry table (containing "Gotcha!"/"Box is full!" etc., matching `gBattleStringsTable`'s size) is still solid and unchanged. What's revised is the earlier claim about what the 26 *code* cross-references to the table's base are for — "26 generic battle-message call sites" was an oversimplification, and for at least these 4, likely an incorrect one.
  - **Net effect on risk #1**: still de-risked (this is real, coherent, sensibly-structured ARM/Thumb code — not something exotic), but the *specific* claim "found the catch handler's neighborhood" needs walking back. The catch-success/catch-failure handler is still genuinely unconfirmed.
  - **Decompiled 5 more of the 26 sites** (`0x080CF148`, `0x080CF3A8`, `0x080CF438`, `0x080CF46C`, `0x080CF498`) — all show the same family shape: write a few fields into a `(bank_index)*8 + base` struct (offsets `+0x14`/`+0x16`/`+0x18` recur — plausibly per-active-script-instance state, stride 8 bytes per instance), sometimes call `FUN_080d77f4`/`func_0x080d87bc` (print-adjacent calls, same two functions recur across sites), and return via a **shared tail-branch epilogue at `0x080cf526`–`0x080cf536`** (`pop {r3,r4,r5} / mov r8,r3 / ... / pop {r0} / bx r0`). Ghidra's decompiler mislabeled this shared epilogue as an "UNRECOVERED_JUMPTABLE" (its switch-table heuristic misfired on it) — **corrected**: it's an ordinary function return sequence multiple nearby functions tail-branch into to share code size, not a script-command dispatch table. No opcode-to-handler mapping has actually been found yet.
  - **Working theory (still not fully confirmed)**: this whole `0xCEFEC`–`0xD8494` region is very plausibly the compiled `scrcmd.c`-equivalent (many small per-command handler functions, each touching a per-script-instance state struct and calling shared print helpers) — this would line up with the *retained debug-assert string* naming `scrcmd.c` as a real source file in this ROM (found earlier this session, see the strings-dump section above). If true, this is exactly the right neighborhood for catch/gift/trade script commands generally, just not confirmed to be reached via "battle string table" specifically — the 374-entry table may be a broader shared text bank used by many different script commands (of which catching is one), not something exclusively battle-specific.
  - Two remaining avenues: (a) find the actual opcode→handler dispatch mechanism (not yet located — would let us map a known opcode byte value, like the `0x2B`/`0x16` found in the enhancement-menu script, directly to its handler function address); (b) fall back to the plan's originally-envisioned technique — live mGBA watchpoint tracing while the built-in Species Randomizer or an actual catch attempt is exercised interactively, which needs the user's involvement per the ROWE precedent (Phase 5 territory, not attempted this session).
- **Mystery Gift dialogue — confirmed to be script-invoked.** True string start (after backing up past a plausible preceding terminator) is `0x1A62D3` ("Oh, hello! You know those words? That means you must know about the MYSTERY GIFT..."). Its one pointer reference is at file offset `0x1A7770`, embedded directly in what looks like compiled map-script bytecode (single-byte opcodes interleaved with a handful of 2-4 byte operands, e.g. `... D3 62 1A 08 09 04 ...` — the 4 bytes `D3 62 1A 08` are exactly our pointer in LE form). This confirms Mystery Gift's intro dialogue is triggered from a scripted event, as expected, but the actual native routine (invoked from the script via a `special`-style call, most likely) hasn't been isolated yet — that needs either Ghidra's script/special-function-table cross-referencing or manually decoding more of the surrounding script bytes against pret's `scrcmd.c` opcode table (which we already have a real anchor for, from the retained debug-assert filename).
- **Trade table — pointer search inconclusive so far.** The naive backward-terminator-scan landed implausibly far back (3.7 KB), a sign the heuristic crossed into non-text bytes rather than finding a real string boundary; needs a smarter string-start detection (e.g. reuse `dump_all_strings.py`'s decode-forward validator to find the previous *valid* decoded run's start, not just the previous raw `0xFF` byte) before trusting a pointer search here.

## Intro "enhancement options" menu — FOUND (major win, was the last big unknown for Phase 4's menu hook)

The exhaustive full-ROM string dump (`tools/dump_all_strings.py`, ~210K lines, ran ~40 min in the background) found exactly what the plan predicted would be the best precedent for Character Mode's own opt-in intro menu — Unbound's real new-game setup flow, starting at file offset `~0x1F1060`:

```
Expert / Insane / Challenging / Back          (difficulty sub-menu options)
"Would you like to view game enhancement options?"
"Would you like to view [randomizer] options?"
"Would you like to enable the [species] randomizer?"
"The [species] randomizer has been enabled."
"Would you like to enable the [level-up moveset] randomizer?" / enabled confirmation
"Would you like to enable the [Ability] randomizer?" / enabled confirmation
"Note that the randomizer will be temporarily disabled during boss battles."
"Would you like to play a variant with stat rebalancing?" / enabled confirmation
  + a full paragraph explaining the rebalancing math (BST ~600, Shedinja/Huge Power exceptions)
```

This is a real, working, **multi-step opt-in toggle system** exposed at new-game setup — a near-ideal structural precedent (or literal insertion point — a "Character Mode" toggle could plausibly be added as one more entry in this same sequence) for where Character Mode's own character-select menu should hook in.

The true string start ("Would you like to view game enhancement options?") is at file offset `0x1F1065C`. Its pointer is referenced once, at file offset `0x1E70005`, embedded in what reads as compiled script bytecode (small-opcode-plus-operand rhythm matching what we saw for the Mystery Gift reference: `... 5C 06 F1 09 ...` — `5C 06 F1 09` is exactly this pointer in LE form, `0x09F1065C`). Confirms this menu is script-driven, same mechanism as other dialogue flows.

### Script opcodes decoded — CONFIRMED (independently cross-validated, not guessed)

Scanned the raw script bytes for `0x1E6FF80`–`0x1E70120` (covering the species/moveset/ability randomizer toggle sequence) for a repeating pattern, since three near-identical "would you like to enable the X randomizer?" prompts should compile to near-identical script snippets differing only in which flag they set:

```
0x01E700AA: 2B FD 09   -> setflag(0x09FD)
0x01E700B3: 2B FE 09   -> setflag(0x09FE)
0x01E700BC: 2B 22 15   -> setflag(0x1522)
```

**`0x09FD` is an exact match for `FLAG_UNBOUND_SPECIES_RANDOMIZER`**, the one flag ID the plan's original research already had documented (via Unbound-Cloud's reverse-engineered save format). This independently confirms two things at once: **opcode `0x2B` is `setflag(u16 flagId)`**, and this specific script-decoding approach is correct, not a coincidental pattern match. `0x09FE` (moveset randomizer, presumably) and `0x1522` (ability randomizer or the next toggle, presumably) are two more real, in-use flag IDs, newly discovered.

Also found the companion `setvar` pattern:
```
0x01E70042 / 0x01E7006B: 16 00 80 ...  -> setvar(VAR=0x8000, ...)
0x01E700DB / 0x01E700E9 / 0x01E700F7: 16 06 80 ...  -> setvar(VAR=0x8006, ...)
```
`0x8000`/`0x8006` land exactly in pret's standard "special var" range (`VAR_RESULT = 0x8000` is the classic convention) — another independent confirmation that Unbound's scripting engine hasn't diverged from the vanilla/CFRU shape.

**Practical takeaway for Phase 4**: `FLAG_CHARACTER_MODE`/`VAR_CHARACTER_ID` must avoid at least `0x09FD`, `0x09FE`, `0x1522`, `0x8000`, `0x8006` (now confirmed in-use) plus the previously-known `VAR_UNBOUND_GAME_DIFFICULTY 0x50DF` — still not a complete unused-range map, but real, growing, confirmed exclusions rather than the empty list Phase 4 started with. **Not yet done**: decode the branch/condition bytes around each `setflag` (which opcode reads the yes/no answer and decides whether to execute it) to fully understand the pattern before reusing it, and locate the very first "difficulty" root prompt that starts this whole flow.

## Not yet found / not yet searched

- Gift-Pokémon-from-NPC handler (distinct from Mystery Gift and from trades) — no confirmed string lead yet. Ruled out one candidate: the generic "received a ___ from ___" phrase (37 separate hits across the ROM) is NOT shared infrastructure — these are independently-written NPC dialogue lines, not one reusable template, so it's not a useful pointer-search anchor.
- **Correction**: the `0x4162E8`/`0x417713` Deposit/Withdraw/Storage text clusters are the **Bag's item-storage PC box** ("Store items in the PC", "Withdraw Item", item pocket categories) — NOT the Pokémon Storage System. Not relevant to Character Mode's party/PC-routing enforcement.
- The actually-relevant "route to PC" message for Character Mode enforcement is **already found**: it's part of the catch-message string bank (`0x3FD790`+ — "[X] was sent to [Y]'s PC", "someone's", "Bill's", "The Box is full!"), already tied into the 26-xref battle-string-table finding above. No separate search needed for this.
- ~~Intro menu / opt-in mode hook point~~ **FOUND** — see the "Intro enhancement options menu" section above.
- Overworld sprite table, trainer-card asset table, battle-intro pic table — not started (these are binary data tables, not findable via text search; need Ghidra's data-type analysis or manual structure hunting once available).
- Entry point / boot sequence address for a "hello world" injection hook — the injection MECHANISM is now built and verified (`tools/inject_code.py`, tested clean against a confirmed-free ROM block, exactly the right bytes changed), but no hook site has been wired yet — still need a call site to branch into injected code, not just a place to put it.

## Free space

See `docs/FREE_SPACE.md` — resolved, ~1.46 MiB confirmed free (0xFF-padded), not a blocker.

## Toolchain status

See `CLAUDE.md` — `arm-none-eabi-gcc`, `armips`, `mgba-qt` (Lua scripting compiled in) all verified working. **Ghidra 12.0.2 + `pudii/gba-ghidra-loader` 1.1.0 now installed** at `tools/ghidra/` (matched-version pair, confirmed the loader auto-detects the ROM as `GBA Loader` / `ARM:LE:32:v4t:default` on import). Full auto-analysis of the imported ROM is running (headless, `ghidra_project/UnboundCM`) — this is a genuinely long-running job on a 32MB binary; check `docs/ghidra_analysis.log` and process status before assuming it's done. Once complete, the next concrete step is running XREF queries against the string anchors above to convert them from "string anchor" to "confirmed routine."
