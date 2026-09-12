# SPECIES GATES — Unbound v2.1.1.1

**76 `ChoosePartyMon` call sites, 34 classified, 26 of them
real species gates.** Only **26** of the call sites are reachable from a
dialogue anchor, which is why every earlier count of this class was wrong.
Measured 2026-09-11; pinned by `tools/tests/check_species_gates.py` (7 checks,
negative-tested).

A *species gate* is an NPC that wants a Pokémon **shown** rather than traded:
it calls `ChoosePartyMon`, tests what you handed it, and gives something back.

## The verdict

🔴 **This game is where the class actually costs something.** Fourteen of its
twenty-six gates are inert without the species, and five more give an item this
ROM sells or gives again — but **seven give a generic item with no mart entry
and no other scripted source found**: an **Eviolite**, a **Moon Stone**, an
**Air Balloon**, a **Destiny Knot**, **TM11**, **Dream Mist**, and the Alolan
evolution stones. A character who cannot keep Basculin, Alolan Sandshrew,
Drifloon, Pichu, Solrock or Oddish cannot reach those items at all.
⚠️ **What this does NOT say is that the PC-withdraw hook took them.** Every one
of these gates wants a species you have to CATCH, and Character Mode's catch
gate already refused an off-roster catch long before the PC hook existed. This
is a cost of Character Mode itself. The hook's own incremental cost is confined
to gate species that can reach the PC *without* being caught — a gift, an egg
or a trade — which nobody has enumerated.

## Every classified site

