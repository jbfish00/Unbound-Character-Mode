# CLAUDE.md — Pokemon Unbound "Character Mode"

Guidance for Claude Code when working in this repo. Keep this file current at every pause — it's the handoff doc for a fresh instance picking this up cold.

## What this project is

Porting the "Character Mode" feature from the Pokemon ROWE project (`/home/jbfish00/Documents/Pokemon Rowe Alteration`) to Pokemon Unbound v2.1.1.1: an opt-in intro-menu choice to play as an iconic Pokemon character, restricted to that character's Bulbapedia-documented roster (evolution families included). See the full plan at `~/.claude/plans/cuddly-nibbling-sutton.md` for phase breakdown. **Roster scope (updated from the original plan): Gen 1-4 full breadth, Gen 5-8 gym leaders/E4/champions/rivals/anime/villains, Alain from Gen 6 — Gen 9 was dropped entirely, confirmed this ROM has no Gen 9 species at all.** 156 characters total, see `tools/character_mode/characters.txt`.

**Critical difference from ROWE: Unbound has no public source.** It's a closed binary hack (Skeli789) built on the open-source CFRU engine, but Unbound's own content is proprietary. This project is classic binary ROM hacking — reverse-engineer a compiled ROM, inject new code/data into free space, output a patch (never redistribute the ROM).

## Standing rules (carried over from the ROWE project, user-confirmed pattern)

- **Checkpoint rule**: at every pause, update this file + the plan file for seamless handoff.
- **Ask questions until 95% confident** before making consequential decisions.
- Distribution: patch only (UPS/BPS via `tools/bin/flips`), never a prebuilt/redistributed ROM.
- Every located ROM address is pinned to the exact SHA1 in `rom.sha1`. Re-verify before trusting notes against any other copy.

## Repo layout

- `rom/` — extracted ROM + readme (gitignored, never commit).
- `rom.sha1` — checksum of the source ROM; all findings are pinned to this.
- `docs/ROM_INFO.md` — ROM header/provenance notes.
- `docs/FREE_SPACE.md` — free-space audit results.
- `tools/scan_free_space.py` — free-space scanner (rerunnable).
- `tools/armips/` — armips source clone + build (`tools/armips/build/armips`).
- `tools/bin/` — convenience copies: `armips`, `flips`.

## Toolchain (confirmed working this session)

- `arm-none-eabi-gcc` (system-installed, 13.2.1) — for new freestanding C, **not** `~/agbcc` (that exists to byte-match GameFreak's original compiler for decomp source; irrelevant here since we're writing brand-new injected functions, not reproducing existing ones). Verified: `-mthumb -mcpu=arm7tdmi -mtune=arm7tdmi -O2 -ffreestanding -fno-builtin` produces correct ARMv4T Thumb code.
- `armips` v0.11.0 — built from source (`Kingcom/armips`, cmake+make, no apt package available). Binary at `tools/bin/armips`.
- `mgba-qt` 0.10.2 (system-installed) — confirmed linked against `liblua5.4`, so its Scripting console (Tools → Scripting) is available for dynamic tracing/watchpoints. Not yet exercised against the real ROM.
- `flips` — reused read-only copy from the ROWE repo (`tools/bin/flips`), for UPS/BPS patch output later.
- Ghidra + a GBA loader plugin (`pudii/gba-ghidra-loader` or `SiD3W4y/GhidraGBA`) — **not yet installed**. Needed for static disassembly once we start hunting for actual game-logic routines (catch/gift/trade/menu).
- `cmake` was installed via `apt-get` this session (was missing; needed to build armips).

## Free space (resolved — see docs/FREE_SPACE.md)

~1.46 MiB confirmed free (0xFF-padded) across 264 runs; three big blocks (337 KiB @ 0x015FBC90, 147 KiB @ 0x00B2B280, 101 KiB @ 0x01FE6C64) are the primary injection targets. This was flagged as an open risk in the plan and is now resolved — free space is not the bottleneck.

