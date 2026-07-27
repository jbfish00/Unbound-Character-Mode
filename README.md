# Character Mode — Pokémon Unbound v2.1.1.1

An opt-in game mode for [Pokémon Unbound](https://www.pokecommunity.com/threads/pok%C3%A9mon-unbound-completed.382178/)
(by Skeli789): at the start of a new game you pick one of **193 iconic Pokémon
characters** — protagonists, rivals, gym leaders, Elite Four, champions,
villains, and anime cast, Generations 1–8 — and play the whole game restricted
to that character's canon roster (Bulbapedia-documented teams, expanded to full
evolution families).

The character table holds 208 records; 15 are hidden from the select screen
because fewer than six of their Pokémon evolve fully in this game's dex, which
would make for a bare playthrough. Character ids are save data, so the hidden
ones keep their slots and the remaining numbers are unchanged — the numbered
list in `dist/CHARACTERS.md` simply skips them.

This is a binary ROM-hacking port of the "Character Mode" feature originally
built in source for Pokémon ROWE. Unbound has no public source, so the mode is
injected directly into the compiled ROM (via the CFRU engine's free space) and
distributed **as a patch only — never as a ROM**.

## What it does

- **New-game prompt** — right after Unbound's difficulty questionnaire, an extra
  question offers Character Mode. Enter your character's **number** (see
  [Character numbers](#character-numbers) below, or
  [`dist/CHARACTERS.md`](dist/CHARACTERS.md)), confirm, and it's locked in for
  that save. Answering "No" leaves the game completely vanilla.
- **Portrait at selection** — the character's 64x64 mugshot is drawn next to the
  "Play as {NAME}?" confirmation, so you see who you are picking before you commit.
- **Starter** replaced by your character's own signature starter.
- **Catching** — off-roster wild Pokémon can't be caught (the ball is dodged,
  like the game's no-catch zones).
- **Gifts** — off-roster scripted gifts are routed to your PC instead of your
  party, so nothing is ever lost and no event is blocked.
- **In-game trades** — every Borrius trade still completes; an off-roster
  incoming Pokémon is sent to your PC.
- **Wild encounters** — ~10% of wild encounters are replaced by a non-legendary
  member of your character's roster, level-matched to the area (all four
  random-table sites: grass/cave, surf, rock smash, every fishing tier).
- **Legendary encounters** — an independent ~1% roll offers a legendary from
  your character's roster, level-matched the same way. Filtered by the Pokédex
  so each is offered until caught; a roster that is *entirely* legendary keeps
  them repeatable, so those characters always have something to catch. 93 of
  the 208 characters have at least one legendary. Full spec:
  [`../game_plans/legendary_encounters.md`](../game_plans/legendary_encounters.md);
  per-character pools in [`ENCOUNTERS.md`](ENCOUNTERS.md).

## Installing

