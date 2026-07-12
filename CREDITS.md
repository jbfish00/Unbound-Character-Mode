# Character Mode (Unbound) — Art Credits

Character Mode's playable-character sprites are staged from donor sources
via the ROWE Character Mode project (`assets/donor_sprites_staged/`,
`tools/stage_donor_sprites.py`), which itself credits the following games,
decompilation projects, and fan works. Huge thanks to every artist. This mod
is distributed as a patch only, never as a prebuilt ROM.

## Base game / engine

- **Pokémon Unbound** by Skeli789 — the ROM this mod patches.
- **Complete FireRed Upgrade (CFRU)** by Skeli789 and ghoulslash — the open-
  source engine Unbound is built on top of; used here as a structural/shape
  reference during reverse-engineering (not as injected code).
- **Skeli789/Dynamic-Pokemon-Expansion** ("Unbound" branch) — species,
  evolution, and base-stat data tables used to resolve Bulbapedia roster
  names to Unbound's likely internal species ids (provisional pending
  ROM-side verification).
- **pret/pokefirered** decompilation — structural reference for the
  underlying FireRed engine Unbound extends.

## Overworld & trainer sprites (staged via the ROWE project; same original credits apply)

- **pret/pokefirered** — FRLG overworld sprites and trainer fronts for
  Kanto characters.
- **sinnoh-remakes/pokeemerald-platinum** — Gen IV (DPPt) overworld sheets
  and DP trainer fronts (Lucas, Dawn, Cynthia, gym leaders, Elite Four,
  Team Galactic).
- **PokemonHnS-Development/pokemonHnS** — HGSS-style overworld sheets and
  trainer fronts for Johto characters, and HGSS-style walking upgrades for
  the Kanto cast.
- **DiegoWT — "Gen 5 Characters in Gen 4 OW style"**
  (https://eeveeexpo.com/resources/370/) — Unova cast overworld sprites,
  downscaled 0.5x to GBA proportions. Credit required by the resource
  terms; please keep this notice with any redistribution.
- **StreakOfSprites** (https://www.deviantart.com/streakofsprites) — Ash
  Ketchum FRLG-style overworld sprite set.

## Rosters

- Character Pokémon rosters compiled from **Bulbapedia**
  (https://bulbapedia.bulbagarden.net), CC BY-NC-SA.

## Coverage note

96 of 156 characters (Gen 1-5 cast, plus a few Gen 1 anime characters) have
staged donor art. The remaining 60 (Gen 6-8 game-original characters, plus a
handful of anime-only Gen 1-5 characters) have no GBA-style pixel art
anywhere, official or fan-made — per user-confirmed policy, these get a
trainer-card/menu-select portrait only, with a generic/default overworld
costume fallback. See `docs/SPRITE_COVERAGE.md` for the full breakdown.
