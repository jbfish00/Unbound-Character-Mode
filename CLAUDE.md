# CLAUDE.md — Pokemon Unbound "Character Mode"

Guidance for Claude Code when working in this repo. Keep this file current at every pause — it's the handoff doc for a fresh instance picking this up cold.

## What this project is

Porting the "Character Mode" feature from the Pokemon ROWE project (`/home/jbfish00/Documents/Pokemon Rowe Alteration`) to Pokemon Unbound v2.1.1.1: an opt-in intro-menu choice to play as an iconic Pokemon character, restricted to that character's Bulbapedia-documented roster (evolution families included). See the full plan at `~/.claude/plans/cuddly-nibbling-sutton.md` for roster scope (Gen 1-4 full breadth, Gen 5-9 gym leaders/E4/champions/rivals/anime/villains, Alain from Gen 6) and phase breakdown.

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

## Status (2026-07-12 v4)

Phase 0 complete (see v1 below for detail — checksum, ROM header, provenance note).

**Phase 1 (reverse-engineering/feasibility) — substantially advanced, not yet gate-closed.** Toolchain fully verified: `arm-none-eabi-gcc` Thumb output correct, `armips` built, `mgba-qt` has Lua scripting compiled in, `flips` available, **Ghidra 12.0.2 + `pudii/gba-ghidra-loader` 1.1.0 installed** and confirmed working (auto-detects the ROM as `GBA Loader`/`ARM:LE:32:v4t:default`). Free-space audit resolved plan risk #3 (~1.46 MiB confirmed free, not a bottleneck). Full Ghidra auto-analysis has been running headlessly in the background for **over an hour** as of this checkpoint — a background wait (`until ! pgrep ...` via Bash `run_in_background`) is armed and will notify on completion; do not assume it's done without checking `docs/ghidra_analysis.log` / process status, it may also be worth just re-running with a shorter scope or `-noanalysis` + targeted scripting if it never finishes cleanly.

