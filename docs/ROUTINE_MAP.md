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

## Starter selection — WEAK LEAD, needs verification

File offset `0x75CB20`: "Go ahead, choose a Pokémon." — plausible starter-selection or gift-selection prompt, but not yet confirmed which screen it belongs to (could be a lab starter pick, a gift-egg pick, or something else entirely). Text immediately following this string decodes to garbage/mixed encoding, suggesting the window read past the string's actual terminator into unrelated data — needs a tighter re-read once we know the real string length. **Do not build on this without confirming first.**

False leads ruled out during this search (recorded so they aren't re-tried): plain `"starter"` substring-matched unrelated dialogue about "starters" (ferry/ocean traffic flavor text) — too generic a search term. `"was caught"` substring-matched a battle move effect message ("was caught in a sticky web!" — String Shot/Sticky Web) as well as the real catch text — needs the fuller surrounding-context check every time, not just a raw hit count.

## Pointer-reference technique (no Ghidra needed for this class of finding)

Discovered a technique that works without waiting for Ghidra: GBA code and data reference strings via plain 4-byte little-endian pointers (`file_offset + 0x08000000`) — this is true both for data tables *and* for ARM/Thumb literal pools and compiled script bytecode, since none of those embed the address as a relative/encoded value. `tools/find_pointer_refs.py` searches the raw ROM bytes for a given string's pointer value directly. Important nuance learned the hard way: the pointer always targets the **true start** of the enclosing string, not wherever a keyword search happened to match mid-sentence — back up to the preceding `0xFF` terminator first (with caution: `0xFF` also appears in non-text binary/script data, so a long backtrack distance is a red flag that the heuristic wandered into non-text bytes, not a real string boundary; short, plausible backtracks like the mystery-gift case below are trustworthy, the trade-table case's 3.7 KB backtrack was not and needs a different approach).

Results:
- **Catch message ("Gotcha!") — table fully bounded, code region found (upgraded from earlier pass).** File offset `0x3FD7A2`'s pointer is referenced at `0x3FE338`, inside a table now fully bounded by scanning outward for the full run of valid `0x08xxxxxx`-range pointers: starts at `0x3FDF3C`, ends (exclusive) at `0x3FE514` — **374 entries**, a size right in line with pret's known `gBattleStringsTable`. Searching for pointer references to the table's *base* (`0x3FDF3C`, not just the one "Gotcha!" entry) found **26 hits**, almost all densely clustered in file offsets `0xCEFEC`–`0xD8494` (~57 KB code region), plus 3 outliers (`0x883580`, `0x8C0DDC`, `0x9A32E8`). Dense multi-site references to the same table base is exactly the shape of many separate battle-message-printing call sites throughout a `battle_script_commands.c`-equivalent file (ARM/Thumb code commonly keeps a local literal-pool copy of a constant per call site, rather than one shared reference) — this is now a strong, converging, MULTI-SOURCE signal (not just one lucky find) that Unbound's battle-message plumbing has NOT diverged from the CFRU/vanilla shape (risk #1 substantially de-risked). Once Ghidra's disassembly is available, the next step is narrowing which of the 26 call sites specifically handles the catch-success flow (most of the 26 are probably generic — used for damage/status/faint text too, not catch-specific) rather than treating all 26 as catch routines.
- **Mystery Gift dialogue — confirmed to be script-invoked.** True string start (after backing up past a plausible preceding terminator) is `0x1A62D3` ("Oh, hello! You know those words? That means you must know about the MYSTERY GIFT..."). Its one pointer reference is at file offset `0x1A7770`, embedded directly in what looks like compiled map-script bytecode (single-byte opcodes interleaved with a handful of 2-4 byte operands, e.g. `... D3 62 1A 08 09 04 ...` — the 4 bytes `D3 62 1A 08` are exactly our pointer in LE form). This confirms Mystery Gift's intro dialogue is triggered from a scripted event, as expected, but the actual native routine (invoked from the script via a `special`-style call, most likely) hasn't been isolated yet — that needs either Ghidra's script/special-function-table cross-referencing or manually decoding more of the surrounding script bytes against pret's `scrcmd.c` opcode table (which we already have a real anchor for, from the retained debug-assert filename).
- **Trade table — pointer search inconclusive so far.** The naive backward-terminator-scan landed implausibly far back (3.7 KB), a sign the heuristic crossed into non-text bytes rather than finding a real string boundary; needs a smarter string-start detection (e.g. reuse `dump_all_strings.py`'s decode-forward validator to find the previous *valid* decoded run's start, not just the previous raw `0xFF` byte) before trusting a pointer search here.

## Not yet found / not yet searched

- Gift-Pokémon-from-NPC handler (distinct from Mystery Gift and from trades) — no confirmed string lead yet.
- Party/PC "route to PC when full or disallowed" logic — Deposit/Withdraw/Storage/Release/Nickname text banks were found (`0x4162E8` deposit cluster, `0x417713` withdraw cluster) but not yet cross-referenced to code.
- Intro menu / opt-in mode hook point (the plan's lead was Unbound's built-in Species Randomizer "enhancement options" intro menu) — not yet searched for by text; needs candidate phrases for that specific menu's wording (guesses tried: RANDOMIZER, ENHANCEMENT, OPTIONS, DIFFICULTY, CHALLENGE, FEATURES, SETTINGS, SANDBOX, NEW GAME+ — none hit except "CHALLENGE" once, single unconfirmed hit at `0x3E8B0B`, not yet decoded/verified).
- Overworld sprite table, trainer-card asset table, battle-intro pic table — not started (these are binary data tables, not findable via text search; need Ghidra's data-type analysis or manual structure hunting once available).
- Entry point / boot sequence address for a "hello world" injection hook — not yet attempted (deliberately deferred until Ghidra static analysis gives us a real candidate instead of guessing blind).

## Free space

See `docs/FREE_SPACE.md` — resolved, ~1.46 MiB confirmed free (0xFF-padded), not a blocker.

## Toolchain status

See `CLAUDE.md` — `arm-none-eabi-gcc`, `armips`, `mgba-qt` (Lua scripting compiled in) all verified working. **Ghidra 12.0.2 + `pudii/gba-ghidra-loader` 1.1.0 now installed** at `tools/ghidra/` (matched-version pair, confirmed the loader auto-detects the ROM as `GBA Loader` / `ARM:LE:32:v4t:default` on import). Full auto-analysis of the imported ROM is running (headless, `ghidra_project/UnboundCM`) — this is a genuinely long-running job on a 32MB binary; check `docs/ghidra_analysis.log` and process status before assuming it's done. Once complete, the next concrete step is running XREF queries against the string anchors above to convert them from "string anchor" to "confirmed routine."