## Status (2026-07-12 v7)

Continued Phase 1 solo (no interactive mGBA session this pass — see v6's note that live tracing needs the user; this pass focused on the two static-analysis avenues v6 flagged as still available solo). Three concrete units of progress, one of them a definitive negative result rather than a "maybe":

1. **Battle-string-table xref cluster (26 sites) — fully surveyed, 26/26 now decompiled, and the catch-handler hypothesis is formally RULED OUT for this region**, not just "still unconfirmed" as v6 left it. Every site is the same `scrcmd.c`-equivalent per-instance-state-write family (small helper calls + shared tail-branch epilogue), none show catch-success/failure or PC-routing logic. Real tooling gotcha found and fixed along the way: `InspectRegions.java`/`DecompileFunc.java`/`FindXrefs.java`'s own header comments about the hex address format were wrong/self-contradictory — addresses must include the `0x08` ROM-base prefix (e.g. `080CF068`, not `000CF068`) or `toAddr()` silently resolves to an unmapped address and every downstream call becomes a silent no-op. Fixed the comments in all three scripts. (Initially misdiagnosed this as possible Ghidra-project data loss from an interrupted second full-analysis attempt found mid-session — `docs/ghidra_analysis2.log`, no completion report, stale-looking `.lock` files — but that was a red herring; the project data was intact, targeted per-address analysis just needs the right address format. The interrupted second full-analysis attempt itself is still a minor loose end: no idea why it was started, given v6 explicitly recommended against it, or why it didn't run to completion — not investigated further since it turned out not to matter.)
2. **Enhancement-menu Yes/No branch mechanism decoded.** Found the actual `compare_var_to_value`/`goto_if` pair that gates each `setflag`, and that the Yes/No answer itself lands in a newly-identified scratch var, **`0x800D`** — the concrete var Character Mode's own opt-in prompt will need to read. Also surfaced a caveat worth remembering: opcode `0x29` touches the same flag ids as the real `setflag` (`0x2B`) but is a different instruction (likely `checkflag`/`clearflag`) — don't conflate the two when scanning for flag usage. Three more real flag ids found in the process (`0x16E4`, `0x1503`, `0x170E`), added to Phase 4's exclusion list.
3. **Gift-Pokémon-from-NPC handler — found, two distinct real instances** (an "exhausted Sinnoh caretaker" NPC offering Turtwig/Chimchar/Piplup, and a "neglected companions" NPC with 3 unspecified Pokémon), both confirmed script-invoked via pointer refs. Correctly distinguished from a superficially similar but different case (a battle ally/partner-selection picker) — see `docs/ROUTINE_MAP.md` for the full writeup and how to tell them apart.

Full details, decoded byte sequences, and exact offsets are in `docs/ROUTINE_MAP.md` (updated this pass, not duplicated here). Net effect on Phase 1: the catch handler search needs a new avenue (the 26-site cluster is now eliminated, not just deprioritized) — most promising remaining static-analysis avenues are (a) finding the actual opcode→handler dispatch table now that several real opcode values are confirmed (`0x06`,`0x16`,`0x21`,`0x2B`, maybe `0x29`), or (b) tracing the two new gift-Pokémon leads' native handlers the same way Mystery Gift/trade still need tracing. Both are solo-doable. Live mGBA watchpoint tracing (v6's other suggested avenue) still needs the user's involvement and wasn't attempted this pass.

