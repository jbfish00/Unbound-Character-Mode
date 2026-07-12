# Sprite/asset coverage — Phase 3 planning

Cross-referenced our 156-character roster (`tools/character_mode/characters.txt`) against the ROWE Character Mode project's already-built sprite report (`/home/jbfish00/Documents/Pokemon Rowe Alteration/tools/character_mode/sprite_report.txt`), since our Gen 1-8 roster is largely the same real-world characters ROWE already sourced donor art for.

## Coverage summary

| | count | % of 156 |
|---|---|---|
| Have an overworld sprite candidate | 97 | 62% |
| Have a trainer front-pic candidate | 69 | 44% |
| Have a battle back-pic candidate | 11 | 7% |
| Have AT LEAST ONE asset | 97 | 62% |
| Have NO assets in ROWE's tree | 59 | 38% |

## Pattern (matches plan expectations exactly)

The 59 characters with zero ROWE coverage are, without exception, Gen 6-8 (Kalos/Alola/Galar) roles plus a handful of Gen 1-5 anime-only characters (Ritchie, Tracey, Jessie, James, Lyra, Drew, Paul, Zoey, Nando, Trip) that ROWE's own status notes already flagged as never sourced ("no GBA-style walking sheets exist publicly"). This is exactly the split the user already accepted when scoping this project: GBA-style pixel art genuinely doesn't exist anywhere (official or fan-made) for 3D-model-era (Gen 6-8) characters, so those get the lighter-weight trainer-card/menu-portrait-only treatment, not full OW+front+back sprites.

## What this means for Phase 3

- **97 characters (Gen 1-5 + a few Gen1 anime like Ash/Gary)**: candidate donor PNGs exist in ROWE's `graphics/trainers/front_pics/`, `graphics/trainers/back_pics/`, `graphics/object_events/` (303 front pics, 18 back pics, 1546 OW-related PNGs total in that tree, not all character-mode-specific — needs filtering). ROWE's sprite_report.txt gives *symbol names* (`OBJ_EVENT_GFX_CM_X`, `TRAINER_PIC_X`, `TRAINER_BACK_PIC_X`), not raw file paths — resolving symbol → exact PNG filename needs ROWE's `spritesheet_rules.mk`/`graphics_file_rules.mk` (not yet done; deferred until Phase 3 actually starts, since the real injection work is gated on Phase 1 anyway).
- **59 characters (Gen 6-8 + a few anime)**: no GBA-style art exists anywhere. Per user-confirmed policy: trainer-card/menu-select portrait only (widely available as fan-ripped icons for these game-original characters), generic/default costume fallback for their overworld appearance — no bespoke pixel art expected.
- Actually copying/injecting any of this is blocked on Phase 1 confirming: (a) Unbound's OW sprite table and trainer-pic table addresses, (b) whether Unbound uses standard GBA 4bpp+LZ77 compression for its custom sprite additions (open risk #7 in the plan, unconfirmed).

## Reuse mechanics (once unblocked)

Same credits-file discipline as ROWE (`CREDITS_CHARACTER_MODE.md` pattern) — a `CREDITS.md` will need the same donor list: pret/pokefirered, sinnoh-remakes/pokeemerald-platinum, PokemonHnS-Development/pokemonHnS, DiegoWT's Gen5-in-Gen4-style resource, StreakOfSprites' Ash sheet. Injection differs from ROWE's Makefile-automated pipeline: raw tile/palette data needs manual LZ77 compression and free-space injection with hand-patched pointers (see Phase 3 in the plan).