Two independent techniques found real routine leads **without needing Ghidra at all** — both documented in full in `docs/ROUTINE_MAP.md`:
1. `tools/search_gametext.py`/`decode_gametext.py`: Gen3-charmap text search (reused from ROWE's `charmap.txt`), validated against known vanilla strings first.
2. `tools/find_pointer_refs.py`: raw 4-byte-LE pointer search — GBA code/data reference strings via plain pointers in both data tables and ARM/Thumb literal pools/compiled scripts, findable without disassembly.

Key findings:
- **Catch mechanic — much stronger than a single lead now.** The vanilla catch-message bank (`Gotcha!`/nickname/PC-deposit/"Box is full!") sits inside a fully-bounded 374-entry pointer table (`0x3FDF3C`–`0x3FE514`) matching pret's `gBattleStringsTable` size. Searching for references to the table's *base* (not just one entry) found **26 hits**, densely clustered in file offsets `0xCEFEC`–`0xD8494` (~57 KB) — the shape of many separate battle-message call sites in a `battle_script_commands.c`-equivalent file. This is now a multi-source, converging signal that Unbound's battle-message plumbing hasn't diverged from CFRU/vanilla — a real de-risk of the plan's risk #1. Next: narrow which of the 26 sites is catch-specific (most are probably generic).
- **Mystery Gift**: confirmed script-triggered (pointer embedded in compiled map-script bytecode), true dialogue start `0x1A62D3`.
- **Trade**: corrected a mischaracterization — it's Unbound's own named "Borrius Trade Quest" NPC table, not link-trade dialogue.
- Weak unconfirmed starter-selection lead, several false leads ruled out and documented so they aren't re-tried.

Still NOT done: the "hello world" injection test (deliberately deferred until a real hook site is known), intro-menu hook point (text search for likely wording came up empty — an exhaustive full-ROM string dump, `tools/dump_all_strings.py`, has ALSO been running in the background for 35+ minutes; a second background wait is armed for it too), sprite/trainer-card/battle-pic table locations.

**Phase 2 (roster data pipeline) — DONE and fully tested, independent of Phase 1.**
- **Major mid-pipeline discovery: Unbound v2.1.1.1 has NO Gen 9 content.** Confirmed two ways: (a) empirically, every Gen 8 species tested via text-search (including legendaries like Zacian) was found in-ROM, all 18 Gen 9 species tested (starters, popular mons, Paradox forms, Koraidon/Miraidon) were not; (b) the DPE Unbound-branch donor's own `species.h` independently stops at Gen 8 Gigantamax forms (`NUM_SPECIES` = 1294). Matches the plan's original web research. User confirmed: **Gen 9 characters dropped from `characters.txt` entirely** (22 characters removed — Geeta, Nemona, Team Star, Liko/Roy, etc.). Final roster scope is Gen 1-8 + Alain, not Gen 1-9.
- `characters.txt`: 156 characters, adapted from ROWE's already-vetted roster with Gen 5-8 restricted to gym leaders/E4/champions/rivals/villains/anime (no protagonists; Gen 7 excludes Trial Captains/Kahunas; Gen 8 has no Elite Four).
- `scrape_rosters.py`: reused verbatim from ROWE (game-agnostic), reusing ROWE's 3761-file Bulbapedia cache — all 156 characters scraped cleanly, 0 missing pages, 0 empty rosters.
- `map_species.py`: **required real rework, not a copy** — resolves against `Skeli789/Dynamic-Pokemon-Expansion`'s `Unbound` branch (cloned to `tools/dpe_unbound_donor/`, gitignored). Discovered the donor's string-table `NAME_X` labels do NOT reliably match `species.h`'s `SPECIES_X` constants (e.g. `NAME_CRABMINBLE` for `SPECIES_CRABOMINABLE`) — the reliable anchor turned out to be the string table's **0-indexed position exactly equals the numeric species id** (verified against multiple spot-checks, and the table's total length exactly matches `NUM_SPECIES`). Rewrote around that instead of name-label parsing. Final result: 156/156 characters mapped, 0 empty rosters, only the 4 expected Gen-9-only names left unmatched. **All numeric species ids are PROVISIONAL** (from the DPE donor, not yet cross-checked against the real compiled ROM) — flagged in every output file, do not trust for actual injection until Phase 1 verifies them.
- `emit_characters.py`: rewritten from ROWE's C-header generator into a flat binary emitter (`characters.bin`/`rosters.bin`/`names.bin`, 12-byte fixed records, ~10 KB total) — reuses the Gen3 charmap encoder for real in-game text bytes. Round-trip tested (Red → Pikachu id 25 signature, correct Kanto roster; names decode correctly). `sprite_asset_id` is a placeholder (`0xFFFF`) pending Phase 3.

**Phase 3 (sprites) — survey done, injection blocked on Phase 1.** Cross-referenced our 156 characters against ROWE's existing sprite coverage: **97/156 (62%) have at least one reusable donor asset** already sitting in ROWE's tree (Gen 1-5 cast), the other 59 are exactly the Gen 6-8 (+ a few anime-only) characters with zero GBA-style art anywhere, matching the user-agreed lighter "trainer-card portrait only" policy. Full detail in `docs/SPRITE_COVERAGE.md`. Actual injection needs Unbound's sprite table addresses and compression format confirmed (Phase 1), so this is prep, not yet actionable.

**Phases 4-6 not started** — all gated on Phase 1 producing confirmed (not just anchored) routine addresses.

NEXT: check both armed background waits (Ghidra analysis, exhaustive string dump) for completion; run the XREF script against all string/pointer anchors once Ghidra is available; narrow the 26 battle-string-table call sites to find the specific catch handler; keep pushing the pointer-reference technique (worked well twice now — table-boundary scanning + base-pointer search) on the Mystery Gift and gift-handler leads before falling back to Ghidra/mGBA for everything.
