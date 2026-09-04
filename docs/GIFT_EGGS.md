# GIFT EGGS — Unbound v2.1.1.1

**5 `giveegg` sites, all reachable from dialogue, all GATED** by
`tools/character_mode/egg_hook.py`. Measured 2026-09-03. Pinned by
`tools/tests/check_gift_eggs.py` (5 checks, negative-tested 7/7).

This repo is the worked example the other three ports are measured against: it
is the only one of the four that hooks the hatch, and its own hook summary
calls that hole *"the one enforcement hole reachable in ordinary play"*.

| site | source | what it gives |
|---|---|---|
| `0x08773833` | *"Please take good care of it. It is a very special Egg."* | species **175** (Togepi) |
| `0x09E6A69B` | the same script, upper-half mirror region | species **175** |
| `0x09E72474` | the tomb-treasure reward — *"you found all of the treasure hidden in the tomb!"* | species **689** |
| `0x09E7B3A6` | **the Day-Care Man's sister**, whose job is *"to give away Eggs Trainers did not want to keep"* | VAR 0x800D — a computed species |
| `0x09EAE4EE` | *"Take this Egg, too."* | species **239** |

⭐ The fourth entry is why the hook is the right shape: its species is not a
literal anywhere, so no inventory of `giveegg` operands could ever enumerate
what it gives. Gating the **hatch** covers it without knowing.

## How this was measured, and the primitive that does NOT work

`tools/tests/check_gift_eggs.py` is the tool; run it, it is fast and needs
nothing but the base ROM and this repo's own donor tree.

⭐ **The obvious scan is useless, and knowing why is the transferable part.**
`giveegg` is opcode `0x7A` followed by a `u16`. Scanning a ROM for that byte
pattern with a plausible species operand gives, measured on Radical Red,
**3,249 raw candidates**. Filtering on "some aligned ROM word points into the
512 bytes before it, and the script decodes cleanly forward to a terminator"
cuts that to **116** — of which, on inspection, **zero were real**. Script
bytecode is not word-aligned (so an aligned-pointer filter has false negatives
as well as false positives) and one command in isolation is indistinguishable
from data.

✅ **What works is an anchor data cannot cheaply fake**: the byte pair `0F 00`
(`loadword` into destination 0) followed by a ROM pointer whose target decodes
as Gen 3 text. Every dialogue script contains one. Decode linearly from each
anchor, follow `goto`/`call`/`goto_if`/`call_if`, and record every `giveegg`
reached. That is a reachability claim about the script graph, not a byte
pattern. **It was validated on a known positive before it was believed** — the
stock Emerald Lavaridge hot-spring script, which decodes to `giveegg 360`
(Wynaut) in both Emerald ports.

⚠️ **AND THE TEXT SEARCH FOUND WHAT THE OPCODE SCAN CANNOT.** Radical Red's egg
vendor advertises *"a Wonder Egg that just contains a random first form
Pokemon"*; a species that is **computed in native code never appears as a
`giveegg` operand at all**. The inventory is a **floor on the reachable gift
eggs, not a ceiling**. Two independent primitives were used here — decode the
script graph, and read the game's own dialogue — and each found sites the other
did not.

## What this inventory does NOT cover

- **Day Care breeding.** Deliberately out of scope and believed safe: a roster
  stores whole evolution families and only on-roster parents can be kept, so
  offspring are on-roster by construction. Gift eggs are the way in.
- **Eggs whose species is computed in native code** (see above).
- **Whether each script is actually placed on a reachable map.** The scan
  proves the script exists and is entered from dialogue; it does not walk map
  event tables. For the custom content below that is not in doubt (the NPCs
  have their own new dialogue, flags and object removal), but the two stock
  Emerald hot-spring scripts are marked as inherited and their map placement is
  **unverified**.

## If the hook is ever removed or moved

Flip the verdicts to UNGATED **and** clear `HATCH_HOOK` in
`tools/tests/check_gift_eggs.py`. The checker's fifth check fails if only one
of those two happens — a verdict of GATED is a claim about this repo's code,
not about the ROM.