NEXT: hunt for the opcode→handler dispatch table (would let confirmed opcode values `0x06`/`0x16`/`0x21`/`0x2B` map straight to handler addresses, and by extension find catch/gift/trade's real handlers without more guesswork); trace the two new gift-Pokémon NPCs' native routines from their script pointer refs (`0x1E63745`, `0x1E8E8C6`); resolve opcode `0x29`'s exact semantics (checkflag vs clearflag) since it's now a confirmed-but-unlabeled instruction; when a session with the user is available, prefer live mGBA watchpoint tracing during an actual catch/gift/trade over further blind static analysis, per v6's original recommendation.

## Status (2026-07-12 v6)

Continued Phase 1 deep-dive after v5. Two genuinely new, solid wins, plus an important self-correction:

1. **Decoded real script opcodes from the enhancement-options menu, cross-validated independently.** Found `setflag` = opcode `0x2B` (u16 operand) and `setvar` = opcode `0x16`, by spotting a repeated pattern across the 3 near-identical randomizer-toggle prompts. The species-randomizer prompt's flag decoded to `0x09FD` — an **exact match** for `FLAG_UNBOUND_SPECIES_RANDOMIZER`, the one flag id the plan already had from Unbound-Cloud's research. That's a real independent confirmation, not a coincidental pattern. Also found `0x09FE`, `0x1522` (two more real flags), `0x8000`/`0x8006` (setvar targets, landing exactly in pret's standard "special var" range). Practical effect: `FLAG_CHARACTER_MODE`/`VAR_CHARACTER_ID` now have five confirmed real IDs to avoid, up from zero.
2. **Self-corrected the battle-string-table/catch-handler hypothesis after decompiling more sites.** Ran Ghidra's Decompiler (not just disassembly) on 9 of the 26 xref sites. The code doesn't look like generic battle-message printing as first claimed — it's a `get-candidate → validate → branch, with a species/id embedded via a Gen3 text placeholder on failure` shape, more consistent with Species Randomizer validation internals. Also caught Ghidra's decompiler mislabeling a shared function-return epilogue as an "UNRECOVERED_JUMPTABLE" — it's not a dispatch table, just several nearby functions tail-branching into a shared `pop {...} / bx r0` return sequence. Current working theory (not fully confirmed): this whole code region is the compiled `scrcmd.c`-equivalent (matches a retained debug-assert string naming that exact file), which would still make it the right neighborhood for catch/gift script commands generally — just not confirmed to be catch-specific yet. **The catch-success handler is still genuinely unconfirmed** — this is deliberately walked back from the more confident-sounding v4/early-v5 framing.

