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

## Status (2026-07-12 v3)

Phase 0 complete: project scaffolded, ROM extracted from the user-provided zip and checksummed (`b4776b82a4c7915d0fadeaa27e013523f99dfd94`), git initialized, ROM/patches gitignored. ROM header confirms `POKEMON FIRE` / `BPRE` / rev 0 — genuinely FireRed-based, consistent with the CFRU research behind the plan. Note: the zip's readme.txt is a ROM-site watermark ("ROMSFUN.COM & ROMSPURE.CC"), not a self-produced patch record — flagged to the user, proceeding as a personal hobby project per their direction.

Phase 1 in progress, real substance now underway. Toolchain fully verified: `arm-none-eabi-gcc` Thumb output correct, `armips` built and runs, `mgba-qt` has Lua scripting compiled in, `flips` available, and **Ghidra 12.0.2 + `pudii/gba-ghidra-loader` 1.1.0 installed** (`tools/ghidra/`) — confirmed the loader auto-detects the ROM (`GBA Loader`, `ARM:LE:32:v4t:default`) on import. Free-space audit resolved plan risk #3 (~1.46 MiB confirmed free). Full Ghidra auto-analysis of the ROM has been running headlessly in the background for 25+ minutes as of this checkpoint (`ghidra_project/UnboundCM`, log at `docs/ghidra_analysis.log`) — genuinely slow on a 32MB binary with no prior symbol info; still actively consuming CPU, no fatal errors, only benign warnings (thunk-overlap, ARM/Thumb context-switch ambiguity at a handful of addresses — all normal for this kind of raw-binary analysis). A prepared XREF script (`tools/ghidra_scripts/find_xrefs.py`) is ready to run via `-postScript` once it completes.

**Big wins this session** — two independent techniques that don't require waiting on Ghidra at all:
1. `tools/search_gametext.py` + `decode_gametext.py`: encode/decode the Gen3 charmap (reused from ROWE's `charmap.txt`) to search the ROM for game text directly. Validated against known vanilla strings first (`TRAINER`, `POKéMON`, `SAVE`).
2. `tools/find_pointer_refs.py`: GBA code/data reference strings via plain 4-byte little-endian pointers (`file_offset + 0x08000000`) in BOTH data tables and ARM/Thumb literal pools/compiled scripts — so a raw byte search for a string's pointer value finds real references without needing disassembly.

Findings (full detail + exact offsets in `docs/ROUTINE_MAP.md`):
- **Catch mechanic**: the full vanilla catch-message bank (`Gotcha! X was caught!` / nickname / PC-deposit / "Box is full!") at file offset `0x3FD790`+, byte-for-byte the standard FRLG/CFRU bank. Its pointer is referenced once, inside a long ~60+-entry monotonic pointer array — unmistakably pret's `gBattleStringsTable` shape. Strong signal that Unbound's battle-message plumbing hasn't diverged structurally from CFRU/vanilla (a real de-risk of plan risk #1).
- **Mystery Gift**: true dialogue start at `0x1A62D3` ("Oh, hello! You know those words?..."), corroborating the earlier `mevent.c`/`mevent_server.c` debug-string find. Its pointer is referenced once, embedded directly in what reads as compiled map-script bytecode — confirms it's script-triggered, narrows the search but doesn't yet isolate the native routine.
- **Trade**: corrected an earlier mischaracterization — file offset `~0x1F8590`+ is not link-trade dialogue but **Unbound's own "Borrius Trade Quest"**, a self-contained NPC trade-quest table with real named pairs (Alolan Sandshrew↔Quacker the Ducklett, Onix↔Roly-Poly the Electrode, Lickitung↔Top the Hitmontop, Manectric↔Squirry the Pachirisu, Amoonguss↔Shiinotic, ...↔Torch the Lampent). Pointer-search on this one is inconclusive so far — the naive backward-terminator scan wandered into non-text bytes; needs a smarter string-start detector before retrying.
- A weak, unconfirmed starter-selection lead ("Go ahead, choose a Pokémon.") at `0x75CB20` — not yet re-verified.
- Several false leads ruled out and documented in ROUTINE_MAP.md so they aren't re-tried (generic substring matches hitting unrelated text — e.g. "was caught in a sticky web" is a battle move message, not the catch mechanic).

These are **string/script anchors, mostly not confirmed native routines yet** — full XREF analysis (pending Ghidra) or targeted mGBA watchpoints are still needed to close the gap for most of them, though the catch-message table finding is close to confirmed already given how distinctive its shape is.

Still NOT done: the "hello world" injection test (deliberately deferred — Ghidra will make picking a safe hook site far less risky than guessing blind), full XREF-derived routine addresses, intro-menu hook point (text search for likely wording came up empty except one unconfirmed "CHALLENGE" hit — an exhaustive full-ROM string dump, `tools/dump_all_strings.py`, was also kicked off in the background to grep more broadly, still running as of this checkpoint), sprite/trainer-card/battle-pic table locations (need Ghidra's data typing, not text search).

NEXT: check on both background jobs (Ghidra analysis, exhaustive string dump) and pick up from there — run the XREF script against all string/pointer anchors once Ghidra is done, grep the full string dump for menu/mode/option/randomizer wording, fix the trade-table string-start detection, and re-verify the starter-selection lead.
