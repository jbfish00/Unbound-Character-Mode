# Phase 4 dependency checklist — src/character_mode.c

`src/character_mode.c` compiles cleanly now (`arm-none-eabi-gcc -c -mthumb -mcpu=arm7tdmi -O2 -ffreestanding -fno-builtin`, zero warnings — verified this session) but is **not link-complete**: it has 13 unresolved external symbols that need real Unbound ROM addresses/definitions before this can be injected. This is the concrete, scoped remainder of Phase 1+4's work as far as this file is concerned.

Run `arm-none-eabi-nm` on the compiled object to reproduce this list:
```
U CalculatePlayerPartyCount
U CompactPartySlots
U FlagGet
U gCharacterCount        -- from Phase 2's emit_characters.py output, needs a ROM address once injected
U gCharacterRosters       -- rosters.bin, needs a ROM address once injected
U gCharacterTable         -- characters.bin, needs a ROM address once injected
U GetBaseFormSpeciesId
U GetFirstEvolution
U GetMonData
U GetMonDataIsEgg
U gPlayerParty
U SendMonToPC
U VarGet
U ZeroMonData
```

## Group A — our own injected data (Phase 2 output, needs Phase 1's free-space injection mechanics)

Already built and tested (`tools/character_mode/{characters,rosters,names}.bin`) — just needs an actual ROM address once the insert script (Phase 1-informed) places these blobs in free space (candidates: 337 KiB @ file offset `0x015FBC90` or 147 KiB @ `0x00B2B280`, see `docs/FREE_SPACE.md`).

- `gCharacterTable` → `characters.bin`
- `gCharacterRosters` → `rosters.bin`
- `gCharacterCount` → constant, 156 (or however many after any later roster edits)

## Group B — Unbound engine functions (Phase 1 reverse-engineering, NOT yet located)

These are the real remaining unknowns. Assumed CFRU/vanilla-shaped signatures based on the battle-string-table finding (`docs/ROUTINE_MAP.md` — Unbound's battle-message plumbing hasn't diverged structurally), but that's supporting evidence, not confirmation for these specific functions.

- `FlagGet(u16 flagId)` / `VarGet(u16 varId)` — save-block flag/var accessors. Vanilla FRLG has these as simple, extremely commonly-called leaf functions; should be easy to spot via Ghidra once available (called from hundreds of sites) or via the Species Randomizer's own flag checks (it must call these to know its settings — a good tracing entry point).
- `GetMonData(mon, field, unused)` — the field-id enum (`MON_DATA_SPECIES` etc.) is Unbound-specific; CFRU is known to extend the vanilla enum for new mechanics (Tera-equivalent, Battle Styles, etc.) so vanilla field ids are a starting guess, not a given.
- `GetMonDataIsEgg(mon)` — may not exist as a separate function; could just be `GetMonData(mon, MON_DATA_IS_EGG, ...)` — this file's split is speculative, revisit once the real API shape is known.
- `GetFirstEvolution(species)` / `GetBaseFormSpeciesId(species)` — ROWE has these as real functions in its decomp source (`src/level_scaling.c`); Unbound's equivalent (if it exists as a discrete function at all — could be inlined) needs to be found or reimplemented against Unbound's real evolution table once its address is known.
- `SendMonToPC(mon)` — the actual PC-deposit routine; return-value convention (`MON_CANT_GIVE`-equivalent) unconfirmed.
- `ZeroMonData(mon)` / `CompactPartySlots()` / `CalculatePlayerPartyCount()` — party-array maintenance helpers.
- `gPlayerParty` — base address of the live party array; this file's indexing math (`gPlayerParty + i * 0`) is a literal placeholder — `sizeof(struct Pokemon)` (or Unbound's equivalent struct) must be known before this is real code, not just compiles-cleanly code.

## Group C — flag/var allocation (Phase 4, needs an empirical unused-range scan)

`FLAG_CHARACTER_MODE` / `VAR_CHARACTER_ID` are placeholder `0` in the source — must be chosen from a confirmed-unused range. Known-real Unbound ids so far (via Unbound-Cloud, see the plan): `FLAG_UNBOUND_SPECIES_RANDOMIZER 0x9FD`, `VAR_UNBOUND_GAME_DIFFICULTY 0x50DF` — neither of these two placeholders has been checked against a fuller list yet.

## What this means practically

This file is **ready to receive real values** the moment Phase 1 produces them — no further logic design work is needed here, just filling in Group B's addresses/signatures (the hard part) and Group A's injection addresses (mechanical, once free-space allocation is decided). Group C is a quick empirical scan once a save file or fuller flag/var reference exists.
