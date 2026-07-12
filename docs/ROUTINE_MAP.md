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

## Trade sequence — STRING ANCHOR (moderate lead, likely link/wireless trade not NPC in-game trade)

File offset `0x1F85A25`–`0x1F85BBA`: tight cluster of "In exchange"/"Traded" strings — this reads as the link-trade confirmation dialogue ("In exchange, I'll send you a Pokémon!" / "Traded ... for ..."), which is probably NOT the same code path as an NPC in-game trade (give-one-get-one, no link cable). Both eventually call something like the ROWE precedent's species-assignment site, but need to be treated as two separate hook candidates, not assumed to be one. **Next step**: also locate NPC in-game trade dialogue specifically (search terms tried so far were too generic — need better candidate phrases, e.g. names of actual known in-game trade NPCs once we have a walkthrough/map reference).

## Starter selection — WEAK LEAD, needs verification

File offset `0x75CB20`: "Go ahead, choose a Pokémon." — plausible starter-selection or gift-selection prompt, but not yet confirmed which screen it belongs to (could be a lab starter pick, a gift-egg pick, or something else entirely). Text immediately following this string decodes to garbage/mixed encoding, suggesting the window read past the string's actual terminator into unrelated data — needs a tighter re-read once we know the real string length. **Do not build on this without confirming first.**

False leads ruled out during this search (recorded so they aren't re-tried): plain `"starter"` substring-matched unrelated dialogue about "starters" (ferry/ocean traffic flavor text) — too generic a search term. `"was caught"` substring-matched a battle move effect message ("was caught in a sticky web!" — String Shot/Sticky Web) as well as the real catch text — needs the fuller surrounding-context check every time, not just a raw hit count.

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
