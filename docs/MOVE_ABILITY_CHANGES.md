# Pokémon Unbound: move, ability and stat changes

> **Generated 2026-11-26** from the repo manifests by `make_change_docs.py`. Sections 1-3 are in the shipped release; section 4 (Planned) is **not in any release**.
>
> Status: 15 cards pushed (8dbfdeb, build 584287cf).

The change sets here apply with Character Mode on or off (they change the game's move data). Source manifest: `Unbound-Character-Mode/tools/character_mode/move_changes.json`.

## 1. Move values

Every move the hack changed is raised to the best value any generation gave it (accuracy, PP, power, effect chance, priority, type). **394 moves changed**: 50 power, 343 pp, 22 accuracy, 39 effect %, 7 priority, 2 type edits. Cells read old → new.

| Move | Power | PP | Accuracy | Effect % | Priority | Type |
|---|---|---|---|---|---|---|
| Comet Punch | 18 → 30 |  |  |  |  |  |
| Fire Punch |  | 15 → 16 |  | 10 → 30 |  |  |
| Ice Punch |  | 15 → 16 |  | 10 → 30 |  |  |
| Thunder Punch |  | 15 → 16 |  | 10 → 30 |  |  |
| Guillotine |  | 5 → 8 |  |  |  |  |
| Swords Dance |  | 20 → 30 |  |  |  |  |
| Whirlwind |  |  |  |  | -6 → 0 |  |
| Fly |  | 15 → 16 |  |  |  |  |
| Mega Kick |  | 5 → 8 |  |  |  |  |
| Jump Kick |  | 10 → 25 |  |  |  |  |
| Horn Drill |  | 5 → 8 |  |  |  |  |
| Tackle | 40 → 50 |  |  |  |  |  |
| Body Slam |  | 15 → 16 |  |  |  |  |
| Thrash |  | 10 → 20 |  |  |  |  |
| Double-Edge |  | 15 → 16 |  |  |  |  |
| Poison Sting | 15 → 30 |  |  | 30 → 50 |  |  |
| Pin Missile |  |  | 95 → 100 |  |  |  |
| Roar |  |  |  |  | -6 → 0 |  |
| Sing |  | 15 → 16 |  |  |  |  |
| Acid |  |  |  | 10 → 33 |  |  |
| Ember |  |  |  | 10 → 30 |  |  |
| Flamethrower |  | 15 → 16 |  | 10 → 20 |  |  |
| Hydro Pump |  | 5 → 8 | 80 → 85 |  |  |  |
| Surf |  | 15 → 16 |  |  |  |  |
| Ice Beam |  | 10 → 12 |  | 10 → 20 |  |  |
| Blizzard |  | 5 → 8 | 70 → 90 | 10 → 30 |  |  |
| Bubble Beam |  |  |  | 10 → 33 |  |  |
| Aurora Beam |  |  |  | 10 → 33 |  |  |
| Hyper Beam |  | 5 → 8 |  |  |  |  |
| Submission |  | 20 → 25 |  |  |  |  |
| Counter |  |  |  |  | -5 → -1 |  |
| Absorb | 25 → 40 |  |  |  |  |  |
| Mega Drain | 40 → 75 |  |  |  |  |  |
| Leech Seed |  | 10 → 12 |  |  |  |  |
| Growth |  | 20 → 40 |  |  |  | Normal → Grass |
| Solar Beam | 120 → 200 | 10 → 12 |  |  |  |  |
| Poison Powder |  |  | 75 → 80 |  |  |  |
| Stun Spore |  |  | 75 → 80 |  |  |  |
| Sleep Powder |  | 15 → 20 | 75 → 80 |  |  |  |
| Petal Dance |  | 10 → 20 |  |  |  |  |
| Fire Spin |  | 15 → 16 |  |  |  |  |
| Thunder Shock |  |  |  | 10 → 30 |  |  |
| Thunderbolt |  | 15 → 16 |  | 10 → 20 |  |  |
| Thunder Wave |  |  | 90 → 100 |  |  |  |
| Thunder |  | 10 → 12 | 70 → 75 |  |  |  |
| Earthquake |  | 10 → 12 |  |  |  |  |
| Fissure |  | 5 → 8 |  |  |  |  |
| Dig | 80 → 100 | 10 → 12 |  |  |  |  |
| Toxic |  | 10 → 12 |  |  |  |  |
| Psychic |  | 10 → 12 |  | 10 → 33 |  |  |
| Hypnosis |  |  | 60 → 70 |  |  |  |
| Teleport |  |  |  |  | -6 → 0 |  |
| Night Shade |  | 15 → 16 |  |  |  |  |
| Double Team |  | 15 → 16 |  |  |  |  |
| Recover |  | 10 → 20 |  |  |  |  |
| Minimize |  | 10 → 20 |  |  |  |  |
| Confuse Ray |  | 10 → 12 |  |  |  |  |
| Barrier |  | 20 → 30 |  |  |  |  |
| Self-Destruct |  | 5 → 8 |  |  |  |  |
| Sludge |  |  |  | 30 → 40 |  |  |
| Fire Blast |  | 5 → 8 |  | 10 → 30 |  |  |
| Waterfall |  | 15 → 16 |  |  |  |  |
| Skull Bash | 130 → 150 | 10 → 15 |  |  |  |  |
| Constrict |  |  |  | 10 → 33 |  |  |
| High Jump Kick |  | 10 → 20 |  |  |  |  |
| Leech Life | 20 → 80 |  |  |  |  |  |
| Sky Attack | 140 → 200 | 5 → 8 |  |  |  |  |
| Transform |  | 10 → 12 |  |  |  |  |
| Bubble |  |  |  | 10 → 33 |  |  |
| Acid Armor |  | 20 → 40 |  |  |  |  |
| Crabhammer |  | 10 → 12 | 90 → 95 |  |  |  |
| Explosion |  | 5 → 8 |  |  |  |  |
| Bonemerang | 50 → 55 |  |  |  |  |  |
| Rock Slide |  | 10 → 12 |  |  |  |  |
| Tri Attack |  | 10 → 12 |  | 20 → 30 |  |  |
| Super Fang |  | 10 → 12 |  |  |  |  |
| Slash | 70 → 80 |  |  |  |  |  |
| Substitute |  | 10 → 12 |  |  |  |  |
| Struggle |  | 1 → 10 |  |  |  |  |
| Nightmare |  |  | 100 → 101 |  |  |  |
| Flame Wheel |  |  |  | 10 → 30 |  |  |
| Snore |  | 15 → 16 |  |  |  |  |
| Curse |  | 10 → 12 |  |  |  |  |
| Flail |  | 15 → 16 |  |  |  |  |
| Reversal |  | 15 → 16 |  |  |  |  |
| Spite |  | 10 → 12 |  |  |  |  |
| Powder Snow |  |  |  | 10 → 30 |  |  |
| Scary Face |  | 10 → 12 |  |  |  |  |
| Sweet Kiss |  | 10 → 12 |  |  |  |  |
| Belly Drum |  | 10 → 12 |  |  |  |  |
| Sludge Bomb |  | 10 → 12 |  |  |  |  |
| Mud-Slap | 20 → 30 | 10 → 20 |  |  |  |  |
| Octazooka |  | 10 → 15 |  |  |  |  |
| Zap Cannon |  | 5 → 8 |  |  |  |  |
| Destiny Bond |  | 5 → 8 |  |  |  |  |
| Perish Song |  | 5 → 8 |  |  |  |  |
| Icy Wind | 55 → 60 | 15 → 20 |  |  |  |  |
| Detect |  | 5 → 8 |  |  |  |  |
| Bone Rush | 25 → 30 | 10 → 12 |  |  |  |  |
| Lock-On |  | 5 → 8 |  |  |  |  |
| Outrage |  | 10 → 15 |  |  |  |  |
| Giga Drain |  | 10 → 12 |  |  |  |  |
| Endure |  | 10 → 12 |  |  |  |  |
| Rollout | 30 → 60 |  |  |  |  |  |
| Swagger |  | 15 → 16 | 85 → 90 |  |  |  |
| Mean Look |  | 5 → 8 |  |  |  |  |
| Attract |  | 15 → 16 |  |  |  |  |
| Sleep Talk |  | 10 → 12 |  |  |  |  |
| Heal Bell |  | 5 → 8 |  |  |  |  |
| Dynamic Punch |  | 5 → 8 |  |  |  |  |
| Megahorn |  | 10 → 12 |  |  |  |  |
| Encore |  | 5 → 8 |  |  |  |  |
| Iron Tail |  | 15 → 16 |  |  |  |  |
| Morning Sun |  | 5 → 8 |  |  |  |  |
| Synthesis |  | 5 → 8 |  |  |  |  |
| Moonlight |  | 5 → 8 |  |  |  |  |
| Cross Chop |  | 5 → 8 |  |  |  |  |
| Twister |  | 20 → 25 |  |  |  |  |
| Rain Dance |  | 5 → 8 |  |  |  |  |
| Sunny Day |  | 5 → 8 |  |  |  |  |
| Crunch |  | 15 → 16 |  |  |  |  |
| Mirror Coat |  |  |  |  | -5 → -1 |  |
| Psych Up |  | 10 → 12 |  |  |  |  |
| Extreme Speed |  | 5 → 8 |  |  |  |  |
| Ancient Power |  | 5 → 15 |  | 10 → 20 |  |  |
| Shadow Ball |  | 15 → 16 |  |  |  |  |
| Future Sight |  | 10 → 15 |  |  |  |  |
| Rock Smash |  | 15 → 20 |  |  |  |  |
| Whirlpool |  | 15 → 16 |  |  |  |  |
| Beat Up |  | 10 → 12 |  |  |  |  |
| Fake Out |  | 10 → 12 |  |  |  |  |
| Uproar |  | 10 → 12 |  |  |  |  |
| Spit Up |  | 10 → 12 |  |  |  |  |
| Swallow |  | 10 → 12 |  |  |  |  |
| Heat Wave |  | 10 → 12 |  |  |  |  |
| Torment |  | 15 → 16 |  |  |  |  |
| Flatter |  | 15 → 16 |  |  |  |  |
| Will-O-Wisp |  | 15 → 16 |  |  |  |  |
| Memento |  | 10 → 12 | 100 → 101 |  |  |  |
| Facade | 70 → 75 |  |  |  |  |  |
| Follow Me |  |  |  |  | 2 → 3 |  |
| Trick |  | 10 → 12 |  |  |  |  |
| Role Play |  | 10 → 12 |  |  |  |  |
| Superpower |  | 5 → 8 |  |  |  |  |
| Recycle |  | 10 → 12 |  |  |  |  |
| Brick Break |  | 15 → 16 |  |  |  |  |
| Yawn |  | 10 → 12 |  |  |  |  |
| Endeavor |  | 5 → 8 |  |  |  |  |
| Eruption |  | 5 → 8 |  |  |  |  |
| Skill Swap |  | 10 → 12 |  |  |  |  |
| Imprison |  | 10 → 12 |  |  |  |  |
| Dive |  | 10 → 12 |  |  |  |  |
| Luster Purge | 70 → 95 |  |  |  |  |  |
| Mist Ball | 70 → 95 |  |  |  |  |  |
| Feather Dance |  | 15 → 16 |  |  |  |  |
| Blaze Kick |  | 10 → 12 |  |  |  |  |
| Ice Ball | 30 → 40 |  |  |  |  |  |
| Hyper Voice |  | 10 → 12 |  |  |  |  |
| Poison Fang |  | 15 → 16 |  |  |  |  |
| Crush Claw |  | 10 → 12 |  |  |  |  |
| Blast Burn |  | 5 → 8 |  |  |  |  |
| Hydro Cannon |  | 5 → 8 |  |  |  |  |
| Meteor Mash |  | 10 → 12 |  |  |  |  |
| Astonish |  | 15 → 25 |  |  |  |  |
| Weather Ball |  | 10 → 12 |  |  |  |  |
| Overheat |  | 5 → 8 |  |  |  |  |
| Rock Tomb |  | 15 → 16 |  |  |  |  |
| Silver Wind |  | 5 → 15 |  | 10 → 20 |  |  |
| Water Spout |  | 5 → 8 |  |  |  |  |
| Extrasensory |  | 20 → 30 |  |  |  |  |
| Sand Tomb |  | 15 → 16 |  |  |  |  |
| Sheer Cold |  | 5 → 8 |  |  |  |  |
| Muddy Water |  | 10 → 12 |  |  |  |  |
| Iron Defense |  | 15 → 20 |  |  |  |  |
| Block |  | 5 → 8 |  |  |  |  |
| Dragon Claw |  | 15 → 16 |  |  |  |  |
| Frenzy Plant |  | 5 → 8 |  |  |  |  |
| Bounce |  | 5 → 8 |  |  |  |  |
| Mud Shot |  | 15 → 16 |  |  |  |  |
| Covet |  | 25 → 40 |  |  |  |  |
| Volt Tackle |  | 15 → 16 |  | 10 → 30 |  |  |
| Leaf Blade |  | 15 → 16 |  |  |  |  |
| Rock Blast |  | 10 → 12 |  |  |  |  |
| Water Pulse |  |  | 100 → 101 |  |  |  |
| Air Slash |  | 15 → 20 |  |  |  |  |
| Aqua Tail |  | 10 → 12 |  |  |  |  |
| Avalanche |  | 10 → 12 |  |  |  |  |
| Brave Bird |  | 15 → 16 |  |  |  |  |
| Bug Buzz |  | 10 → 12 |  | 10 → 20 |  |  |
| Charge Beam |  | 10 → 15 |  |  |  |  |
| Close Combat |  | 5 → 8 |  |  |  |  |
| Cross Poison |  |  |  | 10 → 20 |  |  |
| Dark Pulse |  | 15 → 16 | 100 → 101 |  |  |  |
| Discharge |  | 15 → 16 |  |  |  |  |
| Draco Meteor |  | 5 → 8 |  |  |  |  |
| Dragon Pulse |  | 10 → 12 | 100 → 101 |  |  |  |
| Drain Punch |  | 10 → 12 |  |  |  |  |
| Earth Power |  | 10 → 12 |  | 10 → 20 |  |  |
| Energy Ball |  | 10 → 12 |  | 10 → 20 |  |  |
| Focus Blast |  | 5 → 8 |  |  |  |  |
| Giga Impact |  | 5 → 8 |  |  |  |  |
| Gunk Shot |  | 5 → 8 |  |  |  |  |
| Hammer Arm |  | 10 → 12 |  |  |  |  |
| Head Smash |  | 5 → 8 |  |  |  |  |
| Iron Head |  | 15 → 16 |  |  |  |  |
| Lava Plume |  | 15 → 16 |  |  |  |  |
| Magnet Bomb | 60 → 95 |  |  |  |  |  |
| Mud Bomb |  | 10 → 15 |  |  |  |  |
| Night Slash |  | 15 → 20 |  |  |  |  |
| Ominous Wind |  | 5 → 15 |  | 10 → 20 |  |  |
| Power Whip |  | 10 → 12 |  |  |  |  |
| Rock Wrecker |  | 5 → 8 |  |  |  |  |
| Seed Bomb |  | 15 → 16 |  |  |  |  |
| Shadow Claw |  | 15 → 16 |  |  |  |  |
| X-Scissor |  | 15 → 16 |  |  |  |  |
| Zen Headbutt |  | 15 → 16 |  |  |  |  |
| Switcheroo |  | 10 → 12 |  |  |  |  |
| Drill Run |  | 10 → 12 |  |  |  |  |
| Electroweb |  | 15 → 16 |  |  |  |  |
| Frost Breath | 60 → 65 | 10 → 12 |  |  |  |  |
| Horn Leech |  | 10 → 12 |  |  |  |  |
| Hurricane |  | 10 → 12 | 70 → 75 |  |  |  |
| Icicle Crash |  | 10 → 12 |  |  |  |  |
| Leaf Tornado |  |  |  | 30 → 50 |  |  |
| Snarl | 55 → 60 | 15 → 16 | 95 → 100 |  |  |  |
| Storm Throw | 60 → 65 | 10 → 12 |  |  |  |  |
| Venoshock |  | 10 → 15 |  |  |  |  |
| Wild Charge |  | 15 → 16 |  |  |  |  |
| Fiery Dance |  | 10 → 12 |  |  |  |  |
| Clear Smog |  | 15 → 16 |  |  |  |  |
| Leaf Storm |  | 5 → 8 |  |  |  |  |
| Stone Edge |  | 5 → 8 |  |  |  |  |
| Payback |  | 10 → 12 |  |  |  |  |
| Fire Fang |  | 15 → 16 |  | 10 → 20 |  |  |
| Ice Fang |  | 15 → 16 |  | 10 → 20 |  |  |
| Thunder Fang |  | 15 → 16 |  | 10 → 20 |  |  |
| Flare Blitz |  | 15 → 16 |  | 10 → 20 |  |  |
| Inferno |  | 5 → 8 |  |  |  |  |
| Hex |  | 10 → 15 |  |  |  |  |
| Dual Chop | 40 → 45 |  |  |  |  |  |
| Double Hit | 35 → 50 | 10 → 12 |  |  |  |  |
| Cotton Guard |  | 10 → 12 |  |  |  |  |
| Acrobatics |  | 15 → 16 |  |  |  |  |
| Dragon Tail |  | 10 → 12 |  |  |  |  |
| Circle Throw |  | 10 → 12 |  |  |  |  |
| Wood Hammer |  | 15 → 16 |  |  |  |  |
| Heal Pulse |  | 10 → 12 |  |  |  |  |
| Flash Cannon |  | 10 → 12 |  | 10 → 20 |  |  |
| Shell Smash |  | 15 → 16 |  |  |  |  |
| Rage Powder |  |  |  |  | 2 → 3 |  |
| Razor Shell |  | 10 → 12 |  |  |  |  |
| Sucker Punch | 70 → 80 | 5 → 8 |  |  |  |  |
| Scald |  | 15 → 16 |  |  |  |  |
| Play Rough |  | 10 → 12 |  | 10 → 20 |  |  |
| Moonblast |  | 15 → 16 |  |  |  |  |
| Draining Kiss |  | 10 → 15 |  |  |  |  |
| Dazzling Gleam |  | 10 → 12 |  |  |  |  |
| Healing Wish |  | 10 → 12 |  |  |  |  |
| Tailwind |  | 15 → 30 |  |  |  |  |
| Boomburst |  | 10 → 12 |  |  |  |  |
| Worry Seed |  | 10 → 12 |  |  |  |  |
| Gastro Acid |  | 10 → 12 |  |  |  |  |
| Shift Gear |  | 10 → 12 |  |  |  |  |
| Stored Power |  | 10 → 12 |  |  |  |  |
| Assurance |  | 10 → 12 |  |  |  |  |
| Dragon Rush |  | 10 → 12 |  |  |  |  |
| Dark Void |  |  | 80 → 90 |  |  |  |
| Feint |  | 10 → 12 |  |  |  |  |
| Phantom Force |  | 10 → 12 |  |  |  |  |
| Petal Blizzard |  | 15 → 16 |  |  |  |  |
| Final Gambit |  | 5 → 8 |  |  |  |  |
| Psyshock |  | 10 → 12 |  |  |  |  |
| Round |  | 15 → 16 |  |  |  |  |
| Tail Slap |  | 10 → 12 |  |  |  |  |
| Gear Grind | 50 → 60 |  | 85 → 90 |  |  |  |
| Smack Down |  | 15 → 16 |  |  |  |  |
| Gyro Ball |  | 5 → 8 |  |  |  |  |
| Defog |  | 15 → 16 |  |  |  |  |
| Guard Swap |  | 10 → 12 |  |  |  |  |
| Metal Burst |  | 10 → 12 |  |  |  |  |
| Power Swap |  | 10 → 12 |  |  |  |  |
| Power Trick |  | 10 → 12 |  |  |  |  |
| Sludge Wave |  | 10 → 12 |  |  |  |  |
| Heavy Slam |  | 10 → 12 |  |  |  |  |
| Synchronoise |  | 10 → 15 |  |  |  |  |
| Electro Ball |  | 10 → 12 |  |  |  |  |
| Foul Play |  | 15 → 16 |  |  |  |  |
| Entrainment |  | 15 → 16 |  |  |  |  |
| Night Daze | 85 → 90 | 10 → 12 |  |  |  |  |
| Sacred Sword |  | 15 → 20 |  |  |  |  |
| Heat Crash |  | 10 → 12 |  |  |  |  |
| Mystical Fire |  | 10 → 12 |  |  |  |  |
| Eerie Impulse |  | 15 → 16 |  |  |  |  |
| Anchor Shot | 80 → 90 |  |  |  |  |  |
| Beak Blast | 100 → 120 |  |  |  |  |  |
| Burn Up |  | 5 → 8 |  |  |  |  |
| Clanging Scales |  | 5 → 8 |  |  |  |  |
| Darkest Lariat |  | 10 → 12 |  |  |  |  |
| Dragon Hammer | 90 → 100 |  |  |  |  |  |
| Fire Lash | 80 → 90 | 15 → 16 |  |  |  |  |
| First Impression | 90 → 100 | 10 → 12 |  |  |  |  |
| High Horsepower |  | 10 → 12 |  |  |  |  |
| Ice Hammer |  | 10 → 12 |  |  |  |  |
| Liquidation |  | 10 → 12 |  |  |  |  |
| Lunge |  | 15 → 16 |  |  |  |  |
| Pollen Puff |  | 15 → 16 |  |  |  |  |
| Power Trip |  | 10 → 12 |  |  |  |  |
| Psychic Fangs |  | 10 → 12 |  |  |  |  |
| Revelation Dance | 90 → 100 |  |  |  |  |  |
| Smart Strike |  | 10 → 12 |  |  |  |  |
| Solar Blade |  | 10 → 12 |  |  |  |  |
| Sparkling Aria |  | 10 → 12 |  |  |  |  |
| Speed Swap |  | 10 → 12 |  |  |  |  |
| Spirit Shackle | 80 → 90 | 10 → 12 |  |  |  |  |
| Stomping Tantrum |  | 10 → 12 |  |  |  |  |
| Throat Chop |  | 15 → 16 |  |  |  |  |
| Trop Kick | 70 → 85 | 15 → 16 |  |  |  |  |
| Zing Zap |  | 10 → 12 |  |  |  |  |
| Electric Terrain |  | 10 → 12 |  |  |  |  |
| Grassy Terrain |  | 10 → 12 |  |  |  |  |
| Misty Terrain |  | 10 → 12 |  |  |  |  |
| Psychic Terrain |  | 10 → 12 |  |  |  |  |
| Trick Room |  | 5 → 8 |  |  |  |  |
| Magic Room |  | 10 → 12 |  |  |  |  |
| Wonder Room |  | 10 → 12 |  |  |  |  |
| Quick Guard |  | 15 → 16 |  |  |  |  |
| Wide Guard |  | 10 → 12 |  |  |  |  |
| Belch |  | 10 → 12 |  |  |  |  |
| Fling |  | 10 → 12 |  |  |  |  |
| Flying Press |  | 10 → 12 |  |  |  |  |
| Gravity |  | 5 → 8 |  |  |  |  |
| Guard Split |  | 10 → 12 |  |  |  |  |
| Magnet Rise |  | 10 → 12 |  |  |  |  |
| Power Split |  | 10 → 12 |  |  |  |  |
| Reflect Type |  | 15 → 16 |  |  |  |  |
| Simple Beam |  | 15 → 16 |  |  |  |  |
| Fairy Lock |  | 10 → 12 |  |  |  |  |
| Light of Ruin |  | 5 → 8 |  |  |  |  |
| After You |  | 15 → 16 |  |  |  |  |
| Instruct |  | 15 → 16 |  |  |  |  |
| Quash |  | 15 → 16 |  |  |  |  |
| Last Resort |  | 5 → 8 |  |  |  |  |
| Snipe Shot | 80 → 85 | 15 → 16 |  |  |  |  |
| Jaw Lock |  | 10 → 12 |  |  |  |  |
| Stuff Cheeks |  | 10 → 12 |  |  |  |  |
| No Retreat |  | 5 → 8 |  |  |  |  |
| Dragon Darts |  | 10 → 12 |  |  |  |  |
| Teatime |  | 10 → 12 |  |  |  |  |
| Octolock |  | 15 → 16 |  |  |  |  |
| Court Change |  | 10 → 12 |  |  |  |  |
| Clangorous Soul |  | 5 → 8 |  |  |  |  |
| Body Press |  | 10 → 12 |  |  |  |  |
| Decorate |  | 15 → 16 |  |  |  |  |
| Drum Beating |  | 10 → 12 |  |  |  |  |
| Snap Trap |  | 15 → 16 |  |  |  | Grass → Steel |
| Pyro Ball |  | 5 → 8 |  |  |  |  |
| Aura Wheel |  | 10 → 12 |  |  |  |  |
| Breaking Swipe |  | 15 → 16 |  |  |  |  |
| Overdrive |  | 10 → 12 |  |  |  |  |
| Apple Acid | 80 → 90 | 10 → 12 |  |  |  |  |
| Grav Apple | 80 → 90 | 10 → 12 |  |  |  |  |
| Spirit Break |  | 15 → 16 |  |  |  |  |
| Life Dew |  | 10 → 12 |  |  |  |  |
| Meteor Assault | 150 → 170 | 5 → 8 |  |  |  |  |
| Steel Beam |  | 5 → 8 |  |  |  |  |
| Steel Roller |  | 5 → 8 |  |  |  |  |
| Meteor Beam |  | 10 → 12 |  |  |  |  |
| Shell Side Arm |  | 10 → 12 |  | 10 → 20 |  |  |
| Misty Explosion |  | 5 → 8 |  |  |  |  |
| Terrain Pulse |  | 10 → 12 |  |  |  |  |
| Skitter Smack |  | 10 → 12 |  |  |  |  |
| Burning Jealousy |  | 5 → 8 |  |  |  |  |
| Lash Out |  | 5 → 8 |  |  |  |  |
| Poltergeist |  | 5 → 8 |  |  |  |  |
| Coaching |  | 10 → 12 |  |  |  |  |
| Triple Axel | 20 → 40 | 10 → 12 |  |  |  |  |
| Dual Wingbeat | 40 → 45 | 10 → 12 |  |  |  |  |
| Scorching Sands |  | 10 → 12 |  |  |  |  |
| Eerie Spell |  | 5 → 8 |  |  |  |  |
| Dire Claw | 60 → 80 | 15 → 16 |  |  |  |  |
| Psyshield Bash | 70 → 90 | 10 → 12 |  |  |  |  |
| Stone Axe |  | 15 → 16 |  |  |  |  |
| Raging Fury |  | 10 → 12 | 85 → 100 |  |  |  |
| Wave Crash | 75 → 120 | 10 → 12 |  |  |  |  |
| Mountain Gale | 110 → 120 | 5 → 12 |  |  |  |  |
| Headlong Rush |  | 5 → 8 |  |  |  |  |
| Barb Barrage |  |  |  | 30 → 50 |  |  |
| Esper Wing | 75 → 80 |  | 90 → 100 |  |  |  |
| Bitter Malice | 60 → 75 |  |  | 30 → 100 |  |  |
| Triple Arrows | 60 → 90 |  |  |  |  |  |
| Ceaseless Edge |  | 15 → 16 |  |  |  |  |
| Bleakwind Storm |  | 5 → 10 |  |  |  |  |
| Wildbolt Storm |  | 5 → 10 |  |  |  |  |
| Sandsear Storm |  | 5 → 10 |  |  |  |  |

## 2. Critical hits and move properties

**High critical-hit ratio (+2 stages):** 23 moves: Karate Chop, Razor Wind, Razor Leaf, Sky Attack, Crabhammer, Slash, Aeroblast, Cross Chop, Blaze Kick, Air Cutter, Poison Tail, Leaf Blade, Cross Poison, Night Slash, Psycho Cut, Shadow Claw, Drill Run, Stone Edge, Spacial Rend, Attack Order, Snipe Shot, Esper Wing, TripleArrows.

**Properties:**

- **Magic Coat / Magic Bounce no longer reflect it** (16): Defog, Disable, Embargo, Encore, Foresight, Heal Block, Miracle Eye, Odor Sleuth, Roar, Spikes, Spite, Stealth Rock, Taunt, Torment, Toxic Spikes, Whirlwind
- **Mirror Move / Copycat can no longer copy it** (3): Feint, Taunt, Teeter Dance
- **Protect / Detect no longer block it** (1): Spider Web
- **Snatch no longer steals it** (9): Aqua Ring, Healing Wish, Imprison, Lucky Chant, Lunar Dance, Magnet Rise, Power Trick, Recycle, Wish
- **now hits all adjacent foes (doubles)** (1): Surf

## 3. Behaviour changes (moves and abilities)

**committed behaviour_cards.json at HEAD**

| Card | Kind | What it does |
|---|---|---|
| Double-Edge (Gen I) | move | Recoil. Gen I-II: 1/4 of damage dealt (Gen I: none when it breaks a Substitute). Gen III onward: 1/3. Lowest recoil is Gen I-II. (Power 100 in Gen I-III, 120 after, is a separate row.) |
| Astonish (Gen III) | move | Gen III only: double damage against a target that used Minimize. Removed from Gen IV. |
| Extrasensory (Gen III) | move | Gen III only: double damage against a target that used Minimize. Removed from Gen IV. |
| Needle Arm (Gen III) | move | Gen III only: double damage against a target that used Minimize. Removed from Gen IV. |
| Phantom Force (Gen VI) | move | Gen VI only: double damage and never misses against a target that used Minimize. Removed from Gen VII. |
| Substitute (Gen II-V) | move | Gen I: a Substitute blocks sleep, paralysis and Leech Seed less reliably, and a 255+ damage hit always breaks it. Gen II-V: blocks all status and stat drops from others. Gen VI onward: sound moves and Infiltrator go through it, a drawback for the user. |
| Protect / Detect / Endure (Gen IV) | move | Chance when used repeatedly. Gen II: halves each time. Gen III: halves for three uses, then erratic. Gen IV-V: halves each time, floor 1/8. Gen VI onward: drops to 1/3 each time. Gen II and IV-V keep the best odds. Chance when used repeatedly. Gen II: halves each time. Gen III: halves for three uses, then erratic. Gen IV-V: halves each time, floor 1/8. Gen VI onward: drops to 1/3 each time. Gen IV-V keeps the best odds. |
| Parental Bond (Gen VI) | ability | Second hit does 50% damage in Gen VI, 25% from Gen VII. |
| High Jump Kick / Jump Kick (Gen I) | move | Crash damage on a miss. Gen I: 1 HP. Gen II: 1/8 of the damage it would have done. Gen III-IV: half the damage it would have done. Gen V onward: half the user's max HP. Smallest crash is Gen I. |
| Intimidate (Gen VII) | ability | Gen III-VII: lowers foes' Attack by 1. Gen VIII onward: Inner Focus, Oblivious, Own Tempo and Scrappy block it (worse for the holder). Strongest for the holder: Gen VII. |
| Heal Bell / Soundproof (Gen V) | mixed | Soundproof Pokemon are not cured in Gen III-IV and VI-VII; cured in Gen V. Gen VIII onward: Soundproof party members are skipped but the user is always cured. Gen II and V cure everyone. Whether the holder is cured by an ally's Heal Bell: no in Gen III-IV and VI-VII, yes in Gen V, and Gen VIII onward cured only if it used the move itself. Gen V helps the holder most. |
| Leaf Guard (Gen IV) | ability | Gen IV: in sun blocks status, but the holder can still use Rest. Gen V onward: Rest fails in sun. Gen IV is better for the holder. |
| Parting Shot (Gen VI) | move | Gen VII onward: the user doesn't switch out if neither stat could be lowered. Gen VI always switches. |
| Destiny Bond (Gen III-VI) | move | Gen VII onward: fails if used twice in a row. Earlier: can be used every turn. |
| Disguise (Gen VII) | ability | Gen VIII onward: breaking the disguise also costs Mimikyu 1/8 HP. Gen VII doesn't. |

**Not done yet in this engine:** Brick Break (hook), Disable / Encore / Taunt, Moody, Swallow, Explosion, Anger Point, Magic Guard, trapping abilities, Rapid Spin +1 Speed, Teleport, Healing Wish / Lunar Dance, Howl, Illuminate, Thrash, Moonlight / Morning Sun / Synthesis, Flail / Reversal, Psywave, Sticky Hold, Intrepid Sword / Dauntless Shield (binary arm). (CFRU.md bottom)

## 4. Planned (NOT in any release)

Everything below is the Pokémon Legacy balance pass (`game_plans/legacy_balance_2026-11-26/`): decisions are closed and the manifests are built, but it is not applied in this repo; nothing here ships until the apply step runs.

### Planned: Pokémon Legacy move values (155 moves)

`from` is the value in the release plus the best-version tier above; Legacy values below the hack's are not applied.

| Move | Power | PP | Accuracy | Effect % | Priority | Type |
|---|---|---|---|---|---|---|
| Double Slap | 15 → 20 | 10 → 35 | 85 → 100 |  |  | Normal → Fairy |
| Comet Punch |  | 15 → 25 | 85 → 100 |  |  |  |
| Mega Punch | 80 → 90 |  | 85 → 95 |  |  |  |
| Pay Day | 40 → 60 |  |  |  |  |  |
| Razor Wind |  | 10 → 15 |  |  |  | Normal → Flying |
| Cut | 50 → 60 |  | 95 → 100 |  |  | Normal → Bug |
| Fly |  |  | 95 → 100 |  |  |  |
| Bind | 15 → 35 |  | 85 → 100 |  |  |  |
| Slam |  | 20 → 25 | 75 → 100 |  |  |  |
| Mega Kick |  | 8 → 10 | 75 → 85 |  |  |  |
| Rolling Kick | 60 → 70 | 15 → 25 | 85 → 100 |  |  |  |
| Fury Attack | 15 → 20 | 20 → 35 | 85 → 100 |  |  |  |
| Wrap | 15 → 30 |  | 90 → 100 |  |  |  |
| Take Down | 90 → 95 |  | 85 → 100 |  |  |  |
| Poison Sting | 30 → 35 |  |  |  |  |  |
| Twineedle | 25 → 40 |  |  |  |  |  |
| Pin Missile |  | 20 → 30 |  |  |  |  |
| Supersonic |  |  | 55 → 70 |  |  |  |
| Sonic Boom |  |  | 90 → 100 |  |  |  |
| Acid | 40 → 65 |  |  |  |  |  |
| Hydro Pump |  | 8 → 10 |  |  |  |  |
| Ice Beam |  | 12 → 15 |  |  |  |  |
| Submission | 80 → 90 |  | 80 → 100 |  |  |  |
| Mega Drain |  | 15 → 25 |  |  |  |  |
| PoisonPowder |  |  | 80 → 90 |  |  |  |
| Dragon Rage |  | 10 → 20 |  |  |  |  |
| Fire Spin |  |  | 85 → 100 |  |  |  |
| Thunder |  |  | 75 → 85 |  |  |  |
| Rock Throw |  | 15 → 25 | 90 → 95 |  |  |  |
| Dig |  | 12 → 20 |  |  |  |  |
| Psychic |  | 12 → 15 |  |  |  |  |
| Rage | 20 → 60 |  |  |  |  |  |
| Egg Bomb | 100 → 110 | 10 → 15 | 75 → 100 |  |  | Normal → Grass |
| Lick | 30 → 40 |  |  |  |  |  |
| Smog | 30 → 40 |  |  |  |  |  |
| Sludge | 65 → 90 |  |  |  |  |  |
| Bone Club |  | 20 → 25 | 85 → 100 |  |  |  |
| Clamp | 35 → 50 | 15 → 20 | 85 → 100 |  |  |  |
| Spike Cannon | 20 → 30 |  |  |  |  | Normal → Steel |
| Constrict | 10 → 40 |  |  |  |  |  |
| Kinesis |  |  | 80 → 100 |  |  |  |
| Barrage | 15 → 20 |  | 85 → 100 |  |  |  |
| Leech Life |  | 15 → 25 |  |  |  |  |
| Sky Attack |  | 8 → 10 |  |  |  |  |
| Transform |  |  |  |  | 0 → 1 |  |
| Dizzy Punch |  | 10 → 20 |  |  |  |  |
| Crabhammer | 100 → 110 |  | 95 → 100 |  |  |  |
| Fury Swipes | 18 → 20 | 15 → 20 | 80 → 100 |  |  |  |
| Bonemerang |  | 10 → 20 |  |  |  |  |
| Rock Slide | 75 → 80 | 12 → 15 | 90 → 95 |  |  |  |
| Tri Attack | 80 → 85 | 12 → 15 |  |  |  |  |
| Triple Kick | 10 → 30 | 10 → 15 | 90 → 100 |  |  |  |
| Flame Wheel | 60 → 65 |  |  |  |  |  |
| Snore |  | 16 → 20 |  |  |  |  |
| Aeroblast |  | 5 → 10 |  |  |  |  |
| Mach Punch | 40 → 50 |  |  |  |  |  |
| Feint Attack | 60 → 70 |  |  |  |  |  |
| Sludge Bomb | 90 → 95 | 12 → 15 |  |  |  |  |
| Octazooka | 65 → 70 |  | 85 → 100 |  |  |  |
| Zap Cannon |  | 8 → 10 | 50 → 70 |  |  |  |
| Icy Wind | 60 → 65 |  | 95 → 100 |  |  |  |
| Bone Rush |  | 12 → 20 | 90 → 100 |  |  |  |
| Giga Drain |  | 12 → 15 |  |  |  |  |
| Steel Wing | 70 → 75 |  | 90 → 100 |  |  |  |
| Present |  | 15 → 25 | 90 → 100 |  |  |  |
| Sacred Fire |  | 5 → 10 |  |  |  |  |
| DynamicPunch |  | 8 → 10 | 50 → 70 |  |  |  |
| DragonBreath | 60 → 70 |  |  |  |  |  |
| Iron Tail |  |  | 75 → 90 |  |  |  |
| Metal Claw | 50 → 70 |  | 95 → 100 | 10 → 20 |  |  |
| Vital Throw |  | 10 → 20 |  |  |  |  |
| Cross Chop |  | 8 → 10 | 80 → 90 |  |  |  |
| Twister | 40 → 70 |  |  |  |  |  |
| Rain Dance |  | 8 → 10 |  |  |  |  |
| Sunny Day |  | 8 → 10 |  |  |  |  |
| ExtremeSpeed |  | 8 → 15 |  |  |  |  |
| Rock Smash | 40 → 60 |  |  |  |  |  |
| Whirlpool |  |  | 85 → 100 |  |  |  |
| Uproar |  | 12 → 25 |  |  |  |  |
| Heat Wave |  |  | 90 → 100 |  |  |  |
| SmellingSalt | 70 → 75 | 10 → 15 |  |  |  |  |
| Dive |  | 12 → 15 |  |  |  |  |
| Arm Thrust | 15 → 18 |  |  |  |  |  |
| Luster Purge |  | 5 → 15 |  |  |  |  |
| Mist Ball |  | 5 → 15 |  |  |  |  |
| Blaze Kick |  | 12 → 15 | 90 → 100 | 10 → 20 |  |  |
| Needle Arm | 60 → 80 | 15 → 20 |  |  |  |  |
| Hyper Voice | 90 → 100 |  |  |  |  |  |
| Poison Fang | 50 → 60 |  |  |  |  |  |
| Crush Claw | 75 → 80 | 12 → 15 |  |  |  |  |
| Meteor Mash |  |  | 90 → 95 |  |  |  |
| Astonish | 30 → 50 |  |  |  |  |  |
| Weather Ball |  | 12 → 30 |  |  |  |  |
| Air Cutter | 60 → 65 |  |  |  |  |  |
| Rock Tomb |  | 16 → 25 |  |  |  |  |
| Grasswhistle |  |  | 55 → 75 |  |  |  |
| Signal Beam | 75 → 85 |  |  |  |  |  |
| Shadow Punch | 60 → 80 |  |  |  |  |  |
| Sky Uppercut | 85 → 90 |  | 90 → 95 |  |  |  |
| Sand Tomb |  |  | 85 → 100 |  |  |  |
| Muddy Water |  | 12 → 15 | 85 → 95 | 30 → 50 |  |  |
| Dragon Claw | 80 → 90 |  |  |  |  |  |
| Bounce |  | 8 → 15 | 85 → 90 |  |  |  |
| Mud Shot |  | 16 → 20 |  |  |  |  |
| Poison Tail | 50 → 80 |  |  |  |  |  |
| Covet |  |  |  |  |  | Normal → Fairy |
| Rock Blast |  | 12 → 15 |  |  |  |  |
| Doom Desire | 140 → 150 |  |  |  |  |  |
| Aqua Tail |  | 12 → 15 | 90 → 95 |  |  |  |
| Cross Poison | 70 → 80 |  |  |  |  |  |
| Dragon Pulse |  | 12 → 15 |  |  |  |  |
| Energy Ball |  | 12 → 15 |  |  |  |  |
| Focus Blast |  | 8 → 10 |  |  |  |  |
| Gunk Shot |  | 8 → 10 | 80 → 85 |  |  |  |
| Hammer Arm |  |  | 90 → 100 |  |  |  |
| Head Smash |  |  | 80 → 85 |  |  |  |
| Mud Bomb | 65 → 70 |  | 85 → 90 |  |  |  |
| Night Slash | 70 → 75 |  |  |  |  |  |
| Psycho Cut | 70 → 75 |  |  |  |  |  |
| Rock Climb | 90 → 100 |  | 85 → 90 |  |  |  |
| X-Scissor | 80 → 85 |  |  |  |  |  |
| Zen Headbutt | 80 → 85 |  | 90 → 95 |  |  |  |
| Drill Run |  | 12 → 15 | 95 → 100 |  |  |  |
| Frost Breath |  | 12 → 15 | 90 → 100 |  |  |  |
| Heart Stamp |  |  |  | 30 → 40 |  |  |
| Horn Leech |  | 12 → 15 |  |  |  |  |
| Icicle Crash |  |  | 90 → 95 |  |  |  |
| Steamroller | 65 → 80 |  |  |  |  |  |
| Storm Throw |  | 12 → 15 |  |  |  |  |
| Stone Edge |  | 8 → 10 | 80 → 85 |  |  |  |
| Payback | 50 → 60 |  |  |  |  |  |
| Inferno |  |  | 50 → 60 |  |  |  |
| Double Hit |  | 12 → 20 |  |  |  |  |
| Mirror Shot | 65 → 70 | 10 → 15 | 85 → 90 |  |  |  |
| Flash Cannon | 80 → 90 | 12 → 15 |  |  |  |  |
| Razor Shell | 75 → 80 | 12 → 15 | 95 → 100 |  |  |  |
| Play Rough |  | 12 → 15 | 90 → 100 |  |  |  |
| Dragon Rush |  |  | 75 → 80 |  |  |  |
| PhantomForce |  | 12 → 15 |  |  |  |  |
| Retaliate |  | 5 → 10 |  |  |  |  |
| Psyshock |  | 12 → 15 |  |  |  |  |
| Round | 60 → 65 | 16 → 20 |  |  |  |  |
| Tail Slap |  | 12 → 15 | 85 → 100 |  |  |  |
| Gear Grind |  |  | 90 → 95 |  |  |  |
| Smack Down |  | 16 → 20 |  |  |  |  |
| Gyro Ball |  | 8 → 10 |  |  |  |  |
| Attack Order | 90 → 100 |  |  |  |  |  |
| Night Daze |  | 12 → 15 | 95 → 100 |  |  |  |
| Head Charge | 120 → 130 |  |  |  |  |  |
| Relic Song | 75 → 85 |  |  |  |  |  |
| Fusion Flare |  | 5 → 10 |  |  |  |  |
| Fusion Bolt |  | 5 → 10 |  |  |  |  |
| Infestation | 20 → 30 |  |  |  |  |  |
| Flying Press |  | 12 → 15 |  |  |  |  |
| Sky Drop | 60 → 70 |  |  |  |  |  |

**Planned move effects (18; candidates, the apply step checks each hack's current effect first):**

- Vise Grip: stat:Attack-1 20% (emerald L.)
- Razor Wind: one turn + 100% trapping (bind-style), keep power/crit/targeting (user note)
- Razor Wind: status:Capture 100% (xy L.)
- Razor Wind: one-turn (emerald L.)
- Razor Wind: status:Trapped 100% (emerald L.)
- Razor Wind: one-turn (yellow L.)
- Slam: flinch 10% (yellow L.)
- Egg Bomb: category Special (Grass, X&Y L.) where the engine has the split
- Skull Bash: one-turn (yellow L.)
- Sky Attack: one turn (no charge), no retype, keep 200/90 and current flinch/crit (user note)
- Sky Attack: one-turn (emerald L.)
- Sky Attack: one-turn (crystal L.)
- Sky Attack: one-turn (yellow L.)
- Dizzy Punch: status:Confusion 10% (yellow L.)
- Rock Slide: flinch 10% (yellow L.)
- Crunch: defence drop matches Dark's category in this game (user note)
- Hyper Voice: status:Confusion 30% (emerald L.)
- Power Gem: stat:Special Defense-1 20% (xy L.)

**Skipped (2):** Night Shade (power 1 is a placeholder (fixed/variable damage); Legacy yellow power 60 not applied); Beat Up (power 1 is a placeholder (fixed/variable damage); Legacy crystal power 20 not applied)

### Planned: base stat changes (254 species)

Species Legacy changed get Legacy's per-stat delta on the hack's own line; a hack-customised line keeps the higher of each stat (user ruling 2026-11-26).

<details><summary>Show the stat table</summary>

| Species | Changes |
|---|---|
| Butterfree | HP 60 → 70, Atk 45 → 35, Def 50 → 60, SpD 80 → 90 |
| Beedrill | Atk 90 → 100, Spe 75 → 85 |
| Pidgeotto | SpA 50 → 55, SpD 50 → 55 |
| Pidgeot | SpA 70 → 80, SpD 70 → 80 |
| Raticate | Atk 81 → 86, Spe 97 → 102 |
| Fearow | Atk 90 → 95, Spe 100 → 105 |
| Ekans | HP 35 → 40, Atk 60 → 65, Spe 55 → 60 |
| Arbok | HP 60 → 65, Atk 95 → 105, Spe 80 → 90 |
| Sandslash | Spe 65 → 75 |
| Vulpix | HP 38 → 48, Def 40 → 45, Spe 65 → 75, SpA 50 → 61, SpD 65 → 70 |
| Ninetales | HP 73 → 78, Atk 76 → 71, Def 75 → 80, SpA 81 → 91 |
| Jigglypuff | Def 20 → 30, SpA 45 → 55, SpD 25 → 30 |
| Wigglytuff | Def 45 → 60, SpA 85 → 90, SpD 50 → 60 |
| Oddish | HP 45 → 50 |
| Gloom | HP 60 → 70, Def 70 → 75 |
| Vileplume | HP 75 → 90, Def 85 → 95 |
| Paras | HP 35 → 55, Def 55 → 60, SpD 55 → 60 |
| Parasect | HP 60 → 85, Atk 95 → 100, Def 80 → 90, SpD 80 → 90 |
| Venomoth | Atk 65 → 75, Spe 90 → 100, SpA 90 → 95 |
| Diglett | Atk 55 → 70 |
| Dugtrio | Atk 100 → 120 |
| Meowth | Atk 45 → 55 |
| Persian | Atk 70 → 85, Spe 115 → 120 |
| Mankey | HP 40 → 45, Spe 70 → 75 |
| Primeape | HP 65 → 70, Spe 95 → 100 |
| Poliwrath | Atk 95 → 105, SpA 70 → 60 |
| Victreebel | Atk 105 → 120, Spe 70 → 75, SpA 100 → 115, SpD 70 → 60 |
| Golem | SpD 65 → 75 |
| Ponyta | Spe 90 → 100 |
| Rapidash | Spe 105 → 115 |
| Farfetch’d | HP 52 → 67, Atk 90 → 105, Def 55 → 70, Spe 60 → 70, SpD 62 → 72 |
| Dodrio | Spe 110 → 120 |
| Seel | Atk 45 → 55 |
| Dewgong | Atk 70 → 80 |
| Grimer | HP 80 → 90, SpD 50 → 75 |
| Muk | HP 105 → 115 |
| Onix | HP 35 → 45, Atk 45 → 55 |
| Drowzee | HP 60 → 70, Spe 42 → 34 |
| Hypno | HP 85 → 100, Spe 67 → 59 |
| Kingler | Atk 130 → 140 |
| Electrode | Spe 150 → 160 |
| Exeggutor | Atk 95 → 85, SpD 75 → 95 |
| Marowak | HP 60 → 70 |
| Hitmonlee | Atk 120 → 125, Spe 87 → 97 |
| Hitmonchan | Atk 105 → 115, Def 79 → 84 |
| Lickitung | Atk 55 → 65, Def 75 → 80, SpD 75 → 80 |
| Weezing | HP 65 → 75 |
| Rhyhorn | HP 80 → 90, SpD 30 → 40 |
| Seaking | Atk 92 → 102, Spe 68 → 78 |
| Jynx | Spe 95 → 100, SpD 95 → 100 |
| Flareon | HP 65 → 95, SpA 95 → 65 |
| Omanyte | Atk 40 → 30, SpD 55 → 65 |
| Omastar | Atk 60 → 50, SpD 70 → 80 |
| Articuno | Atk 85 → 75, SpA 95 → 105 |
| Furret | Atk 76 → 86, Def 64 → 74 |
| Noctowl | HP 100 → 110, SpA 86 → 96 |
| Ledian | HP 55 → 75, Spe 85 → 95, SpA 55 → 60 |
| Ariados | HP 70 → 75, Atk 90 → 100, SpA 60 → 70, SpD 70 → 80 |
| Chinchou | SpA 56 → 66 |
| Lanturn | SpA 76 → 86 |
| Igglybuff | Def 15 → 20 |
| Togetic | HP 55 → 65 |
| Natu | Spe 70 → 75 |
| Xatu | Spe 95 → 105 |
| Bellossom | HP 75 → 90, SpD 100 → 110 |
| Sudowoodo | HP 70 → 80, SpD 65 → 85 |
| Politoed | SpA 90 → 100 |
| Aipom | Atk 70 → 75 |
| Sunflora | HP 75 → 85, SpA 105 → 135 |
| Wooper | SpA 25 → 35, SpD 25 → 35 |
| Quagsire | SpA 65 → 75, SpD 65 → 75 |
| Murkrow | Atk 85 → 90, Spe 91 → 96 |
| Girafarig | SpA 90 → 100 |
| Dunsparce | HP 100 → 110, SpA 65 → 70, SpD 65 → 70 |
| Granbull | HP 90 → 100, Atk 120 → 130 |
| Qwilfish | HP 65 → 75, Def 85 → 95, SpA 55 → 65, SpD 55 → 75 |
| Ursaring | Atk 130 → 140, Def 75 → 80, SpA 75 → 55, SpD 75 → 80 |
| Slugma | HP 40 → 50, Atk 40 → 70, Def 40 → 60, SpD 40 → 60 |
| Magcargo | HP 60 → 70, Atk 50 → 80, Def 120 → 130, SpA 90 → 100, SpD 80 → 90 |
| Corsola | HP 65 → 95, Atk 55 → 65, Def 95 → 105, SpA 65 → 75, SpD 95 → 105 |
| Remoraid | HP 35 → 45, Atk 65 → 60, SpA 65 → 70 |
| Octillery | HP 75 → 85, Atk 105 → 95, Spe 45 → 35, SpA 105 → 115 |
| Delibird | HP 45 → 60, Atk 55 → 75, Def 45 → 55, Spe 75 → 80, SpA 65 → 85, SpD 45 → 55 |
| Mantine | HP 85 → 105 |
| Stantler | Atk 95 → 105 |
| Hitmontop | Def 95 → 100, Spe 70 → 80 |
| Smoochum | Spe 65 → 70, SpD 65 → 70 |
| Treecko | Atk 45 → 50, SpD 55 → 50 |
| Grovyle | Atk 65 → 70, SpD 65 → 60 |
| Sceptile | Atk 85 → 100, SpA 105 → 110, SpD 85 → 70 |
| Blaziken | Spe 80 → 85 |
| Mightyena | HP 70 → 75, Atk 90 → 95, Def 70 → 75, Spe 70 → 80 |
| Linoone | Atk 70 → 80 |
| Beautifly | Atk 70 → 80, Spe 65 → 75 |
| Dustox | HP 60 → 75, Def 70 → 80, Spe 65 → 60, SpD 90 → 100 |
| Ludicolo | HP 80 → 90, SpA 90 → 100 |
| Shiftry | Atk 100 → 110, Spe 80 → 85, SpA 90 → 95 |
| Swellow | SpA 75 → 100 |
| Pelipper | HP 60 → 70, SpA 95 → 105 |
| Kirlia | HP 38 → 43, Atk 35 → 40, Def 35 → 40, SpA 65 → 75, SpD 55 → 65 |
| Masquerain | Spe 80 → 100, SpA 100 → 120 |
| Shedinja | SpA 30 → 75 |
| Loudred | SpA 71 → 76 |
| Exploud | HP 104 → 114, Def 63 → 73, SpA 91 → 101 |
| Makuhita | HP 72 → 82, Def 30 → 40, SpD 30 → 40 |
| Nosepass | HP 30 → 45, Atk 45 → 40, Def 135 → 125, SpA 45 → 70, SpD 90 → 105 |
| Skitty | Spe 50 → 60, SpA 35 → 50, SpD 35 → 40 |
| Delcatty | HP 70 → 75, Atk 65 → 70, Def 65 → 75, Spe 90 → 115, SpA 55 → 80, SpD 55 → 70 |
| Sableye | HP 50 → 70, Def 75 → 95, Spe 50 → 40, SpD 65 → 95 |
| Mawile | Atk 85 → 95, Def 85 → 95, SpD 55 → 65 |
| Plusle | Atk 50 → 70, Spe 95 → 105, SpA 85 → 95, SpD 75 → 65 |
| Minun | HP 60 → 70, Def 50 → 80, Spe 95 → 85, SpA 75 → 65, SpD 85 → 95 |
| Volbeat | HP 65 → 70, Atk 73 → 78, SpA 47 → 97, SpD 85 → 75 |
| Illumise | HP 65 → 80, Def 75 → 95, SpD 85 → 100 |
| Gulpin | HP 70 → 85 |
| Swalot | HP 100 → 115 |
| Carvanha | Spe 65 → 75 |
| Sharpedo | Spe 95 → 115 |
| Wailmer | Spe 60 → 55, SpA 70 → 85 |
| Wailord | Def 45 → 50, Spe 60 → 45, SpA 90 → 115, SpD 45 → 50 |
| Numel | HP 60 → 70 |
| Camerupt | HP 70 → 90, Atk 100 → 105, Spe 40 → 30, SpA 105 → 110 |
| Torkoal | SpA 85 → 95 |
| Spoink | Def 35 → 40, Spe 60 → 65 |
| Grumpig | HP 80 → 90, Atk 45 → 35, Def 65 → 70, Spe 80 → 85 |
| Vibrava | HP 50 → 60, Atk 70 → 80, Def 50 → 60, Spe 70 → 80, SpA 50 → 70, SpD 50 → 60 |
| Flygon | SpA 80 → 90 |
| Cacnea | HP 50 → 60, Atk 85 → 70, Def 40 → 55, Spe 35 → 25, SpD 40 → 45 |
| Cacturne | HP 70 → 100, Atk 115 → 80, Def 60 → 90, Spe 55 → 35, SpD 60 → 80 |
| Swablu | HP 45 → 60 |
| Altaria | HP 75 → 85 |
| Zangoose | HP 73 → 78, Atk 115 → 120 |
| Seviper | HP 73 → 93, Def 60 → 70, Spe 65 → 55, SpA 100 → 80, SpD 60 → 70 |
| Lunatone | HP 90 → 110, SpA 95 → 105 |
| Solrock | Atk 95 → 105, Spe 70 → 90 |
| Barboach | SpA 46 → 56 |
| Whiscash | SpA 76 → 91 |
| Corphish | HP 43 → 53, SpA 50 → 60 |
| Crawdaunt | HP 63 → 73, SpA 90 → 100 |
| Armaldo | SpA 70 → 60, SpD 80 → 90 |
| Castform | HP 70 → 75, Def 70 → 75, Spe 70 → 95, SpA 70 → 90, SpD 70 → 75 |
| Kecleon | HP 60 → 75, SpA 60 → 70 |
| Banette | HP 64 → 74, SpA 83 → 93 |
| Tropius | HP 99 → 120, Atk 68 → 63, SpA 72 → 91 |
| Chimecho | HP 75 → 85, Def 80 → 90, SpA 95 → 100, SpD 90 → 100 |
| Absol | Spe 75 → 95 |
| Snorunt | HP 50 → 60, Atk 50 → 60, Def 50 → 60, Spe 50 → 60, SpA 50 → 60, SpD 50 → 60 |
| Glalie | HP 80 → 85, Atk 80 → 85, Def 80 → 85, Spe 80 → 85, SpA 80 → 85, SpD 80 → 85 |
| Huntail | Atk 104 → 114, SpA 94 → 84 |
| Relicanth | Atk 90 → 110 |
| Luvdisc | HP 43 → 58, Def 55 → 75, Spe 97 → 102, SpA 40 → 70, SpD 65 → 85 |
| Torterra | HP 95 → 100, Atk 109 → 114, SpA 75 → 65 |
| Bibarel | HP 79 → 89, SpA 55 → 65 |
| Kricketune | Atk 85 → 45, Def 51 → 66, Spe 65 → 60, SpA 55 → 95, SpD 51 → 66 |
| Shinx | HP 45 → 50, Atk 65 → 70, SpA 40 → 30 |
| Luxio | HP 60 → 70, Atk 85 → 90, SpA 60 → 45 |
| Luxray | HP 80 → 90, Atk 120 → 130, SpA 95 → 75 |
| Rampardos | HP 97 → 107, Spe 58 → 63, SpA 65 → 60 |
| Bastiodon | HP 60 → 80, Spe 30 → 20 |
| Vespiquen | HP 70 → 80, Def 102 → 112, SpD 102 → 112 |
| Pachirisu | HP 60 → 70, Spe 95 → 110 |
| Cherubi | Atk 35 → 55 |
| Ambipom | Atk 100 → 105 |
| Drifloon | Atk 50 → 40, SpA 60 → 70 |
| Drifblim | Atk 80 → 60, SpA 90 → 110 |
| Lopunny | Atk 76 → 81, Spe 105 → 130, SpA 54 → 44 |
| Mismagius | Spe 105 → 110, SpA 105 → 110, SpD 105 → 110 |
| Honchkrow | Spe 71 → 91 |
| Glameow | HP 49 → 59, SpA 42 → 32 |
| Purugly | HP 71 → 103, SpA 64 → 49 |
| Chingling | SpA 65 → 70 |
| Bonsly | SpD 45 → 55 |
| Chatot | Def 45 → 60, SpA 92 → 102, SpD 42 → 57 |
| Spiritomb | Atk 92 → 108, Spe 35 → 23, SpA 92 → 108 |
| Croagunk | HP 48 → 58, Atk 61 → 76, Spe 50 → 60, SpA 61 → 66 |
| Toxicroak | Atk 106 → 112, Spe 85 → 90, SpA 86 → 80 |
| Carnivine | HP 74 → 95, Atk 100 → 110, SpA 90 → 75 |
| Lumineon | Atk 69 → 59, Spe 91 → 106, SpA 69 → 74 |
| Mantyke | HP 45 → 55 |
| Snover | HP 60 → 70, Spe 40 → 30, SpA 62 → 72 |
| Abomasnow | HP 90 → 110, Spe 60 → 50, SpA 92 → 112, SpD 85 → 75 |
| Lickilicky | Atk 85 → 95, Spe 50 → 45 |
| Probopass | HP 60 → 70, Atk 55 → 45, Def 145 → 130, SpA 75 → 105, SpD 150 → 140 |
| Dusknoir | HP 45 → 65, Atk 100 → 110, Def 135 → 130, Spe 45 → 25, SpD 135 → 130 |
| Froslass | HP 70 → 75, Atk 80 → 85, Def 70 → 75, Spe 110 → 115, SpA 80 → 85, SpD 70 → 75 |
| Rotom | Def 77 → 87, Spe 91 → 101, SpA 95 → 105, SpD 77 → 87 |
| Phione | HP 80 → 85, Atk 80 → 85, Def 80 → 85, Spe 80 → 85, SpA 80 → 85, SpD 80 → 85 |
| Emboar | Def 65 → 70, SpA 100 → 90, SpD 65 → 70 |
| Dewott | Atk 75 → 86, SpA 83 → 72 |
| Samurott | Atk 100 → 116, SpA 108 → 92 |
| Watchog | HP 60 → 87, Atk 85 → 95, Def 69 → 74, Spe 77 → 60, SpA 60 → 45, SpD 69 → 74 |
| Pidove | Atk 55 → 41, SpA 36 → 55 |
| Tranquill | Atk 77 → 55, SpA 50 → 77 |
| Unfezant | Atk 115 → 75, SpA 65 → 115 |
| Blitzle | Spe 76 → 81 |
| Zebstrika | Spe 116 → 121 |
| Swoobat | HP 67 → 72, Atk 57 → 67, Def 55 → 65, Spe 114 → 119, SpA 77 → 82, SpD 55 → 65 |
| Audino | Atk 60 → 50, Def 86 → 91, SpA 60 → 70, SpD 86 → 91 |
| Leavanny | Atk 103 → 108, Spe 92 → 102, SpA 70 → 55 |
| Lilligant | HP 70 → 80, SpA 110 → 115 |
| Maractus | HP 75 → 85, Atk 86 → 110, Def 67 → 72, Spe 60 → 76, SpA 106 → 61, SpD 67 → 72 |
| Crustle | Atk 105 → 115, Spe 45 → 55, SpA 65 → 45, SpD 75 → 85 |
| Yamask | Def 85 → 95, SpA 55 → 60 |
| Cofagrigus | Def 145 → 155, SpA 95 → 100 |
| Carracosta | Spe 32 → 52, SpA 83 → 73 |
| Garbodor | Atk 95 → 105 |
| Minccino | Spe 75 → 80 |
| Cinccino | Spe 115 → 120 |
| Swanna | Spe 98 → 108 |
| Vanilluxe | Atk 95 → 70, SpA 110 → 135 |
| Frillish | HP 55 → 70, SpA 65 → 75 |
| Jellicent | SpA 85 → 95 |
| Galvantula | Spe 108 → 113 |
| Klink | SpA 45 → 55, SpD 60 → 50 |
| Klang | SpA 70 → 80, SpD 85 → 75 |
| Klinklang | SpA 70 → 80, SpD 85 → 75 |
| Tynamo | SpA 45 → 55 |
| Eelektrik | SpA 75 → 85 |
| Eelektross | SpA 105 → 115 |
| Elgyem | Atk 55 → 40, SpA 85 → 100 |
| Beheeyem | Atk 75 → 60, SpA 125 → 140 |
| Cubchoo | HP 55 → 65, Spe 40 → 50, SpA 60 → 40 |
| Beartic | HP 95 → 100, Atk 130 → 145, Spe 50 → 70, SpA 70 → 50 |
| Cryogonal | HP 80 → 90, Def 50 → 70 |
| Accelgor | Atk 70 → 60, SpA 100 → 110 |
| Golett | HP 59 → 79, Atk 74 → 94, Def 50 → 55, Spe 35 → 40, SpA 35 → 40, SpD 50 → 55 |
| Golurk | HP 89 → 109, Atk 124 → 134 |
| Heatmor | HP 85 → 95, Atk 97 → 77, Def 66 → 76, Spe 65 → 55, SpD 66 → 76 |
| Virizion | Spe 108 → 129, SpD 129 → 108 |
| Pyroar | Atk 68 → 78, SpA 109 → 119 |
| Skiddo | HP 66 → 76, Atk 65 → 70, Def 48 → 58, SpA 62 → 37 |
| Gogoat | Atk 100 → 105, Def 62 → 87, SpA 97 → 62, SpD 81 → 86 |
| Pangoro | HP 95 → 110, Spe 58 → 53, SpA 69 → 59 |
| Aromatisse | HP 101 → 106, Atk 72 → 70, Def 72 → 82, SpA 99 → 104 |
| Swirlix | Atk 48 → 59, Spe 49 → 44, SpA 59 → 53 |
| Slurpuff | Atk 80 → 85, SpA 85 → 80 |
| Inkay | HP 53 → 58, Atk 54 → 60, Def 53 → 58, Spe 45 → 50, SpD 46 → 51 |
| Malamar | Atk 92 → 100, Def 88 → 93, SpA 68 → 60, SpD 75 → 80 |
| Binacle | Atk 52 → 62, Def 67 → 77, SpD 56 → 61 |
| Barbaracle | Spe 68 → 78, SpA 54 → 44 |
| Skrelp | HP 50 → 55, SpA 60 → 70, SpD 60 → 75 |
| Dragalge | HP 65 → 76 |
| Clauncher | Def 62 → 67, SpA 58 → 73, SpD 63 → 68 |
| Amaura | HP 77 → 87, Atk 59 → 46, Def 50 → 58, Spe 46 → 26, SpA 67 → 77, SpD 63 → 68 |
| Aurorus | Atk 77 → 57, Def 72 → 92, Spe 58 → 33, SpA 99 → 114, SpD 92 → 102 |
| Dedenne | HP 67 → 82 |
| Sliggoo | Spe 60 → 55, SpA 83 → 88 |
| Goodra | Spe 80 → 70, SpA 110 → 120 |
| Phantump | SpD 60 → 80 |
| Trevenant | Atk 110 → 120, SpD 82 → 107 |
| Bergmite | Atk 69 → 74, Def 85 → 90, SpA 32 → 22, SpD 35 → 50 |
| Avalugg | SpA 44 → 34, SpD 46 → 76 |
| Noibat | HP 40 → 55, Atk 30 → 35, Def 35 → 50, Spe 55 → 75, SpA 45 → 65, SpD 40 → 50 |
| Noivern | Atk 70 → 65, Spe 123 → 128, SpA 97 → 102 |

</details>

Not built yet: 92 Mega / form stat rows.

### Planned: species ability changes (219 slots)

<details><summary>Show the ability table</summary>

| Species | Slot | Old → new |
|---|---|---|
| Caterpie | 2 | (none) → Run Away |
| Butterfree | 2 | (none) → Tinted Lens |
| Butterfree | 3 | Tinted Lens → Overcoat |
| Weedle | 2 | Shield Dust → Run Away |
| Pidgey | 2 | Tangled Feet → Early Bird |
| Pidgeotto | 2 | Tangled Feet → Early Bird |
| Pidgeot | 2 | Tangled Feet → No Guard |
| Spearow | 2 | Sniper → Rivalry |
| Fearow | 2 | Sniper → Defiant |
| Sandshrew | 1 | Sand Veil → Sand Rush |
| Sandshrew | 2 | (none) → Tough Claws |
| Sandshrew | 3 | Sand Rush → Sand Veil |
| Sandslash | 1 | Sand Veil → Sand Rush |
| Sandslash | 2 | (none) → Tough Claws |
| Sandslash | 3 | Sand Rush → Sand Veil |
| Vulpix | 2 | (none) → Drought |
| Vulpix | 3 | Drought → Solar Power |
| Ninetales | 2 | (none) → Drought |
| Ninetales | 3 | Drought → Solar Power |
| Jigglypuff | 2 | Competitive → Friend Guard |
| Wigglytuff | 2 | Competitive → Magic Bounce |
| Zubat | 2 | (none) → Infiltrator |
| Zubat | 3 | Infiltrator → Unnerve |
| Golbat | 2 | (none) → Infiltrator |
| Golbat | 3 | Infiltrator → Unnerve |
| Poliwrath | 2 | Damp → Iron Fist |
| Rapidash | 1 | Flame Body → Quick Feet |
| Farfetch’d | 3 | Defiant → Sniper |
| Seel | 2 | Ice Body → Swift Swim |
| Dewgong | 2 | Ice Body → Swift Swim |
| Drowzee | 3 | Forewarn → Frisk |
| Krabby | 2 | Shell Armor → Weak Armor |
| Krabby | 3 | Sheer Force → Tough Claws |
| Kingler | 2 | Shell Armor → Weak Armor |
| Kingler | 3 | Sheer Force → Tough Claws |
| Lickitung | 2 | Oblivious → Sticky Hold |
| Goldeen | 2 | Water Veil → Lightning Rod |
| Goldeen | 3 | Lightning Rod → Water Veil |
| Seaking | 2 | Water Veil → Lightning Rod |
| Seaking | 3 | Lightning Rod → Water Veil |
| Electabuzz | 2 | (none) → Vital Spirit |
| Magmar | 2 | (none) → Vital Spirit |
| Vaporeon | 2 | Water Absorb → Hydration |
| Vaporeon | 3 | Hydration → Storm Drain |
| Jolteon | 2 | Volt Absorb → Motor Drive |
| Flareon | 2 | Flash Fire → Guts |
| Flareon | 3 | Guts → Mold Breaker |
| Kabuto | 3 | Weak Armor → Sand Rush |
| Kabutops | 3 | Weak Armor → Sand Rush |
| Chikorita | 3 | Leaf Guard → Sweet Veil |
| Bayleef | 3 | Leaf Guard → Sweet Veil |
| Cyndaquil | 3 | Flash Fire → Unnerve |
| Quilava | 3 | Flash Fire → Unnerve |
| Sentret | 2 | Keen Eye → Limber |
| Furret | 2 | Keen Eye → Limber |
| Ledian | 1 | Swarm → Simple |
| Crobat | 2 | (none) → Infiltrator |
| Crobat | 3 | Infiltrator → Unnerve |
| Igglybuff | 2 | Competitive → Friend Guard |
| Igglybuff | 3 | Friend Guard → Competitive |
| Politoed | 2 | Damp → Drizzle |
| Politoed | 3 | Drizzle → Swift Swim |
| Espeon | 2 | Synchronize → Forewarn |
| Umbreon | 2 | Synchronize → Pressure |
| Girafarig | 2 | Sap Sipper → Scrappy |
| Pineco | 2 | (none) → Aftermath |
| Forretress | 2 | (none) → Aftermath |
| Granbull | 2 | Quick Feet → Strong Jaw |
| Qwilfish | 2 | Swift Swim → Intimidate |
| Qwilfish | 3 | Intimidate → Swift Swim |
| Corsola | 2 | Natural Cure → Regenerator |
| Corsola | 3 | Regenerator → Natural Cure |
| Remoraid | 3 | Moody → Sniper |
| Octillery | 3 | Moody → Sniper |
| Phanpy | 2 | (none) → Oblivious |
| Donphan | 2 | (none) → Battle Armor |
| Elekid | 2 | (none) → Vital Spirit |
| Magby | 2 | (none) → Vital Spirit |
| Raikou | 1 | Pressure → Volt Absorb |
| Raikou | 3 | Volt Absorb → Mold Breaker |
| Entei | 1 | Pressure → Flash Fire |
| Entei | 3 | Flash Fire → Mold Breaker |
| Suicune | 1 | Pressure → Water Absorb |
| Suicune | 3 | Water Absorb → Mold Breaker |
| Lugia | 1 | Pressure → Multiscale |
| Lugia | 2 | (none) → Multiscale |
| Lugia | 3 | Multiscale → Pressure |
| Ho-Oh | 1 | Pressure → Regenerator |
| Ho-Oh | 2 | (none) → Regenerator |
| Ho-Oh | 3 | Regenerator → Pressure |
| Sceptile | 3 | Unburden → Harvest |
| Shiftry | 3 | Pickpocket → Infiltrator |
| Wingull | 3 | Rain Dish → Hydration |
| Pelipper | 3 | Rain Dish → Drizzle |
| Whismur | 3 | Rattled → Anticipation |
| Loudred | 3 | Scrappy → Mold Breaker |
| Exploud | 3 | Scrappy → Mold Breaker |
| Carvanha | 2 | (none) → Anger Point |
| Sharpedo | 2 | (none) → Strong Jaw |
| Wailmer | 2 | Oblivious → Rain Dish |
| Wailord | 2 | Oblivious → Rain Dish |
| Camerupt | 1 | Magma Armor → Flame Body |
| Camerupt | 3 | Anger Point → Sheer Force |
| Torkoal | 3 | Shell Armor → Drought |
| Whiscash | 1 | Oblivious → Gluttony |
| Shuppet | 2 | Frisk → Prankster |
| Banette | 2 | Frisk → Prankster |
| Glalie | 1 | Inner Focus → Intimidate |
| Huntail | 2 | (none) → Water Veil |
| Huntail | 3 | Water Veil → Guts |
| Gorebyss | 2 | (none) → Hydration |
| Gorebyss | 3 | Hydration → Marvel Scale |
| Regirock | 3 | Sturdy → Solid Rock |
| Piplup | 3 | Defiant → Competitive |
| Prinplup | 3 | Defiant → Competitive |
| Empoleon | 3 | Defiant → Competitive |
| Drifloon | 2 | Unburden → Flare Boost |
| Drifloon | 3 | Flare Boost → Unburden |
| Drifblim | 2 | Unburden → Flare Boost |
| Drifblim | 3 | Flare Boost → Unburden |
| Stunky | 3 | Keen Eye → Defiant |
| Chatot | 2 | Tangled Feet → Soundproof |
| Carnivine | 2 | (none) → Strong Jaw |
| Lickilicky | 2 | Oblivious → Unaware |
| Electivire | 2 | (none) → Vital Spirit |
| Magmortar | 2 | (none) → Vital Spirit |
| Leafeon | 3 | Chlorophyll → Sniper |
| Glaceon | 2 | Snow Cloak → Ice Body |
| Gliscor | 2 | Sand Veil → Sand Rush |
| Gallade | 1 | Steadfast → Justified |
| Gallade | 3 | Justified → Steadfast |
| Dusknoir | 1 | Pressure → Cursed Body |
| Dusknoir | 2 | (none) → Cursed Body |
| Froslass | 1 | Snow Cloak → Frisk |
| Phione | 2 | (none) → Serene Grace |
| Oshawott | 3 | Shell Armor → Water Veil |
| Dewott | 3 | Shell Armor → Water Veil |
| Samurott | 3 | Shell Armor → Intimidate |
| Patrat | 3 | Analytic → Tinted Lens |
| Watchog | 2 | Keen Eye → Analytic |
| Watchog | 3 | Analytic → Tinted Lens |
| Purrloin | 2 | Unburden → Prankster |
| Purrloin | 3 | Prankster → Hustle |
| Liepard | 2 | Unburden → Prankster |
| Liepard | 3 | Prankster → Hustle |
| Pansage | 2 | (none) → Overgrow |
| Simisage | 2 | (none) → Overgrow |
| Pansear | 2 | (none) → Blaze |
| Simisear | 2 | (none) → Blaze |
| Panpour | 2 | (none) → Torrent |
| Simipour | 2 | (none) → Torrent |
| Musharna | 2 | Synchronize → Unaware |
| Gigalith | 3 | Sand Force → Sand Stream |
| Woobat | 1 | Unaware → Simple |
| Woobat | 3 | Simple → Unaware |
| Swoobat | 1 | Unaware → Simple |
| Swoobat | 3 | Simple → Unaware |
| Seismitoad | 2 | Poison Touch → Poison Heal |
| Throh | 1 | Guts → Scrappy |
| Leavanny | 3 | Overcoat → Adaptability |
| Maractus | 1 | Water Absorb → Storm Drain |
| Maractus | 2 | Chlorophyll → Sand Rush |
| Maractus | 3 | Storm Drain → Skill Link |
| Garbodor | 2 | Weak Armor → Regenerator |
| Ducklett | 1 | Keen Eye → Hydration |
| Swanna | 1 | Keen Eye → Hydration |
| Vanillite | 3 | Weak Armor → Snow Cloak |
| Vanillish | 3 | Weak Armor → Snow Cloak |
| Vanilluxe | 3 | Weak Armor → Snow Warning |
| Jellicent | 3 | Damp → Hydration |
| Alomomola | 2 | Hydration → Regenerator |
| Alomomola | 3 | Regenerator → Hydration |
| Accelgor | 2 | Sticky Hold → Frisk |
| Druddigon | 3 | Mold Breaker → Solid Rock |
| Heatmor | 2 | Flash Fire → No Guard |
| Kyurem | 1 | Pressure → Unnerve |
| Kyurem | 2 | (none) → Unnerve |
| Fletchling | 2 | (none) → Gale Wings |
| Fletchling | 3 | Gale Wings → Keen Eye |
| Talonflame | 2 | (none) → Gale Wings |
| Talonflame | 3 | Gale Wings → Keen Eye |
| Pyroar | 2 | Unnerve → Competitive |
| Espurr | 2 | Infiltrator → Own Tempo |
| Espurr | 3 | Own Tempo → Soundproof |
| Spritzee | 1 | Healer → Aroma Veil |
| Aromatisse | 1 | Healer → Aroma Veil |
| Swirlix | 3 | Unburden → Gluttony |
| Slurpuff | 3 | Unburden → Gluttony |
| Malamar | 3 | Infiltrator → Moxie |
| Skrelp | 2 | Poison Touch → Adaptability |
| Skrelp | 3 | Adaptability → Liquid Ooze |
| Dragalge | 2 | Poison Touch → Adaptability |
| Dragalge | 3 | Adaptability → Liquid Ooze |
| Helioptile | 2 | Sand Veil → Solar Power |
| Helioptile | 3 | Solar Power → Sand Veil |
| Heliolisk | 2 | Sand Veil → Solar Power |
| Heliolisk | 3 | Solar Power → Sand Veil |
| Tyrunt | 2 | (none) → Sturdy |
| Tyrunt | 3 | Sturdy → Intimidate |
| Tyrantrum | 2 | (none) → Rock Head |
| Tyrantrum | 3 | Rock Head → Intimidate |
| Amaura | 2 | (none) → Wonder Skin |
| Aurorus | 2 | (none) → Wonder Skin |
| Sylveon | 2 | Cute Charm → Frisk |
| Goomy | 2 | Hydration → Gooey |
| Goomy | 3 | Gooey → Hydration |
| Sliggoo | 2 | Hydration → Gooey |
| Sliggoo | 3 | Gooey → Hydration |
| Goodra | 2 | Hydration → Gooey |
| Goodra | 3 | Gooey → Hydration |
| Phantump | 1 | Natural Cure → Harvest |
| Phantump | 3 | Harvest → Natural Cure |
| Trevenant | 1 | Natural Cure → Harvest |
| Trevenant | 3 | Harvest → Natural Cure |
| Bergmite | 1 | Own Tempo → Sturdy |
| Bergmite | 3 | Sturdy → Filter |
| Avalugg | 1 | Own Tempo → Sturdy |
| Avalugg | 3 | Sturdy → Filter |
| Noivern | 2 | Infiltrator → Limber |

</details>

126 slots where the hack already holds something other than Legacy's old ability keep the hack's (user ruling).

### Planned: learnset changes (3201 moves added, 3219 moves learned earlier)

Moves this engine lacks (skipped): 136 entries across 20 moves.
<details><summary>Show the learnset changes</summary>

| Species | Added | Earlier |
|---|---|---|
| Bulbasaur | Acid L13, Sludge L25, Body Slam L34, Energy Ball L40 | Sleep Powder L15→L11, Poison Powder L15→L11, Sweet Scent L24→L16 |
| Ivysaur | Acid L10, Sludge L25, Body Slam L34, Energy Ball L40 | Sleep Powder L15→L11, Poison Powder L15→L11, Sweet Scent L30→L16, Synthesis L41→L39, Sludge Bomb L46→L43, Solarbeam L56→L46 |
| Venusaur | Acid L10, Sludge L25, Body Slam L34, Energy Ball L40, Ancientpower L50, Frenzy Plant L55 | Sleep Powder L15→L11, Poison Powder L15→L11, Sweet Scent L30→L16, Worry Seed L37→L36, Synthesis L43→L39, Sludge Bomb L49→L43, Solarbeam L61→L46 |
| Charmander | Leer L13, Rage L13, Fire Punch L19, Flame Wheel L19, Bite L23, Dragon Claw L38, Body Slam L42, Slam L50, Fire Blast L52 | Fire Spin L22→L15 |
| Charmeleon | Leer L13, Rage L13, Fire Punch L19, Flame Wheel L19, Bite L23, Dragon Claw L38, Body Slam L42, Dragon Rage L43, Slam L48, Fire Blast L52 | Fire Spin L27→L15, Scary Face L37→L25, Flamethrower L42→L31 |
| Charizard | Tailwind L1, Rage L13, Fire Punch L19, Flame Wheel L19, Bite L23, Body Slam L42, Dragon Rage L43, Slam L48, Outrage L48, Fire Blast L52, Blast Burn L55 | Fire Spin L27→L15, Scary Face L39→L25, Flamethrower L46→L31, Inferno L54→L49 |
| Squirtle | Bubblebeam L21, Soak L26, Body Slam L27, Waterfall L33, Ice Beam L45 | Skull Bash L36→L30 |
| Wartortle | Bubblebeam L21, Soak L26, Body Slam L27, Waterfall L33, Ice Beam L45 | Skull Bash L49→L30, Iron Defense L39→L33 |
| Blastoise | Dragon Pulse L1, Bubblebeam L21, Soak L26, Body Slam L27, Waterfall L33, Ice Beam L45, Hydro Cannon L55 | Skull Bash L56→L30, Iron Defense L42→L33, Hydro Pump L49→L47 |
| Metapod | Tackle L1, String Shot L1 |  |
| Butterfree | Leech Life L10, Giga Drain L27, Psychic L32, Signal Beam L37, Synchronoise L42 | Silver Wind L24→L22 |
| Kakuna | Poison Sting L1, String Shot L1 |  |
| Beedrill | Leech Life L10, Acid L21, Sludge L25, Spike Cannon L25, Swords Dance L30, U-turn L30, Drill Run L37 | Pin Missile L43→L10, Rage L14→L10, Focus Energy L20→L12, Toxic Spikes L29→L21, Fell Stinger L34→L23, Poison Jab L40→L32 |
| Pidgey | Mud-Slap L24, Take Down L29, Sky Attack L42, Hyper Voice L49 | Sand Attack L5→L4, Gust L9→L6, Quick Attack L12→L10, Whirlwind L15→L13, Twister L21→L16, Feather Dance L24→L22, Agility L30→L28, Roost L37→L34, Mirror Move L47→L39, Brave Bird L54→L53 |
| Pidgeotto | Mud-Slap L24, Take Down L29, Sky Attack L42, Hyper Voice L49 | Quick Attack L12→L10, Whirlwind L15→L13, Twister L22→L16, Feather Dance L26→L22, Agility L35→L28, Roost L44→L34, Mirror Move L57→L39, Tailwind L53→L46, Brave Bird L66→L53 |
| Pidgeot | Feint L1, Mud-Slap L24, Take Down L29, Extremespeed L36, Sky Attack L40, Hyper Voice L49 | Whirlwind L15→L13, Twister L22→L16, Feather Dance L26→L22, Agility L35→L28, Roost L47→L34, Mirror Move L63→L39, Tailwind L58→L46, Brave Bird L74→L53 |
| Rattata | Dig L23, Take Down L26 | Bite L16→L9, Assurance L19→L18, Super Fang L31→L28 |
| Raticate | Ice Fang L1, Fire Fang L1, Thunder Fang L1, Dig L23, Take Down L26 | Bite L16→L9, Assurance L19→L18, Crunch L34→L23, Super Fang L39→L28, Endeavor L49→L41 |
| Spearow | Swift L18, Sharpen L26, Whirlwind L28, Drill Run L36, Brave Bird L43, Thrash L47 | Focus Energy L33→L7, Fury Attack L11→L10, Take Down L27→L21, Drill Peck L30→L24 |
| Fearow | Swift L18, Sharpen L26, Whirlwind L28, Brave Bird L43, Thrash L47 | Focus Energy L38→L1, Fury Attack L11→L10, Take Down L30→L21, Drill Peck L34→L24, Roost L42→L39 |
| Ekans | Substitute L22, Sludge L27, Crunch L28, Poison Jab L33, Sludge Bomb L36, Foul Play L48 | Bite L9→L6, Glare L11→L10, Acid L14→L13, Screech L17→L15, Poison Fang L20→L18, Gastro Acid L36→L20, Haze L41→L22, Acid Spray L28→L24, Mud Bomb L33→L30, Coil L44→L42, Gunk Shot L49→L45 |
| Arbok | Substitute L22, Sludge L27, Poison Jab L33, Sludge Bomb L36, Foul Play L48 | Glare L11→L10, Acid L14→L13, Screech L17→L15, Poison Fang L20→L18, Gastro Acid L39→L20, Haze L51→L22, Acid Spray L31→L24, Stockpile L27→L26, Swallow L27→L26, Spit Up L27→L26, Mud Bomb L35→L30, Belch L43→L39, Coil L55→L42, Gunk Shot L59→L45 |
| Pikachu | Headbutt L18, Thunderpunch L20, Iron Tail L44, Volt Tackle L50 | Spark L20→L13, Discharge L32→L27 |
| Raichu | Headbutt L18, Iron Tail L44, Volt Tackle L53 | Thunder L48→L41 |
| Sandshrew | Sand Tomb L5, Mud-Slap L9, Metal Claw L16, Cut L28, Drill Run L30, X-Scissor L38, Spike Cannon L46 | Fury Swipes L24→L1, Sand Attack L6→L1, Magnitude L28→L12, Dig L30→L14, Swift L21→L18, Sandstorm L42→L32, Earthquake L45→L33 |
| Sandslash | Mud-Slap L9, Metal Claw L16, Spike Cannon L24, Cut L28, Drill Run L30, X-Scissor L38 | Fury Swipes L26→L1, Sand Tomb L31→L5, Magnitude L33→L12, Dig L36→L14, Swift L21→L18, Earthquake L61→L30, Sandstorm L56→L32, Swords Dance L51→L42 |
| Nidoran♀ | Dig L26, Headbutt L30, Sludge Bomb L32 | Tail Whip L8→L4, Bite L27→L8, Double Kick L19→L8, Helping Hand L31→L19, Poison Fang L23→L22, Flatter L40→L32 |
| Nidorina | Headbutt L21, Dig L24, Sludge L32, Sludge Bomb L32, Earthquake L40 | Bite L31→L8, Double Kick L21→L8, Helping Hand L36→L19, Poison Fang L26→L22, Flatter L48→L32, Crunch L52→L41 |
| Nidoqueen | Dig L1, Headbutt L8, Magnitude L23, Sludge L32, Sludge Bomb L32, Earthquake L40 |  |
| Nidoran♂ | Dig L26 | Focus Energy L8→L4, Double Kick L19→L8, Horn Attack L27→L17, Helping Hand L31→L19, Poison Tail L23→L22, Flatter L40→L32, Horn Drill L51→L41 |
| Nidorino | Bite L21, Dig L24, Sludge L32, Sludge Bomb L37, Earthquake L40 | Double Kick L21→L8, Horn Attack L31→L17, Helping Hand L36→L19, Poison Tail L26→L22, Flatter L48→L32, Horn Drill L62→L38, Poison Jab L52→L38 |
| Nidoking | Dig L1, Magnitude L26, Sludge L32, Earthquake L36, Sludge Bomb L36 | Poison Jab L52→L38 |
| Clefairy | Light Screen L43 | Defense Curl L13→L12, Follow Me L16→L14, Minimize L25→L19, Stored Power L28→L27, Metronome L31→L30, Body Slam L37→L35, Gravity L46→L42 |
| Clefable | Cosmic Power L33, Light Screen L41 | Meteor Mash L49→L45 |
| Vulpix | Roar L4, Feint Attack L17, Flame Wheel L19, Reflect L25, Shadow Ball L36, Night Shade L37, Captivate L37, Sunny Day L40, Nasty Plot L51 | Quick Attack L8→L7, Fire Spin L46→L11, Confuse Ray L17→L14, Flame Burst L26→L19, Will-O-Wisp L23→L22, Safeguard L42→L27, Flamethrower L38→L30, Fire Blast L58→L40, Inferno L50→L47 |
| Ninetales | Roar L1, Feint Attack L17, Flame Wheel L19, Reflect L25, Shadow Ball L36, Night Shade L37, Captivate L37, Sunny Day L40 | Fire Blast L58→L40 |
| Jigglypuff | Fake Tears L17, Lovely Kiss L22, Encore L33, Perish Song L48, Moonblast L51 | Play Nice L10→L5, Double Slap L14→L8, Rollout L17→L12, Round L20→L15, Rest L26→L24, Body Slam L28→L25, Play Rough L44→L33, Hyper Voice L40→L36, Double-Edge L48→L41 |
| Wigglytuff | Boomburst L1, Fake Tears L17, Lovely Kiss L22, Encore L33, Perish Song L48, Moonblast L51 | Double-Edge L48→L39 |
| Zubat | Gust L4, Acid L27, Sludge L27, Sludge Bomb L36, Cross Poison L38 | Bite L20→L11, Wing Attack L16→L14, Confuse Ray L35→L17, Air Cutter L31→L22, Poison Fang L27→L25, Haze L46→L34 |
| Golbat | Gust L1, Acid L27, Sludge L27, Sludge Bomb L36, Cross Poison L38 | Bite L20→L11, Wing Attack L16→L14, Confuse Ray L41→L17, Air Cutter L36→L22, Poison Fang L31→L25, Acrobatics L64→L31, Haze L55→L34, Air Slash L45→L41 |
| Oddish | Tackle L1, Leech Seed L8, Lucky Chant L20, Sludge L23, Natural Gift L28, Sludge Bomb L36 | Sweet Scent L8→L4, Poisonpowder L15→L5, Stun Spore L17→L12, Sleep Powder L18→L13, Moonlight L32→L28 |
| Gloom | Tackle L1, Leech Seed L8, Lucky Chant L20, Sludge L23, Natural Gift L28, Sludge Bomb L36, Solarbeam L50 | Poison Powder L15→L11, Stun Spore L17→L12, Sleep Powder L18→L13, Moonlight L44→L28, Petal Dance L68→L35 |
| Vileplume | Tackle L1, Leech Seed L8, Lucky Chant L20, Sludge L23, Natural Gift L28, Sludge Bomb L36, Solarbeam L50 | Petal Dance L68→L40 |
| Paras | Absorb L3, Mega Drain L13, Twineedle L29, Swords Dance L37, Moonlight L46 | Leech Life L11→L8, Spore L25→L24, Giga Drain L29→L26, Aromatherapy L38→L31, Seed Bomb L43→L34, Rage Powder L48→L40 |
| Parasect | Absorb L1, Mega Drain L13, Infestation L24, Twineedle L29, Swords Dance L37, Moonlight L46 | Spore L27→L24, Giga Drain L32→L26, Aromatherapy L43→L31, Seed Bomb L49→L34, Rage Powder L55→L40 |
| Venonat | Infestation L23, Skill Swap L33, Endeavor L38, Signal Beam L39, Sludge Bomb L42, Bug Buzz L48 | Supersonic L5→L4, Confusion L11→L7, Poison Powder L13→L9, Leech Life L17→L12, Poison Fang L33→L16, Stun Spore L23→L18, Psychic L42→L41 |
| Venomoth | Tailwind L1, Acid L25, Skill Swap L33, Air Slash L38, Sludge L46 | Confusion L11→L7, Poison Powder L13→L9, Leech Life L17→L12, Stun Spore L23→L18, Psychic L47→L41, Sludge Bomb L55→L42 |
| Diglett | Rototiller L1, Pursuit L12, Rock Tomb L18, Rock Slide L33, Screech L35, Night Slash L43 | Growl L5→L3, Astonish L8→L5, Magnitude L18→L10, Bulldoze L28→L15, Slash L36→L21, Dig L32→L24, Earthquake L40→L39 |
| Dugtrio | Pursuit L12, Rock Tomb L18, Rock Slide L33, Screech L35 | Magnitude L18→L10, Bulldoze L30→L15, Slash L42→L21, Dig L36→L24, Earthquake L48→L39, Fissure L54→L48 |
| Meowth | Captivate L15, Swift L20, Assurance L26, Take Down L28, Power Gem L32, Snatch L36, Double-Edge L38, Swagger L40, Knock Off L43, Hyper Beam L45, Trump Card L48 | Bite L16→L1, Fury Swipes L20→L8, Feint Attack L29→L17, Screech L36→L22, Taunt L24→L22, Slash L32→L24, Night Slash L40→L34 |
| Persian | Captivate L15, Assurance L26, Take Down L28, Snatch L36, Double-Edge L38, Swagger L40, Knock Off L43, Trump Card L48, Hyper Beam L50 | Fury Swipes L20→L8, Feint Attack L30→L17, Swift L52→L20, Taunt L24→L22, Slash L36→L24, Screech L42→L32, Night Slash L47→L34 |
| Psyduck | Bubblebeam L17, Signal Beam L29, Scald L34, Power Gem L42 | Tail Whip L4→L1, Water Gun L7→L4, Confusion L10→L7, Disable L19→L10, Fury Swipes L13→L10, Water Pulse L16→L13, Screech L22→L18, Zen Headbutt L25→L21, Aqua Tail L28→L24, Psych Up L34→L26, Amnesia L40→L29 |
| Golduck | Bubblebeam L17, Signal Beam L29, Calm Mind L31, Scald L34 | Amnesia L46→L1, Confusion L10→L7, Fury Swipes L13→L10, Water Pulse L16→L13, Screech L22→L18, Zen Headbutt L25→L21, Aqua Tail L28→L24, Psych Up L36→L26, Psychic L41→L37, Hydro Pump L51→L43, Wonder Room L56→L47 |
| Mankey | Submission L24, Work Up L26, Mega Punch L30 | Seismic Toss L15→L11, Assurance L22→L14, Low Sweep L28→L16, Screech L25→L19, Cross Chop L44→L33, Thrash L40→L39, Close Combat L52→L44, Final Gambit L56→L48 |
| Primeape | Shadow Punch L1, Submission L24, Work Up L26, Mega Punch L30 | Seismic Toss L15→L11, Assurance L22→L14, Low Sweep L28→L16, Screech L25→L19, Cross Chop L49→L33, Punishment L39→L36, Thrash L44→L39, Close Combat L61→L44, Outrage L55→L52 |
| Growlithe | Growl L1, Snarl L24, Extreme Speed L49 | Odor Sleuth L10→L8, Helping Hand L16→L10, Take Down L36→L16, Flamethrower L40→L35 |
| Arcanine | Growl L1, Snarl L24, Flame Burst L28 | Outrage L57→L50, Flare Blitz L60→L55 |
| Poliwag | Mind Reader L1, Mist L4, Helping Hand L27, Muddy Water L31, Amnesia L36 | Doubleslap L11→L1, Bubble Beam L19→L18, Double-Edge L51→L49 |
| Poliwhirl | Mist L1, Mind Reader L1, Karate Chop L25, Helping Hand L27, Ice Punch L30, Muddy Water L31, Amnesia L36 | Doubleslap L11→L10, Bubble Beam L19→L18, Rain Dance L33→L25, Body Slam L42→L31, Hydro Pump L61→L42, Double-Edge L56→L49 |
| Poliwrath | Mist L1, Karate Chop L1, Ice Punch L1, Hammer Arm L1, Dive L1, Detect L1, Comet Punch L12, Mach Punch L15, Muddy Water L31, Bulk Up L36, Amnesia L48 | Belly Drum L52→L43 |
| Machop | Assurance L21, Vital Throw L25, Mega Punch L30, Take Down L33, Counter L37 | Focus Energy L4→L3, Seismic Toss L42→L15, Revenge L46→L19, Submission L38→L28 |
| Machoke | Assurance L21, Vital Throw L25, Mega Punch L30, Body Slam L33, Counter L37 | Seismic Toss L46→L15, Revenge L51→L19, Submission L41→L28, Cross Chop L61→L40, Dynamic Punch L66→L49, Double-Edge L56→L54 |
| Machamp | Bullet Punch L1, Assurance L21, Vital Throw L25, Mega Punch L30, Take Down L33, Counter L37 | Seismic Toss L46→L15, Revenge L51→L19, Submission L41→L28, Cross Chop L61→L40, Dynamic Punch L66→L49, Double-Edge L56→L54 |
| Bellsprout | Sludge L25, Headbutt L27, Leaf Tornado L27, Body Slam L30, Sludge Bomb L32, Cross Poison L38, Leaf Blade L40, Leaf Storm L53 | Sweet Scent L24→L1, Growth L7→L5, Wrap L11→L8, Acid L14→L12, Poisonpowder L17→L13, Sleep Powder L17→L14, Stun Spore L17→L16, Razor Leaf L21→L20, Gastro Acid L35→L32, Wring Out L47→L45 |
| Weepinbell | Sludge L25, Headbutt L27, Leaf Tornado L27, Body Slam L30, Sludge Bomb L32, Cross Poison L38, Leaf Blade L40, Leaf Storm L53 | Poisonpowder L17→L1, Sweet Scent L26→L1, Acid L14→L12, Sleep Powder L17→L14, Stun Spore L17→L16, Razor Leaf L21→L20, Gastro Acid L40→L32, Wring Out L59→L45 |
| Victreebel | Sludge L25, Headbutt L27, Body Slam L30, Sludge Bomb L32, Cross Poison L38 | Wring Out L59→L45 |
| Tentacool | Bubble L1, Whirlpool L9, Sludge L25, Barrier L26, Sludge Bomb L34 | Supersonic L12→L1, Constrict L6→L3, Water Pulse L16→L13, Acid Spray L22→L18, Bubble Beam L24→L19, Poison Jab L36→L29, Brine L34→L33, Sludge Wave L44→L40 |
| Tentacruel | Bubble L1, Whirlpool L9, Sludge L20, Barrier L26, Sludge Bomb L34 | Water Pulse L16→L13, Acid Spray L22→L18, Bubble Beam L24→L19, Poison Jab L40→L29, Brine L37→L33, Sludge Wave L52→L40, Hydro Pump L58→L47 |
| Geodude | Rapid Spin L1, Mud-Slap L6, Dig L21, Steamroller L36 | Mud Sport L4→L1, Rock Polish L28→L6, Self-Destruct L24→L21, Stealth Rock L36→L29, Stone Edge L52→L49 |
| Graveler | Rapid Spin L1, Mud-Slap L6, Dig L21, Harden L26, Steamroller L36 | Self-Destruct L24→L21, Stealth Rock L39→L29, Rock Slide L44→L40, Earthquake L48→L40, Explosion L63→L45, Stone Edge L58→L49, Double-Edge L53→L52 |
| Golem | Rapid Spin L1, Mud-Slap L6, Dig L21, Harden L26 | Self-Destruct L24→L21, Stealth Rock L39→L29, Rock Slide L44→L40, Earthquake L48→L40, Explosion L63→L45, Stone Edge L58→L49, Double-Edge L53→L52 |
| Ponyta | Double Kick L14, Sunny Day L25, Blaze Kick L29, Flamethrower L33, High Jump Kick L42, Double-Edge L49 | Fire Spin L32→L1, Ember L8→L6, Stomp L28→L9, Flame Charge L16→L12, Flame Wheel L24→L20, Take Down L37→L22, Bounce L52→L32, Fire Blast L47→L45 |
| Rapidash | Double Kick L14, Sunny Day L25, Blaze Kick L29, Flamethrower L33, Hi Jump Kick L40, Double-Edge L49 | Fire Spin L32→L1, Stomp L28→L9, Flame Charge L16→L12, Flame Wheel L24→L20, Take Down L37→L22, Bounce L59→L32, Fire Blast L53→L45 |
| Slowpoke | Psybeam L25, Waterfall L28, Brine L35, Withdraw L36, Aqua Tail L51 | Water Gun L6→L5, Confusion L12→L11, Headbutt L21→L18, Heal Pulse L45→L27 |
| Slowbro | Psybeam L25, Waterfall L28, Brine L35, Aqua Tail L51 | Confusion L12→L11, Headbutt L21→L18 |
| Magnemite | Swift L24, Reflect L27, Tri Attack L30, Thunderbolt L33, Thunder L50 | Supersonic L4→L3, Sonic Boom L17→L8, Screech L24→L19, Magnet Rise L31→L28, Light Screen L48→L40, Gyro Ball L52→L45, Zap Cannon L60→L54 |
| Magneton | Swift L24, Reflect L27, Thunderbolt L33, Thunder L50, Refresh L57 | Screech L24→L19, Magnet Rise L34→L28, Discharge L39→L37, Light Screen L53→L40, Gyro Ball L57→L45, Zap Cannon L66→L50, Lock-On L62→L50 |
| Farfetch'd | Sharpen L9, Wing Attack L18, Baton Pass L28, Drill Peck L31, Air Slash L41, Body Slam L43 | Knock Off L30→L10, False Swipe L26→L15, Swords Dance L38→L22, Slash L34→L23, Night Slash L42→L25, Acrobatics L46→L31, Leaf Blade L50→L39 |
| Doduo | Uproar L1, Double Kick L11, Low Kick L23, Bounce L24, Tri Attack L39, Double-Edge L50, Mega Kick L52 | Acupressure L28→L27, Drill Peck L42→L34, Endeavor L46→L37 |
| Dodrio | Uproar L1, Blaze Kick L1, Double Kick L11, Low Kick L23, Bounce L24, Double-Edge L50, Mega Kick L52 | Thrash L58→L1, Acupressure L28→L27, Agility L34→L33, Drill Peck L48→L34, Endeavor L53→L37 |
| Seel | Whirlpool L1, Powder Snow L1, Water Gun L5, Bubblebeam L25, Work Up L27, Avalanche L44, Blizzard L50 | Growl L3→L1, Water Sport L7→L3, Aqua Jet L16→L7, Icy Wind L22→L10, Encore L13→L12, Aqua Ring L19→L15, Aurora Beam L32→L16, Brine L29→L20, Rest L25→L21, Take Down L36→L24, Dive L40→L30, Ice Beam L47→L32, Safeguard L44→L38, Aqua Tail L51→L41, Hail L55→L46 |
| Dewgong | Water Gun L1, Powder Snow L1, Drill Run L1, Whirlpool L1, Bubblebeam L25, Work Up L27, Avalanche L44, Blizzard L50 | Aqua Jet L16→L7, Encore L13→L12, Aqua Ring L19→L15, Brine L29→L20, Rest L25→L21, Aurora Beam L32→L22, Take Down L39→L24, Dive L44→L30, Ice Beam L53→L32, Safeguard L49→L38, Aqua Tail L58→L41, Hail L63→L46 |
| Grimer | Acid L16, Toxic L24, Mud Shot L26, Payback L27, Sludge Bomb L36, Body Slam L37, Pain Split L38, Punishment L45 | Mud-Slap L7→L6, Disable L12→L8, Sludge L15→L11, Minimize L21→L12, Mud Bomb L18→L14, Fling L29→L17, Screech L37→L19, Sludge Wave L26→L22, Acid Armor L43→L24, Poison Jab L32→L30, Belch L46→L35 |
| Muk | Fire Punch L1, Ice Punch L1, Thunder Punch L1, Acid L16, Toxic L24, Mud Shot L26, Payback L27, Sludge Bomb L36, Body Slam L37, Pain Split L38, Punishment L45, Hammer Arm L52 | Disable L12→L1, Sludge L15→L11, Minimize L21→L12, Mud Bomb L18→L14, Fling L29→L17, Screech L37→L19, Sludge Wave L26→L22, Acid Armor L46→L24, Poison Jab L32→L30, Belch L52→L35, Memento L57→L48 |
| Shellder | Bubble Beam L22, Blizzard L50, Explosion L55 | Withdraw L4→L1, Supersonic L20→L4, Whirlpool L16→L7, Aurora Beam L24→L12, Protect L36→L14, Clamp L28→L22, Razor Shell L40→L31, Iron Defense L44→L33, Ice Beam L47→L35, Hydro Pump L54→L44, Shell Smash L51→L47 |
| Cloyster | Bubble Beam L22, Blizzard L50 |  |
| Gastly | Psywave L15, Clear Smog L18, Poison Gas L23 |  |
| Haunter | Psywave L15, Clear Smog L18, Nightmare L51 | Dream Eater L66→L35, Shadow Ball L48→L42, Destiny Bond L60→L48 |
| Gengar | Psywave L1, Clear Smog L18 | Dream Eater L66→L35, Shadow Ball L48→L42, Destiny Bond L60→L48 |
| Onix | Rock Throw L4, Rage L6, Bulldoze L18 | Slam L36→L13, Stealth Rock L32→L15, Dig L44→L18, Sandstorm L40→L29, Earthquake L60→L40, Stone Edge L52→L43, Double-Edge L56→L46 |
| Drowzee | Dream Eater L24, Payback L27, Skill Swap L35, Foul Play L42 | Disable L5→L4, Confusion L9→L6, Headbutt L17→L9, Poison Gas L13→L11, Meditate L21→L14, Psybeam L24→L17, Psych Up L32→L20, Swagger L39→L30, Psychic L49→L33, Future Sight L53→L46 |
| Hypno | Dream Eater L24, Payback L27, Skill Swap L35, Foul Play L42 | Headbutt L17→L9, Poison Gas L13→L11, Meditate L21→L14, Psybeam L24→L17, Psych Up L35→L20, Swagger L44→L30, Psychic L57→L32, Zen Headbutt L39→L38, Future Sight L62→L45 |
| Krabby | Brine L20, Hone Claws L28, Cut L29, X-Scissor L31 | Harden L3→L1, Bubble Beam L20→L11, Stomp L24→L23, Razor Shell L32→L25, Crabhammer L44→L34 |
| Kingler | Brine L20, Cut L28, Hone Claws L28, X-Scissor L31 | Bubble Beam L20→L11, Stomp L24→L23, Razor Shell L36→L25, Crabhammer L54→L27, Swords Dance L48→L46 |
| Voltorb | Rapid Spin L1, Thunder Wave L14, Thundershock L19, Thunderbolt L35, Thunder L40, Signal Beam L40, Rain Dance L42, Nasty Plot L54 | Sonic Boom L18→L6, Rollout L12→L11, Screech L15→L13, Charge Beam L21→L16, Swift L25→L17, Electro Ball L46→L24, Self Destruct L28→L26, Magnet Rise L39→L37 |
| Electrode | Volt Tackle L1, Weather Ball L1, Rapid Spin L1, Thunder Wave L14, Thundershock L19, Thunderbolt L35, Thunder L40, Signal Beam L40, Rain Dance L42, Nasty Plot L54, Refresh L59 | Rollout L12→L11, Screech L15→L13, Charge Beam L21→L16, Swift L25→L17, Electro Ball L52→L24, Self Destruct L28→L26, Discharge L38→L35, Magnet Rise L43→L37, Explosion L47→L44, Mirror Coat L57→L49 |
| Exeggcute | Poisonpowder L10, Stun Spore L17, Sleep Powder L19, Psybeam L28, Egg Bomb L40, Bestow L42, Psychic L45, Soft-Boiled L45 | Confusion L17→L13, Bullet Seed L25→L16, Worry Seed L49→L25, Giga Drain L34→L31, Extrasensory L39→L37, Solarbeam L54→L42 |
| Exeggutor | Poisonpowder L10, Stun Spore L17, Sleep Powder L19, Psybeam L28, Growth L30, Soft-Boiled L45 | Psychic L49→L45 |
| Cubone | Tackle L1, Earthquake L47, Belly Drum L51, Iron Head L53 | Leer L10→L5, Focus Energy L22→L13, Bonemerang L33→L31, Bone Rush L41→L33, Double-Edge L45→L41 |
| Marowak | Tackle L1, Thrash L31, Earthquake L46, Belly Drum L51, Iron Head L53 | Head Smash L60→L1, Leer L10→L5, Focus Energy L22→L13, Bonemerang L36→L31, Bone Rush L48→L33, Endeavor L42→L37, Double-Edge L54→L41 |
| Hitmonlee | Knock Off L27, Bounce L43 | Meditate L12→L4, Mind Reader L30→L23 |
| Hitmonchan | Foresight L1, Karate Chop L25, Dynamic Punch L36, Dizzy Punch L39, Submission L42, Shadow Punch L47 | Agility L30→L4, Mega Punch L34→L23, Sky Uppercut L39→L30 |
| Lickitung | Pound L1, Headbutt L19, Slam L21, Chip Away L24, Curse L25, Me First L40 | Wrap L6→L1, Disable L19→L1, Stomp L15→L13, Rollout L29→L17, Refresh L40→L29, Body Slam L37→L32, Belly Drum L55→L40, Power Whip L48→L47 |
| Koffing | Rapid Spin L1, Acid L23, Venoshock L25, Amnesia L26, Payback L28, Pain Split L49 | Clear Smog L12→L10, Selfdestruct L28→L15, Sludge L20→L16, Haze L23→L22, Memento L48→L30, Explosion L44→L39 |
| Weezing | Acid L23, Venoshock L25, Amnesia L26, Payback L28, Pain Split L49 | Clear Smog L12→L10, Sludge L20→L16, Self-Destruct L28→L20, Haze L23→L22, Memento L50→L30, Explosion L62→L39, Destiny Bond L68→L43 |
| Rhyhorn | Rock Throw L12, Magnitude L23, Dig L24, Rock Slide L36, Double-Edge L56 | Stomp L16→L9, Chip Away L24→L19, Take Down L36→L29, Earthquake L40→L39, Horn Drill L52→L40, Megahorn L48→L45 |
| Rhydon | Rock Throw L12, Magnitude L23, Dig L24, Rock Slide L36, Double-Edge L56 | Smack Down L8→L1, Chip Away L24→L19, Take Down L36→L29, Earthquake L40→L39, Megahorn L54→L45 |
| Chansey | Bestow L12, Heal Bell L42, Mega Punch L50 | Softboiled L76→L10, Echoed Voice L24→L10, Helping Hand L20→L14, Minimize L72→L18, Fling L48→L27, Healing Wish L68→L49 |
| Tangela | Body Slam L37, Energy Ball L43, Morning Sun L55 | Vine Whip L16→L7, Poison Powder L20→L10, Knock Off L27→L22, Sleep Powder L39→L25, Tickle L47→L28, Giga Drain L35→L31 |
| Kangaskhan | Leer L7, Circle Throw L29, Body Slam L37, Double-Edge L48 | Fake Out L8→L5, Focus Energy L20→L8, Bite L14→L12, Chip Away L24→L15, Mega Punch L47→L24, Dizzy Punch L37→L25, Crunch L42→L36, Endure L52→L41, Reversal L57→L44 |
| Horsea | Aurora Beam L24, Dragon Rage L26, Waterfall L33, Flail L36 | Water Gun L13→L10, Bubblebeam L25→L22, Agility L29→L26 |
| Seadra | Aurora Beam L24, Dragon Rage L26, Waterfall L33, Flail L38, Slam L41, Body Slam L47 | Water Gun L13→L10, Bubblebeam L25→L22, Agility L29→L26, Dragon Pulse L47→L42, Hydro Pump L53→L43, Dragon Dance L59→L50 |
| Goldeen | Bubble L1, Water Gun L3, Drill Peck L27, Swords Dance L30, Rain Dance L32, Aqua Tail L38, Hydro Pump L50 | Horn Attack L18→L9, Flail L34→L13, Waterfall L38→L15, Fury Attack L26→L19, Aqua Ring L30→L21, Horn Drill L54→L34, Megahorn L50→L35 |
| Seaking | Bubble L1, Water Gun L1, Drill Run L1, Drill Peck L27, Swords Dance L30, Rain Dance L32, Aqua Tail L38, Hydro Pump L50 | Horn Attack L18→L9, Flail L35→L13, Waterfall L41→L15, Fury Attack L26→L19, Aqua Ring L30→L21, Horn Drill L59→L34, Megahorn L53→L35 |
| Staryu | Confusion L10, Gyro Ball L22, Psyshock L40, Refresh L55 | Rapid Spin L11→L7, Reflect Type L34→L10, Swift L21→L15, Bubble Beam L18→L16, Light Screen L32→L27, Psychic L40→L37, Cosmic Power L52→L41, Hydro Pump L56→L49 |
| Starmie | Confusion L1, Gravity L1, Icy Wind L1, Signal Beam L19, Gyro Ball L22, Psyshock L40, Refresh L55 | Hydro Pump L56→L46 |
| Scyther | Razor Wind L1, Pursuit L8, Cut L15, Double Team L31, Twineedle L42, Acrobatics L52 | Fury Cutter L4→L1, Focus Energy L32→L6 |
| Jynx | Icy Wind L13, Captivate L19, Psybeam L22, Frost Breath L28, Ice Beam L41 | Heart Stamp L23→L10, Double Slap L16→L13, Ice Punch L30→L16, Wring Out L49→L46, Perish Song L54→L51, Blizzard L58→L54 |
| Electabuzz | Spark L17, Work Up L21, Mega Punch L32, Cross Chop L48 | Low Kick L41→L6, Shock Wave L15→L9, Thunder Wave L19→L16, Electro Ball L29→L19, Light Screen L53→L40, Thunderbolt L47→L42, Thunder L58→L52 |
| Magmar | Fire Spin L9, Work Up L21, Will-O-Wisp L22, Poison Gas L25, Mega Punch L32, Dark Pulse L48 | Flame Burst L30→L19, Fire Punch L36→L25, Sunny Day L56→L30, Lava Plume L41→L35, Flamethrower L51→L39, Fire Blast L60→L50 |
| Pinsir | Twineedle L1, Leech Life L1, Revenge L13, Slash L42, Megahorn L44 | Seismic Toss L12→L1, Vital Throw L20→L10, Submission L52→L36, Guillotine L56→L37 |
| Tauros | Refresh L1, Rock Climb L1, Iron Head L1, Outrage L1, Captivate L1, Leer L15, Stomp L19, Headbutt L22, Punishment L29, Double-Edge L50, Superpower L50 | Horn Attack L16→L7, Rest L42→L18, Take Down L37→L32, Swagger L47→L40, Thrash L52→L45, Giga Impact L70→L60 |
| Gyarados | Gust L20, Bounce L44, Slam L48 | Waterfall L40→L25, Thrash L51→L35, Hyper Beam L59→L50 |
| Lapras | Icy Wind L15, Aurora Beam L23, Waterfall L34, Surf L43, Heal Pulse L46, Blizzard L55 | Brine L32→L29, Safeguard L56→L33 |
| Eevee | Double Kick L14, Headbutt L22, Focus Energy L30, Wish L35, Jump Kick L36 | Sand Attack L5→L4, Quick Attack L10→L6, Bite L25→L9, Charm L45→L20, Baton Pass L35→L30, Take Down L40→L36 |
| Vaporeon | Bubble L1, Icy Wind L1, Jump Kick L1, Mist L12, Double Kick L14, Bubblebeam L26, Brine L29, Rest L47, Ice Beam L52 | Sand Attack L5→L4, Quick Attack L10→L6, Aqua Ring L35→L22, Acid Armor L45→L41, Hydro Pump L50→L49 |
| Jolteon | Magnet Rise L1, Jump Kick L1, Charge L12, Eerie Impulse L22, Spark L26, Charge Beam L29, Thunderbolt L36, Zap Cannon L52 | Sand Attack L5→L4, Quick Attack L10→L6, Double Kick L25→L14, Pin Missile L35→L30, Agility L45→L41, Thunder L50→L49 |
| Flareon | Leer L1, Inferno L1, Jump Kick L1, Double Kick L14, Facade L25, Flame Wheel L26, Growth L32, Will-O-Wisp L35, Flamethrower L36, Blaze Kick L37, Play Rough L48, Fire Blast L52, Superpower L52 | Sand Attack L5→L4, Quick Attack L10→L6, Fire Spin L35→L12, Scary Face L45→L22, Lava Plume L40→L29 |
| Porygon | Swift L10, Electroweb L18, Barrier L40, Psyshock L44 | Psybeam L20→L4, Agility L32→L7, Recover L35→L14, Signal Beam L29→L24, Tri Attack L45→L28, Discharge L40→L31, Magic Coat L50→L34, Lock-On L55→L41, Zap Cannon L60→L48, Hyper Beam L65→L50 |
| Omanyte | Bite L11, Rock Throw L14, Clamp L14, Bubblebeam L18, Horn Attack L22, Spike Cannon L27, Iron Defense L29, Tickle L35, Rock Slide L37, Power Gem L38, Earth Power L45, Spikes L51 | Leer L20→L1, Water Gun L15→L5, Mud Shot L25→L17, Protect L41→L23, Ancient Power L30→L26, Hydro Pump L60→L46, Shell Smash L55→L49 |
| Omastar | Stealth Rock L1, Rock Throw L14, Clamp L14, Bubblebeam L18, Iron Defense L29, Tickle L35, Rock Slide L37, Power Gem L38, Earth Power L45, Spikes L51 | Leer L20→L1, Water Gun L15→L1, Mud Shot L25→L17, Protect L43→L23, Ancient Power L30→L26, Hydro Pump L70→L46, Shell Smash L63→L49 |
| Kabuto | Rock Throw L6, Water Gun L11, Smack Down L15, Mega Drain L20, Slash L32, Rock Slide L36, Swords Dance L42, X-Scissor L43, Hydro Pump L48 | Leer L20→L1, Sand Attack L10→L1, Metal Sound L55→L21, Ancient Power L30→L26, Stone Edge L60→L53 |
| Kabutops | Rock Throw L1, Water Gun L11, Smack Down L15, Mega Drain L20, Rock Slide L36, Swords Dance L42, X-Scissor L43, Hydro Pump L48, Wring Out L56 | Leer L20→L11, Metal Sound L63→L21, Ancient Power L30→L26, Slash L43→L32, Stone Edge L70→L53 |
| Aerodactyl | Gust L1, Rock Throw L27, Double-Edge L45, Hyper Beam L50, Dragon Claw L50 | Agility L50→L15, Take Down L40→L25, Sky Drop L55→L30 |
| Snorlax | Harden L33 | Rollout L26→L25 |
| Articuno | Extrasensory L1, Heal Bell L1, Defog L1, Air Cutter L15, Drill Peck L40, Air Slash L40, Sky Attack L55 | Ice Shard L20→L10, Mind Reader L60→L20 |
| Zapdos | Wing Attack L1, Extrasensory L1, Metal Sound L1, Eerie Impulse L1, Defog L1, Shock Wave L20, Electro Ball L30, Thunderbolt L45, Sky Attack L55, Baton Pass L61, Tailwind L80 | Detect L60→L10, Pluck L20→L15, Drill Peck L45→L42 |
| Moltres | Extrasensory L1, Whirlwind L1, Defog L1, Growth L20, Flame Burst L30, Drill Peck L40, Flamethrower L45, Fire Blast L51, Tailwind L80 | Ember L5→L1, Endure L60→L10, Incinerate L30→L15, Sky Attack L80→L55, Solar Beam L70→L65 |
| Dratini | Tackle L1, Headbutt L18, Dragon Breath L31, Tri Attack L53 | Dragon Rage L34→L14, Outrage L55→L45, Dragon Dance L50→L48, Hyper Beam L60→L54 |
| Dragonair | Tackle L1, Headbutt L18, Dragon Breath L31, Tri Attack L53 | Dragon Rage L37→L14, Safeguard L46→L40, Dragon Dance L60→L48, Outrage L67→L50, Hyper Beam L74→L61 |
| Dragonite | Tackle L1, Heal Bell L1, Headbutt L18, Dragon Breath L31, Tri Attack L53 | Dragon Rage L37→L14, Safeguard L46→L40, Dragon Dance L62→L48, Outrage L71→L56, Hyper Beam L80→L61 |
| Mew | Sky Attack L1, Superpower L1, Knock Off L1, Iron Tail L1, Icy Wind L1, Stealth Rock L1, Helping Hand L1, Trick L1, Defog L1, Psywave L1, Hyper Voice L10, Confusion L15, Psybeam L25, Zen Headbutt L30 |  |
| Chikorita | Leech Seed L9, Mega Drain L21, Giga Drain L26, Seed Bomb L39, Heal Pulse L42, Sunny Day L46 | Razor Leaf L6→L4, Poison Powder L9→L6, Reflect L15→L12, Magical Leaf L18→L15, Natural Gift L22→L20, Light Screen L37→L23, Body Slam L33→L30, Safeguard L40→L34, Solarbeam L46→L45 |
| Bayleef | Leech Seed L9, Mega Drain L21, Giga Drain L26, Seed Bomb L39, Heal Pulse L42, Sunny Day L46 | Reflect L15→L12, Magical Leaf L19→L15, Natural Gift L24→L20, Light Screen L43→L23, Body Slam L38→L30, Safeguard L47→L34, Solarbeam L55→L45 |
| Meganium | Power Whip L1, Weather Ball L1, Leech Seed L9, Mega Drain L21, Giga Drain L26, Heal Pulse L42, Sunny Day L46 | Reflect L15→L12, Magical Leaf L19→L15, Natural Gift L24→L20, Light Screen L47→L23, Body Slam L41→L30, Safeguard L52→L34, Solarbeam L62→L45 |
| Cyndaquil | Work Up L25, Sunny Day L34, Endure L47, Fire Blast L50, Heat Wave L51 | Ember L6→L4, Quick Attack L12→L10, Defense Curl L15→L12, Flame Wheel L24→L16, Swift L28→L19, Lava Plume L32→L29, Flamethrower L37→L31, Inferno L48→L42 |
| Quilava | Work Up L25, Sunny Day L34, Heat Wave L45, Endure L47, Fire Blast L50 | Quick Attack L12→L10, Defense Curl L15→L12, Flame Wheel L27→L16, Swift L32→L19, Lava Plume L37→L29, Flamethrower L43→L31, Inferno L56→L42, Double-Edge L49→L45 |
| Typhlosion | Thunder Punch L1, Work Up L25, Sunny Day L34, Heat Wave L45, Endure L47, Fire Blast L50 | Quick Attack L12→L10, Defense Curl L15→L12, Flame Wheel L27→L16, Swift L32→L19, Lava Plume L40→L29, Flamethrower L47→L31, Inferno L62→L42, Eruption L78→L60 |
| Totodile | Bubble Beam L17, Agility L25, Dive L28 | Water Gun L6→L4, Bite L12→L11, Scary Face L16→L13, Chip Away L26→L22, Screech L42→L40, Aqua Tail L45→L40, Hydro Pump L57→L50 |
| Croconaw | Bubble Beam L17, Agility L25, Dive L28 | Bite L12→L11, Scary Face L16→L13, Ice Fang L21→L20, Chip Away L30→L22, Slash L45→L35, Screech L50→L37, Aqua Tail L54→L40, Thrash L59→L47, Hydro Pump L69→L50, Superpower L64→L51 |
| Feraligatr | Dynamic Punch L1, Bubble Beam L17, Circle Throw L22, Dive L28, Outrage L47 | Bite L12→L11, Scary Face L16→L13, Ice Fang L21→L20, Slash L49→L35, Screech L55→L37, Aqua Tail L60→L40, Hydro Pump L78→L50, Superpower L72→L51 |
| Sentret | Thief L9, Headbutt L15, Pursuit L16, Dig L20, Coil L22, Double-Edge L43 | Quick Attack L7→L6, Helping Hand L16→L10, Fury Swipes L13→L12, Baton Pass L40→L28, Extremespeed L43→L30 |
| Furret | Thief L1, Tackle L1, Headbutt L15, Pursuit L16, Dig L20, Double-Edge L43 | Hyper Voice L20→L1, Helping Hand L17→L10, Fury Swipes L13→L12, Baton Pass L45→L28, Extremespeed L48→L30, Sucker Punch L38→L34, Amnesia L42→L40 |
| Hoothoot | Psybeam L20, Light Screen L22, Wing Attack L24, Mirror Coat L30, Psychic L40, Hyper Voice L41, Defog L43, Future Sight L50 | Hypnosis L36→L14, Take Down L24→L18 |
| Noctowl | Future Sight L1, Psybeam L20, Light Screen L22, Wing Attack L24, Mirror Coat L30, Psychic L40, Hyper Voice L41, Defog L43 | Hypnosis L48→L14, Take Down L28→L18, Roost L33→L29, Dream Eater L53→L45 |
| Ledyba | Leech Life L6, Work Up L22, Agility L24, Signal Beam L27, Giga Drain L36, Barrier L41, Me First L46 | Supersonic L5→L3, Baton Pass L43→L20 |
| Ledian | Leech Life L1, Power Swap L1, Guard Swap L1, Work Up L22, Agility L24, Signal Beam L27, Giga Drain L36, Barrier L41, Me First L46 | Baton Pass L51→L20 |
| Spinarak | Poison Fang L13, Twineedle L18, Fell Stinger L22, Giga Drain L25, Psychic L30, Knock Off L44 | Scary Face L8→L1, Night Shade L21→L8, Fury Swipes L15→L10, Shadow Sneak L18→L15, Spider Web L30→L20, Poison Jab L42→L27, Sticky Web L45→L38, Megahorn L48→L43 |
| Ariados | Electroweb L1, Poison Fang L13, Twineedle L18, Giga Drain L25, Psychic L30, Knock Off L44 | Leech Life L5→L1, Night Shade L21→L8, Fury Swipes L15→L10, Shadow Sneak L18→L15, Spider Web L33→L20, Poison Jab L49→L27, Sticky Web L53→L38, Megahorn L57→L43 |
| Crobat | Gust L1, Giga Drain L1, Sludge L27, Sludge Bomb L36, X-Scissor L46 | Bite L20→L11, Wing Attack L16→L14, Confuse Ray L41→L17, Air Cutter L36→L22, Poison Fang L31→L25, Acrobatics L64→L31, Haze L55→L34, Air Slash L45→L41 |
| Chinchou | Thunderbolt L33, Rain Dance L33, Dive L35, Thunder L42 | Flail L37→L1, Thunder Wave L9→L5, Take Down L41→L15, Spark L20→L19, Signal Beam L31→L26, Ion Deluge L49→L38 |
| Lanturn | Thunderbolt L33, Rain Dance L33, Dive L35, Thunder L42 | Flail L42→L1, Take Down L48→L15, Spark L20→L19, Signal Beam L33→L26, Ion Deluge L58→L38, Hydro Pump L54→L41 |
| Togepi | Helping Hand L1, Fairy Wind L1, Return L10, Swift L25, Tri Attack L43, Soft-Boiled L50 | Metronome L24→L5, Follow Me L40→L17, Safeguard L36→L32 |
| Togetic | Helping Hand L1, Return L10, Tailwind L22, Wing Attack L24, Air Cutter L25, Air Slash L38, Tri Attack L39, Defog L47, Soft-Boiled L50 | Metronome L24→L5, Follow Me L40→L17, Safeguard L36→L32 |
| Natu | Morning Sun L1, Confusion L4, Air Cutter L16, Psybeam L21, Recover L30, Baton Pass L30, Air Slash L31, Wing Attack L40, Drill Peck L40 | Miracle Eye L35→L1, Teleport L8→L7, Night Shade L14→L9, Wish L42→L25, Psychic L38→L35 |
| Xatu | Confusion L1, Air Cutter L16, Psybeam L21, Recover L30, Baton Pass L30, Wing Attack L40, Drill Peck L40, Morning Sun L49 | Miracle Eye L41→L1, Teleport L8→L7, Wish L50→L25, Psychic L45→L35 |
| Mareep | Shock Wave L21, Thunderbolt L47, Natural Gift L47, Tail Glow L62 | Cotton Spore L12→L4, Thundershock L8→L7, Confuse Ray L26→L24 |
| Flaaffy | Shock Wave L21, Thunderbolt L47, Natural Gift L47, Thunder L52, Tail Glow L62 | Cotton Spore L12→L1, Take Down L19→L18, Confuse Ray L29→L24, Discharge L38→L37, Signal Beam L47→L41 |
| Ampharos | Shock Wave L21, Thunderbolt L47, Thunder L52, Tail Glow L62 | Cotton Spore L12→L1, Take Down L19→L18, Confuse Ray L29→L24, Power Gem L35→L33, Discharge L41→L37, Light Screen L58→L39, Signal Beam L52→L41, Cotton Guard L47→L44 |
| Bellossom | Poisonpowder L1, Charm L1, Sleep Powder L13, Lucky Chant L20, Razor Leaf L23, Morning Sun L28, Natural Gift L28, Giga Drain L31, Moonlight L35, Solar Beam L45, Moonblast L51 | Quiver Dance L39→L1, Petal Dance L59→L40 |
| Marill | Double Slap L19, Take Down L22, Aqua Jet L27, Covet L32, Belly Drum L45 | Rain Dance L30→L28, Superpower L42→L39 |
| Azumarill | Double Slap L19, Take Down L22, Aqua Jet L27, Covet L32, Belly Drum L45 | Bounce L15→L1, Aqua Ring L28→L24, Rain Dance L32→L28, Superpower L48→L39 |
| Sudowoodo | Fake Out L1, Submission L28, Curse L37, Thrash L46 | Rock Tomb L21→L20, Counter L40→L25 |
| Politoed | Mist L1, Weather Ball L1, Sweet Kiss L1, Light Screen L15, Muddy Water L31, Ice Beam L36, Amnesia L36 |  |
| Hoppip | Gust L1, Protect L24, Seed Bomb L42, Cotton Guard L45 | Tackle L8→L1, Synthesis L4→L3, Tail Whip L6→L5, Fairy Wind L10→L9, Poisonpowder L12→L10, Bullet Seed L23→L12, Cotton Spore L31→L24, U-turn L38→L26, Giga Drain L33→L30 |
| Skiploom | Gust L1, Protect L24, Seed Bomb L42, Cotton Guard L45 | Fairy Wind L10→L9, Poisonpowder L12→L10, Bullet Seed L26→L12, Leech Seed L23→L21, Cotton Spore L37→L24, U-turn L47→L26, Giga Drain L40→L30, Worry Seed L44→L38, Bounce L51→L48, Memento L55→L52 |
| Jumpluff | Gust L1, Encore L1, Protect L24, Seed Bomb L42, Cotton Guard L45 | Fairy Wind L10→L9, Poisonpowder L12→L10, Bullet Seed L26→L12, Leech Seed L23→L21, Cotton Spore L41→L24, Giga Drain L45→L30, Rage Powder L37→L35, Worry Seed L50→L38, Bounce L59→L48, Memento L64→L52 |
| Aipom | Pursuit L17, Low Kick L19, Dizzy Punch L28, Fake Out L38, Focus Punch L43, Beat Up L50 | Sand Attack L4→L3, Astonish L8→L6, Fury Swipes L15→L8, Tickle L18→L14, Swift L22→L20, Fling L36→L35 |
| Sunkern | Bullet Seed L24, Petal Dance L30, Earth Power L46 | Grass Whistle L7→L6, Mega Drain L10→L9, Leech Seed L13→L11, Razor Leaf L16→L14, Worry Seed L25→L16, Synthesis L34→L25, Solarbeam L43→L36, Sunny Day L40→L37 |
| Sunflora | Agility L1, Earth Power L46 | Grass Whistle L7→L6, Mega Drain L10→L9, Leech Seed L13→L11, Razor Leaf L16→L14, Worry Seed L25→L16, Solarbeam L43→L36, Sunny Day L40→L37 |
| Yanma | Leech Life L1, Twister L12, Signal Beam L24, Twineedle L25, Air Cutter L26, Acrobatics L49 | Quick Attack L6→L4, Double Team L12→L7, Sonic Boom L15→L10, Wing Attack L30→L15, U-turn L57→L35, Air Slash L53→L38, Bug Buzz L63→L43 |
| Wooper | Mud-Slap L5, Headbutt L10, Bubble Beam L14, Magnitude L20, Body Slam L25 | Mud Shot L8→L7, Mud Bomb L24→L17, Amnesia L36→L19 |
| Quagsire | Recover L1, Mud-Slap L5, Headbutt L10, Bubble Beam L14, Magnitude L20, Body Slam L25 | Mud Bomb L28→L17, Amnesia L46→L19, Aqua Tail L34→L31, Earthquake L56→L33 |
| Espeon | Jump Kick L1, Telekinesis L12, Double Kick L14, Miracle Eye L25, Stored Power L45, Calm Mind L48, Reflect L52, Tri Attack L52 | Sand Attack L5→L4, Quick Attack L10→L6, Power Swap L35→L22, Psychic L40→L36 |
| Umbreon | Curse L1, Sucker Punch L1, Jump Kick L1, Torment L12, Double Kick L14, Snarl L20 | Sand Attack L5→L4, Quick Attack L10→L6, Guard Swap L35→L22 |
| Murkrow | Beat Up L1, Drill Peck L33, Sky Attack L53, Torment L57 | Quash L66→L1, Haze L11→L9, Wing Attack L15→L13, Night Shade L21→L17, Assurance L39→L21, Taunt L30→L25, Mean Look L44→L37, Foul Play L57→L41, Tailwind L53→L45 |
| Slowking | Heal Block L1, Psybeam L25, Brine L35, Future Sight L50 | Confusion L12→L11, Headbutt L21→L18 |
| Misdreavus | Night Shade L4, Ominous Wind L17, Trick L19, Icy Wind L22, Screech L24, Sing L24, Extrasensory L32, Wonder Room L40 | Spite L5→L1, Astonish L10→L4, Confuse Ray L14→L8, Mean Look L19→L10, Psybeam L28→L14, Shadow Ball L41→L27, Pain Split L32→L29, Grudge L50→L35, Perish Song L55→L43 |
| Unown | Ancientpower L1 |  |
| Girafarig | Bite L8, Work Up L29, Tri Attack L40, Body Slam L42, Skill Swap L48 | Odor Sleuth L5→L4, Psybeam L19→L15, Double Hit L28→L24, Zen Headbutt L32→L27, Crunch L37→L32, Baton Pass L41→L33, Psychic L50→L38, Nasty Plot L46→L44 |
| Pineco | Harden L1, Pin Missile L7, Mega Drain L15, Steamroller L32 | Rapid Spin L12→L4, Bug Bite L9→L7, Bide L17→L14, Spikes L28→L27, Payback L31→L30 |
| Forretress | Harden L1, Pin Missile L1, Mega Drain L15, Steamroller L32, Spike Cannon L33 | Rapid Spin L12→L1, Bide L17→L14, Spikes L28→L27, Payback L32→L30, Explosion L68→L36, Double-Edge L50→L46 |
| Dunsparce | Tackle L1, Headbutt L10, Endure L37 | Rollout L16→L1, Spite L10→L4, Pursuit L7→L6, Screech L19→L12, Yawn L28→L14, Dig L34→L15, Take Down L37→L20, Roost L40→L22, Coil L49→L34, Endeavor L55→L44 |
| Gligar | Sand Tomb L10, Mud-Slap L16, Wing Attack L18, Air Cutter L24 | Sand Attack L4→L1, Harden L7→L3, Quick Attack L13→L6, Fury Cutter L16→L14, Screech L38→L24, Earthquake L57→L36, Sky Uppercut L47→L38 |
| Steelix | Rock Throw L4, Rage L6, Bulldoze L18 | Rock Slide L20→L1, Slam L36→L13, Stealth Rock L32→L15, Dig L44→L18, Iron Tail L48→L40, Stone Edge L52→L43, Earthquake L60→L45, Double-Edge L56→L46 |
| Snubbull | Double Slap L14, Covet L24, Heal Bell L31, Take Down L32, Super Fang L34, Thrash L44, Double-Edge L47 | Roar L33→L16, Crunch L43→L39 |
| Granbull | Double Slap L14, Covet L24, Heal Bell L31, Take Down L32, Super Fang L34, Thrash L44, Double-Edge L47 | Roar L37→L16, Play Rough L55→L38, Crunch L49→L39 |
| Qwilfish | Poison Tail L16, Sludge L20, Bubblebeam L30, Protect L32, Sludge Bomb L45 | Minimize L15→L5, Water Gun L7→L6, Revenge L29→L21, Pin Missile L33→L26, Poison Jab L40→L31, Toxic L55→L36, Aqua Tail L51→L36 |
| Scizor | Razor Wind L1, Pursuit L8, Cut L15, Double Team L24, Steel Wing L35, Twineedle L42 |  |
| Shuckle | Acid L1, Knock Off L1, Stealth Rock L1, Infestation L12, Defense Curl L18, Sandstorm L24, Acid Armor L31, Protect L35 | Shell Smash L59→L1, Rock Throw L15→L3, Gastro Acid L42→L6, Safeguard L20→L15, Rock Slide L37→L30, Stone Edge L54→L45 |
| Heracross | Spike Cannon L1, Struggle Bug L1, Work Up L6, Twineedle L34, Cross Chop L38 | Pin Missile L34→L5, Reversal L52→L41, Megahorn L61→L45 |
| Sneasel | Pursuit L4, Knock Off L12, Assurance L15, Ice Punch L33, Night Slash L39, Icicle Crash L48, Blizzard L50 | Quick Attack L10→L6, Icy Wind L18→L9, Fury Swipes L22→L13, Agility L38→L18, Slash L42→L22, Ice Shard L34→L23, Screech L48→L30 |
| Teddiursa | Metal Claw L15, Headbutt L24, Captivate L28, Submission L44, Yawn L53 | Fury Swipes L12→L6, Sweet Scent L20→L11, Rest L36→L29, Snore L36→L34, Thrash L52→L42 |
| Ursaring | Submission L1, Metal Claw L15, Circle Throw L24, Focus Energy L28, Yawn L53, Giga Impact L57 | Sweet Scent L20→L11, Rest L40→L29, Slash L34→L33, Snore L40→L34, Thrash L64→L42, Play Rough L52→L50 |
| Slugma | Flame Wheel L21, Rock Blast L27, Power Gem L39, Fire Blast L48 | Harden L13→L1, Rock Throw L8→L7, Incinerate L15→L14, Clear Smog L18→L17, Ancient Power L21→L20, Amnesia L36→L22, Body Slam L39→L28, Flamethrower L42→L34, Earth Power L48→L45 |
| Magcargo | Inferno L1, Flame Wheel L21, Rock Blast L27, Fire Blast L48, Earthquake L50 | Harden L13→L1, Incinerate L15→L14, Clear Smog L18→L17, Ancient Power L21→L20, Body Slam L42→L28, Flamethrower L46→L34, Lava Plume L35→L34 |
| Swinub | Ice Fang L30, Dig L35, Icicle Crash L44 | Powder Snow L8→L6, Endure L29→L12, Ice Shard L25→L19, Take Down L43→L26, Earthquake L48→L39 |
| Piloswine | Mud Shot L22, Dig L35, Icicle Crash L44 | Endure L29→L12, Ice Shard L25→L19, Take Down L46→L26, Earthquake L52→L39, Thrash L64→L40, Blizzard L58→L50 |
| Corsola | Bubble L1, Growth L1, Rock Throw L9, Spikes L22, Hydro Pump L43 | Refresh L13→L7, Lucky Chant L23→L12, Bubble Beam L25→L14, Ancientpower L20→L18, Brine L32→L26, Power Gem L40→L31 |
| Remoraid | Swift L5, Simple Beam L28, Seed Bomb L30, Scald L36, Sludge Bomb L41 | Lock-On L24→L1, Psybeam L12→L8, Bubble Beam L20→L11, Bullet Seed L28→L14, Ice Beam L36→L33 |
| Octillery | Zap Cannon L1, Seed Bomb L30, Scald L36, Sludge Bomb L41, Egg Bomb L53 | Lock-On L24→L1, Bubble Beam L20→L11, Bullet Seed L30→L14, Ice Beam L42→L33, Signal Beam L36→L33, Hydro Pump L48→L44, Hyper Beam L60→L48, Soak L54→L50 |
| Mantine | Gust L1, Scald L33, Mirror Coat L45, Hurricane L52 | Headbutt L28→L7, Take Down L44→L24, Air Slash L32→L28, Hydro Pump L48→L45 |
| Skarmory | Whirlwind L1, Swift L12, Air Cutter L14, Feint L17, Iron Head L50, Defog L55 | Metal Claw L12→L9, Spikes L44→L17, Metal Sound L40→L19, Steel Wing L28→L26, Night Slash L52→L43 |
| Houndour | Torment L20, Flame Wheel L22, Snarl L23, Flame Burst L26, Feint Attack L29, Dark Pulse L41, Destiny Bond L56 | Roar L22→L7, Bite L19→L12, Embargo L36→L31, Flamethrower L39→L38, Nasty Plot L47→L45, Inferno L54→L52 |
| Houndoom | Beat Up L1, Torment L20, Flame Wheel L22, Snarl L23, Flame Burst L26, Feint Attack L29, Dark Pulse L41, Destiny Bond L56 | Roar L22→L1, Bite L19→L1, Embargo L40→L31, Flamethrower L44→L38 |
| Kingdra | Aurora Beam L24, Flail L38, Body Slam L47, Outrage L56 | Bubblebeam L25→L22, Agility L29→L26, Hydro Pump L59→L43, Dragon Dance L65→L50 |
| Phanpy | Mud-Slap L5, Mud Sport L7, Magnitude L14, Knock Off L36, Curse L52 | Natural Gift L26→L12, Endure L30→L19, Earthquake L46→L40 |
| Donphan | Mud-Slap L1, Body Slam L30, Superpower L44, Curse L52 | Assurance L27→L12, Magnitude L41→L14, Endure L32→L19, Earthquake L46→L40 |
| Porygon2 | Curse L1, Imprison L1, Swift L10, Electroweb L18, Psyshock L44 | Psybeam L20→L4, Agility L32→L7, Recover L35→L14, Signal Beam L29→L24, Discharge L40→L31, Tri Attack L45→L38, Lock-On L55→L41, Hyper Beam L65→L50 |
| Stantler | Pursuit L17, Captivate L20, Reflect L33, Light Screen L33, Rock Climb L35, Dream Eater L45, Imprison L46 | Role Play L42→L1, Astonish L7→L6, Hypnosis L17→L9, Stomp L13→L12, Confuse Ray L24→L18, Zen Headbutt L32→L31, Double-Edge L46→L40, Jump Kick L51→L41 |
| Hitmontop | Foresight L1, Low Kick L9, Low Sweep L15, Seismic Toss L22, Storm Throw L28, Dynamic Punch L36, Iron Tail L51 | Dig L34→L29 |
| Smoochum | Double Slap L13, Icy Wind L16, Psybeam L22, Frost Breath L28, Ice Beam L41, Nasty Plot L46 | Powder Snow L4→L1, Sweet Kiss L41→L7, Heart Stamp L23→L10 |
| Elekid | Spark L17, Work Up L21, Mega Punch L32, Cross Chop L48 | Thundershock L4→L1, Low Kick L37→L6, Shock Wave L15→L9, Thunder Wave L19→L16, Electro Ball L29→L19 |
| Magby | Fire Spin L9, Work Up L21, Poison Gas L25, Will-O-Wisp L28, Mega Punch L32, Dark Pulse L48 | Ember L4→L1, Smokescreen L8→L6, Flame Burst L30→L19, Fire Punch L34→L25 |
| Miltank | Block L1, Iron Head L1, Helping Hand L1, Work Up L1, Refresh L1, Mega Punch L22, Flail L45, Last Resort L60 | Defense Curl L8→L4, Stomp L12→L7, Wake-Up Slap L36→L29, Play Rough L51→L50, Double-Edge L61→L55 |
| Raikou | Thunderbolt L31, Mind Reader L74 | Roar L24→L1, Thunder Fang L30→L18, Reflect L60→L24, Crunch L42→L41, Rain Dance L66→L54, Thunder L72→L60 |
| Entei | Curse L11, Light Screen L24, Flamethrower L31, Flare Blitz L60 | Roar L24→L1, Fire Fang L30→L18, Crunch L42→L41, Sunny Day L66→L54, Fire Blast L72→L61 |
| Suicune | Air Slash L1, Whirlpool L1, Aqua Ring L1, Ice Beam L31, Reflect L41, Light Screen L51 | Surf L54→L36, Hydro Pump L72→L61 |
| Larvitar | Smack Down L13, Payback L21, Dragon Claw L56 | Screech L17→L9, Thrash L38→L26 |
| Pupitar | Smack Down L13, Payback L21, Dragon Claw L56 | Thrash L43→L26, Stone Edge L47→L43, Earthquake L51→L47 |
| Tyranitar | Smack Down L13, Payback L21, Dragon Claw L56 | Thrash L43→L26, Stone Edge L47→L43, Earthquake L53→L47 |
| Lugia | Aqua Tail L1, Defog L1, Whirlpool L10, Natural Gift L15, Tailwind L75 | Safeguard L18→L5, Extrasensory L36→L20, Recover L45→L22, Hydro Pump L72→L35, Aeroblast L54→L40, Future Sight L81→L60, Psycho Boost L90→L66, Sky Attack L90→L70 |
| Ho-Oh | Heat Wave L1, Defog L1, Feather Dance L1, Fire Spin L10, Natural Gift L15, Tailwind L75 | Safeguard L18→L5, Extrasensory L36→L20, Recover L45→L22, Fire Blast L72→L25, Sacred Fire L54→L40, Sky Attack L90→L60, Future Sight L81→L70 |
| Celebi | Natural Gift L1, Helping Hand L1, Mega Drain L20, Zen Headbutt L25, Psybeam L30, Giga Drain L35, Psychic L40, Nasty Plot L60, Earth Power L65 | Heal Block L72→L1, Safeguard L32→L5, Ancient Power L24→L15, Healing Wish L80→L30, Future Sight L64→L45, Perish Song L96→L50, Leaf Storm L88→L55 |
| Igglybuff | Fairy Wind L7, Double Slap L14, Round L14, Perish Song L25 | Defense Curl L4→L3 |
| Treecko | Absorb L5, Pursuit L10, False Swipe L13, Astonish L16, Growth L18, Dragon Breath L21, Agility L26, Chip Away L29, Fling L41, Solar Beam L46 | Endeavor L40→L36 |
| Grovyle | Pursuit L10, Razor Leaf L15, Growth L18, Dragon Breath L21, Leaf Tornado L24, Focus Energy L26, Slash L29, Dual Chop L36, Extreme Speed L41, Dragon Pulse L54 | X-Scissor L44→L41, Leaf Storm L58→L46 |
| Sceptile | Extreme Speed L1, Fake Out L5, Vine Whip L10, Pursuit L10, Razor Leaf L15, Astonish L16, Growth L18, Dragon Breath L21, Leaf Tornado L24, Focus Energy L26, Slash L29, Dragon Claw L48, Solar Beam L51, Dragon Pulse L54 |  |
| Torchic | Sand Attack L10, Flame Burst L31, Overheat L48 | Peck L9→L6, Mirror Move L39→L28 |
| Combusken | Sand Attack L10, Fire Punch L23, Rolling Kick L25, Mach Punch L32, Overheat L48, High Jump Kick L51, Brave Bird L55 | Peck L9→L7, Mirror Move L53→L28, Sky Uppercut L48→L38 |
| Blaziken | Mach Punch L1, Thunder Punch L1, Sand Attack L10, Rolling Kick L25, Overheat L48 | Peck L9→L1, Sky Uppercut L52→L38 |
| Mudkip | Foresight L10, Mud Shot L13, Bubble Beam L16, Mud Sport L18, Mud Bomb L23, Whirlpool L28, Aqua Tail L38, Double-Edge L43 |  |
| Marshtomp | Foresight L10, Bubble Beam L16, Mud Sport L18, Dive L28, Earthquake L43 | Mud Bomb L44→L23, Take Down L30→L26, Endeavor L53→L46, Hydro Pump L58→L50 |
| Swampert | Earth Power L1, Foresight L10, Bubble Beam L16, Mud Sport L18, Dive L28 | Mud Shot L15→L13, Take Down L30→L26, Muddy Water L41→L36, Earthquake L47→L43, Endeavor L58→L46, Hydro Pump L64→L50 |
| Poochyena | Pursuit L8, Thief L15, Super Fang L39, Double-Edge L43, Torment L46 | Odor Sleuth L9→L1, Bite L22→L10, Roar L19→L12, Embargo L37→L22, Take Down L29→L27, Crunch L40→L34, Taunt L44→L36 |
| Mightyena | Pursuit L18, Super Fang L39, Double-Edge L43, Torment L46 | Roar L20→L12, Embargo L43→L22, Take Down L33→L27, Crunch L47→L34, Taunt L52→L36 |
| Zigzagoon | Fury Swipes L18, Slash L31, Play Rough L42 | Tail Whip L6→L4, Fling L33→L24, Flail L36→L26, Belly Drum L39→L35, Double-Edge L42→L38 |
| Linoone | Pursuit L20, Night Slash L46 | Fury Swipes L27→L18, Fling L41→L24, Belly Drum L51→L35, Double-Edge L55→L38 |
| Silcoon | Tackle L1, String Shot L1, Poison Sting L5 |  |
| Beautifly | Leech Life L10, Sleep Powder L12, Signal Beam L43, Hurricane L43, Beat Up L45, Defog L47 | Stun Spore L15→L12, Morning Sun L21→L16, Air Cutter L24→L18, Mega Drain L27→L22, Silver Wind L30→L25, Whirlwind L36→L26, Attract L33→L27, Air Slash L45→L30, Giga Drain L39→L32, Bug Buzz L42→L35, Quiver Dance L48→L40 |
| Cascoon | Tackle L1, Poison Sting L1, String Shot L1 |  |
| Dustox | Leech Life L10, Silver Wind L17, Hypnosis L20, Reflect L27, Sludge Bomb L30, Toxic L32, Synchronoise L43, Imprison L45, Sticky Web L47, Psychic L48 | Poison Powder L15→L12, Moonlight L21→L16, Venoshock L24→L18, Psybeam L27→L22, Light Screen L33→L27, Bug Buzz L42→L35, Quiver Dance L48→L40 |
| Lotad | Natural Gift L11, Seed Bomb L30, Worry Seed L32, Tickle L42, Hydro Pump L49 | Bubble L6→L1, Nature Power L24→L12, Bubble Beam L20→L17, Rain Dance L33→L27 |
| Lombre | Soak L32, Tickle L42 | Fury Swipes L18→L11, Bubble Beam L24→L17, Rain Dance L48→L27, Uproar L42→L30 |
| Ludicolo | Water Gun L1, Natural Gift L11, Water Pulse L18, Petal Dance L26, Soak L32 | Hydro Pump L66→L49 |
| Seedot | Bullet Seed L8, Leech Seed L14, Headbutt L17, Seed Bomb L30, Self-Destruct L36, Worry Seed L39, Torment L42, Solar Beam L44 | Nature Power L21→L11, Synthesis L27→L19 |
| Nuzleaf | Knock Off L18, Leaf Tornado L23, Leaf Storm L44 | Razor Wind L20→L1, Sunny Day L36→L27, Leaf Blade L57→L36, Extrasensory L43→L39 |
| Shiftry | Assurance L1, Defog L11, Knock Off L18, Tailwind L32 | Leaf Blade L57→L36 |
| Taillow | Chip Away L22, Whirlwind L23, Tailwind L28, Hyper Voice L39 | Double Team L16→L15, Aerial Ace L27→L18, Air Slash L34→L32, Brave Bird L50→L48 |
| Swellow | Sky Attack L1, Chip Away L22, Whirlwind L23, Tailwind L28, Hyper Voice L39 | Double Team L16→L15, Aerial Ace L32→L18, Brave Bird L61→L48 |
| Wingull | Hydro Pump L42, Tailwind L44, Defog L47 | Supersonic L10→L5, Wing Attack L13→L8, Mist L40→L11, Water Pulse L17→L15, Pursuit L29→L27 |
| Pelipper | Feather Dance L25, Rain Dance L32 | Mist L41→L11, Water Pulse L17→L15, Stockpile L28→L25, Swallow L28→L25, Spit Up L28→L25, Hydro Pump L59→L47, Hurricane L53→L51 |
| Kirlia | Fairy Wind L1, Wish L42, Moonblast L58 | Magical Leaf L17→L1, Charm L28→L16, Imprison L38→L32, Dream Eater L53→L49 |
| Gardevoir | Fairy Wind L1, Captivate L23 | Magical Leaf L17→L1, Imprison L42→L32, Psychic L48→L36, Dream Eater L63→L49 |
| Surskit | Leech Life L5, Infestation L14, Hydro Pump L37 | Bubble Beam L17→L16, Aqua Jet L30→L26, Baton Pass L35→L33 |
| Masquerain | Leech Life L1, Icy Wind L32, Hydro Pump L42, Signal Beam L47 | Gust L17→L14, Silver Wind L32→L27, Air Slash L38→L36 |
| Shroomish | Synthesis L31 | Mega Drain L12→L11, Poison Powder L19→L18, Growth L29→L21, Toxic L33→L29, Seed Bomb L36→L34 |
| Breloom | Brick Break L29 | Bullet Seed L33→L11, Feint L19→L18, Counter L22→L21, Force Palm L28→L26, Mind Reader L56→L33, Seed Bomb L44→L37, Dynamic Punch L56→L49 |
| Slakoth | Fury Swipes L12, Mega Punch L31, Block L34, Knock Off L38 | Encore L6→L5, Slack Off L9→L8, Amnesia L22→L17, Chip Away L25→L24, Counter L30→L27 |
| Vigoroth | Vital Throw L15, Mega Punch L31, Retaliate L38 | Fury Swipes L14→L12, Counter L33→L27 |
| Nincada | Silver Wind L28, X-Scissor L30 | Mud-Slap L15→L8, Fury Swipes L30→L11, Mind Reader L35→L15, Metal Claw L25→L18, Dig L39→L22 |
| Ninjask | Gust L8, Silver Wind L28, U-turn L28, Air Cutter L34, Acrobatics L34, Night Slash L46, Quick Guard L50 | Fury Swipes L36→L9, Mind Reader L43→L15, Slash L50→L25, X-Scissor L57→L42 |
| Shedinja | Astonish L8, Gust L12, Silver Wind L23, X-Scissor L35, Faint Attack L38, Bug Buzz L44 | Leech Life L10→L1, Fury Swipes L36→L9, Mind Reader L43→L15, Spite L57→L18, Shadow Sneak L29→L21, Shadow Ball L50→L29, Heal Block L71→L32 |
| Whismur | Work Up L22, Flail L29, Boomburst L44, Endeavor L49 | Echoed Voice L5→L4, Howl L10→L6, Supersonic L30→L11, Stomp L21→L18, Hyper Voice L40→L29, Synchronoise L50→L39 |
| Loudred | Work Up L22, Crunch L35, Boomburst L44, Outrage L49, Hyper Beam L50 | Supersonic L35→L11, Stomp L23→L18, Roar L29→L26, Hyper Voice L47→L29, Screech L53→L30, Synchronoise L59→L39 |
| Exploud | Work Up L22, Outrage L49 | Supersonic L35→L11, Stomp L23→L18, Roar L29→L26, Hyper Voice L50→L29, Screech L57→L30, Synchronoise L64→L39, Hyper Beam L78→L55 |
| Makuhita | Wake-Up Slap L24, Brick Break L30, Body Slam L32, Fling L35, Superpower L38 | Seismic Toss L29→L1, Sand Attack L4→L3, Arm Thrust L7→L5, Fake Out L10→L8, Force Palm L13→L12, Whirlwind L27→L14, Smelling Salts L24→L20, Heavy Slam L46→L41 |
| Hariyama | Bulk Up L1, Wake-Up Slap L24, Brick Break L30, Body Slam L32, Fling L35, Superpower L38, Focus Punch L51 | Seismic Toss L31→L1, Close Combat L57→L1, Fake Out L10→L8, Force Palm L13→L12, Whirlwind L28→L14, Smelling Salts L24→L20, Heavy Slam L52→L41, Reversal L47→L43 |
| Nosepass | Headbutt L11, Shock Wave L17, Ancient Power L20, Smelling Salts L26, Iron Defense L34, Tri Attack L39, Thunderbolt L40, Sleep Talk L45 | Harden L4→L1, Block L7→L5, Rock Throw L10→L9, Rock Slide L31→L28, Sandstorm L34→L33 |
| Skitty | Fury Swipes L9, Take Down L23, Encore L32, Hyper Voice L34, Moonblast L42, Mimic L43, Wish L47 | Attract L10→L3, Copycat L19→L6, Double Slap L16→L11, Covet L34→L11, Assist L31→L16, Wake-Up Slap L28→L20, Charm L25→L23, Play Rough L46→L30 |
| Delcatty | Helping Hand L1, Follow Me L1, Fury Swipes L9, Take Down L19, Encore L32, Hyper Voice L34, Moonblast L42, Mimic L43, Wish L47 | Play Rough L46→L30 |
| Sableye | Taunt L9, Bite L12, Shadow Punch L24, Crunch L27, Pain Split L31, Parting Shot L41, Sucker Punch L45 | Punishment L38→L1, Quash L30→L1, Fury Swipes L24→L5, Detect L19→L17, Knock Off L27→L21, Shadow Claw L33→L24, Shadow Ball L45→L36 |
| Mawile | Double Slap L12, Metal Claw L20, Faint Attack L24, Covet L31, Meteor Mash L45, Metal Burst L47, Swords Dance L53 | Swallow L19→L1, Spit Up L19→L1, Sweet Scent L22→L1, Fake Tears L44→L3, Bite L15→L6, Iron Defense L29→L27 |
| Aron | Rock Throw L9, Rock Blast L23, Submission L42, Earthquake L51, Head Smash L56 | Headbutt L15→L7, Iron Defense L44→L15, Take Down L33→L21, Metal Sound L30→L25, Double-Edge L51→L41 |
| Lairon | Rock Throw L9, Rock Blast L23, Submission L42, Earthquake L51, Head Smash L56 | Iron Defense L49→L15, Take Down L35→L21, Metal Sound L30→L25, Iron Tail L44→L37, Double-Edge L58→L41, Heavy Slam L53→L47, Metal Burst L63→L60 |
| Aggron | Submission L1, Rock Throw L9, Rock Blast L23, Earthquake L51, Head Smash L56 | Iron Defense L52→L15, Take Down L35→L21, Metal Sound L30→L25, Iron Tail L46→L37, Double-Edge L63→L41, Heavy Slam L57→L47, Metal Burst L69→L60 |
| Meditite | Karate Chop L13, Jump Kick L22, Rolling Kick L23, Extrasensory L29, Zen Headbutt L44 | Detect L12→L1, Endure L37→L10, Force Palm L16→L12, Psych Up L34→L20, Calm Mind L27→L26, Reversal L40→L38 |
| Medicham | Karate Chop L14, Jump Kick L22, Rolling Kick L23, Extrasensory L29 | Endure L37→L10, Force Palm L16→L12, Psych Up L34→L20, Calm Mind L27→L26, Reversal L42→L38, Power Trick L47→L46, Recover L51→L48 |
| Electrike | Thunder Shock L7, Snarl L32, Thunderbolt L36, Crunch L40, Rain Dance L46 | Roar L27→L1, Shock Wave L23→L17, Thunder Fang L30→L26, Charge L38→L31 |
| Manectric | Thunder Shock L1, Flamethrower L1, Snarl L32, Thunderbolt L36, Crunch L40, Rain Dance L46 | Roar L28→L1, Shock Wave L23→L17, Thunder Fang L33→L26, Charge L43→L31, Discharge L38→L35, Wild Charge L47→L43, Thunder L52→L50 |
| Plusle | Thunder Shock L1, Quick Guard L1, Fake Tears L21, Thunderbolt L28, Fake Out L30, Extreme Speed L37, Volt Tackle L48 | Swift L16→L14, Discharge L31→L26, Agility L40→L33 |
| Minun | Thunder Shock L1, Wide Guard L1, Shock Wave L10, Follow Me L16, Charm L25, Thunderbolt L28, Trick L34, Wish L37, Volt Tackle L48 | Charge L28→L1, Swift L16→L14, Discharge L34→L26, Agility L40→L33 |
| Volbeat | Captivate L1, Leech Life L10, Silver Wind L23, Baton Pass L29, U-turn L35, Bug Buzz L40, Light Screen L41, Moonblast L45 | Struggle Bug L18→L12, Tail Glow L25→L19, Signal Beam L28→L24, Protect L32→L26, Helping Hand L39→L32, Zen Headbutt L35→L32 |
| Illumise | Leech Life L10, Follow Me L16, Silver Wind L23, Signal Beam L24, Extrasensory L32, U-turn L35, Reflect L41, Moonblast L45 | Flatter L32→L1, Charm L8→L6, Struggle Bug L18→L12, Wish L25→L19, Helping Hand L39→L32, Bug Buzz L42→L40 |
| Roselia | Venoshock L25, Sludge L27, Solar Beam L50 | Sweet Scent L25→L1, Aromatherapy L50→L22, Ingrain L55→L33, Toxic L40→L37, Petal Dance L60→L40 |
| Gulpin | Body Slam L26, Recover L38 | Yawn L7→L4, Encore L17→L16, Gastro Acid L36→L18, Toxic L25→L24, Gunk Shot L49→L43 |
| Swalot | Recover L38 | Encore L17→L16, Gastro Acid L42→L18, Toxic L25→L24, Sludge Bomb L36→L34 |
| Carvanha | Water Pulse L18, Dive L28, Slash L30, Taunt L34, Skull Bash L42, Hydro Pump L46 | Focus Energy L8→L7 |
| Sharpedo | Water Pulse L18, Dive L28, Hydro Pump L46 | Skull Bash L60→L41 |
| Wailmer | Tackle L1, Yawn L21, Curse L45, Wide Guard L51 | Water Gun L12→L5, Rollout L15→L8, Whirlpool L27→L11, Mist L18→L16, Water Pulse L21→L19, Rest L42→L24, Brine L30→L26, Body Slam L39→L29, Water Spout L51→L32 |
| Wailord | Double-Edge L1, Tackle L1, Yawn L21, Curse L45, Wide Guard L51 | Whirlpool L27→L11, Mist L18→L16, Water Pulse L21→L19, Rest L44→L24, Brine L30→L26, Body Slam L39→L29, Water Spout L59→L32, Amnesia L49→L46, Hydro Pump L54→L48 |
| Numel | Mud-Slap L1, Flame Wheel L17, Rock Slide L32, Eruption L45, Fissure L55 | Ember L5→L4, Focus Energy L8→L7, Flame Burst L22→L14, Take Down L29→L20, Flamethrower L43→L36, Double-Edge L47→L46 |
| Camerupt | Mud-Slap L1, Heat Wave L1, Flame Wheel L17 | Flame Burst L22→L14, Take Down L29→L20, Earthquake L46→L40 |
| Torkoal | Yawn L18, Sunny Day L24, Slack Off L33, Heat Crash L46, Overheat L50 | Withdraw L4→L1, Smokescreen L12→L1, Rapid Spin L8→L1, Fire Spin L10→L6, Clear Smog L15→L14, Flame Wheel L19→L17, Body Slam L26→L25, Lava Plume L30→L29, Heat Wave L52→L30, Amnesia L56→L37 |
| Spoink | Tackle L1, Confusion L8, Extrasensory L21, Barrier L23, Payback L26, Sleep Talk L32, Yawn L42, Skill Swap L48 | Psych Up L17→L10, Psybeam L21→L13, Confuse Ray L25→L15, Magic Coat L33→L18, Rest L45→L32 |
| Grumpig | Headbutt L1, Tackle L1, Slack Off L1, Confusion L8, Extrasensory L21, Barrier L23, Payback L26, Sleep Talk L32, Yawn L42, Skill Swap L48 | Snore L49→L1, Psych Up L17→L10, Confuse Ray L25→L15, Magic Coat L34→L18, Rest L49→L32, Psychic L39→L36 |
| Spinda | Petal Dance L1, Superpower L1, Role Play L1, Assist L1, Rapid Spin L1, Play Rough L33, Outrage L39, Dynamic Punch L45 | Copycat L5→L4, Psybeam L14→L13, Hypnosis L19→L16, Dizzy Punch L23→L20, Sucker Punch L28→L23, Teeter Dance L32→L25, Psych Up L41→L27, Thrash L55→L30, Flail L50→L36, Double-Edge L46→L42 |
| Trapinch | Hyper Fang L33, Magnitude L38, Block L39, Screech L43, Bug Bite L43 | Mud-Slap L7→L4, Sand Tomb L15→L12, Sandstorm L43→L15, Bulldoze L23→L18, Dig L31→L21, Rock Slide L27→L22, Crunch L35→L25, Earth Power L39→L36 |
| Vibrava | Signal Beam L33, Dragon Dance L39 | Supersonic L4→L1, Sandstorm L55→L15, Bulldoze L23→L18, Uproar L45→L20, Rock Slide L27→L22, Earth Power L40→L36, Earthquake L50→L47, Boomburst L64→L59 |
| Flygon | Signal Beam L33 | Sandstorm L58→L1, Supersonic L4→L1, Bulldoze L23→L18, Rock Slide L27→L22, Dragon Breath L34→L30, Earth Power L40→L36, Earthquake L52→L47, Boomburst L69→L59 |
| Cacnea | Pursuit L7, Seed Bomb L24, Giga Drain L34, Dark Pulse L37 | Absorb L4→L1, Growth L13→L4, Needle Arm L16→L14, Ingrain L22→L21, Sucker Punch L35→L27, Spikes L32→L28, Cotton Spore L44→L39, Sandstorm L48→L47, Destiny Bond L76→L48 |
| Cacturne | Spike Cannon L1, Pursuit L7, Seed Bomb L24, Giga Drain L34, Dark Pulse L37 | Needle Arm L16→L14, Ingrain L22→L21, Sucker Punch L36→L27, Spikes L32→L28, Cotton Spore L48→L39, Sandstorm L54→L45, Destiny Bond L76→L48 |
| Swablu | Air Cutter L13, Pluck L23, Feather Dance L28, Heal Bell L29, Sky Attack L45 | Astonish L3→L1, Sing L31→L3, Fury Attack L12→L5, Safeguard L24→L7, Refresh L41→L11, Take Down L27→L19, Hyper Voice L47→L33, Perish Song L55→L46 |
| Altaria | Dragon Rush L1, Air Cutter L13, Feather Dance L28, Heal Bell L29, Dragon Claw L42 | Fury Attack L12→L5, Safeguard L24→L7, Refresh L43→L11, Take Down L27→L19, Hyper Voice L51→L33, Perish Song L61→L46, Sky Attack L65→L49, Moonblast L56→L54 |
| Zangoose | Metal Claw L24, Feint Attack L34, Double-Edge L40 | False Swipe L30→L1, Pursuit L12→L11, Hone Claws L19→L15, Revenge L26→L22, Swords Dance L55→L32, Detect L45→L41 |
| Seviper | Poison Sting L1, Revenge L25, Super Fang L32, Gunk Shot L40, Iron Tail L43, Sucker Punch L48 | Lick L6→L3, Haze L42→L5, Poison Fang L19→L10, Screech L16→L12, Venom Drench L28→L15, Glare L22→L17, Coil L61→L23, Night Slash L35→L27, Poison Jab L46→L30, Crunch L57→L37, Wring Out L64→L46 |
| Lunatone | Icy Wind L12, Psybeam L19, Calm Mind L21, Ancient Power L28, Baton Pass L43, Ice Beam L46 | Psywave L13→L1, Heal Block L33→L30 |
| Solrock | Will-O-Wisp L9, Flame Charge L12, Rock Tomb L19, Curse L21, Psybeam L25, Ancient Power L29, Zen Headbutt L33, Rock Blast L38, Baton Pass L43 | Psywave L13→L1, Heal Block L33→L30 |
| Barboach | Yawn L14, Zen Headbutt L29, Earth Power L36 | Mud Sport L6→L5, Water Sport L6→L5, Magnitude L27→L13, Amnesia L20→L17, Muddy Water L35→L29, Future Sight L43→L39 |
| Whiscash | Yawn L14, Sleep Talk L26, Earth Power L36 | Magnitude L27→L13, Amnesia L20→L17, Muddy Water L39→L29, Aqua Tail L33→L32, Future Sight L51→L39, Fissure L57→L50 |
| Corphish | Assurance L15, Aqua Jet L20, Metal Claw L24 | Leer L11→L9, Bubble Beam L14→L12, Protect L30→L17, Night Slash L37→L28, Crunch L44→L39 |
| Crawdaunt | Assurance L15, Aqua Jet L20, Metal Claw L24 | Bubble Beam L14→L12, Protect L30→L17, Night Slash L39→L28, Crabhammer L53→L36, Crunch L48→L39, Swords Dance L44→L42 |
| Baltoy | Smokescreen L3, Stealth Rock L8, Mud Shot L19, Psychic L36, Zen Headbutt L41, Earthquake L42, Hyper Beam L48, Recover L53 | Psybeam L15→L11, Self-Destruct L33→L17, Sandstorm L39→L30 |
| Claydol | Gravity L1, Smokescreen L3, Stealth Rock L8, Mud Shot L19, Psychic L36, Zen Headbutt L41, Earthquake L42, Recover L53 | Psybeam L15→L11, Self-Destruct L33→L17, Sandstorm L48→L30 |
| Lileep | Rock Throw L7, Rock Blast L33, Stealth Rock L38, Recover L44, Wring Out L50 | Ingrain L12→L9, Mega Drain L20→L12, Brine L24→L20, Gastro Acid L32→L22, Giga Drain L36→L26, Stockpile L41→L30, Swallow L41→L30, Spit Up L41→L30, Energy Ball L44→L42 |
| Cradily | Rock Throw L1, Rock Blast L33, Stealth Rock L38, Recover L44 | Mega Drain L20→L12, Brine L24→L20, Gastro Acid L32→L22, Giga Drain L36→L26, Energy Ball L48→L42 |
| Anorith | Rock Throw L15, Hone Claws L25, Twineedle L36, Stone Edge L45, Swords Dance L50 | Smack Down L16→L8, Brine L24→L20, Crush Claw L32→L28, Rock Blast L36→L32 |
| Armaldo | Iron Tail L1, Rock Throw L15, Hone Claws L25, Twineedle L36, Stone Edge L45, Swords Dance L50 | Smack Down L16→L8, Brine L24→L20, Rock Blast L36→L32 |
| Milotic | Sing L1, Whirlpool L10, Dragon Breath L30, Light Screen L40, Dragon Pulse L46, Mirror Coat L50 | Attract L16→L1, Refresh L6→L4, Safeguard L40→L5, Twister L8→L7, Recover L33→L25, Coil L50→L34 |
| Castform | Water Pulse L10, Flame Wheel L10, Aurora Beam L10, Incinerate L10, Icy Wind L10, Secret Power L15, Muddy Water L30, Heat Wave L30, Freeze-Dry L30, Tri Attack L35 | Water Gun L10→L1, Ember L10→L1, Powder Snow L10→L1, Headbutt L15→L5 |
| Kecleon | Fake Out L1, Conversion L1, Swift L20, Swagger L22, Psychic L37, Double-Edge L44 | Feint L10→L7, Psybeam L18→L16, Camouflage L30→L27, Substitute L42→L30, Shadow Claw L33→L32, Sucker Punch L46→L40 |
| Shuppet | Lick L1, Astonish L14, Revenge L25, Substitute L34, Destiny Bond L56 | Screech L36→L3, Spite L11→L9, Curse L25→L17, Snatch L43→L41, Grudge L46→L44, Phantom Force L49→L48 |
| Banette | Lick L1, Play Rough L1, Astonish L14, Revenge L25, Substitute L34, Destiny Bond L50 | Snatch L46→L41, Grudge L50→L44, Phantom Force L54→L48, Trick L59→L51 |
| Duskull | Hypnosis L31, Shadow Punch L32, Pain Split L37, Snatch L37, Sucker Punch L44, Phantom Force L53 | Pursuit L14→L11, Will-O-Wisp L24→L18, Hex L32→L21, Curse L36→L28 |
| Dusclops | Hypnosis L31, Pain Split L37, Snatch L37, Sucker Punch L44, Phantom Force L53 | Pursuit L14→L11, Will-O-Wisp L24→L18, Hex L32→L21, Curse L36→L28, Shadow Ball L42→L40 |
| Tropius | Outrage L1, Air Cutter L18, Sunny Day L23, Defog L43, Dragon Pulse L46 | Sweet Scent L6→L5, Stomp L10→L9, Whirlwind L21→L11, Magical Leaf L16→L14, Air Slash L35→L32, Body Slam L40→L35, Solar Beam L58→L38, Synthesis L54→L45 |
| Chimecho | Follow Me L1, Helping Hand L1, Recover L1, Echoed Voice L6, Psyshock L20, Wish L38, Magic Room L44, Hyper Voice L47 | Psywave L12→L1, Uproar L27→L10, Heal Bell L24→L22, Heal Pulse L42→L27, Psychic L45→L38 |
| Absol | Bite L18, Air Cutter L26, Crunch L40, Air Slash L44 | Slash L25→L23, Future Sight L45→L26, Night Slash L35→L30, Psycho Cut L40→L35, Sucker Punch L55→L41, Perish Song L65→L45 |
| Snorunt | Icicle Spear L24, Ice Beam L37, Body Slam L40, Endeavor L43 | Ice Shard L10→L7, Hail L44→L13, Headbutt L25→L18, Ice Fang L28→L21, Fake Tears L35→L23, Frost Breath L41→L26, Crunch L32→L30 |
| Glalie | Ice Ball L1, Super Fang L1, Scary Face L23, Icicle Spear L24, Body Slam L40, Explosion L47, Wide Guard L49 | Hail L53→L15, Headbutt L25→L18, Ice Fang L28→L21, Frost Breath L45→L26, Crunch L33→L30, Icicle Crash L41→L37, Blizzard L57→L43, Sheer Cold L61→L51 |
| Spheal | Water Pulse L25, Frost Breath L29, Dive L33, Avalanche L40, Hydro Pump L47, Slack Off L53 | Ice Ball L12→L11, Brine L23→L15, Body Slam L34→L16, Aurora Beam L27→L18 |
| Sealeo | Water Pulse L25, Frost Breath L29, Dive L33, Avalanche L40, Hydro Pump L47, Slack Off L53 | Ice Ball L12→L11, Brine L23→L15, Body Slam L36→L16, Aurora Beam L27→L18, Blizzard L46→L43, Sheer Cold L56→L50 |
| Walrein | Icicle Spear L1, Super Fang L1, Water Pulse L25, Frost Breath L29, Dive L33, Avalanche L40, Hydro Pump L47, Slack Off L53 | Ice Ball L12→L11, Brine L23→L15, Body Slam L36→L16, Aurora Beam L27→L18, Blizzard L50→L43, Sheer Cold L64→L50 |
| Huntail | Agility L1, Take Down L21, Dragon Dance L29, Double-Edge L43 | Water Pulse L13→L9, Dive L26→L25, Coil L45→L30, Aqua Tail L39→L35, Hydro Pump L50→L47 |
| Gorebyss | Psybeam L27, Double-Edge L43 | Captivate L23→L5, Water Pulse L13→L9, Amnesia L16→L13, Dive L26→L25, Coil L45→L30, Aqua Tail L39→L35, Hydro Pump L50→L47 |
| Relicanth | Water Pulse L18, Sleep Talk L30, Rock Slide L37, Stealth Rock L46 | Yawn L17→L13, Take Down L28→L22, Rest L40→L30, Double-Edge L57→L41 |
| Luvdisc | Rain Dance L23, Dive L31, Lovely Kiss L32 | Sweet Kiss L31→L1, Agility L7→L3, Heart Stamp L22→L21, Safeguard L49→L39, Aqua Ring L40→L39 |
| Bagon | Slam L13, Twister L15, Fire Fang L24, Thrash L47 | Zen Headbutt L35→L33 |
| Shelgon | Slam L13, Twister L15, Fire Fang L24, Thrash L47 | Zen Headbutt L39→L33, Double-Edge L67→L58 |
| Salamence | Slam L13, Twister L15, Thrash L47 | Zen Headbutt L39→L33, Flamethrower L55→L53, Double-Edge L73→L61 |
| Metang | Psybeam L30, Gravity L34, Flash Cannon L37, Hammer Arm L49 | Pursuit L23→L22, Scary Face L42→L25, Iron Defense L60→L39 |
| Metagross | Thunder Punch L1, Ice Punch L1, Stealth Rock L1, Refresh L11, Psybeam L30, Gravity L34, Flash Cannon L37, Hyper Beam L60 | Pursuit L23→L22, Scary Face L42→L25, Iron Defense L66→L39, Meteor Mash L61→L50 |
| Regirock | Gravity L1, Stealth Rock L1, Rapid Spin L1, Thunder Punch L10, Rock Blast L35, Recover L65 | Iron Defense L36→L25, Hyper Beam L72→L70 |
| Regice | Gravity L1, Spikes L1, Rapid Spin L1, Shock Wave L10, Water Pulse L15, Recover L65 | Amnesia L36→L25, Blizzard L48→L45, Hyper Beam L72→L70 |
| Registeel | Gravity L1, Autotomize L1, Seismic Toss L15, Meteor Mash L45, Recover L65 | Amnesia L36→L25, Iron Defense L36→L25, Hyper Beam L72→L70 |
| Kyogre | Avalanche L1, Icy Wind L10, Rest L25, Surf L40 | Double-Edge L81→L50, Water Spout L90→L65 |
| Groudon | Iron Tail L1, Fire Punch L10, Stealth Rock L30, Flamethrower L45 | Rest L54→L25, Solar Beam L81→L50, Fire Blast L72→L60, Eruption L90→L65 |
| Rayquaza | Earth Power L1, Sky Drop L10, Dragon Claw L20, Tailwind L30, Sky Attack L75 | Rest L54→L15, Fly L63→L60 |
| Deoxys | Fire Punch L1, Thunder Punch L1, Ice Punch L1, Confusion L1, Drain Punch L30, Trick L65 | Night Shade L7→L5, Teleport L13→L10, Pursuit L25→L15, Snatch L37→L20, Zen Headbutt L49→L25, Cosmic Power L55→L35, Psycho Shift L43→L40, Hyper Beam L73→L50, Recover L61→L55, Psycho Boost L67→L60 |
| Kadabra | Power Split L44 | Recover L37→L33, Role Play L52→L38 |
| Alakazam | Power Split L44 | Recover L37→L33, Calm Mind L62→L38 |
| Magikarp | Bounce L35 |  |
| Mewtwo | Metronome L1, Zen Headbutt L1, Drain Punch L1, Psybeam L7, Submission L31 | Psych Up L29→L13, Miracle Eye L36→L19, Power Swap L43→L37, Guard Swap L43→L37, Recover L50→L49, Barrier L64→L55, Aura Sphere L70→L67, Amnesia L79→L73, Mist L86→L79, Psystrike L100→L85, Me First L93→L91 |
| Pichu | Thunder Wave L8, Bestow L18, Electro Ball L22 | Spark L24→L11 |
| Cleffa | Metronome L24 | Encore L16→L3 |
| Wobbuffet | Tickle L1 |  |
| Delibird | Celebrate L1, Powder Snow L5, Charm L10, Hail L30, Blizzard L45, Roost L50, Sky Attack L55 | Pluck L16→L15 |
| Tyrogue | Rock Smash L10 |  |
| Blissey | Wish L1, Recycle L1, Bestow L12, Heal Bell L42 | Tail Whip L4→L1, Echoed Voice L24→L10, Helping Hand L20→L14, Fling L48→L27, Healing Wish L68→L49 |
| Ralts | Fairy Wind L1, Wish L42, Moonblast L58 | Confusion L6→L5, Charm L24→L23 |
| Slaking | Sucker Punch L1, Mega Punch L31, Block L34, Knock Off L38, Double-Edge L50 | Amnesia L23→L17, Chip Away L27→L24, Counter L33→L27 |
| Azurill | Tackle L7, Double Slap L19 |  |
| Feebas | Bounce L35 | Flail L30→L25 |
| Wynaut | Tickle L30 |  |
| Beldum | Iron Defense L25, Zen Headbutt L30, Iron Head L40 |  |
| Latias | Safeguard L1, Twister L8, Trick L55 | Helping Hand L5→L1, Mist Ball L35→L25, Psycho Shift L75→L28, Zen Headbutt L40→L35, Psychic L60→L50 |
| Latios | Safeguard L1, Twister L8, Imprison L55 | Helping Hand L5→L1, Luster Purge L35→L25, Psycho Shift L75→L28, Zen Headbutt L40→L35, Psychic L60→L50 |
| Jirachi | Ice Punch L1, Thunder Punch L1, Fire Punch L1, Mirror Shot L12, Skill Swap L16, Play Rough L24, Iron Head L32, Moonblast L70 | Refresh L32→L1, Helping Hand L14→L1, Rest L75→L4, Healing Wish L82→L48 |
| Turtwig | Worry Seed L7, Headbutt L13, Seed Bomb L28, Body Slam L30, Natural Gift L45 | Withdraw L5→L1, Absorb L9→L4, Razor Leaf L13→L10, Mega Drain L24→L22 |
| Grotle | Worry Seed L7, Headbutt L13, Seed Bomb L28, Body Slam L30, Natural Gift L45 | Razor Leaf L13→L10, Bite L22→L20, Mega Drain L27→L22, Synthesis L41→L34, Crunch L50→L38, Giga Drain L45→L41, Leaf Storm L55→L50 |
| Torterra | Worry Seed L1, Bulldoze L13, Seed Bomb L28, Body Slam L30, Head Smash L45, Fissure L55, Shell Smash L60 | Bite L22→L20, Mega Drain L27→L22, Synthesis L43→L34, Crunch L54→L38, Giga Drain L48→L41, Leaf Storm L60→L50 |
| Chimchar | Feint Attack L20, Flame Burst L30, Covet L33, Endeavor L47 | Ember L7→L4, Taunt L9→L8, Fury Swipes L15→L12 |
| Monferno | Wake-Up Slap L24, Flame Burst L30, Covet L33, Endeavor L47 | Fury Swipes L16→L12, Flame Wheel L19→L17, Feint L26→L20, Torment L29→L26, Acrobatics L46→L43, Flare Blitz L56→L55 |
| Infernape | Wake-Up Slap L24, Flame Burst L30, Heat Wave L40, Focus Punch L47 | Fury Swipes L16→L12, Flame Wheel L19→L17, Feint L26→L20, Calm Mind L58→L51 |
| Piplup | Icy Wind L15, Pluck L24, Defog L33, Chip Away L38, Dive L41 | Growl L4→L1, Bubble L8→L4, Water Sport L11→L7, Peck L15→L9, Whirlpool L32→L12, Bide L22→L21, Brine L29→L27 |
| Prinplup | Icy Wind L15, Pluck L24, Steel Wing L29, Defog L33, Chip Away L38, Dive L41 | Peck L15→L9, Whirlpool L37→L12, Bide L24→L21, Brine L33→L27 |
| Empoleon | Icy Wind L15, Iron Defense L21, Pluck L24, Steel Wing L29, Defog L33, Flash Cannon L38, Dive L41, Metal Burst L56 | Swords Dance L11→L1, Peck L15→L9, Brine L33→L27, Mist L46→L43, Drill Peck L52→L47, Hydro Pump L59→L52 |
| Starly | Work Up L28, Pluck L31, Retaliate L36, Double-Edge L49 | Double Team L13→L11, Endeavor L17→L15, Whirlwind L21→L18, Aerial Ace L25→L22, Take Down L29→L26 |
| Staravia | Work Up L28, Pluck L31, Retaliate L36, Double-Edge L49 | Double Team L13→L11, Endeavor L18→L15, Whirlwind L23→L18, Aerial Ace L28→L22, Take Down L33→L26 |
| Staraptor | Work Up L28, Pluck L31, Retaliate L36, Double-Edge L49, Giga Impact L58 | Double Team L13→L11, Endeavor L18→L15, Whirlwind L23→L18, Aerial Ace L28→L22, Take Down L33→L26, Agility L41→L40, Brave Bird L49→L45, Final Gambit L57→L53 |
| Bidoof | Bide L24, Natural Gift L38, Double-Edge L49 | Amnesia L41→L28 |
| Bibarel | Water Pulse L24, Double-Edge L49 | Hyper Fang L23→L21, Take Down L38→L31, Super Fang L43→L35, Superpower L58→L42, Curse L63→L45 |
| Kricketot | Uproar L18 | Bug Bite L16→L12 |
| Kricketune | Round L10, Snarl L17, Silver Wind L19, Metal Sound L23, Hyper Voice L29, Knock Off L37, Heal Bell L39, Boomburst L42 | Focus Energy L15→L11, Fell Stinger L18→L13, Screech L26→L23, X-Scissor L29→L26, Taunt L33→L31 |
| Shinx | Howl L19, Facade L28, Discharge L40, Sucker Punch L44 | Charge L9→L7, Spark L16→L11, Roar L20→L16, Thunder Fang L33→L22, Swagger L43→L24, Crunch L36→L31, Wild Charge L40→L34 |
| Luxio | Howl L19, Facade L28, Discharge L40, Sucker Punch L44 | Charge L9→L1, Spark L18→L11, Roar L22→L16, Thunder Fang L37→L22, Swagger L49→L24, Crunch L41→L31, Wild Charge L45→L34 |
| Luxray | Ice Fang L1, Howl L19, Facade L28, Discharge L40, Sucker Punch L44 | Spark L18→L11, Roar L22→L16, Thunder Fang L39→L22, Swagger L54→L24, Crunch L44→L31, Wild Charge L49→L34, Volt Tackle L58→L52 |
| Budew | Venoshock L20 |  |
| Roserade | Venoshock L25 | Petal Dance L60→L50 |
| Cranidos | Smack Down L12, Rock Slide L32, Stealth Rock L38, Iron Head L42, Agility L49 | Focus Energy L6→L5, Pursuit L10→L9, Scary Face L19→L18, Assurance L24→L21, Ancient Power L33→L23, Chip Away L28→L26, Screech L42→L28, Zen Headbutt L37→L35 |
| Rampardos | Superpower L1, Smack Down L12, Rock Slide L32, Stealth Rock L38, Iron Head L42, Agility L49, Head Charge L54 | Scary Face L19→L18, Assurance L24→L21, Ancient Power L36→L23, Chip Away L28→L26, Screech L51→L28, Zen Headbutt L43→L35, Head Smash L58→L46 |
| Shieldon | Smack Down L7, Counter L14, Mirror Shot L19, Stealth Rock L34, Stone Edge L38, Power Split L44 | Taunt L6→L4, Iron Defense L19→L16, Swagger L24→L21, Ancient Power L28→L23, Endure L33→L27, Iron Head L42→L32 |
| Bastiodon | Super Fang L1, Quick Guard L1, Wide Guard L1, Smack Down L1, Counter L14, Mirror Shot L19, Stealth Rock L34, Stone Edge L38, Power Split L44, King’s Shield L52 | Iron Defense L19→L16, Swagger L24→L21, Ancient Power L28→L23, Endure L36→L27, Iron Head L51→L32, Metal Burst L43→L41, Heavy Slam L58→L47 |
| Vespiquen | Infestation L15, Silver Wind L21, Signal Beam L26 | Bug Buzz L49→L1, Fury Swipes L18→L12, Swagger L22→L21, Heal Order L46→L24 |
| Pachirisu | Volt Switch L25, Lovely Kiss L41, Volt Tackle L49 | Quick Attack L12→L1, Endure L16→L15, Swift L23→L17, Electro Ball L30→L20, Sweet Kiss L34→L22, Super Fang L53→L27, Discharge L41→L33 |
| Buizel | Pound L1, Helping Hand L1, Pursuit L14, Bite L22, Quick Guard L25, Whirlpool L27, Ice Fang L33, Crunch L40, Iron Tail L47 | Growl L4→L1, Water Sport L7→L3, Swift L23→L17 |
| Floatzel | Pound L1, Helping Hand L1, Pursuit L14, Bite L22, Quick Guard L25, Whirlpool L27, Iron Tail L47 | Swift L23→L17, Aqua Tail L38→L36, Agility L48→L43, Hydro Pump L52→L51 |
| Cherubi | Sunny Day L16, Natural Gift L30, After You L32, Body Slam L39, Heal Pulse L46 | Helping Hand L13→L1, Growth L10→L5, Leech Seed L23→L8, Magical Leaf L16→L12, Take Down L45→L20, Worry Seed L38→L22, Petal Dance L49→L25 |
| Ambipom | Fire Punch L1, Thunder Punch L1, Ice Punch L1, Pursuit L17, Low Kick L23, Dizzy Punch L28, Fake Out L38, Focus Punch L43 | Fury Swipes L15→L8, Tickle L18→L14, Swift L22→L20, Fling L36→L35 |
| Drifloon | Whirlwind L1, Air Cutter L22, Air Slash L42, Phantom Force L49 | Tailwind L32→L16, Amnesia L45→L39 |
| Drifblim | Defog L1, Whirlwind L1, Air Cutter L22, Air Slash L42 | Tailwind L34→L16, Shadow Ball L42→L36, Amnesia L51→L39, Baton Pass L47→L46 |
| Buneary | Rototiller L1, Endure L5, Me First L18, Mega Kick L42, High Jump Kick L53 | Quick Attack L16→L13, Double Kick L20→L16, Dizzy Punch L44→L22, Baton Pass L28→L24, Agility L36→L26, Entrainment L40→L38, Bounce L56→L45, Healing Wish L64→L49 |
| Lopunny | Last Resort L1, Endure L5, Me First L18, Mega Kick L42 | Quick Attack L16→L13, Double Kick L20→L16, Dizzy Punch L44→L22, Baton Pass L28→L24, Agility L36→L26, Entrainment L40→L38, High Jump Kick L68→L53 |
| Mismagius | Ominous Wind L17, Trick L19, Icy Wind L22, Sing L24, Extrasensory L32, Wonder Room L40 | Shadow Ball L41→L38 |
| Honchkrow | Beat Up L1, Sky Attack L53, Torment L57 | Brave Bird L70→L1, Quash L66→L1, Night Shade L21→L17, Assurance L25→L21, Swagger L44→L23, Taunt L30→L25, Drill Peck L34→L33, Dark Pulse L57→L55 |
| Glameow | Hone Claws L27, Night Slash L30, Super Fang L37 | Scratch L4→L1, Charm L21→L19, Assist L32→L22, Slash L28→L25, Attract L44→L42, Play Rough L56→L45, Double-Edge L52→L49 |
| Purugly | Slack Off L1, Hone Claws L27, Night Slash L30 | Charm L21→L19, Assist L28→L22, Slash L32→L25, Body Slam L43→L37, Attract L46→L42, Play Rough L64→L45, Double-Edge L60→L49 |
| Chingling | Psyshock L19, Recover L24 | Growl L4→L1, Astonish L7→L3, Confusion L10→L5, Yawn L13→L8, Entrainment L19→L11, Uproar L16→L15 |
| Stunky | Pursuit L12, Poison Tail L24, Memento L38, Gunk Shot L44 | Screech L24→L6, Fury Swipes L12→L9, Toxic L27→L26, Night Slash L36→L29, Sludge Bomb L42→L31 |
| Skuntank | Fire Fang L1, Pursuit L12, Poison Tail L24, Memento L38, Gunk Shot L44 | Screech L24→L1, Fury Swipes L12→L9, Toxic L27→L26, Night Slash L38→L29, Sludge Bomb L48→L31, Explosion L65→L48 |
| Bronzor | Gravity L1, Mirror Shot L16, Stealth Rock L24, Skill Swap L40, Zen Headbutt L52 | Imprison L12→L7, Psywave L15→L12, Extrasensory L28→L27, Metal Sound L44→L30 |
| Bronzong | Trick L1, Gravity L1, Mirror Shot L16, Skill Swap L24, Zen Headbutt L52 | Psywave L15→L12, Extrasensory L28→L27, Metal Sound L50→L30 |
| Bonsly | Uproar L28, Curse L37, Stone Edge L43 | Rock Tomb L21→L20, Counter L40→L25 |
| Mime Jr. | Psywave L15, Magical Leaf L21 | Role Play L26→L3, Meditate L14→L5, Double Slap L11→L10, Encore L20→L12, Light Screen L50→L18, Reflect L50→L18, Substitute L41→L27, Recycle L38→L30, Trick L44→L32, Safeguard L50→L47 |
| Happiny | Natural Gift L14, Soft-Boiled L18, Uproar L23, Last Resort L28 | Covet L16→L7 |
| Chatot | Flatter L1, Air Slash L33, Nasty Plot L40, Parting Shot L46 | Echoed Voice L37→L1, Growl L5→L4, Mirror Move L9→L7, Round L21→L10, Uproar L46→L28, Mimic L33→L30, Feather Dance L56→L35, Synchronoise L51→L44, Boomburst L65→L49 |
| Spiritomb | Ancient Power L1, Switcheroo L20, Revenge L25, Grudge L55, Phantom Force L60, Outrage L65, Parting Shot L70 | Feint Attack L14→L5, Hypnosis L56→L10, Dream Eater L60→L10, Ominous Wind L32→L15, Sucker Punch L37→L30, Shadow Ball L46→L40 |
| Gible | Slam L7, Dragon Breath L24, Scary Face L40, Rock Climb L45 | Sandstorm L13→L10, Sand Tomb L18→L17 |
| Gabite | Slam L1, Scary Face L40, Rock Climb L45 | Sand Tomb L18→L17, Dig L41→L36, Earthquake L56→L55 |
| Garchomp | Earth Power L1, Slam L1, Scary Face L40, Rock Climb L45, Giga Impact L61 | Sand Tomb L18→L17, Dig L41→L36, Dragon Rush L57→L51, Earthquake L63→L55 |
| Munchlax | Slack Off L62 | Recycle L8→L1, Screech L30→L17, Rollout L26→L25 |
| Riolu | Vacuum Wave L25, Dizzy Punch L33 | Force Palm L36→L13, Copycat L48→L17, Screech L28→L21, Final Gambit L52→L44 |
| Lucario | Me First L13, Iron Head L47 | Counter L12→L1, Heal Pulse L48→L38 |
| Hippopotas | Sleep Talk L25, Bulldoze L28 | Sand Tomb L12→L10, Take Down L28→L16, Sandstorm L24→L21, Rest L36→L25, Slack Off L52→L49 |
| Hippowdon | Sleep Talk L25, Bulldoze L28 | Sand Tomb L12→L1, Take Down L28→L16, Sandstorm L24→L21, Rest L38→L25, Double-Edge L50→L44, Slack Off L62→L49, Fissure L56→L54 |
| Drapion | Focus Energy L1 | Pursuit L12→L1, Bug Bite L15→L9, Acupressure L49→L12, Poison Jab L54→L31, Night Slash L39→L37, X-Scissor L44→L40 |
| Croagunk | Drain Punch L30, Flatter L37, Gunk Shot L53 | Swagger L30→L23, Poison Jab L37→L32, Sludge Bomb L47→L40, Cross Chop L55→L48 |
| Toxicroak | Drain Punch L30, Flatter L37, Gunk Shot L53 | Belch L59→L1, Swagger L30→L23, Poison Jab L37→L32, Sludge Bomb L53→L40, Cross Chop L65→L48 |
| Carnivine | Thunder Fang L1, Acid L1, Razor Leaf L14, Hyper Fang L18, Grass Whistle L27, Poison Fang L30, Seed Bomb L36, Super Fang L45, Energy Ball L52 | Vine Whip L14→L1, Bite L7→L5, Sweet Scent L11→L8, Ingrain L18→L10, Leaf Tornado L28→L24, Crunch L38→L34, Power Whip L48→L42 |
| Finneon | Defog L1, Air Slash L28, Scald L31, Hydro Pump L44, Tailwind L46, Follow Me L51 | Attract L10→L1, Water Gun L6→L4, Gust L16→L7, Rain Dance L13→L11, Whirlpool L33→L13, Water Pulse L20→L19, Captivate L24→L21, Silver Wind L41→L24 |
| Lumineon | Quiver Dance L1, Defog L1, Air Slash L28, Scald L31, Hydro Pump L44, Tailwind L46, Follow Me L51 | Whirlpool L35→L13, Water Pulse L20→L19, Captivate L24→L21, Silver Wind L50→L24 |
| Mantyke | Gust L4, Scald L33, Mirror Coat L48, Hurricane L52 | Supersonic L4→L1, Headbutt L28→L7, Take Down L44→L24, Air Slash L32→L28, Hydro Pump L48→L45 |
| Snover | Grass Knot L19, Ice Punch L32, Energy Ball L34, Worry Seed L39, Hammer Arm L50 | Ingrain L34→L28 |
| Abomasnow | Leaf Storm L1, Grass Knot L19, Energy Ball L34, Worry Seed L39, Hammer Arm L50 | Ingrain L34→L28, Blizzard L51→L43, Sheer Cold L67→L55 |
| Weavile | Pursuit L1, Slash L33, Ice Punch L35, Beat Up L44, Icicle Crash L48, Knock Off L57 | Icy Wind L18→L9, Fury Swipes L22→L13, Nasty Plot L38→L18, Ice Shard L34→L23, Screech L48→L30 |
| Lickilicky | Drain Punch L1, Pound L1, Chip Away L24, Curse L27, Me First L40 | Belly Drum L62→L1, Disable L19→L18, Refresh L43→L29, Body Slam L39→L36 |
| Rhyperior | Stealth Rock L1, Rock Slide L36, Double-Edge L56 | Smack Down L8→L1, Chip Away L24→L19, Take Down L36→L29 |
| Tangrowth | Body Slam L37, Energy Ball L43, Morning Sun L55 | Sleep Powder L39→L1, Poison Powder L20→L10, Knock Off L27→L22, Giga Drain L35→L31, Tickle L47→L40, Wring Out L50→L46, Power Whip L54→L52 |
| Electivire | Ice Punch L1, Work Up L21, Mega Punch L32, Cross Chop L48 | Shock Wave L15→L9, Thunder Wave L19→L16, Electro Ball L29→L19, Thunder L58→L52, Giga Impact L64→L57 |
| Magmortar | Aura Sphere L1, Zap Cannon L1, Fire Spin L9, Work Up L21, Will-O-Wisp L28, Mega Punch L32, Dark Pulse L48 | Flame Burst L30→L19, Fire Punch L36→L25, Lava Plume L41→L35, Flamethrower L51→L42, Fire Blast L60→L52, Hyper Beam L65→L57 |
| Togekiss | Return L10, Tailwind L22, Air Cutter L25, Defog L47, Soft-Boiled L50 |  |
| Yanmega | Defog L1, Leech Life L1, Twister L12, Signal Beam L24, Acrobatics L49, Dragon Pulse L53 | Sonic Boom L15→L10, Slash L30→L28, U-turn L57→L35 |
| Leafeon | Worry Seed L1, Jump Kick L1, Double Kick L14, Bullet Seed L29, X-Scissor L48, Solar Beam L52 | Sand Attack L5→L4, Quick Attack L10→L6, Magical Leaf L25→L9, Leaf Blade L60→L37 |
| Glaceon | Sheer Cold L1, Jump Kick L1, Powder Snow L9, Disable L12, Double Kick L14, Haze L22, Frost Breath L29, Yawn L35, Ice Beam L37 | Sand Attack L5→L4, Quick Attack L10→L6, Freeze-Dry L50→L48 |
| Gliscor | Sand Tomb L10, Wing Attack L18, Sky Attack L59 | Quick Attack L13→L1, Fury Cutter L16→L14, Screech L38→L24, Sky Uppercut L47→L38, Earthquake L57→L44 |
| Mamoswine | Dig L35 | Endure L29→L12, Ice Shard L25→L19, Take Down L46→L26, Thrash L64→L40, Icicle Crash L72→L44 |
| Porygon-Z | Curse L1, Imprison L1, Swift L10, Electroweb L18, Gravity L21, Trick L34, Foul Play L44 | Psybeam L20→L4, Agility L32→L7, Recover L35→L14, Signal Beam L29→L24, Discharge L40→L31, Tri Attack L45→L38, Lock-On L55→L41, Hyper Beam L65→L52 |
| Gallade | Cross Chop L1, Double Kick L1, Brick Break L28, Sacred Sword L39, Zen Headbutt L46 | Quick Guard L56→L18, Wide Guard L56→L20, Psycho Cut L42→L32 |
| Probopass | Rock Throw L1, Heavy Slam L11, Shock Wave L17, Ancient Power L20, Flash Cannon L39, Iron Head L54 | Rock Slide L31→L28, Sandstorm L34→L33 |
| Dusknoir | Snatch L37, Sucker Punch L44, Phantom Force L53, Drain Punch L58 | Pursuit L14→L11, Will-O-Wisp L24→L18, Hex L32→L21, Curse L36→L29, Shadow Ball L42→L40 |
| Froslass | Trick L1, Icicle Spear L21, Captivate L23, Ice Beam L37, Curse L49, Sheer Cold L58 | Hail L50→L15, Frost Breath L40→L26, Shadow Ball L45→L43, Blizzard L60→L47 |
| Rotom | Eerie Impulse L45, Hyper Voice L55, Shadow Ball L60 | Uproar L60→L5, Shock Wave L30→L15, Ominous Wind L35→L20, Substitute L45→L30 |
| Uxie | Stealth Rock L1, Giga Drain L1, Iron Tail L1, Helping Hand L1, Skill Swap L1, Hex L41, Stored Power L56, Barrier L61, Disable L66 | Extrasensory L35→L21, Yawn L49→L26 |
| Mesprit | Stealth Rock L1, Earth Power L1, Signal Beam L1, Helping Hand L1, Wonder Room L1, Trick L1, Incinerate L6, Fake Tears L16, Knock Off L41, Zen Headbutt L56, Heal Bell L66 | Extrasensory L35→L21 |
| Azelf | Stealth Rock L1, Fire Punch L1, Outrage L1, Helping Hand L1, Magic Room L1, Spite L1, Tri Attack L41, Final Gambit L46, Psyshock L56, Power Split L66 | Extrasensory L35→L21, Uproar L49→L26 |
| Dialga | Magnet Rise L1, Mirror Shot L15, Stealth Rock L30, Trick Room L55, Dragon Pulse L65, Cosmic Power L75 | Slash L24→L5, Dragon Claw L40→L25, Iron Tail L88→L35, Roar of Time L96→L45 |
| Palkia | Brine L15, Haze L30, Gravity L55, Dragon Pulse L65, Dragon Dance L75 | Aqua Ring L32→L1, Slash L24→L5, Dragon Claw L40→L25, Spacial Rend L80→L45 |
| Heatran | Mirror Shot L7, Stealth Rock L25, Dragon Pulse L67 | Fire Fang L18→L13, Metal Sound L48→L19, Crunch L36→L31, Lava Plume L42→L37 |
| Regigigas | Dynamic Punch L1, Gravity L1, Drain Punch L5, Double-Edge L40, Block L45, Superpower L60, Power Split L75, Guard Split L75, Shadow Punch L80 | Stomp L18→L1, Mega Punch L36→L15, Wide Guard L48→L20, Zen Headbutt L54→L35 |
| Cresselia | Helping Hand L1, Icy Wind L13, Ice Beam L49 | Safeguard L48→L1, Future Sight L66→L37 |
| Phione | Helping Hand L1, Icy Wind L17, Signal Beam L33, Play Rough L41, Muddy Water L45, Ice Beam L53, Soak L57, Hydro Pump L61, Heal Bell L65 | Charm L7→L5, Whirlpool L28→L9, Bubble Beam L39→L21, Dive L60→L29, Rain Dance L50→L37 |
| Manaphy | Icy Wind L17, Dive L29, Signal Beam L33, Ancient Power L41, Ice Beam L53, Soak L57, Hydro Pump L61 | Charm L7→L5, Whirlpool L28→L9, Bubble Beam L39→L21, Rain Dance L50→L37, Surf L60→L45, Heart Swap L71→L65 |
| Darkrai | Knock Off L1, Trick L1, Double Team L1 | Hypnosis L20→L15, Nightmare L50→L15, Feint Attack L30→L22, Haze L40→L36, Sucker Punch L60→L43, Dark Void L70→L50, Nasty Plot L100→L57, Dream Eater L90→L64, Dark Pulse L80→L71 |
| Arceus | Iron Head L1, Aqua Tail L1, Phantom Force L1, Heat Wave L1, Giga Drain L1, Dragon Pulse L1, Discharge L1, Icy Wind L1, Defog L1, Tailwind L1, Stealth Rock L1, Outrage L40 |  |
| Victini | Helping Hand L1, Follow Me L30, Discharge L50, Psychic L65, Volt Tackle L70 | Work Up L7→L1, Endure L38→L5, Headbutt L28→L10, Stored Power L21→L20, Flame Burst L33→L25, Zen Headbutt L42→L35, Double-Edge L70→L40, Inferno L49→L45, Flare Blitz L77→L70, Final Gambit L91→L75 |
| Snivy | Glare L21, Synthesis L35, Iron Tail L39, Flail L45 | Leer L4→L1, Vine Whip L7→L5, Wrap L10→L8, Growth L13→L10, Slam L25→L13, Gastro Acid L40→L26 |
| Servine | Glare L21, Synthesis L35, Iron Tail L39, Flail L45 | Growth L13→L10, Slam L28→L13, Leech Seed L20→L19, Gastro Acid L48→L26, Leaf Blade L32→L30, Coil L36→L33 |
| Serperior | Noble Roar L1, Glare L21, Synthesis L35, Iron Tail L39, Dragon Pulse L45 | Growth L13→L10, Slam L28→L13, Leech Seed L20→L19, Gastro Acid L56→L26, Leaf Blade L32→L30, Coil L38→L33, Giga Drain L44→L42, Wring Out L50→L49, Leaf Storm L62→L54 |
| Tepig | Headbutt L17, Flame Burst L24, Body Slam L36, Double-Edge L46 | Tail Whip L3→L1, Ember L7→L5, Odor Sleuth L9→L7, Defense Curl L13→L10, Smog L19→L12, Assurance L31→L29, Roar L39→L38 |
| Pignite | Fire Punch L24, Submission L36, Work Up L38, Superpower L46 | Defense Curl L13→L10, Smog L20→L12, Rollout L23→L21, Take Down L28→L27, Assurance L36→L29 |
| Emboar | Fire Punch L24, Submission L36, Work Up L38, Superpower L46 | Defense Curl L13→L10, Smog L20→L12, Rollout L23→L21, Take Down L28→L27, Assurance L38→L29, Flamethrower L43→L42, Flare Blitz L62→L56 |
| Oshawott | Aerial Ace L20, Slash L29, X-Scissor L41, Knock Off L55 | Tail Whip L5→L1, Water Gun L7→L5, Water Sport L11→L8, Focus Energy L13→L11, Fury Cutter L19→L14 |
| Dewott | Aerial Ace L20, Slash L29, X-Scissor L41, Knock Off L55 | Focus Energy L13→L11, Fury Cutter L21→L14, Water Pulse L26→L23, Revenge L29→L26, Aqua Jet L34→L31, Encore L37→L34, Aqua Tail L42→L38, Swords Dance L50→L48 |
| Samurott | Knock Off L1, Aerial Ace L20, X-Scissor L41, Horn Drill L55 | Focus Energy L13→L11, Fury Cutter L21→L14, Water Pulse L25→L23, Revenge L29→L26, Aqua Jet L34→L31, Encore L39→L34, Aqua Tail L46→L38, Retaliate L51→L44, Swords Dance L58→L48, Hydro Pump L63→L52 |
| Patrat | Bide L6, Chip Away L14, Bullet Seed L25, Seed Bomb L38, Flail L42, Iron Tail L46 | Leer L3→L1, Bite L6→L4, Detect L13→L9, Hypnosis L18→L16, Super Fang L39→L18, Mean Look L34→L27 |
| Watchog | Bide L1, Chip Away L14, Bullet Seed L25, Lock-On L35, Seed Bomb L38, Mega Kick L42, Iron Tail L46 | Detect L13→L9, Hypnosis L18→L16, Super Fang L49→L18, Mean Look L43→L27, Hyper Fang L33→L30 |
| Lillipup | Headbutt L13, Covet L18, Punishment L37, Double-Edge L42 | Odor Sleuth L6→L3, Helping Hand L32→L10 |
| Herdier | Headbutt L13, Covet L18, Punishment L37, Double-Edge L42 | Helping Hand L38→L10, Roar L42→L27 |
| Stoutland | Headbutt L13, Covet L18, Punishment L37, Double-Edge L42 | Helping Hand L42→L10, Roar L48→L27, Last Resort L60→L46, Play Rough L54→L49, Giga Impact L66→L55 |
| Purrloin | Captivate L30, U-turn L32, Snatch L35, Dark Pulse L38 | Assist L6→L5, Pursuit L15→L8, Torment L18→L14, Assurance L21→L17, Slash L32→L22, Night Slash L40→L27 |
| Liepard | Copycat L1, Snarl L20, Captivate L30, U-turn L32, Snatch L35, Dark Pulse L38 | Pursuit L15→L1, Torment L18→L14, Assurance L23→L17, Slash L40→L22, Hone Claws L28→L25, Night Slash L52→L27, Nasty Plot L46→L42, Play Rough L58→L48 |
| Pansage | Role Play L8, Dizzy Punch L40, Wood Hammer L46, Snatch L49 | Lick L7→L6 |
| Simisage | Work Up L1, Role Play L8, Dizzy Punch L40, Wood Hammer L46, Snatch L49 |  |
| Pansear | Role Play L8, Blaze Kick L34, Endeavor L40, Me First L49 | Lick L7→L6 |
| Simisear | Work Up L1, Role Play L8, Blaze Kick L34, Endeavor L40, Me First L49 |  |
| Panpour | Role Play L8, Hyper Voice L40, Hydro Pump L46, Encore L49 | Lick L7→L6 |
| Simipour | Work Up L1, Role Play L8, Hyper Voice L40, Hydro Pump L46, Encore L49 |  |
| Munna | Psyshock L25, Heal Bell L42 | Yawn L32→L6, Moonlight L19→L15, Zen Headbutt L25→L17, Telekinesis L39→L27, Dream Eater L46→L39 |
| Musharna | Gravity L1, Psywave L1, Psyshock L25, Heal Bell L42 |  |
| Pidove | Echoed Voice L15, Swift L25, Hyper Voice L38 | Air Cutter L16→L12, Detect L28→L20, Razor Wind L34→L22 |
| Tranquill | Echoed Voice L15, Swift L25, Hyper Voice L38 | Air Cutter L16→L12, Detect L34→L20, Razor Wind L41→L22, Air Slash L38→L29, Tailwind L50→L43, Sky Attack L57→L47 |
| Unfezant | Echoed Voice L15, Swift L25, Hyper Voice L38 | Air Cutter L16→L12, Detect L36→L20, Razor Wind L46→L22, Air Slash L42→L29, Tailwind L58→L43, Sky Attack L65→L47 |
| Blitzle | Double Kick L17, Blaze Kick L34, Ion Deluge L42, Jump Kick L46 | Tail Whip L4→L3, Charge L8→L5, Shock Wave L11→L9, Thunder Wave L15→L11, Flame Charge L18→L15, Spark L25→L20, Stomp L29→L25, Discharge L32→L28, Agility L36→L30, Wild Charge L39→L37, Thrash L47→L40, Volt Tackle L51→L50 |
| Zebstrika | Outrage L1, Double Kick L17, Blaze Kick L34, Jump Kick L46 | Flame Charge L18→L15, Spark L25→L20, Stomp L31→L25, Discharge L36→L28, Agility L42→L30, Wild Charge L47→L37, Thrash L58→L40, Volt Tackle L68→L50 |
| Roggenrola | Rock Climb L32, Heavy Slam L37, Curse L46 |  |
| Boldore | Rock Climb L32, Heavy Slam L37, Curse L46 | Rock Slide L36→L28, Sandstorm L42→L34, Stone Edge L48→L42, Explosion L60→L52 |
| Gigalith | Rock Climb L32, Heavy Slam L37, Curse L46 | Rock Slide L36→L28, Sandstorm L42→L34, Stone Edge L48→L42, Explosion L60→L52 |
| Woobat | Extrasensory L26, Roost L35, Hurricane L43 | Assurance L26→L8, Heart Stamp L22→L11, Simple Beam L50→L22, Amnesia L30→L28, Air Slash L34→L31, Psychic L46→L38 |
| Swoobat | Trick L1, Extrasensory L26, Roost L35, Hurricane L43 | Heart Stamp L22→L11, Simple Beam L50→L22, Amnesia L30→L28, Air Slash L34→L31, Psychic L46→L38 |
| Drilbur | Rototiller L1, Smack Down L21, Iron Head L43 | Drill Run L45→L33 |
| Excadrill | Smack Down L21, Iron Head L43 | Drill Run L50→L33, Fissure L62→L58 |
| Audino | Round L8, Wish L38, Heal Bell L45 | Entrainment L56→L18, Heal Pulse L46→L25, Hyper Voice L42→L30, Simple Beam L39→L33, Double-Edge L52→L42 |
| Timburr | Work Up L28 |  |
| Gurdurr | Work Up L28 |  |
| Conkeldurr | Fire Punch L1, Ice Punch L1, Thunder Punch L1, Work Up L28 |  |
| Tympole | Water Pulse L21, Mud Bomb L27, Screech L48 | Supersonic L8→L3, Round L15→L6, Bubble Beam L19→L10, Aqua Ring L31→L18, Rain Dance L42→L30, Earth Power L45→L42 |
| Palpitoad | Water Pulse L21, Mud Bomb L27, Screech L48 | Bubble Beam L19→L10, Aqua Ring L33→L18, Rain Dance L47→L30, Earth Power L51→L42, Hydro Pump L56→L46 |
| Seismitoad | Ice Punch L1, Water Pulse L21, Mud Bomb L27, Acid Spray L36, Toxic L48 | Bubble Beam L19→L10, Aqua Ring L33→L18, Rain Dance L51→L30, Hydro Pump L62→L46 |
| Throh | Ice Punch L1, Thunder Punch L1, Fire Punch L1, Helping Hand L1, Work Up L1, Chip Away L17, Payback L25, Drain Punch L35, Knock Off L54 | Seismic Toss L37→L11, Vital Throw L32→L13, Storm Throw L42→L23, Superpower L56→L47, Reversal L51→L49 |
| Sawk | Ice Punch L1, Thunder Punch L1, Fire Punch L1, Helping Hand L1, Work Up L1, Chip Away L17, Feint Attack L25, Sky Uppercut L35, Dual Chop L54 | Double Kick L32→L11, Close Combat L56→L47, Reversal L51→L49 |
| Sewaddle | Grass Whistle L23, Energy Ball L30 | Struggle Bug L8→L6 |
| Swadloon | Energy Ball L30 |  |
| Leavanny | Barrier L20, Knock Off L46 | Helping Hand L31→L30, Swords Dance L46→L43 |
| Venipede | Leech Life L6, Pin Missile L39 | Bug Bite L31→L18, Poison Jab L38→L33, Rock Climb L45→L36, Venom Drench L49→L44 |
| Whirlipede | Leech Life L6, Pin Missile L39 | Bug Bite L35→L18, Venoshock L25→L24, Agility L40→L29, Poison Jab L44→L33, Rock Climb L53→L36, Double-Edge L62→L48 |
| Scolipede | Leech Life L1, Pin Missile L39 | Venoshock L25→L24, Agility L44→L29, Poison Jab L49→L33, Rock Climb L64→L36, Toxic L54→L42, Venom Drench L59→L44, Double-Edge L70→L48 |
| Cottonee | Gust L15, Tailwind L23, Hurricane L47, Moonblast L50 | Growth L18→L1, Leech Seed L30→L4, Mega Drain L12→L10, Cotton Spore L33→L12, Poison Powder L21→L20, Endeavor L42→L37, Solar Beam L48→L44 |
| Petilil | Teeter Dance L12, Uproar L23, Petal Dance L31, Quiver Dance L37, Hyper Voice L50 | After You L27→L1, Leech Seed L24→L4, Sleep Powder L18→L7, Synthesis L33→L15 |
| Lilligant | Uproar L23, Hyper Voice L50 |  |
| Sandile | Mud-Slap L1 | Torment L18→L7, Bulldoze L29→L19 |
| Krokorok | Mud-Slap L1 | Torment L18→L7 |
| Krookodile | Block L1, Mud-Slap L1 | Torment L18→L7 |
| Darumaka | Rage L7, Swagger L17, Overheat L33, Blaze Kick L39, Zen Headbutt L42 | Rollout L3→L1, Incinerate L12→L4, Uproar L36→L10 |
| Maractus | Astonish L7, Bullet Seed L10, Bounce L27, Teeter Dance L33, Sandstorm L43, Wood Hammer L45, Play Rough L50 | Sweet Scent L27→L1, Growth L4→L3, Cotton Spore L37→L17, Acupressure L47→L23, Petal Dance L50→L37 |
| Dwebble | Rock Throw L1, Sharpen L1, Stone Edge L40, Snatch L46 | X-Scissor L40→L34 |
| Crustle | Rock Throw L1, Sharpen L1, Stone Edge L40, Heavy Slam L46 | X-Scissor L42→L34, Rock Wrecker L57→L51 |
| Scraggy | Jump Kick L31, Fling L50 |  |
| Scrafty | Zen Headbutt L1, Jump Kick L31, Fling L50, Focus Punch L54 |  |
| Sigilyph | Mirror Move L28, Psycho Shift L44 | Reflect L43→L24, Sky Attack L56→L48 |
| Yamask | Ominous Wind L13, Role Play L16, Foul Play L32, Earth Power L47, Phantom Force L50 | Disable L12→L4, Night Shade L8→L7, Curse L36→L26, Power Split L48→L29, Guard Split L48→L29 |
| Cofagrigus | Knock Off L1, Ominous Wind L13, Role Play L16, Foul Play L32, Earth Power L47, Phantom Force L50 | Curse L38→L26, Power Split L56→L29, Guard Split L56→L29, Shadow Ball L44→L37, Destiny Bond L62→L54 |
| Tirtouga | Rollout L4, Stone Edge L53 | Bite L15→L7, Iron Defense L33→L18, Curse L30→L26, Aqua Tail L36→L35 |
| Carracosta | Super Fang L1, Stone Edge L53 | Bite L15→L7, Iron Defense L33→L16, Curse L30→L26, Aqua Tail L36→L35 |
| Archen | Gust L1, Stone Edge L47, Sky Attack L57 | Crunch L30→L28, Thrash L45→L37 |
| Archeops | Defog L1, Gust L1, Stone Edge L47, Sky Attack L57 | Crunch L30→L28 |
| Trubbish | Barrage L13, Poison Fang L16, Poison Jab L32, Dizzy Punch L38 | Toxic Spikes L18→L6, Stockpile L24→L20, Swallow L24→L20, Take Down L27→L23 |
| Garbodor | Rock Blast L1, Barrage L13, Poison Fang L16, Poison Jab L32, Dizzy Punch L38 | Stockpile L24→L20, Swallow L24→L20, Body Slam L27→L23 |
| Zorua | Snarl L15, Embargo L40, Dark Pulse L43, Uproar L46 | Pursuit L6→L4, Fake Tears L28→L7, Fury Swipes L12→L11 |
| Zoroark | Extrasensory L1, Snarl L15, Embargo L40, Dark Pulse L43, Crush Claw L46 | Fury Swipes L12→L11, Nasty Plot L52→L50 |
| Minccino | Fury Swipes L18, Covet L26 | Echoed Voice L6→L5, Double Slap L13→L8, Swift L20→L13, Hyper Voice L48→L38, Last Resort L56→L44, Play Rough L52→L47 |
| Cinccino | Knock Off L1, Fury Swipes L18, Covet L26 | Play Rough L52→L47 |
| Gothita | Torment L5, Trick Room L29, Dark Pulse L38, Foul Play L49 | Play Nice L8→L1, Double Slap L14→L10, Psybeam L16→L13, Embargo L19→L18, Feint Attack L24→L21, Psyshock L25→L24, Flatter L28→L26, Charm L46→L40 |
| Gothorita | Torment L5, Trick Room L29, Dark Pulse L38, Foul Play L49 | Double Slap L14→L10, Psybeam L16→L13, Embargo L19→L18, Feint Attack L24→L21, Psyshock L25→L24, Flatter L28→L26, Charm L50→L40, Magic Room L53→L52 |
| Gothitelle | Fake Out L1, Torment L1, Trick Room L29, Dark Pulse L38, Foul Play L49 | Double Slap L14→L10, Psybeam L16→L13, Embargo L19→L18, Feint Attack L24→L21, Psyshock L25→L24, Flatter L28→L26, Charm L54→L40, Magic Room L59→L52 |
| Solosis | Psybeam L11, Counter L43 | Snatch L10→L9, Recover L24→L23, Wonder Room L48→L31 |
| Duosion | Psybeam L11, Counter L43 | Recover L24→L23, Wonder Room L53→L31 |
| Reuniclus | Psybeam L11, Counter L43, Hammer Arm L57 | Recover L24→L23, Wonder Room L59→L31, Heal Block L54→L52 |
| Ducklett | Bubble Beam L18, Razor Wind L23, Acrobatics L36, Scald L41 | Hurricane L48→L44 |
| Swanna | Bubble Beam L18, Razor Wind L23, Acrobatics L36, Scald L41 | Tailwind L47→L38, Hurricane L65→L44 |
| Vanillite | Frost Breath L28, Recycle L30, Natural Gift L54 | Icy Wind L12→L11, Mirror Shot L26→L24, Flash Cannon L44→L37 |
| Vanillish | Frost Breath L28, Recycle L30, Natural Gift L54 | Icy Wind L12→L11, Mirror Shot L27→L24, Flash Cannon L52→L37, Blizzard L57→L51 |
| Vanilluxe | Frost Breath L28, Recycle L30, Belch L54 | Icy Wind L12→L11, Mirror Shot L27→L24, Flash Cannon L54→L37, Blizzard L62→L51 |
| Emolga | Aerial Ace L17, Air Slash L46, Nasty Plot L50, Volt Tackle L55 | Quick Attack L9→L3, Charge L21→L6, Spark L25→L9, Pursuit L17→L14, Encore L33→L25, Agility L57→L40, Discharge L52→L43 |
| Karrablast | Bug Buzz L20, Revenge L25, Pin Missile L42 | Endure L8→L6, Fury Attack L16→L13, Headbutt L20→L16, X-Scissor L32→L29 |
| Escavalier | Drill Run L1, Mirror Shot L16, Bug Buzz L20, Revenge L25, Gyro Ball L50 | Fury Attack L16→L13, X-Scissor L36→L29, Megahorn L66→L54 |
| Foongus | Smog L9, Protect L34, Sludge Bomb L40 | Growth L4→L1, Ingrain L36→L11, Sweet Scent L24→L17 |
| Amoonguss | Smog L9, Protect L34, Sludge Bomb L40 | Ingrain L36→L11, Sweet Scent L24→L17, Solar Beam L60→L44, Rage Powder L48→L46, Spore L54→L50 |
| Frillish | Astonish L3, Refresh L14, Water Pulse L21, Icy Wind L24, Pain Split L52 | Ominous Wind L20→L18, Shadow Ball L48→L45, Wring Out L52→L48 |
| Jellicent | Giga Drain L1, Astonish L1, Water Pulse L21, Icy Wind L24, Pain Split L52 | Ominous Wind L20→L18, Hydro Pump L43→L42, Shadow Ball L53→L45 |
| Alomomola | Dive L35, Zen Headbutt L51 | Aqua Jet L17→L8, Double Slap L13→L11, Heal Pulse L21→L15, Protect L61→L18, Helping Hand L33→L25, Wake-Up Slap L29→L28, Soak L41→L31, Safeguard L57→L41 |
| Joltik | Fury Cutter L11, Bug Bite L17, Sticky Web L45, Zap Cannon L50 | Gastro Acid L48→L19, Slash L37→L22, Signal Beam L32→L29, Agility L44→L31, Discharge L40→L34, Bug Buzz L52→L41 |
| Galvantula | Fury Cutter L11, Bug Bite L17, Zap Cannon L50 | Gastro Acid L53→L19, Slash L39→L22, Signal Beam L32→L29, Agility L48→L31, Discharge L43→L34, Bug Buzz L58→L41 |
| Ferroseed | Bullet Seed L25, Rock Climb L42, Spike Cannon L48, Seed Bomb L51 | Iron Defense L37→L9, Payback L45→L44 |
| Ferrothorn | Bullet Seed L25, Spike Cannon L48, Seed Bomb L51 | Iron Defense L37→L1, Payback L49→L44, Explosion L62→L56 |
| Klink | Spark L17, Iron Head L37, Wild Charge L45, Heavy Slam L53 | Charge L8→L1, Mirror Shot L20→L9, Screech L36→L29 |
| Klang | Double Hit L1, Spark L17, Iron Head L37, Wild Charge L45, Heavy Slam L53 | Mirror Shot L20→L9, Screech L36→L29 |
| Klinklang | Heat Crash L1, Tri Attack L1, Spark L17, Iron Head L37, Wild Charge L45, Heavy Slam L53 | Mirror Shot L20→L9, Screech L36→L29 |
| Eelektrik | Mega Drain L15, Thunder Fang L20, Giga Drain L46 | Acid L19→L5, Acid Spray L46→L25, Coil L50→L38, Wild Charge L54→L42, Gastro Acid L58→L50, Thrash L66→L56, Zap Cannon L62→L59 |
| Eelektross | Drain Punch L1, Aqua Tail L1, Mega Drain L15, Thunder Fang L20, Giga Drain L46, Superpower L63 |  |
| Elgyem | Psyshock L28, Signal Beam L34, Power Gem L54 | Miracle Eye L7→L1, Heal Block L38→L5, Psybeam L17→L11, Hidden Power L24→L17, Zen Headbutt L31→L22, Psych Up L45→L31, Psychic L51→L38, Calm Mind L48→L41, Synchronoise L59→L48 |
| Beheeyem | Gravity L1, Psyshock L28, Signal Beam L34, Power Gem L54 | Psybeam L17→L11, Hidden Power L24→L17, Zen Headbutt L31→L22, Psych Up L46→L31, Psychic L54→L38, Calm Mind L50→L41 |
| Litwick | Lava Plume L33 | Imprison L44→L23, Pain Split L48→L30 |
| Lampent | Lava Plume L33 | Imprison L46→L23, Pain Split L52→L30, Overheat L58→L52 |
| Chandelure | Hypnosis L1, Ember L1, Lava Plume L33 | Overheat L58→L52 |
| Axew | Slam L10, X-Scissor L34, Night Slash L44 | Swords Dance L42→L41 |
| Fraxure | Slam L1, X-Scissor L34, Night Slash L44 | Swords Dance L46→L41, Guillotine L56→L48, Giga Impact L61→L60 |
| Haxorus | Slam L1, X-Scissor L34, Night Slash L44 | Swords Dance L46→L41, Guillotine L60→L48, Giga Impact L67→L60 |
| Cubchoo | Ice Shard L18, Ice Punch L27, Tickle L51 | Play Nice L12→L1, Icy Wind L9→L8, Charm L27→L23 |
| Beartic | Scary Face L1, Ice Shard L18, Ice Punch L27, Submission L39, Bulk Up L51 | Swagger L27→L23 |
| Cryogonal | Hail L16, Water Pulse L25, Memento L52, Blizzard L55 | Icy Wind L16→L13, Aurora Beam L28→L22, Acid Armor L52→L28, Slash L32→L31, Freeze-Dry L36→L34 |
| Shelmet | Bug Bite L24, Mud Bomb L30, Signal Beam L33, Metal Sound L38, Wide Guard L41 | Acid L4→L3, Struggle Bug L16→L11, Yawn L20→L18 |
| Accelgor | Mud Bomb L30, Signal Beam L33, Spikes L38, Quick Guard L41 | Struggle Bug L16→L11, Swift L20→L18, Me First L24→L21, U-turn L40→L24, Agility L28→L26 |
| Stunfisk | Eerie Impulse L49, Recover L52 | Mud Shot L11→L10, Camouflage L45→L13, Bounce L49→L34, Earth Power L41→L37 |
| Mienfoo | Vacuum Wave L8, Me First L31, Focus Blast L54 | Meditate L14→L1, Swift L21→L15, Quick Guard L25→L23, Drain Punch L36→L29, Jump Kick L43→L35, Bounce L50→L47 |
| Mienshao | Vacuum Wave L1, Me First L31, Focus Blast L54 | Wide Guard L25→L1, Swift L21→L15, Drain Punch L36→L29, Jump Kick L43→L35, Bounce L52→L47, High Jump Kick L67→L50 |
| Druddigon | Slam L8, Chip Away L14, Night Slash L31, Dragon Rush L46 | Hone Claws L36→L1, Scary Face L16→L11, Revenge L40→L29, Rock Climb L55→L39, Iron Head L60→L49, Superpower L65→L53, Outrage L70→L58 |
| Golett | Focus Punch L53 | Night Shade L23→L11, Magnitude L30→L15, Mega Punch L34→L20, Heavy Slam L42→L37, Phantom Force L46→L41, Hammer Arm L50→L45 |
| Golurk | Fire Punch L1, Ice Punch L1, Thunder Punch L1, Bullet Punch L43, Heat Crash L57, Zap Cannon L64 | Night Shade L23→L11, Magnitude L30→L15, Mega Punch L34→L20, Heavy Slam L42→L37, Hammer Arm L53→L45, Earthquake L58→L48 |
| Pawniard | Embargo L34, Sucker Punch L53 | Pursuit L8→L5, Scary Face L23→L19, Assurance L32→L22, Metal Sound L37→L24, Iron Defense L50→L37, Night Slash L54→L41, Iron Head L63→L45, Swords Dance L59→L50, Guillotine L68→L58 |
| Bisharp | Embargo L34, Sucker Punch L53 | Scary Face L23→L19, Assurance L32→L22, Metal Sound L37→L24, Iron Defense L50→L37, Night Slash L56→L41, Swords Dance L62→L50 |
| Bouffalant | Work Up L13, Headbutt L17, Endure L45, Zen Headbutt L57 | Horn Attack L23→L5, Thrash L47→L29, Giga Impact L57→L53 |
| Rufflet | Rock Smash L15, Aerial Ace L20, Revenge L30, Rock Climb L47, Superpower L51 | Wing Attack L10→L9, Scary Face L29→L17, Slash L38→L24, Defog L57→L26, Crush Claw L52→L37, Whirlwind L43→L41, Brave Bird L66→L55, Thrash L61→L58 |
| Braviary | Zen Headbutt L1, Rock Smash L15, Aerial Ace L20, Revenge L30, Rock Climb L47, Final Gambit L62 | Scary Face L29→L17, Slash L38→L24, Defog L59→L26, Crush Claw L54→L37 |
| Vullaby | Embargo L12, Bone Club L15, Feint Attack L20, Air Cutter L24, Bounce L33, Bone Rush L51 | Pluck L10→L9, Defog L49→L26, Dark Pulse L44→L37, Foul Play L57→L47, Brave Bird L62→L55 |
| Mandibuzz | Block L1, Embargo L12, Bone Club L15, Feint Attack L20, Air Cutter L24, Bounce L33 | Defog L49→L26, Dark Pulse L44→L37, Foul Play L60→L47 |
| Heatmor | Bind L6, Flame Charge L21, Mega Drain L24, Giga Drain L38, Wring Out L42 | Fire Spin L4→L1, Odor Sleuth L8→L4, Snatch L34→L17, Flamethrower L51→L45 |
| Durant | Leech Life L1, Fell Stinger L46 | Bite L20→L9, Dig L28→L26, Entrainment L48→L29 |
| Deino | Slam L1, Hyper Fang L26, Dark Pulse L54 | Dragon Pulse L56→L30 |
| Zweilous | Slam L1, Hyper Fang L26, Dark Pulse L54 | Dragon Pulse L60→L30, Outrage L66→L64 |
| Hydreigon | Tailwind L1, Slam L1, Hyper Fang L26 | Dragon Pulse L60→L30, Dark Pulse L75→L54 |
| Larvesta | Fire Spin L15, Sunny Day L35, Rage Powder L40 | Leech Life L6→L5, Thrash L63→L45, Bug Buzz L53→L50 |
| Volcarona | Tailwind L1, Flame Burst L30, Sunny Day L35, Air Slash L45 | Silver Wind L39→L25 |
| Cobalion | Night Slash L1, Zen Headbutt L1, Metal Sound L1, Vacuum Wave L11, Thunder Fang L21, Flash Cannon L51 | Double Kick L21→L1, Metal Claw L7→L6, Retaliate L28→L26, Iron Head L63→L31, Sacred Sword L49→L41 |
| Terrakion | Night Slash L1, Zen Headbutt L1, Sandstorm L1, Vacuum Wave L11, Bulldoze L21, Rock Blast L51 | Double Kick L21→L1, Smack Down L7→L6, Retaliate L28→L26, Rock Slide L35→L31, Sacred Sword L49→L41 |
| Virizion | Night Slash L1, Zen Headbutt L1, Vacuum Wave L11, Air Slash L21, Horn Leech L51 | Double Kick L21→L1, Magical Leaf L7→L6, Retaliate L28→L26, Giga Drain L35→L31, Sacred Sword L49→L41 |
| Reshiram | Wish L5, Flame Burst L15, Tailwind L35, Earth Power L65 | Fusion Flare L48→L40, Hyper Voice L56→L50, Fire Blast L64→L60, Outrage L80→L75, Blue Flare L88→L80 |
| Zekrom | Wish L5, Thunder Punch L15, Tailwind L35, Earth Power L65 | Fusion Bolt L48→L40, Hyper Voice L56→L55, Thunder L64→L60, Outrage L80→L75, Bolt Strike L88→L80 |
| Kyurem | Mean Look L1, Snatch L5, Icicle Crash L30, Earth Power L65 | Scary Face L48→L35, Glaciate L80→L40, Sheer Cold L88→L80 |
| Genesect | Electroweb L13, Gravity L35, Iron Head L41, Discharge L48 | Lock-On L82→L10, Magnet Bomb L31→L16, Slash L42→L21, Metal Sound L37→L23, Signal Beam L48→L26, Self-Destruct L100→L30, Simple Beam L77→L58, Zap Cannon L82→L65 |
| Chespin | Needle Arm L18, Drain Punch L34 | Leech Seed L15→L14 |
| Quilladin | Drain Punch L34 | Leech Seed L15→L14, Mud Shot L24→L23, Take Down L29→L27, Seed Bomb L34→L32, Body Slam L48→L43, Wood Hammer L53→L48 |
| Chesnaught | Spike Cannon L1 | Leech Seed L15→L14, Mud Shot L24→L23, Take Down L29→L27, Seed Bomb L34→L32, Drain Punch L46→L34, Bulk Up L41→L40, Body Slam L52→L43, Wood Hammer L56→L48, Giga Impact L68→L61 |
| Fennekin | Hex L45 | Howl L11→L7, Flame Charge L14→L12, Lucky Chant L23→L14, Magic Room L38→L23 |
| Braixen | Hex L45 | Ember L5→L1, Howl L11→L7, Flame Charge L14→L12, Lucky Chant L26→L14, Fire Spin L22→L21, Magic Room L47→L23, Incinerate L29→L26, Psyshock L36→L33, Will-O-Wisp L40→L38 |
| Delphox | Hex L45 | Ember L5→L1, Howl L11→L1, Flame Charge L14→L12, Lucky Chant L26→L14, Fire Spin L22→L21, Magic Room L51→L23, Incinerate L29→L26, Psyshock L36→L33, Will-O-Wisp L42→L38, Psychic L55→L48, Sunny Day L60→L52, Fire Blast L64→L55 |
| Froakie | Assurance L23, Dive L27, Feint Attack L33, Muddy Water L42 | Smokescreen L23→L17 |
| Frogadier | Assurance L23, Dive L27, Feint Attack L33, Muddy Water L42 | Smokescreen L26→L17, Round L22→L20 |
| Greninja | Assurance L23, Dive L27, Muddy Water L42 | Quick Attack L11→L1, Smokescreen L26→L17, Extrasensory L50→L45, Hydro Pump L65→L54 |
| Bunnelby | Mud Bomb L26, Hammer Arm L50, Mega Kick L55 | Quick Attack L9→L5, Double Slap L15→L8, Take Down L36→L14, Dig L27→L17, Earthquake L46→L42 |
| Diggersby | Mud Bomb L26, Mega Kick L55 | Double Slap L15→L8, Take Down L43→L14, Dig L31→L17, Bounce L35→L33, Earthquake L56→L42, Super Fang L60→L46 |
| Fletchling | Pluck L20, Flame Charge L27, Take Down L38, Air Slash L42, Brave Bird L54 | Agility L20→L12, Me First L37→L34 |
| Talonflame | Pluck L20, Heat Wave L38, Air Slash L42 | Agility L22→L12, Roost L48→L24, Me First L52→L34 |
| Spewpa | Tackle L1 |  |
| Litleo | Snarl L27 | Echoed Voice L27→L20, Sunny Day L35→L33 |
| Pyroar | Captivate L1, Snarl L27 | Echoed Voice L27→L20, Sunny Day L35→L33, Flamethrower L40→L37, Hyper Voice L50→L45, Overheat L55→L50 |
| Skiddo | Agility L34, Zen Headbutt L40, Earthquake L51 | Vine Whip L7→L4, Tail Whip L10→L7, Worry Seed L17→L12, Take Down L21→L19, Bulldoze L27→L22, Milk Drink L46→L25, Seed Bomb L31→L28, Horn Leech L42→L37 |
| Gogoat | Rock Climb L1, Agility L34, Zen Headbutt L40 | Leech Seed L12→L1, Worry Seed L17→L12, Take Down L21→L19, Bulldoze L27→L22, Milk Drink L49→L25, Seed Bomb L31→L28, Horn Leech L44→L37, Leaf Blade L54→L46 |
| Pancham | Bite L17, Dizzy Punch L20, Drain Punch L27 | Work Up L20→L9, Comet Punch L16→L14, Sky Uppercut L48→L37 |
| Pangoro | Bite L17, Dizzy Punch L20, Drain Punch L27, Sucker Punch L54 | Work Up L20→L1, Comet Punch L16→L14, Body Slam L40→L34, Sky Uppercut L49→L37, Parting Shot L46→L45 |
| Espurr | Miracle Eye L20 | Confusion L9→L1, Reflect L30→L9, Light Screen L30→L11, Psybeam L21→L15 |
| Honedge | Sharpen L1, Metal Claw L20, Shadow Claw L32 | Metal Sound L16→L7, Iron Defense L32→L29 |
| Doublade | Sharpen L1, Metal Claw L20, Shadow Claw L32 | Metal Sound L16→L7, Iron Defense L32→L29, Power Trick L44→L40 |
| Spritzee | Uproar L30, Lovely Kiss L42 |  |
| Aromatisse | Uproar L30, Lovely Kiss L42 | Odor Sleuth L8→L1 |
| Swirlix | Double Slap L16, Zen Headbutt L45, Belly Drum L50 |  |
| Slurpuff | Drain Punch L1, Double Slap L16, Zen Headbutt L45, Belly Drum L50 |  |
| Inkay | Punishment L16, Encore L23, Zen Headbutt L47 | Psybeam L15→L11 |
| Malamar | Play Rough L1, Reflect L1, Punishment L16, Encore L23, Zen Headbutt L47, Sucker Punch L52 | Psybeam L15→L11 |
| Binacle | Smack Down L9, Rock Blast L39 | Water Gun L4→L1, Fury Swipes L16→L6, Clamp L20→L19, Rock Polish L24→L21, Rock Slide L28→L26, Razor Shell L36→L31, Night Slash L40→L36, Cross Chop L48→L46 |
| Barbaracle | Dual Chop L1, Smack Down L9, Rock Blast L39, Dive L50 | Water Gun L4→L1, Fury Swipes L16→L6, Clamp L20→L19, Rock Polish L24→L21, Rock Slide L28→L26, Razor Shell L36→L31, Night Slash L42→L36, Cross Chop L52→L46 |
| Skrelp | Twister L15, Dragon Tail L29, Gunk Shot L50 | Tail Whip L13→L5, Camouflage L33→L17, Water Pulse L29→L21, Aqua Tail L45→L34 |
| Dragalge | Foul Play L1, Gunk Shot L50, Dragon Dance L59, Sludge Wave L63 | Tail Whip L13→L1, Camouflage L33→L17, Water Pulse L29→L21, Aqua Tail L45→L34, Outrage L66→L54 |
| Clauncher | Vacuum Wave L22, Dragon Pulse L39, Agility L42, Dark Pulse L45 | Hone Claws L29→L10, Aqua Jet L17→L12, Bubble Beam L25→L17, Smack Down L21→L20, Water Pulse L33→L28, Aura Sphere L41→L32 |
| Clawitzer | Vacuum Wave L22, Agility L42, Hyper Beam L55 | Vice Grip L5→L1, Hone Claws L29→L10, Aqua Jet L17→L12, Bubble Beam L25→L17, Smack Down L21→L20, Water Pulse L33→L28, Muddy Water L58→L49 |
| Helioptile | Mud Bomb L33, Eerie Impulse L40 | Charge L16→L4, Swift L32→L22, Thunder Wave L36→L25, Electrify L44→L28, Hyper Voice L48→L38 |
| Heliolisk | Mud Bomb L33, Sunny Day L47, Rain Dance L47, Weather Ball L52 | Hyper Voice L48→L38 |
| Tyrunt | Slam L10, Rock Throw L13, Fire Fang L28, Ice Fang L28, Thunder Fang L28, Hyper Fang L41 | Stomp L24→L8 |
| Tyrantrum | Dragon Rush L1, Slam L10, Rock Throw L13, Fire Fang L28, Ice Fang L28, Thunder Fang L28, Hyper Fang L41, Outrage L55 | Stomp L24→L1, Horn Drill L54→L51 |
| Amaura | Avalanche L30, Power Gem L36, Moonlight L45 | Mist L20→L3, Aurora Beam L24→L19, Hail L48→L27, Ice Beam L40→L39, Blizzard L52→L50, Hyper Beam L56→L55 |
| Aurorus | Wide Guard L1, Avalanche L30, Power Gem L36, Tri Attack L41, Moonlight L45, Stone Edge L60 | Mist L20→L1, Aurora Beam L24→L19, Hail L54→L27, Ice Beam L42→L39, Light Screen L48→L47, Blizzard L60→L50, Hyper Beam L66→L55 |
| Sylveon | Lucky Chant L1, Jump Kick L1, Confide L1, Double Kick L14, Wrap L25, Amnesia L32, Encore L48, Hyper Voice L52 | Sand Attack L5→L4, Quick Attack L10→L6, Swift L20→L12 |
| Hawlucha | Rolling Kick L17, Endure L24 | Submission L24→L1, Encore L16→L1, Wing Attack L4→L1, Aerial Ace L12→L11, Endeavor L52→L14, Sky Drop L54→L20, High Jump Kick L48→L42 |
| Dedenne | Recycle L38, Slack Off L46 | Thunder Wave L19→L1, Thunder Shock L12→L5, Charge L9→L8, Charm L16→L11, Entrainment L26→L19, Snore L37→L30, Discharge L44→L41 |
| Carbink | Helping Hand L1, Fairy Wind L9, Recover L43, Power Split L48 | Stealth Rock L50→L14, Light Screen L30→L24, Power Gem L45→L33, Skill Swap L40→L35, Safeguard L65→L37, Moonblast L55→L40, Stone Edge L60→L46 |
| Goomy | Slam L10, Bubble Beam L18, Acid Armor L32, Recover L52, Outrage L60 | Dragon Pulse L38→L36 |
| Sliggoo | Slam L10, Bubble Beam L18, Acid Armor L32, Recover L52, Outrage L60 | Dragon Pulse L38→L36 |
| Goodra | Slam L10, Bubble Beam L18, Acid Armor L32, Recover L52 | Dragon Pulse L38→L36 |
| Klefki | Iron Head L40, Swagger L47, Metal Burst L50 | Fairy Wind L8→L4, Metal Sound L20→L9, Recycle L28→L21, Imprison L36→L23, Mirror Shot L32→L26, Magic Room L48→L29 |
| Phantump | Vine Whip L3, Mega Drain L15, Echoed Voice L17, Pain Split L53 | Ingrain L40→L11, Destiny Bond L48→L38 |
| Trevenant | Drain Punch L1, Vine Whip L1, Mega Drain L15, Revenge L17, Shadow Punch L30, Pain Split L53 | Ingrain L40→L11, Destiny Bond L48→L38 |
| Bergmite | Skull Bash L33, Icicle Crash L45 | Powder Snow L6→L1, Sharpen L9→L7, Ice Ball L27→L14, Curse L47→L21, Avalanche L50→L30, Iron Defense L54→L36 |
| Avalugg | Ice Shard L1, Block L36, Icicle Crash L45, Sheer Cold L60 | Ice Ball L27→L14, Curse L56→L21, Avalanche L51→L30, Recover L64→L48 |
| Noibat | Twister L11, Dragon Breath L26, Uproar L37, Dragon Pulse L42, Boomburst L57 | Air Cutter L24→L20, Whirlwind L28→L23, Air Slash L36→L31, Hurricane L52→L51 |
| Noivern | Twister L11, Dragon Breath L26, Uproar L37 | Air Cutter L24→L20, Whirlwind L28→L23, Air Slash L36→L31 |
| Yveltal | Heal Block L1, Leech Life L1, Chip Away L10, Perish Song L20, Destiny Bond L55, Final Gambit L75 | Sky Attack L80→L1, Foul Play L60→L35, Phantom Force L55→L50, Hyper Beam L90→L70 |
| Zygarde | Fissure L1, Dragon Tail L25, Pain Split L70 | Safeguard L14→L1, Camouflage L53→L5, Crunch L41→L35, Dragon Pulse L65→L45, Extreme Speed L77→L50, Coil L71→L60, Outrage L89→L65 |
| Diancie | Play Rough L1, Healing Wish L1, Magic Coat L1, Fairy Wind L9, Mirror Coat L30, Trick Room L43, Power Split L48 | Ancient Power L28→L12, Stealth Rock L70→L14, Light Screen L42→L24, Power Gem L63→L28, Skill Swap L56→L35, Safeguard L98→L37, Stone Edge L84→L40, Moonblast L77→L46 |
| Volcanion | Whirlpool L1, Flame Burst L26, Lava Plume L40, Soak L55 | Stomp L42→L1, Leer L6→L4, Flame Charge L18→L10, Water Pulse L24→L17, Scary Face L30→L28, Explosion L96→L46, Overheat L90→L60 |
| Mr. Mime |  | Role Play L26→L3, Meditate L14→L5, Double Slap L11→L10, Encore L20→L12, Reflect L50→L18, Light Screen L50→L18, Substitute L41→L27, Recycle L38→L30, Trick L44→L32, Safeguard L50→L47 |
| Clamperl |  | Shell Smash L50→L40 |
| Skorupi |  | Pursuit L12→L5, Bug Bite L15→L9, Acupressure L45→L12, Poison Jab L48→L31, Night Slash L39→L37, X-Scissor L42→L40 |
| Magnezone |  | Screech L24→L19, Magnet Rise L34→L28, Discharge L39→L37, Gyro Ball L57→L45, Light Screen L53→L47, Lock-On L62→L50 |
| Scatterbug |  | Stun Spore L6→L5, Bug Bite L15→L8 |

</details>

Engine learnset caps may stop adds short of this list (never overflow); Legacy learnset adds never remove a move.

### Planned: evolution changes (62)

- Poliwag → Poliwhirl: level 25 → 18 (yellow)
- Goldeen → Seaking: level 33 → 26 (xy)
- Spinarak → Ariados: level 22 → 21 (crystal)
- Pineco → Forretress: level 31 → 25 (crystal)
- Slugma → Magcargo: level 30 → 27 (crystal)
- Ralts → Kirlia: level 20 → 16 (emerald)
- Aron → Lairon: level 32 → 28 (emerald)
- Meditite → Medicham: level 37 → 33 (emerald)
- Trapinch → Vibrava: level 35 → 30 (xy)
- Vibrava → Flygon: level 45 → 42 (emerald)
- Venonat → Venomoth: level 31 → 28 (xy)
- Psyduck → Golduck: level 33 → 28 (xy)
- Swablu → Altaria: level 35 → 30 (xy)
- Glameow → Purugly: level 34 → 32 (xy)
- Stunky → Skuntank: level 34 → 28 (xy)
- Finneon → Lumineon: level 31 → 28 (xy)
- Pidove → Tranquill: level 21 → 19 (xy)
- Sandile → Krokorok: level 29 → 27 (xy)
- Dwebble → Crustle: level 34 → 32 (xy)
- Scraggy → Scrafty: level 39 → 36 (xy)
- Trubbish → Garbodor: level 36 → 31 (xy)
- Gothita → Gothorita: level 32 → 28 (xy)
- Solosis → Duosion: level 32 → 28 (xy)
- Foongus → Amoonguss: level 39 → 34 (xy)
- Joltik → Galvantula: level 36 → 33 (xy)
- Klink → Klang: level 35 → 29 (xy)
- Tynamo → Eelektrik: level 39 → 35 (xy)
- Elgyem → Beheeyem: level 42 → 35 (xy)
- Litwick → Lampent: level 41 → 28 (xy)
- Axew → Fraxure: level 38 → 34 (xy)
- Mienfoo → Mienshao: level 46 → 41 (xy)
- Pawniard → Bisharp: level 52 → 39 (xy)
- Rufflet → Braviary: level 50 → 42 (xy)
- Vullaby → Mandibuzz: level 50 → 42 (xy)
- Deino → Zweilous: level 50 → 35 (xy)
- Zweilous → Hydreigon: level 64 → 60 (xy)
- Larvesta → Volcarona: level 59 → 47 (xy)
- Litleo → Pyroar: level 35 → 32 (xy)
- Binacle → Barbaracle: level 36 → 35 (xy)
- Skrelp → Dragalge: level 48 → 37 (xy)
- Goomy → Sliggoo: level 40 → 30 (xy)
- Noibat → Noivern: level 48 → 40 (xy)
- Kadabra → Alakazam: **added** method level (42) (yellow)
- Machoke → Machamp: **added** method level (38) (yellow)
- Graveler → Golem: **added** method level (38) (yellow)
- Haunter → Gengar: **added** method level (42) (yellow)
- Rhydon → Rhyperior: **added** method held_day (Protector) (xy)
- Rhydon → Rhyperior: **added** method held_night (Protector) (xy)
- Electabuzz → Electivire: **added** method held_day (Electirizer) (xy)
- Electabuzz → Electivire: **added** method held_night (Electirizer) (xy)
- Magmar → Magmortar: **added** method held_day (Magmarizer) (xy)
- Magmar → Magmortar: **added** method held_night (Magmarizer) (xy)
- Eevee → Glaceon: **added** method item (Dawn Stone) (xy)
- Murkrow → Honchkrow: **added** method move (Beat Up) (xy)
- Dusclops → Dusknoir: **added** method held_night (Reaper Cloth) (xy)
- Boldore → Gigalith: **added** method level (40) (xy)
- Gurdurr → Conkeldurr: **added** method level (40) (xy)
- Karrablast → Escavalier: **added** method party (Shelmet) (xy)
- Karrablast → Escavalier: **added** method party (Accelgor) (xy)
- Shelmet → Accelgor: **added** method party (Karrablast) (xy)
- Shelmet → Accelgor: **added** method party (Escavalier) (xy)
- Inkay → Malamar: **added** method move (Topsy-Turvy) (xy)

Skipped (engine lacks it): Tyrogue -> Hitmontop: item Brick Piece not found in this engine; Lampent -> Chandelure: engine has no "level_night" method (no probe species uses it); Phantump -> Trevenant: move Forest’s Curse not in this engine
