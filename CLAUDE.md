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

## Status (2026-07-12 v1)

Phase 0 complete: project scaffolded, ROM extracted from the user-provided zip and checksummed (`b4776b82a4c7915d0fadeaa27e013523f99dfd94`), git initialized, ROM/patches gitignored. ROM header confirms `POKEMON FIRE` / `BPRE` / rev 0 — genuinely FireRed-based, consistent with the CFRU research behind the plan. Note: the zip's readme.txt is a ROM-site watermark ("ROMSFUN.COM & ROMSPURE.CC"), not a self-produced patch record — flagged to the user, proceeding as a personal hobby project per their direction.

Phase 1 in progress (toolchain bring-up + free-space audit done, real routine-tracing not yet started):
- Toolchain verified: `arm-none-eabi-gcc` Thumb output correct, `armips` built and runs, `mgba-qt` has Lua scripting compiled in, `flips` available.
- Free-space audit done and resolved (see above) — this de-risks plan risk #3 entirely.
- **NOT yet done**: the "hello world" injection test (compile → insert into free space → hook → confirm execution in mGBA) — deliberately not attempted blind this session, since a safe/known hook site hasn't been identified yet and a wrong guess risks wasted cycles on a crash with no diagnostic info. Needs either (a) a well-known, hack-agnostic FireRed boot-sequence address as a first low-stakes hook target, cross-referenced against pret/pokefirered decomp, or (b) Ghidra set up first so a candidate hook site can be read/verified statically before trying it live.
- **NOT yet done**: Ghidra + GBA loader plugin installation.
- **NOT yet done**: any routine tracing (catch/gift/trade/starter/menu/sprite tables) — this is the actual substance of Phase 1's go/no-go gate and hasn't started.

NEXT: install Ghidra + a GBA loader plugin, identify a safe first hook site (likely via pret/pokefirered's well-documented `AgbMain`/boot sequence as a hack-agnostic starting point, verified statically before touching the live ROM), run the hello-world injection test end-to-end in mGBA, then begin empirical routine tracing via the built-in Species Randomizer + mGBA watchpoints as the plan describes.
