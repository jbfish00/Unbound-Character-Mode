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

NEXT: decode the enhancement-options menu's script bytecode to find its flag/var writes (concrete Phase 4 hook target); keep using `InspectRegions.java`-style targeted disassembly rather than full-ROM Ghidra analysis; narrow the 4 inspected battle-string-table call sites (run Ghidra's Decompiler on them, not just disassembly) to find the actual catch-success handler; find the gift-Pokémon-from-NPC handler (still unconfirmed).