| site | what it is | gate species | rewards seen in its window | verdict |
|---|---|---|---|---|
| `0x0816ffb0` | Magikarp size judge | Magikarp (129) | Net Ball ×1 | `ELSEWHERE` |
| `0x0879422c` | Hoopa -- MASTER BALL (low-ROM copy) | Hoopa (828), Hoopa (829) | Master Ball ×1 | `ELSEWHERE` |
| `0x087a82d3` | Happiny -- Oval Stone | Happiny (493) | Oval Stone ×1 | `SPECIES_LOCKED` |
| `0x088aa2c2` | Deoxys meteorite (native test, callasm 0x088AB3CD) | Deoxys (410) | — | `SPECIES_LOCKED` |
| `0x088aa485` | Kyurem FUSION -- "There is no Kyurem in the party!", "Multiple fusions are not allowed!"; NOT dialogue-reachable. Labelled Deoxys at first by PROXIMITY to the meteorite script, which is exactly the mistake the PC-hook work already recorded: the discriminator is the text, not the neighbourhood | Kyurem (699) | — | `SPECIES_LOCKED` |
| `0x088aa4c5` | Kyurem separation, the same NPC -- NOT dialogue-reachable | Kyurem (699) | — | `SPECIES_LOCKED` |
| `0x088aa9d1` | Rotom appliance (native test) -- NOT dialogue-reachable | *tested in native code* | — | `SPECIES_LOCKED` |
| `0x088aaa11` | Rotom appliance, second site -- NOT dialogue-reachable | *tested in native code* | — | `SPECIES_LOCKED` |
| `0x088c0ff1` | one of six identical per-slot stubs; the species in the window belong to a neighbouring table | Egg (252), Maractus (609), Dwebble (610), Crustle (611), Scraggy (612) +1 | — | `NOT_A_GATE` |
| `0x088c1006` | per-slot stub | Egg (252), Maractus (609), Dwebble (610), Crustle (611), Scraggy (612) +1 | — | `NOT_A_GATE` |
| `0x088c101b` | per-slot stub | Egg (252), Maractus (609), Dwebble (610), Crustle (611), Scraggy (612) +1 | — | `NOT_A_GATE` |
| `0x088c1030` | per-slot stub | Egg (252), Maractus (609), Dwebble (610), Crustle (611), Scraggy (612) +2 | — | `NOT_A_GATE` |
| `0x088c1045` | per-slot stub | Egg (252), Maractus (609), Dwebble (610), Crustle (611), Scraggy (612) +3 | — | `NOT_A_GATE` |
| `0x088c105a` | per-slot stub | Egg (252), Maractus (609), Dwebble (610), Crustle (611), Scraggy (612) +5 | — | `NOT_A_GATE` |
| `0x088c1151` | per-slot stub family, second group | Carracosta (618), Archen (619), Archeops (620), Oricorio (958), Oricorio (1043) +2 | — | `NOT_A_GATE` |
| `0x09e57739` | Basculin -- EVIOLITE | Basculin (603) | Eviolite ×1, Ice Stone ×1 | `UNIQUE` |
| `0x09e607fd` | Alolan Sandshrew / Sandslash -- Ice Stone, and a Moon Stone in the same window | Sandshrew (1023), Sandslash (1024) | Ice Stone ×1, Moon Stone ×1 | `UNIQUE` |
| `0x09e63112` | the floating-Pokemon NPC, first site | Igglybuff (174), Drifloon (478), Drifblim (479), Pikachu (1086) | — | `UNIQUE` |
| `0x09e63191` | the floating-Pokemon NPC -- "I'll give you the item, Air Balloon!" | Igglybuff (174), Drifloon (478), Drifblim (479), Pikachu (1086) | Air Balloon ×1 | `UNIQUE` |
| `0x09e68c86` | Oddish scientist -- CONSUMES thirty Oddish, gives Dream Mist | Oddish (43) | Dream Mist ×1 | `UNIQUE` |
| `0x09e69879` | Hoopa -- MASTER BALL (high-ROM copy) | Hoopa (828), Hoopa (829) | Master Ball ×1, Good Rod ×1, Max Repel ×3 | `ELSEWHERE` |
| `0x09e6a780` | Happiny -- Oval Stone (second site) | Happiny (493) | — | `SPECIES_LOCKED` |
| `0x09e6a890` | Happiny -- Oval Stone / Everstone (third site) | Happiny (493) | Oval Stone ×1 | `SPECIES_LOCKED` |
| `0x09e6b2e9` | Butterfree named in flavour text only | Butterfree (12) | — | `NOT_A_GATE` |
| `0x09e7b1cc` | Furfrou trimmer | Furfrou (784) | — | `SPECIES_LOCKED` |
| `0x09e7b2e8` | Furfrou trimmer, second site | Furfrou (784) | — | `SPECIES_LOCKED` |
| `0x09e821fe` | Sneasel -- Luck Incense | Sneasel (215) | Luck Incense ×1 | `ELSEWHERE` |
| `0x09e8569c` | Mr. Sun -- Solrock / Solgaleo, TM11 | Solrock (349), Solgaleo (1008) | TM11 ×1 | `UNIQUE` |
| `0x09e8e901` | Pumpkaboo size judge -- 5 Dusk Balls and a Bottle Cap | Pumpkaboo (818) | Dusk Ball ×5, Bottle Cap ×1 | `ELSEWHERE` |
| `0x09e8eaed` | Pichu -- DESTINY KNOT | Pichu (172), Pichu (1100) | Destiny Knot ×1 | `UNIQUE` |
| `0x09e8eb95` | Pichu -- a gift Pichu (givepokemon 1100 L50 @Light Ball, 0x09E8EC25) | Pichu (172), Pichu (1100) | — | `SPECIES_LOCKED` |
| `0x09eb02a7` | Zygardia / Zygfried -- moves and ability | Zygarde (826), Zygarde (837) | — | `SPECIES_LOCKED` |
| `0x09eb0723` | Zygardia -- disassemble the construct | Zygarde (826) | — | `SPECIES_LOCKED` |
| `0x09eb086a` | Zygardia -- form change | Zygarde (826), Zygarde (837) | — | `SPECIES_LOCKED` |

`CANDIDATE` means a species is named in the dialogue or compared in the window
and **nobody has read the script yet**. Rewards are those found between this
call site and the next one; that is a window, not a proof of reachability,
except for the gates whose scripts were decoded by hand (every
`SPECIES_LOCKED`, `ELSEWHERE` and `UNIQUE` row).

## Which of these can be opened WITHOUT catching the species

This is the only part of the class the **PC-withdraw hook** can be blamed for.
Character Mode's catch gate has always refused an off-roster catch, so a gate
whose species you could only catch was already unreachable before the hook
existed. A gate species that arrives as a **gift**, an **egg**, a **trade** or
from the game's own **starter picker** lands in the party, is swept into the PC
by enforcement — and before the hook shipped could be withdrawn and shown to
the NPC.

🔴 **Three gates, and two of them are the only real cost of the PC-withdraw
hook found in any of the four games.**

- **The floating-Pokémon NPC** (`0x09E63191`, and its first site
  `0x09E63112`) accepts Pikachu **1086** — and the game *gifts* that very
  species at `0x09E6F7B5`, level 35. Its reward, an **Air Balloon**, has no
  mart entry and no other scripted source. **Real cost.**
