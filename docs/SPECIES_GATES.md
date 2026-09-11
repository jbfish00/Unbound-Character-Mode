# SPECIES GATES — Unbound v2.1.1.1

**6 decoded gate(s) out of 76 ChoosePartyMon call sites** (26
of them reachable from a dialogue anchor). Measured 2026-09-11; pinned by
`tools/tests/check_species_gates.py` (7 checks, negative-tested).

A *species gate* is an NPC that wants a Pokémon **shown** rather than traded:
it calls `ChoosePartyMon`, tests what you handed it, and gives something back.
It matters to Character Mode because the PC-withdraw fix (`rowe_parity.md`
§13.26c, option 1) sweeps an off-roster Pokémon back into the PC the moment
you leave the storage system, so you can no longer carry one to an NPC.
§13.28 counted these NPCs and said plainly that **nobody had decoded what any
of them give**, leaving the cost an upper bound. This is the decode.

## The verdict

**Four of the six are inert without the species. The other two are the whole
measured cost of this class across all four games.** The Oddish scientist's
**Dream Mist** and Mr. Sun's **TM11** are generic rewards; TM11 has no other
source in this ROM at all — no mart among the 33 scanned sells it and no other
script gives it. Both gates need a species the catch gate already refuses, and
the Oddish one needs **thirty** of them. ⚠️ Stated precisely: this bounds the
cost rather than proving it zero — whether an in-game trade or the Day-Care
sister's computed egg could still put an Oddish or a Solrock in the PC is not
established here. Either way it is one TM.

## The gates

| site | NPC | gate | what it actually gives | verdict |
|---|---|---|---|---|
| `0x088AA2C2` | Deoxys meteorite — *"bring the Deoxys in your party closer to the meteorite?"* | Deoxys, tested in **native code** (`callasm 0x088AB3CD`) | a **form change** | `SPECIES_LOCKED` |
| `0x09E68C86` | Oddish scientist — *"Which Oddish will you give me?"*; **CONSUMES the Pokémon**, counting into var `0x5029` up to 30 | Oddish (43) | one **Dream Mist** (item 89 at `0x09E68DD7`) | `CATCH_ONLY` — and thirty Oddish must be handed over, each one caught |
| `0x09E8569C` | Mr. Sun — *"Oh Mr. Sun, Sun, Mr. Golden Sun, please shine down on me"* | Solrock (349), Solgaleo (1008) | **TM11** (item 299 at `0x09E856DC`) — no mart among 33 scanned, no other scripted source | `CATCH_ONLY` — the Solrock or Solgaleo must be caught |
| `0x09E8EB95` | Pichu girl — *"Why don't you take the one I found, too?"* | Pichu (172), spiky-eared Pichu (1100) | a **gift Pokémon**: `givepokemon` species 1100 at level 50 holding a Light Ball, at `0x09E8EC25` | `SPECIES_LOCKED` — only a character who already keeps Pichu can open it |
| `0x09EB02A7` | Zygardia / Zygfried — *"Which Zygarde's Ability should I change?"* | Zygarde (826, 837) | special moves and an **ability change** | `SPECIES_LOCKED` |
| `0x09EB086A` | Zygardia — *"Would you like to change the form of your Zygarde?"* | Zygarde (826, 837) | a **form change**; the disassembler at `0x09EB0723` tests the construct natively | `SPECIES_LOCKED` |

⚠️ **Two of §13.28's five were found for the wrong reason.** The Rotom
appliance sites (`0x088AA9D1`, `0x088AAA11`) and two more Deoxys meteorite
sites (`0x088AA485`, `0x088AA4C5`) are **not reachable from any dialogue
anchor** — the walk that produced the count of 5 never saw them. They are
Rotom and Deoxys **form changes**, so the verdict is unchanged, but the count
was not measuring what it claimed.

## Why the raw count was never a count

`rowe_parity.md` §13.28 published **5 / 5 / 2 / 0** species gates for Radical
Red / Unbound / Lazarus / Seaglass, found by decoding forward from dialogue
anchors — the same primitive `check_gift_eggs.py` uses, and the right one
there. It is the wrong one here. Measured 2026-09-11, that walk reaches:

| game | ChoosePartyMon call sites in the ROM | reachable from a dialogue anchor |
|---|---|---|
| Radical Red | **43** | 20 |
| Unbound | **76** | 26 |
| Lazarus | **19** | 3 |
| Seaglass | **11** | 2 |

So between 47% and **84%** of the call sites were never seen. The sites the
walk misses are real — Name Rater, move tutors, the *"Hunh? Your BAG is
crammed full."* item NPCs, and in Unbound four more sites of the Deoxys
meteorite and the Rotom appliances, two of the very NPCs §13.28 named. ⭐ **The
better primitive is the call site itself**: `special <ChoosePartyMon>`
immediately followed by `waitstate`, which every real site has and which no
dialogue reachability question can hide. `tools/tests/check_species_gates.py`
pins the whole set that way.

⚠️ **This document does not claim every one of those sites has been decoded.**
The ones that have are in the table above; the rest are pinned by address, so
a new one cannot arrive silently, and a decode of the remainder is open work.

## Three false-positive constants, all of which decode as a species

Each sits immediately after a `ChoosePartyMon` and looks exactly like a
species gate:

- **255** — `PARTY_NOTHING_CHOSEN` in the Emerald pair. Decodes as Torchic.
- **412** — `SPECIES_EGG` in the FireRed pair. Decodes as Bad Egg.
- **a small value inside a BP facility is the PRICE IN BP**, not a species.
  Five Unbound sites compare 16, 25 or 27 right after the choice; those decode
  as Pidgey, Pikachu and Sandshrew, and all five are Battle-Frontier-style
  services whose own dialogue says *"You don't have enough BP"*.

## A species test can be invisible to every compare scan

Four of the gates in this workspace test the species in **native code**, so
the species id never appears as a script operand at all:

| game | NPC | where the test lives |
|---|---|---|
| Radical Red | Heracross size judge | `special 0x78` |
| Radical Red | gender swapper | `callasm 0x09077B59` |
| Unbound | Deoxys meteorite | `callasm 0x088AB3CD` |
| Unbound | Rotom appliances | `callasm 0x088AABB9` / `0x088AACCD` |
| Seaglass | DEOXYS magic trick | `special 0x224` |

They are in the inventory because the **dialogue** was decoded, not because a
scan found them. Any future count of this class is a floor for the same
reason `check_gift_eggs.py` documents for `giveegg`.

## Re-running it

```bash
python3 tools/tests/check_species_gates.py                   # the inventory
python3 tools/tests/check_species_gates_negative_test.py     # break it on purpose
```

The checker reads the **base ROM** and this repo's own vendored
`tools/charmap.txt`; it builds nothing and changes nothing.
