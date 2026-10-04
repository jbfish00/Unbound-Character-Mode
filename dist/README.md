# Character Mode for Pokemon Unbound v2.1.1.1

An opt-in game mode: at the start of a new game, pick one of 193 iconic
Pokemon characters (protagonists, rivals, gym leaders, Elite Four,
champions, villains, and anime cast, Generations 1-8) and play the whole
game restricted to that character's canon Pokemon.

## What it does

- **New-game prompt**: right after Unbound's difficulty questionnaire, an
  extra question offers Character Mode. Enter your character's number
  (see CHARACTERS.md), confirm, and the mode is locked in for that save.
- **Starter**: your starter is replaced by your character's own starter
  (their signature Pokemon's base stage).
- **Catching**: wild Pokemon outside your character's roster cannot be
  caught — the ball is dodged, like the game's own no-catching zones.
  Rosters include full evolution families of every canon team member.
- **Gifts**: scripted gift Pokemon that are off-roster go to your PC
  instead of your party (so nothing is ever lost, and gift events never
  block progress).
- **In-game trades**: you can still complete every Borrius trade; an
  off-roster incoming Pokemon is sent to your PC after the trade.
- **Wild encounters**: about 10% of wild encounters are replaced by a
  Pokemon from your character's roster, at a level that fits the area,
  so you can actually find your team instead of hunting for it. The
  other ~90% are the game's own encounters, unchanged.
- **Legendaries**: if your character's roster includes a legendary, it
  has about a 1% chance of appearing in any wild encounter, at the
  area's level. Each one is offered until you catch it, then stops
  appearing — unless your character's roster is legendaries only, in
  which case they keep appearing so you always have something to catch.
- **Roster screen**: the START menu gains a "Roster" icon while Character
  Mode is on. It lists your character's Pokemon, one row per evolution
  family, with the highlighted Pokemon's icon beside the list; A or B
  closes it. With Character Mode off the START menu is unchanged.
- **HMs**: any Pokemon in your party can use a field move (Cut, Fly,
  Surf, Strength, Rock Smash, Waterfall, Dive, Rock Climb, and Flash)
  once you have that HM in your bag and the badge it needs. You don't
  have to teach it, and the Pokemon doesn't have to be able to learn
  it, so no character gets stuck for lack of a Surf user. Only while
  Character Mode is on.
- Answering "No" at the prompt (or cancelling the number entry) leaves
  the game completely vanilla. The choice is made once per save file.

## How to apply

1. Obtain a Pokemon FireRed (USA) ROM and apply Skeli's official
   Pokemon Unbound v2.1.1.1 patch to it, producing
   `Pokemon Unbound (v2.1.1.1).gba` (sha1
   `b4776b82a4c7915d0fadeaa27e013523f99dfd94`).
2. Apply `unbound-character-mode.bps` to that ROM with Flips
   (https://github.com/Alcaro/Flips), or any BPS patcher.
3. The result should have sha1 `ddb790933a7e51011c8280dce1f3232d7a636440`.

## Known limitations

- The starter scene's dialogue/preview sprite still shows the original
  species; the Pokemon you actually receive (and its "received!" text)
  is your character's starter.
- Your overworld sprite follows your character while walking and running
  (Red, Leaf, Ethan and Lyra use Unbound's own costumes; characters with no
  overworld art, e.g. Brendan and May, keep the normal player). On a bike,
  surfing, fishing or underwater you look like the normal Unbound player.
  Most characters run with their walk cycle.
  The trainer card and battle back-sprite stay the normal Unbound player art.
- 36 of the 193 selectable characters have no portrait staged
  yet; picking one shows the confirmation with no art beside it.
- If your character's roster makes a required trade species uncatchable,
  that side quest reward may be unreachable — pick accordingly.

## Credits

- Pokemon Unbound by Skeli789 and team.
- Complete FireRed Upgrade (CFRU) engine by Skeli789 et al.
- Character rosters compiled from Bulbapedia.
- Character Mode port: see the project repository.

### Character portrait art

This patch injects trainer front-pic art from several fan projects. Credit is a
condition of use for these, so it travels with the patch:

- **Pokemon Ash Gray** by **metapod23** — anime-cast portraits.
- **Emerald Rogue** (Pokabbie) — the largest set. It ships no per-artist
  mapping, so its whole ~42-name "Additional Sprites" credits roll travels with
  any subset of the art; see CREDITS.md in the project repository.
- **Team Aqua's Asset Repo** — free to use and edit **with credit to the
  original creator** of each sprite.
- **pokemonHnS**, **pokeemerald-platinum**, **Pokesho (ポケしょ)**, **LouLilie**.

Full per-set terms and per-sprite provenance: CREDITS.md, shipped alongside.

This is a fan-made, non-profit patch. Never distributed as a ROM.