- **The Pichu gate** (`0x09E8EAED`) accepts Pichu 1100, which the Pichu girl
  gifts at `0x09E8EC25` (level 50, holding a Light Ball). Its reward, a
  **Destiny Knot**, likewise has no other source. **Real cost.**
- `0x09E8EB95` is that same gift NPC; its reward is *another Pichu*, so it is
  inert without the species either way.
- **The Oddish scientist** (`0x09E68C86`) accepts Oddish, and Oddish is one of
  three species in a pick-one gift at `0x0826D677` — but the scientist consumes
  **thirty** Oddish and the gift grants one, so it stays out of reach.

⚠️ This is also the only port whose in-game trades **complete** (the incoming
mon is swept to the PC rather than the trade being refused), so all nine trade
species are a non-catch route here — none of them happens to be a gate
species.

Pinned by two checks in `tools/tests/check_species_gates.py`: the in-game trade
table is verified by content (a moved or edited table fails), and every gift
that opens a gate must still be that `givemon`. ⚠️ The routes are a **floor**:
a species handed out by native code, or an egg whose species is computed,
appears in no operand anywhere. `rowe_parity.md` §13.42.

## What "UNIQUE" is a floor of, not a proof

`UNIQUE` means: the item appears in **no `pokemart` table in this ROM** and at
**no other site matching the three-command give-item idiom**
(`setorcopyvar 0x8000,item; setorcopyvar 0x8001,qty; callstd 0`). Three sources
are invisible to both scans and would each falsify it — a **ground item**
(the item id lives in the map's object data, not in a script), an item handed
out by **native code**, and **Pickup**. Treat `UNIQUE` as "no cheap source
found", the same way `check_gift_eggs.py` treats its inventory as a floor.

## Why every earlier count of this class was wrong

`rowe_parity.md` §13.28 published **5 / 5 / 2 / 0** species gates for Radical
Red / Unbound / Lazarus / Seaglass. §13.37 then decoded those and concluded the
class costs one TM. Both numbers came from sites reachable by a
**dialogue-anchored walk** — the primitive `check_gift_eggs.py` uses, and the
correct one there. It is the wrong primitive here, measurably:

| game | `ChoosePartyMon` call sites | reachable from a dialogue anchor |
|---|---|---|
| Radical Red | **43** | 20 |
| Unbound | **76** | 26 |
| Lazarus | **19** | 3 |
| Seaglass | **11** | 2 |

⚠️ **And decoding only the reachable subset reproduced the same error one level
down**: §13.37 read the walk-reachable gates, found them all inert or cheap,
and generalised to the class. The sites it never opened contain a Master Ball,
an Eviolite, a Moon Stone, an Air Balloon, a Destiny Knot, a Rare Candy, a
Protein and two Elixirs. **The fix is to enumerate on the call site itself**
(`special <ChoosePartyMon>` followed by `waitstate`), which is what the checker
now pins.

## Two primitives, because each is blind where the other sees

- **A species COMPARE** in the window after the call. Blind whenever the test
  lives in native code — Radical Red's Heracross judge (`special 0x78`) and
  gender swapper (`callasm`), Unbound's Deoxys and Rotom (`callasm`), and
  Seaglass's DEOXYS trick (`special 0x224`) have no species operand at all.
- **A species NAMED in the surrounding dialogue**, matched against this ROM's
  own species-name table. Blind whenever the NPC never says the name, and
  blind to species a curated dex has removed — Lazarus's own big-SEEDOT judge
  is invisible to it, because Seedot is not in Lazarus's dex.

## Four false-positive constants, each of which decodes as a species

- **255** — `PARTY_NOTHING_CHOSEN` in the Emerald pair. Decodes as Torchic.
- **412** — `SPECIES_EGG` in the FireRed pair. Decodes as Bad Egg.
- **`SPECIES_EGG` in the Emerald pair is PER-ROM**, one past that ROM's own
  species table: **1561** in Lazarus, **1524** in Seaglass. The Name Rater and
  the egg kid compare it in both games.
- **A small value after the choice is a PRICE or a SCORE, not a species.**
  Inside a BP facility it is the price in BP (five Unbound sites compare 16, 25
  or 27 — Pidgey, Pikachu, Sandshrew); inside an **IV judge** it is an IV
  total (both Emerald ports compare **120 / 150 / 151** — Staryu, Mewtwo, Mew).

## Re-running it

```bash
python3 tools/tests/check_species_gates.py                   # the inventory
python3 tools/tests/check_species_gates_negative_test.py     # break it on purpose
```

Both read the **base ROM** and this repo's own vendored `tools/charmap.txt`;
they build nothing and change nothing.
