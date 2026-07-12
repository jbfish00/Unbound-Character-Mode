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

## Status (2026-07-12 v2)

Phase 0 complete: project scaffolded, ROM extracted from the user-provided zip and checksummed (`b4776b82a4c7915d0fadeaa27e013523f99dfd94`), git initialized, ROM/patches gitignored. ROM header confirms `POKEMON FIRE` / `BPRE` / rev 0 — genuinely FireRed-based, consistent with the CFRU research behind the plan. Note: the zip's readme.txt is a ROM-site watermark ("ROMSFUN.COM & ROMSPURE.CC"), not a self-produced patch record — flagged to the user, proceeding as a personal hobby project per their direction.

Phase 1 in progress, real substance now underway. Toolchain fully verified: `arm-none-eabi-gcc` Thumb output correct, `armips` built and runs, `mgba-qt` has Lua scripting compiled in, `flips` available, and **Ghidra 12.0.2 + `pudii/gba-ghidra-loader` 1.1.0 installed** (`tools/ghidra/`) — confirmed the loader auto-detects the ROM (`GBA Loader`, `ARM:LE:32:v4t:default`) on import. Free-space audit resolved plan risk #3 (~1.46 MiB confirmed free). Full Ghidra auto-analysis of the ROM is running headlessly in the background (`ghidra_project/UnboundCM`, log at `docs/ghidra_analysis.log`) — this is genuinely slow on a 32MB binary; check process status before assuming it's done (as of this checkpoint: ~6 min CPU time in, still working through the address space, no fatal errors, some benign thunk-overlap warnings).

**Big win this session**: built `tools/search_gametext.py` + `tools/decode_gametext.py`, which encode/decode the Gen3 charmap (reused from ROWE's `charmap.txt`) to search the ROM for game text directly — no Ghidra/disassembly needed for this part. Validated against known vanilla strings first (`TRAINER`, `POKéMON`, `SAVE` all decoded correctly), then found several strong **string anchors** for Phase 1's target routines — see `docs/ROUTINE_MAP.md` for full detail and exact offsets:
- The full vanilla catch-sequence string bank (`Gotcha! X was caught!` / nickname prompt / PC-deposit message / "The Box is full!") at file offset `0x3FD790`+ — byte-for-byte the standard FRLG/CFRU bank, a good sign the catch subsystem hasn't diverged much structurally.
- Mystery Gift explanation dialogue at `0x1A6317`+, corroborating the earlier `mevent.c`/`mevent_server.c` debug-string find.
- A link-trade confirmation dialogue cluster at `0x1F85A25`+ (likely NOT the same path as an NPC in-game trade — that's still unfound).
- A weak, unconfirmed starter-selection lead ("Go ahead, choose a Pokémon.") at `0x75CB20`.
- Several false leads ruled out and documented (generic substring matches hitting unrelated text) — see ROUTINE_MAP.md so they aren't re-tried.

These are **string anchors, not routines yet** — the actual code that reads/displays each string still needs to be found via Ghidra XREF analysis (pending completion) or an mGBA read-watchpoint on the string bytes. That conversion is the next concrete step.

Still NOT done: the "hello world" injection test (deliberately deferred — no confirmed safe hook site yet, and Ghidra will make picking one far less risky than guessing blind), any XREF-derived routine addresses, intro-menu hook point (text search for likely wording came up empty except one unconfirmed "CHALLENGE" hit), sprite/trainer-card/battle-pic table locations (need Ghidra's data typing, not text search).

NEXT: once Ghidra's analysis finishes, run XREF queries against each string anchor above to convert them into confirmed routine addresses (this is the core of the go/no-go gate). In parallel, text-search for better NPC-in-game-trade and intro-menu candidate phrases, and re-check the starter-selection lead with a properly bounded read (it likely got cut off mid-string).
