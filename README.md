# Character Mode — Pokémon Unbound v2.1.1.1

An opt-in game mode for [Pokémon Unbound](https://www.pokecommunity.com/threads/pok%C3%A9mon-unbound-completed.382178/)
(by Skeli789): at the start of a new game you pick one of **156 iconic Pokémon
characters** — protagonists, rivals, gym leaders, Elite Four, champions,
villains, and anime cast, Generations 1–8 — and play the whole game restricted
to that character's canon roster (Bulbapedia-documented teams, expanded to full
evolution families).

This is a binary ROM-hacking port of the "Character Mode" feature originally
built in source for Pokémon ROWE. Unbound has no public source, so the mode is
injected directly into the compiled ROM (via the CFRU engine's free space) and
distributed **as a patch only — never as a ROM**.

## What it does

- **New-game prompt** — right after Unbound's difficulty questionnaire, an extra
  question offers Character Mode. Enter your character's **number** (see
  [`dist/CHARACTERS.md`](dist/CHARACTERS.md)), confirm, and it's locked in for
  that save. Answering "No" leaves the game completely vanilla.
- **Starter** replaced by your character's own signature starter.
- **Catching** — off-roster wild Pokémon can't be caught (the ball is dodged,
  like the game's no-catch zones).
- **Gifts** — off-roster scripted gifts are routed to your PC instead of your
  party, so nothing is ever lost and no event is blocked.
- **In-game trades** — every Borrius trade still completes; an off-roster
  incoming Pokémon is sent to your PC.

## Installing

See [`dist/README.md`](dist/README.md) for the player-facing instructions.
In short: obtain a Pokémon FireRed (USA) ROM, apply Skeli's official Unbound
v2.1.1.1 patch, then apply [`dist/unbound-character-mode.bps`](dist/) with
[Flips](https://github.com/Alcaro/Flips) or any BPS patcher.

## Status

Feature-complete and packaged: enforcement (catch/gift/trade), organic new-game
opt-in, and save persistence are all injected and live-tested. The only
remaining item is optional character sprites (Phase 3) — the mode ships without
them (the player keeps the normal Unbound sprite).

## Known limitations

- The starter scene's dialogue and preview sprite still show the original
  species; the Pokémon you actually receive (and its "received!" text) is your
  character's starter.
- No custom character sprites yet.
- If a character's roster can't catch a species required for a trade side quest,
  that reward may be unreachable — pick accordingly.

## Credits

Pokémon Unbound by Skeli789 and team. Complete FireRed Upgrade (CFRU) engine by
Skeli789 et al. Character rosters compiled from Bulbapedia. This is a fan-made,
non-profit patch.
