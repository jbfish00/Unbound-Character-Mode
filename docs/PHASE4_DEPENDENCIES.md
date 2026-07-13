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

## Group B — Unbound engine functions — **RESOLVED (2026-07-12 v8)**

All addresses confirmed two independent ways: decompiled-handler shape match AND name match in CFRU's FR symbol map (`tools/cfru_donor/BPRE.ld`). Unbound's engine core is vanilla FireRed with CFRU hooks; the vanilla addresses below are live in this ROM. Full derivation in `docs/ROUTINE_MAP.md` (v8 top section).

| Extern | Address | Notes |
|---|---|---|
| `FlagGet` | `0x0806E6D0\|1` | verified via checkflag(0x2B) handler |
| `VarGet` | `0x0806E568\|1` | verified via givemon handler; `VarSet` = `0x0806E584\|1` |
| `GetMonData` | `0x0803FBE8\|1` | vanilla field ids OK for SPECIES/IS_EGG (CFRU only appends past the vanilla enum) |
| `GetMonDataIsEgg` | — | fold into `GetMonData(mon, MON_DATA_IS_EGG, NULL)`; drop the separate extern |
| `SendMonToPC` | `0x08040B90\|1` (vanilla) | CFRU replaces it (commented out in BPRE.ld); **prefer hooking `GiveMonToPlayer` = `0x089C905C\|1`**, which routes party-vs-PC itself (returns `MON_GIVEN_TO_PARTY=0`) |
| `ZeroMonData` | `0x0803D994\|1` | |
| `CompactPartySlots` | `0x080937DC\|1` | |
| `CalculatePlayerPartyCount` | `0x08040C3C\|1` | |
| `gPlayerParty` | `0x02024284` | `sizeof(struct Pokemon)` = 100 (0x64), vanilla layout |
| `GetFirstEvolution` / `GetBaseFormSpeciesId` | — | reimplement against `gEvolutionTable` = `0x08259754` (**verify not DPE-repointed first**), or better: precompute evolution families into the roster data at emit time (Phase 2's scripts already expand families — the ROM-side check may not need evolution walking at all) |

Bonus addresses for the enforcement/menu work (same confidence):
- `GiveMonToPlayer` (CFRU) = `0x089C905C|1` — THE enforcement choke point (all catches + all scripted gifts)
- `atkEF_handleballthrow` = `0x089C8BE4|1`, `atkF0_givecaughtmon` = `0x089C97AC|1` (live battle cmd table @ file `0x099FFFC`)
- `ScriptGiveMon` = `0x080A011C|1`, `ScriptGiveEgg` = `0x080A01AC|1`
- `FlagSet` = `0x0806E680|1`, `FlagClear` = `0x0806E6A8|1`, `GetVarPointer` = `0x0806E454|1`
- `SetMonData` = `0x0804037C|1`, `CopyMon` = `0x08040B08|1`, `GetSpeciesName` = `0x08040FD0|1`
- `gSpecialVar_Result` (VAR 0x800D) = `0x020370D0`, `gStringVar1/2/4` = `0x02021CD0/CF0/D18`
- `gSpecials` table = `0x0815FD60` (444 entries), `gScriptCmdTable` = `0x0815F9B4`

## Group C — flag/var allocation (Phase 4, needs an empirical unused-range scan)

`FLAG_CHARACTER_MODE` / `VAR_CHARACTER_ID` are placeholder `0` in the source — must be chosen from a confirmed-unused range. Known-real Unbound ids so far (via Unbound-Cloud, see the plan): `FLAG_UNBOUND_SPECIES_RANDOMIZER 0x9FD`, `VAR_UNBOUND_GAME_DIFFICULTY 0x50DF` — neither of these two placeholders has been checked against a fuller list yet.

## What this means practically

This file is **ready to receive real values** the moment Phase 1 produces them — no further logic design work is needed here, just filling in Group B's addresses/signatures (the hard part) and Group A's injection addresses (mechanical, once free-space allocation is decided). Group C is a quick empirical scan once a save file or fuller flag/var reference exists.