See [`dist/README.md`](dist/README.md) for the player-facing instructions.
In short: obtain a Pokémon FireRed (USA) ROM, apply Skeli's official Unbound
v2.1.1.1 patch, then apply [`dist/unbound-character-mode.bps`](dist/) with
[Flips](https://github.com/Alcaro/Flips) or any BPS patcher.

## Status

Feature-complete and packaged: enforcement (catch/gift/trade), organic new-game
opt-in, save persistence, and the character-select portrait are all injected and
live-tested. The remaining sprite work is art coverage, not mechanism: 144 of the
193 selectable characters have a portrait staged, the other 49 show the
confirmation on its own.

## Known limitations

- The starter scene's dialogue and preview sprite still show the original
  species; the Pokémon you actually receive (and its "received!" text) is your
  character's starter.
- The portrait appears **only on the character-select confirmation**. Your
  overworld sprite, trainer card and battle back-sprite are the normal Unbound
  player art — deliberately, so the patch touches none of the game's own art
  tables and no real opponent's sprite is ever swapped.
- 49 of the 193 selectable characters have no portrait staged yet; picking one
  shows the confirmation with no art beside it.
- If a character's roster can't catch a species required for a trade side quest,
  that reward may be unreachable — pick accordingly.

## Character numbers

Enter this number at the Character Mode prompt during a new game.
The same list, with roster sizes, ships in the patch as
[`dist/CHARACTERS.md`](dist/CHARACTERS.md).

Numbers are not contiguous: 15 of the 208 records are hidden because
fewer than six of their Pokémon fully evolve in this game's dex, and
the select screen re-asks on those numbers. The gaps are deliberate --
character ids are save data, so the hidden records keep their slots and
nothing is renumbered.

### Generation 1

| # | Character | Role | Starter Pokemon |
|---|---|---|---|
| **1** | Red | Protagonist | Pikachu |
| **2** | Leaf | Protagonist | Eevee |
| **3** | Blue | Champion | Pidgey |
| **4** | Lance | Champion | Dratini |
| **5** | Lorelei | Elite Four | Lapras |
| **6** | Bruno | Elite Four | Machop |
| **7** | Agatha | Elite Four | Gastly |
| **8** | Koga | Elite Four | Koffing |
| **9** | Brock | Gym Leader | Onix |
| **10** | Misty | Gym Leader | Staryu |
| **11** | Lt. Surge | Gym Leader | Pikachu |
| **12** | Erika | Gym Leader | Oddish |
| **13** | Sabrina | Gym Leader | Abra |
| **14** | Blaine | Gym Leader | Growlithe |
| **15** | Giovanni | Villain | Rhyhorn |
| **16** | Ash | Anime | Pikachu |
| **17** | Gary | Anime | Squirtle |
| **18** | Ritchie | Anime | Pikachu |
| **20** | Jessie | Anime | Ekans |
| **21** | James | Anime | Koffing |
| **157** | Oak | Professor | Bulbasaur |

### Generation 2

| # | Character | Role | Starter Pokemon |
|---|---|---|---|
| **22** | Ethan | Protagonist | Cyndaquil |
| **23** | Kris | Protagonist | Totodile |
| **24** | Lyra | Protagonist | Chikorita |
| **25** | Will | Elite Four | Natu |
| **26** | Karen | Elite Four | Eevee |
| **27** | Janine | Gym Leader | Spinarak |
| **28** | Falkner | Gym Leader | Hoothoot |
| **29** | Bugsy | Gym Leader | Scyther |
| **30** | Whitney | Gym Leader | Miltank |
| **31** | Morty | Gym Leader | Gastly |
| **32** | Chuck | Gym Leader | Poliwag |
| **33** | Jasmine | Gym Leader | Onix |
| **34** | Pryce | Gym Leader | Swinub |
| **35** | Clair | Gym Leader | Horsea |
| **36** | Silver | Rival | Totodile |
| **37** | Archer | Villain | Houndour |
| **38** | Ariana | Villain | Ekans |
| **158** | Elm | Professor | Chikorita |

### Generation 3

| # | Character | Role | Starter Pokemon |
|---|---|---|---|
| **39** | Brendan | Protagonist | Treecko |
| **40** | May | Protagonist | Torchic |
| **41** | Steven | Champion | Beldum |
| **42** | Wallace | Champion | Feebas |
| **43** | Sidney | Elite Four | Absol |
| **44** | Phoebe | Elite Four | Duskull |
| **45** | Glacia | Elite Four | Spheal |
| **46** | Drake | Elite Four | Bagon |
| **47** | Roxanne | Gym Leader | Nosepass |
| **48** | Brawly | Gym Leader | Makuhita |
| **49** | Wattson | Gym Leader | Electrike |
| **50** | Flannery | Gym Leader | Torkoal |
| **51** | Norman | Gym Leader | Slakoth |
| **52** | Winona | Gym Leader | Swablu |
| **53** | Tate | Gym Leader | Solrock |
| **54** | Liza | Gym Leader | Lunatone |
| **55** | Juan | Gym Leader | Horsea |
| **56** | Wally | Rival | Ralts |
| **57** | Maxie | Villain | Numel |
| **58** | Archie | Villain | Carvanha |
| **159** | Birch | Professor | Magikarp |
| **170** | Anabel | Frontier Brain | Abra |
| **171** | Brandon | Frontier Brain | Nincada |
| **172** | Greta | Frontier Brain | Gastly |
| **173** | Lucy | Frontier Brain | Abra |
| **174** | Noland | Frontier Brain | Bulbasaur |
| **175** | Spenser | Frontier Brain | Bulbasaur |
| **176** | Tucker | Frontier Brain | Charmander |

### Generation 4

| # | Character | Role | Starter Pokemon |
|---|---|---|---|
| **60** | Lucas | Protagonist | Turtwig |
| **61** | Dawn | Protagonist | Piplup |
| **62** | Cynthia | Champion | Gible |
| **63** | Aaron | Elite Four | Skorupi |
| **64** | Bertha | Elite Four | Hippopotas |
| **65** | Flint | Elite Four | Chimchar |
| **66** | Lucian | Elite Four | Bronzor |
| **67** | Roark | Gym Leader | Cranidos |
| **68** | Gardenia | Gym Leader | Budew |
| **69** | Maylene | Gym Leader | Riolu |
| **70** | Crasher Wake | Gym Leader | Buizel |
| **71** | Fantina | Gym Leader | Misdreavus |
| **72** | Byron | Gym Leader | Shieldon |
| **73** | Candice | Gym Leader | Snorunt |
| **74** | Volkner | Gym Leader | Shinx |
| **75** | Barry | Rival | Piplup |
| **76** | Cyrus | Villain | Sneasel |
| **77** | Mars | Villain | Glameow |
| **78** | Jupiter | Villain | Stunky |
| **79** | Saturn | Villain | Croagunk |
| **80** | Paul | Anime | Elekid |
| **81** | Zoey | Anime | Glameow |
| **82** | Nando | Anime | Budew |
| **160** | Rowan | Professor | Turtwig |
| **177** | Dahlia | Frontier Brain | Togepi |
| **178** | Darach | Frontier Brain | Houndour |
| **179** | Palmer | Frontier Brain | Rhyhorn |
| **205** | Thorton | Frontier Brain | Magnemite |
| **206** | Tobias | Anime | Latios |

### Generation 5

| # | Character | Role | Starter Pokemon |
|---|---|---|---|
| **83** | Alder | Champion | Larvesta |
| **84** | Iris | Champion | Axew |
| **85** | Shauntal | Elite Four | Litwick |
| **86** | Marshal | Elite Four | Timburr |
| **87** | Grimsley | Elite Four | Pawniard |
| **88** | Caitlin | Elite Four | Gothita |
| **89** | Cilan | Gym Leader | Pansage |
| **90** | Chili | Gym Leader | Pansear |
| **91** | Cress | Gym Leader | Panpour |
| **92** | Lenora | Gym Leader | Patrat |
| **93** | Burgh | Gym Leader | Sewaddle |
| **94** | Elesa | Gym Leader | Blitzle |
| **95** | Clay | Gym Leader | Drilbur |
| **96** | Skyla | Gym Leader | Ducklett |
| **97** | Brycen | Gym Leader | Cubchoo |
| **98** | Drayden | Gym Leader | Axew |
| **99** | Cheren | Gym Leader | Lillipup |
| **100** | Roxie | Gym Leader | Venipede |
| **101** | Marlon | Gym Leader | Frillish |
| **102** | Bianca | Rival | Tepig |
| **103** | Hugh | Rival | Trapinch |
| **104** | N | Rival | Zorua |
| **105** | Ghetsis | Villain | Deino |
| **106** | Colress | Villain | Klink |
| **107** | Trip | Anime | Snivy |
| **161** | Juniper | Professor | Snivy |
| **193** | Ingo | Frontier Brain | Abra |

### Generation 6

| # | Character | Role | Starter Pokemon |
|---|---|---|---|
| **108** | Diantha | Champion | Ralts |
| **109** | Malva | Elite Four | Fletchling |
| **110** | Siebold | Elite Four | Clauncher |
| **111** | Wikstrom | Elite Four | Honedge |
| **115** | Korrina | Gym Leader | Riolu |
| **116** | Ramos | Gym Leader | Skiddo |
| **117** | Clemont | Gym Leader | Helioptile |
| **118** | Valerie | Gym Leader | Eevee |
| **121** | Shauna | Rival | Chespin |
| **122** | Lysandre | Villain | Magikarp |
| **123** | Alain | Anime | Charmander |
| **124** | Sawyer | Anime | Treecko |
| **162** | Sycamore | Professor | Bulbasaur |

### Generation 7

| # | Character | Role | Starter Pokemon |
|---|---|---|---|
| **125** | Kukui | Champion | Litten |
| **126** | Hau | Champion | Pichu |
| **127** | Molayne | Elite Four | Diglett |
| **128** | Kahili | Elite Four | Pikipek |
| **129** | Acerola | Elite Four | Sandygast |
| **130** | Olivia | Elite Four | Rockruff |
| **131** | Gladion | Rival | Type:　Null |
| **132** | Guzma | Villain | Wimpod |
| **133** | Plumeria | Villain | Salandit |
| **134** | Lusamine | Villain | Stufful |
| **135** | Lillie (anime) | Anime | Vulpix |
| **136** | Kiawe (anime) | Anime | Turtonator |
| **137** | Lana (anime) | Anime | Popplio |
| **138** | Mallow (anime) | Anime | Bounsweet |
| **164** | Samson Oak | Professor | Rattata |

### Generation 8

| # | Character | Role | Starter Pokemon |
|---|---|---|---|
| **140** | Leon | Champion | Charmander |
| **141** | Milo | Gym Leader | Gossifleur |
| **142** | Nessa | Gym Leader | Chewtle |
| **143** | Kabu | Gym Leader | Sizzlipede |
| **144** | Bea | Gym Leader | Machop |
| **145** | Allister | Gym Leader | Gastly |
| **149** | Piers | Gym Leader | Zigzagoon |
| **150** | Raihan | Gym Leader | Duraludon |
| **151** | Hop | Rival | Wooloo |
| **152** | Bede | Rival | Hatenna |
| **153** | Marnie | Rival | Morpeko |
| **154** | Rose | Villain | Cufant |
| **155** | Goh | Anime | Scorbunny |
| **156** | Chloe | Anime | Eevee |
| **168** | Cerise | Professor | Bulbasaur |
| **169** | Volo | Villain | Growlithe |
| **180** | Adaman | Rival | Eevee |
| **181** | Akari | Protagonist | Pichu |
| **182** | Beni | Villain | Magnemite |
| **183** | Brassius | Anime | Oddish |
| **184** | Calem | Anime | Charmander |
| **185** | Cogita | Other | Enamorus |
| **186** | Elio | Anime | Eevee |
| **187** | Gloria | Anime | Grookey |
| **188** | Hala | Anime | Mankey |
| **189** | Hapu | Anime | Diglett |
| **190** | Hassel | Anime | Dratini |
| **191** | Hilbert | Anime | Eevee |
| **192** | Hilda | Anime | Eevee |
| **194** | Irida | Rival | Eevee |
| **195** | Kamado | Villain | Geodude |
| **196** | Larry | Anime | Tauros |
| **197** | Nate | Anime | Growlithe |
| **198** | Nemona | Anime | Tauros |
| **199** | Penny | Anime | Eevee |
| **200** | Rei | Protagonist | Cyndaquil |
| **201** | Rika | Anime | Diglett |
| **202** | Rosa | Anime | Delibird |
| **203** | Selene | Anime | Scyther |
| **204** | Serena | Anime | Eevee |
| **207** | Victor | Anime | Grookey |
| **208** | Zisu | Galaxy | Ponyta |

## Credits

Pokémon Unbound by Skeli789 and team. Complete FireRed Upgrade (CFRU) engine by
Skeli789 et al. Character rosters compiled from Bulbapedia. This is a fan-made,
non-profit patch.
