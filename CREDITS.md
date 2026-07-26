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

## Ash Gray donor art (added 2026-07-23)

- **Pokemon Ash Gray** (FireRed hack) by **metapod23** — anime-character
  trainer sprites (Jessie & James duo, Ritchie, Tracey, Duplica, Todd,
  Giselle, A.J., Otoshi, Samurai, Damian, Gary, Orange Islands leaders,
  anime-style Kanto leaders) and Ash player art, staged in
  `sprites/donors/ashgray/`. Ripped from a locally-built copy (BPS patch on
  a source-built clean FireRed). Credit metapod23 in any distribution that
  ships this art.


## Emerald Rogue — trainer, back and overworld sprites (added 2026-07-25)

Staged in `sprites/donors/rogue/` — 294 sprites covering 160 Character Mode
characters (149 trainer front pics, 133 overworld sheets, 12 battle back pics),
filtered from a 531-file harvest down to characters actually on the roster.

- **Source**: https://github.com/Pokabbie/pokeemerald-rogue, branch `vanilla`,
  commit `79c1df5f8a2ebb423c7a48d29de0cf21ef5783e7`, fetched 2026-07-25.
- **Format**: converted from the repo's PNGs by `tools/png_to_gba.py` into
  `.4bpp` + `.gbapal` and LZ77 (BIOS type 0x10) streams of each. Every blob was
  round-tripped through the decompressor before staging.
- **Licensing**: the repository has **no LICENSE file**. Its in-game credits
  roll is the only attribution trail that exists, and it maps no artist to any
  individual file — so the **whole list travels with any subset of the art**.

**"Additional Sprites" — Emerald Rogue credits roll, reproduced in full:**

AveonTrainer · PurpleZaffre · UlithiumDragon · HighNoonMoon · xDracolich ·
ZacWeavile · Gnomowladny · Beliot419 · Brumirage · Kyledove · Kymotionian ·
cSc-A7X · 2and2makes5 · Pokegirl4ever · Fernandojl · Silver-Skie · Kid1513 ·
TyranitarDark · Getsuei-H · Milomilotic11 · Kyt666 · kdiamo11 · Chocosrawloid ·
SyleDude · Gallanty · Gizamimi-Pichu · princess-phoenix · LunarDusk6 ·
Larryturbo · Kidkatt · Zender1752 · SageDeoxys · Lasee0 · Ezerart · Wolfang62 ·
DarkusShadow · Anarlaurendil · Lasse00 · shaderr31 · CarmaNekko · EduarPokeN ·
TintjeMadelintje101

Plus the Emerald Rogue project itself (Pokabbie) for assembling and converting
the set.