Given how much manual Ghidra-assisted RE has been squeezed out of static analysis this session (two real wins, but also two real corrections after deeper inspection), the next unit of real progress likely needs either substantially more Ghidra time (targeted decompilation of the remaining ~17 xref sites, or finding the actual opcode dispatch table) or the plan's originally-envisioned live mGBA watchpoint tracing — which needs interactive gameplay, better suited to a session with the user's involvement (matching how ROWE's own testing worked) than further blind static analysis.

## Status (2026-07-12 v5)

Phase 0 complete. **Phase 2 (roster data pipeline) is DONE and fully tested** — 156 characters (Gen 1-8 + Alain; confirmed Gen 9 doesn't exist in this ROM at all, two independent ways, dropped entirely), 0 empty rosters, binary tables emitted and round-trip verified (`tools/character_mode/{characters,rosters,names}.bin`). `map_species.py` needed a real rewrite: the DPE donor's string-table labels don't reliably match its own `SPECIES_*` constants, but the table's 0-indexed **position** exactly equals the numeric species id — rewrote around that once discovered. All species ids remain PROVISIONAL pending ROM-side verification.

**Phase 1 (reverse-engineering) — major progress this session, still not gate-closed.**
- Ghidra's full-ROM auto-analysis **timed out at 60 minutes** without reaching most of the ROM — its own `getReferencesTo()` came back empty even for addresses we'd already proven have real references via manual byte search. Full auto-analysis is not a reliable way to cover a 32MB ROM in one pass; don't re-run it blindly expecting completion.
- Built `tools/ghidra_scripts/InspectRegions.java` (Java GhidraScript — `.py` scripts route through PyGhidra in Ghidra 12, which needs `jpype`/Python bindings we don't have installed; Java scripts need no extra setup) to force-disassemble small windows around specific known addresses instead of waiting on full analysis. Caught a real bug doing this: the default `disassemble()` decodes in **ARM mode**, producing plausible-but-wrong 32-bit instructions for what's actually **Thumb** GBA code — fixed by explicitly setting the `TMode` context register before disassembling.
- With that fixed, found **real code** at 4 of the battle-string-table's 26 xref sites. This corrected an oversimplification from the previous pass: it's not one shared "dispatcher," each site does its own thing (some index the table as 8-byte records via a `×8` stride, not straight 4-byte pointers) — the table's exact semantic shape isn't fully resolved yet, but the code is coherent, sensible, vanilla/CFRU-shaped ARM/Thumb — still a real de-risk of the plan's risk #1, just a more nuanced one than first claimed.
- **Major find: Unbound's real intro "enhancement options" menu located**, via the (separately-run, ~40 min) exhaustive string dump (`tools/dump_all_strings.py`, `docs/all_strings_dump.txt`, gitignored, ~210K lines). Exact flow: difficulty select (Expert/Insane/Challenging) → "Would you like to view game enhancement options?" → randomizer toggles (species/moveset/ability) → stat-rebalancing variant, each with its own enable-confirmation message. This is close to a literal insertion point for Character Mode's own opt-in toggle — add it as one more entry in this same real, working, script-driven sequence. True string start `0x1F1065C`, one pointer reference at `0x1E70005` (script bytecode, same shape as the Mystery Gift reference). Next: decode more of the surrounding script to find the actual flag/var write per prompt answer.
- **Built and verified the actual free-space injection mechanism** (`tools/inject_code.py`, modeled on CFRU's `insert.py` but parameterized by target address instead of one fixed reserved offset): compile → link at a fixed ROM address → extract raw bytes → splice into a ROM copy. Tested end-to-end against a real confirmed-free block — exactly 8 bytes changed in the entire 32MB ROM, and they disassembled back to exactly the expected `x*2+1` Thumb code. This is the literal mechanism Phase 1's "hello world" test and Phase 4's real injection both need; only a confirmed hook/call site is still missing, not the tooling.
- Ruled out: generic "received a ___ from ___" (37 unrelated hardcoded lines, not shared infra), corrected the Deposit/Withdraw text find (it's the Bag's item PC, not the Pokémon Storage System — the real "sent to PC" message for Character Mode enforcement was already found as part of the catch-message bank), corrected the earlier "starter selection" guess (it's actually a mid-story escape-sequence cutscene).

**Phase 3 (sprites) — real staging done, injection still blocked on Phase 1.** Beyond the earlier coverage survey, actually **staged 96/156 characters' donor assets** (`tools/stage_donor_sprites.py`, `assets/donor_sprites_staged/`, 3.5 MB, 157 PNGs) copied from ROWE's tree, including 52 files that are **already LZ77-compressed** (`.4bpp.lz`) — if Unbound turns out to use standard GBA compression (still unconfirmed), these could need little or no reprocessing. `CREDITS.md` written.

**Phase 4 (enforcement logic) — core algorithm written and compiles cleanly.** `src/character_mode.c` ports ROWE's roster-membership/party-sweep logic to read our binary table format directly. Compiles with zero warnings (`arm-none-eabi-gcc -mthumb -mcpu=arm7tdmi -O2 -ffreestanding -fno-builtin`) and produces exactly 4 defined functions with 13 precisely-scoped unresolved externs — see `docs/PHASE4_DEPENDENCIES.md` for exactly what each one needs (mostly: Unbound's real `FlagGet`/`VarGet`/`GetMonData`/`SendMonToPC`-equivalent addresses and signatures, still Phase 1's job to find).

**Phase 5-6 not started** — genuinely blocked on Phase 1 producing confirmed routine addresses, not just anchors.

(superseded by v7 above — see NEXT there for the current handoff point)
