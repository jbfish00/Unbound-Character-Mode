# Routine Map — Pokemon Unbound (v2.1.1.1).gba

## Flag/var persistence — CAVEAT CLOSED (2026-07-17 v12)

The v8-era worry ("range-clearing loops wouldn't show in static reference scans; do 0x18F8/0x51FC survive day-rollover and save/load?") is resolved both ways:

**Static — every flag range-clear loop in the shipped binary is bounded away from 0x18F8:**
- Daily events: `ClearDailyEventFlags` clears `0xE00`–`0xEFF` (CFRU `FLAG_DAILY_EVENTS_START` + 0x100; donor `src/wild_encounter.c`).
- Raid flags (the close call): CFRU clears `FIRST_RAID_BATTLE_FLAG 0x1800 + KANTO_MAPSEC_COUNT` daily. **Shipped bound read from the binary**: compiled `ClearAllRaidBattleFlags` at ROM `0x089DC0F4` — loop from 0x1800, exit compare literal **0x186D** (= stock count 0x6D, Unbound did NOT extend it). Clears `0x1800`–`0x186C`; our 0x18F8 has 0x8B headroom. A second Unbound-custom copy (file 0x1EC2250 region) uses the same 0x6D count.
- Method: all 38 `FlagClear|1` (0x0806E6A9) literal-pool sites were disassembled and screened for inc+compare+back-branch loop shapes; no other loop's bound reaches 0x18F8. No daily/rollover var range-clears exist (only individual VarSets on 0x5009/0x500E etc.).
- Useful trick: compiled code builds constants like 0x1800/0xE00 via `movs`+`lsls`, NOT pool literals — scan for function-pointer literals (who is called) rather than range constants (what is passed).

**Live — full save/load round trip green** (`tools/test_harness/run_persistence_test.sh`, 9/9): free-roam → flag 0x18F8 + var 0x51FC=42 + var 0x51FA=0x1234 set in the expanded-save EWRAM → **vanilla `TrySavingData(SAVE_NORMAL)` = `0x080DA364`** (BPRE.ld) called via register hijack (r0=0, lr parked at CharacterMode_SelfTestDone) → 0 damaged sectors → emulator killed (SIGTERM flushes .sav) → rebooted → CONTINUE → all three values intact. Confirms CFRU's expanded flag/var save region covers our allocations across a real save file.

New-game clearing is a non-issue by construction: the expanded-save init runs before the intro prompt sets our state (proven by the organic gold test reaching the overworld with state intact).

## New-game intro flow + opt-in splice v2 — ORGANIC REACH SOLVED (2026-07-17 v11)

**CORRECTION to v8.1/v9**: the "3 native tables referencing script entry 0x09E70000" (file 0x0253FDE / 0x038F94A / 0x0A7A19E) are **false positives** — two are adjacent-entry straddles inside a monotonically increasing exp-curve table (`… 00 00 | E7 09 00 00 | …`), one is compressed-graphics garbage. There are NO real code/data references to 0x09E70000. Trust repeated exact-target pointer hits; distrust one-off unaligned hits inside data-looking regions.

**The difficulty flow is Unbound's new-game intro speech** (script complex ~0x1E6F9xx–0x1E701xx; neighbors below ~0x1E6F800 are unrelated Game Corner scripts): "Welcome to Pokémon Unbound!" → appearance/trim pick → player naming → **`setflag 0x0001` @0x1E6FBE6** → play-style questionnaire → difficulty recommendation + pick (Vanilla/Difficult/Expert/Insane/Challenging) → converges at the gate below. Key structure at the gate region (hand-decoded, 0x1E6FEF0–0x1E70003):
- level-cap note msg → `compare 0x50DF,0; goto_if NE -> 0x1E6FF2A` (optional-cap yesno only for difficulty 0)
- **0x1E6FF2D: `checkflag 0x0001; goto_if TRUE -> 0x09E7019D`** — flag 1 was just set by the questionnaire, so EVERY first-run new game takes this skip; the fall-through (level-cap/Sandbox/enhancement-options region incl. the old v1 splice site 0x1E70003) only runs on settings-NPC / New-Game-Plus re-entry (temp flag 1 cleared by then). **This is why the v1 splice was never organically reachable** — the enhancement prompt is NOT part of a fresh playthrough.
- 0x1E7019D (first-run continuation): `callasm 0x09ED12E9; goto 0x09E7015B` → story cutscene ("Long ago…").

**Splice v2 (tools/character_mode/optin_script.py)**: the 9 bytes at 0x1E6FF2D are replaced with `call <block>` + 4 nops. The block sets breadcrumb var **0x51FA=0xCA11** (proves reach in blind runs), runs the opt-in yesno → number entry → confirm flow, and both outcomes replay the displaced gate (`checkflag 1; goto_if TRUE -> 0x09E7019D; return`) — byte-identical behavior for both first-run and re-entry paths. Character Mode is deliberately NOT offered on re-entry (the enhancement region is untouched), so mode state can't be toggled mid-game.

**Live-verified**: `run_organic_select_test.sh` 6/6 (fresh save → real intro → prompt appears organically → number typed → mode enabled with valid id → intro continues to overworld with state intact) and `run_organic_intro_test.sh` 3/3 (blind mash: breadcrumb proves reach; cancel/No path continues the intro cleanly).

**Harness facts (hard-won)**:
- The CFRU naming/number screen (sp0B3) **garbles gdb-sliced key presses** (keys register in `heldKeysRaw` but the screen ignores/mangles them — the SIGINT stop/resume around each press breaks its input handling). Yesnos/msgboxes tolerate sliced presses fine. Fix: press keys with clean wall-clock timing during ONE long uninterrupted `continue` (sentinel-file handoff to a background shell typer — see organic_select.gdb / run_organic_select_test.sh).
- Since the splice moved into the first-run path, a blind A-mash intro can wedge in the number-entry validation loop. All live tests now share `tools/test_harness/intro_drive.py` (exec'd from each .gdb): state-machine intro drive that answers **No** at the prompt deterministically; no phase-1 background masher.

## In-game trades — FULLY RESOLVED + HOOKED (2026-07-17 v10)

The last enforcement gap is closed. Unbound's in-game trades (the Borrius Trade Quest) run through **vanilla FireRed trade natives that CFRU never repointed**, wired via specials (resolved through `gSpecials` 0x0815FD60):

| special | native | address |
|---|---|---|
| 0x9F | ChoosePartyMon (slot → 0x8004) | `0x080BF8FD` |
| 0xFC | GetInGameTradeSpeciesInfo (requested species ← trade idx) | `0x08053A9D` |
| 0xFF | GetTradeSpecies (species of party slot 0x8005) | `0x08053D2D` |
| 0xFD | CreateInGameTradePokemon (0x8004=trade idx, 0x8005=slot) | `0x08053D69` |
| 0xFE | DoInGameTradeScene | `0x08054441` |

**`sIngameTrades` survives at vanilla `0x0826CF8C`** — 9 entries × 60 bytes, overwritten in place with Unbound's pairs (received species u16 @+12, requested u16 @+0x38; nickname[11] @+0 charmap): 0 Squirry/Pachirisu 470←Manectric 338, 1 Quacker/Ducklett 633←Alolan Sandshrew 1023, 2 The Top/Hitmontop 237←Lickitung 108, 3 Roly-Poly/Electrode 101←Onix 95, 4 Shin/Shiinotic 973←Amoonguss 644, 5 Among Us/Amoonguss 644←Shiinotic 973, 6 Torch/Lampent 661←Blaziken 282, 7-8 UNUSED (Tangela/Seel). Entries 9+ are unrelated data — the count was NOT expanded.

**Every trade in the ROM executes through exactly three `special 0xFD; special 0xFE; waitstate` junctions** (exhaustive scan; all other 25FD00/25FE00 byte hits are Thumb-code false positives):
1. **`0x1E945A6`** — high-ROM shared execute-trade subroutine `0x1E9459C` (`copyvar 8004←8008; copyvar 8005←800A; special FD; special FE; waitstate; lock; faceplayer; return`), 32 script call sites (`04 9C 45 E9 09`). Sibling subs: picker `0x1E94580` (special 0x9F), requested-species getter `0x1E94570` (special2 0xFC → copied to 0x8009), chosen-species getter `0x1E9458C` (special2 0xFF). NPC scripts branch on `compare 0x800D vs 0x8009` (wrong-species decline) before executing.
2. **`0x1A8CE3`** — identical low-ROM shared subroutine `0x1A8CD9`, 4 call sites (incl. the Master Ball house trade NPC at `0x7C2BE6`).
3. **`0x16E3A8`** — inline junction in a low-ROM script (`setflag 0x275` after; fall-through entry only).

**Hook (tools/character_mode/trade_hook.py, wired by build_patch.py)**: each junction's `25 FE 00 27 …` tail is overlaid with a `goto` into an injected tail script that replays `special 0xFE; waitstate`, inserts **`special 0x1AF`** (dead gSpecials slot, stale `0x0815D835`, repointed to `CharacterMode_SweepPartyToPC`), then finishes the original tail. The scene writes the incoming mon into the traded-away party slot before its waitstate completes, so the sweep sees the final party. ROWE semantics: off-roster non-egg party members → PC, never empties the party, eggs exempt, no-op with Character Mode off.

**Live-verified both directions** (`tools/test_harness/run_trade_test.sh`, 8/8 × 2): trade 2 executed through the real patched junction on a fresh save — as Red (Hitmontop off-roster): party ends [Pikachu], Hitmontop delivered to PC box 0 slot 0; as Bruno (Hitmontop on-roster): party ends [Pikachu, Hitmontop], nothing PC-routed; game healthy after both.

**Facts learned for future harness/RE work**:
- The trade-anim state machine (CB2 `0x08050949` → dispatcher `0x08050F14`; branches on `sTradeData+0x108`, u16 state @+0x94, `sTradeData` ptr at `0x02031DAC`) has **press-A wait states** (state 71 handler polls `gMain.newKeys & A_BUTTON`) — automated runs must keep mashing A through the scene or it wedges forever at state 71.
- **PC storage layout (CFRU dynamic saveblocks)**: `gPokemonStoragePtr` = `0x03005010` (vanilla addr); the box array starts at **storage+0** (no leading currentBox byte); BoxPokemon stride 80, species u16 @+0x20 (unencrypted). Confirmed live by the swept mon landing at storage+0x20.
- `pkill -f` patterns containing the ROM filename kill the invoking shell if the pattern text appears in its own command line — keep such patterns inside script files, not inline bash.


## THE BIG ONE — script & battle dispatch tables located, engine symbol map unlocked (2026-07-12 v8)

**This section supersedes most of the hunting below.** The script-command dispatch table (`gScriptCmdTable`) survives at **vanilla FireRed's exact address `0x0815F9B4`** (file `0x15F9B4`), 0xD6 entries, followed immediately by the special-vars pointer table — byte-identical layout to pret/pokefirered. Found by scanning the ROM for ≥150-entry runs of consecutive Thumb function pointers. From there everything unlocked, because **Unbound leaves the vanilla FR engine core intact and CFRU hooks it surgically** — and `tools/cfru_donor/BPRE.ld` is a full FR symbol map that names every address we extract.

### CRITICAL CORRECTION to v6/v7 opcode labels

The dispatch table proves the standard XSE/pret opcode order — v6 had setflag/checkflag swapped:
- **`0x29` = setflag** (handler `0x0806A82C` → calls `FlagSet 0x0806E680`)
- **`0x2A` = clearflag** (handler `0x0806A840` → calls `FlagClear 0x0806E6A8`)
- **`0x2B` = checkflag** (handler `0x0806A854` → calls `FlagGet 0x0806E6D0`, result → ctx+2)

Re-reading the enhancement-menu script with this fix: the `29 FD 09` right after each Yes-answer **is** the setflag; the batched `2B xx xx` + `06 01 …` sequences later are checkflag→goto_if-TRUE chains (e.g. "if any randomizer enabled, show boss-battle disclaimer"). Everything parses consistently now; v6's claim "0x2B=setflag" was wrong (the 0x9FD flag-id cross-validation was still right — both opcodes touch that same flag).

### Confirmed script-engine symbols (all verified two ways: decompiled handler shape + BPRE.ld name match)

| Symbol | Address | How confirmed |
|---|---|---|
| `gScriptCmdTable` | `0x0815F9B4` | vanilla address, 0xD6 entries, interpreter refs at `0x69A9C/0x69B1C/0x69B78` |
| `gSpecialVars` table | `0x0815FD0C` | follows cmd table; `VAR 0x800D → 0x020370D0 = gSpecialVar_Result` |
| `gSpecials` | `0x0815FD60` | 444 entries (CFRU-extended; vanilla FR has 396) |
| `gStdScripts` | `0x08160450` | 10 entries; **callstd 3–6 repointed to Unbound high-ROM `0x09E7D5BC+`** (custom msgbox/yesno) |
| `ScriptReadHalfword` | `0x080698F8` | used by every u16-operand handler |
| `FlagSet` / `FlagClear` / `FlagGet` | `0x0806E680` / `0x0806E6A8` / `0x0806E6D0` | setflag/clearflag/checkflag handlers + BPRE.ld |
| `GetVarPointer` / `VarGet` / `VarSet` | `0x0806E454` / `0x0806E568` / `0x0806E584` | setvar/compare handlers + BPRE.ld |
| `GetMonData` / `SetMonData` | `0x0803FBE8` / `0x0804037C` | givecaughtmon literal pool + BPRE.ld |
| `ZeroMonData` / `CopyMon` | `0x0803D994` / `0x08040B08` | BPRE.ld |
| `CalculatePlayerPartyCount` / `CompactPartySlots` | `0x08040C3C` / `0x080937DC` | BPRE.ld |
| `GetSpeciesName` / `gEvolutionTable` | `0x08040FD0` / `0x08259754` | BPRE.ld (evolution table may be DPE-repointed — verify before use) |
| `gPlayerParty` / `gEnemyParty` | `0x02024284` / `0x0202402C` | BPRE.ld |
| `gStringVar1/2/4` | `0x02021CD0/CF0/D18` | BPRE.ld + seen in givecaughtmon |
| `gNewBS` (CFRU battle struct ptr) | `0x0203E038` | BPRE.ld + deref'd in givecaughtmon |
| `ScriptGiveMon` | `0x080A011C` | givemon(0x79) handler calls it with CFRU's exact 6-arg signature (`build_pokemon.c:4007`) |
| `ScriptGiveEgg` | `0x080A01AC` | giveegg(0x7A) handler |
| `agbcc call_via_rX` veneers | `0x089C9A70+` | `bx r3/r4/r5/r6/r7` ladder (CFRU compiled code calls natives through these) |

### CATCH HANDLER — FOUND AND CONFIRMED (was the project's #1 unknown)

The battle engine's own command table was repointed by CFRU: live copy at **`0x0899FFFC`** (file; 5 interpreter refs at `0x14C1C/0x15A28/0x15C6C/0x15C98/0x1D054`; the vanilla copy at `0x025011C` and an intermediate at `0x95F480` are orphaned). Commands `0xEE–0xF1` are repointed into CFRU high-ROM while neighbors stay vanilla:

- **`atkEF_handleballthrow` = `0x089C8BE4`** — catch odds/success logic (CFRU `catching.c`)
- **`atkF0_givecaughtmon` = `0x089C97AC`** — decompiled and matched **line-for-line** against CFRU source `src/catching.c` (raid-item restore, Unbound PP fix loop, box-name strings, `GAME_STAT_CAUGHT_TODAY`, `gBattleResults.caughtMonSpecies`)
- `atkF1_trysetcaughtmondexflags` = `0x089C961C`

### THE ENFORCEMENT CHOKE POINT

**`GiveMonToPlayer` (CFRU-compiled) = `0x089C905C`** — called by `atkF0_givecaughtmon` (every catch) AND by `ScriptGiveMon`/`build_pokemon.c` paths (every scripted gift). Signature `u8 GiveMonToPlayer(struct Pokemon* mon)` (`catching.c:600`, comment "//Hook in" — CFRU itself hooks the vanilla one here). Returns `MON_GIVEN_TO_PARTY(0) / MON_GIVEN_TO_PC(1)? / MON_CANT_GIVE(2)?` (check `defines.h` for exact values). One hook at this entry enforces Character Mode for catches and gifts simultaneously. `SendMonToPC` vanilla addr `0x08040B90` (commented out in BPRE.ld — CFRU replaces it; find CFRU's compiled version via GiveMonToPlayer's internals when needed).

### Hook-site working set (v8 continued — everything needed to write the actual patch)

**Catch-block hook (ROWE parity: off-roster species can't be caught, ball is dodged):**
- CFRU `atkEF_handleballthrow` already contains a block path: `gBattleTypeFlags & BATTLE_TYPE_GHOST || FlagGet(FLAG_NO_CATCHING) || FlagGet(FLAG_NO_CATCHING_AND_RUNNING)` → `EmitBallThrowAnim(0,6)` + `BattleScript_DodgedBall`.
- **`FLAG_NO_CATCHING` = `0x09F8`**, **`FLAG_NO_CATCHING_AND_RUNNING` = `0x08E2`** (literals at file `0x9C8E00`/`0x9C8E04`).
- The `FlagGet(FLAG_NO_CATCHING)` call is `bl 0x089C9A76` (call_via_r6, r6=FlagGet) at **ROM `0x089C8CA6`** (bytes `F0 00 E6 FE`… stored LE as `00 F0 E6 FE` at file `0x9C8CA6`). **The hook is a single 4-byte retarget of this `bl`** to our injected `u8 CharacterMode_CatchFlagGet(u16 flagId)` = `FlagGet(flagId) || (InCharacterMode() && !IsSpeciesAllowedForCharacter(gBattleMons[gBankTarget].species))`. Thumb `bl` range ±4MB reaches the `0x08B2B280` free block (+1.45MB) comfortably.
- Battle globals (from givecaughtmon/handleballthrow literal pools, BPRE.ld-confirmed): `gBankTarget` = `0x02023D6C` (u8), `gBattleMons` = `0x02023BE4` (stride 0x58, species u16 at +0), `gBattleTypeFlags` = `0x02022B4C`, `gBattleResults` = `0x03004F90`, `gMain` = `0x030030F0` (`inBattle` = bit 1 of byte +0x439).

**Gift hook (ROWE parity: off-roster non-egg gifts go straight to the PC):**
- `GiveMonToPlayer` (CFRU) = `0x089C905C`, entry bytes `70 B5 04 00 1C F0 CE FE …` (`push {r4-r6,lr}; movs r4,r0; bl TryFormRevert`…). Small function, fully mapped:
  `TryFormRevert` = `0x089E5E00|1` (bl at entry+4), `TryRevertMega` = `0x089F77B0|1`, `TryRevertGigantamax` = `0x089D9D34|1`, `TryRevertOriginFormes` = `0x089E5D08|1`, **CFRU `SendMonToPC` = `0x08A04CB0|1`**, `CopyMon` ptr literal `0x08040B09`, `gSaveBlock2Ptr` = `0x0300500C` (Unbound reads it via pointer — dynamic saveblocks), `gPlayerParty` = `0x02024284` (stride 100, species at +0x20), `gPlayerPartyCount` = `0x02024029` (u8), `MON_GIVEN_TO_PARTY` = 0.
- Hook shape: 8-byte entry trampoline (`ldr r1,=hook|1; bx r1` + literal) replacing the prologue, with our C function fully re-implementing the (small, fully-mapped) original + the ROWE roster check. All callee addresses above are pinned, so the reimplementation is semantics-identical.

**Species names (live, DPE-repointed): `gSpeciesNames` = `0x0966A98C`** (stride 11; extracted from `GetSpeciesName 0x08040FD0`'s literal pool). **Phase 2's species IDs are now ROM-VERIFIED**: all 457 unique roster species IDs checked against this table — 100% match (5 apparent misses are charmap artifacts/10-char truncations: Type: Null, Flabébé, Stonjourner, Blacephalon, Mime Jr.). IDs are no longer provisional.

**ROWE enforcement semantics to port (read from ROWE source this session):**
1. `handleballthrow`: off-roster → ball-block anim + message (no catch, no odds roll).
2. `GiveMonToPlayer`: off-roster && !egg → `return SendMonToPC(mon)` (gift lands in PC, not party).
3. Trades/Mystery Gift/storage: post-event `CharacterMode_SweepPartyToPC()` (party sweep, never empties party, eggs exempt).
4. Roster check = base-stage match: rosters store base stages only; check walks the mon's species down to its base form first. (For the binary port, simpler alternative: emit ALL family members into the binary rosters at build time — Phase 2's scraper already expands families — so the ROM-side check is a flat membership test, no evolution walking.)

### What this means for the phase gates

Phase 1's routine-hunting is **effectively COMPLETE** for the mechanics that matter: catch (`0x089C905C` / `0x089C8BE4` / `0x089C97AC`), gift (`0x080A011C` → same choke point), menu hook (enhancement script + full opcode grammar + `VAR_RESULT 0x800D`), and all of Phase 4's Group-B externs are now real addresses. Remaining unknowns are secondary: trade-handler native (Borrius quest — likely also funnels through party/mon copy natives), sprite/asset tables (Phase 3), and DPE's possibly-repointed evolution table (verify `0x08259754` before relying on it).

---

The project's substitute for a public symbol table. Every finding is tagged:
- **CONFIRMED** — address verified by trace/patch-and-observe (code located and behavior proven).
- **STRING ANCHOR** — a data string is located and its content strongly implies which subsystem/dialogue it belongs to; the *code* that reads/displays it (the actual routine we need) is not yet located. Next step for these is Ghidra XREF analysis (find what code references the string's address) or an mGBA read-watchpoint on the string bytes.
- **LIKELY** — inferred from CFRU/pret source shape, not yet verified against this binary at all.
- **UNKNOWN** — not yet investigated.

All offsets below are **file offsets** into `rom/Pokemon Unbound (v2.1.1.1).gba` (pinned to `rom.sha1`). GBA ROM is memory-mapped at `0x08000000`, so the in-emulator/Ghidra address = file offset + `0x08000000` (e.g. file offset `0x3FD7A2` → ROM address `0x083FD7A2`).

Text was located with `tools/search_gametext.py` (Gen3-charmap string search, reusing ROWE's `charmap.txt`) and read with `tools/decode_gametext.py`. The charmap was sanity-checked against known vanilla strings (`TRAINER`, `POKéMON`, `SAVE` all decoded correctly) before trusting any hit.

## Catch mechanic — STRING ANCHOR (strong lead)

File offset `0x3FD790`–`0x3FD8xx` decodes to the full vanilla catch-sequence string bank, contiguous and in the expected order:
```
Gotcha! [X] was caught!
Gotcha! [X] was caught! (variant, different trailing control codes — likely the "+ new Pokédex entry" flow)
Give a nickname to the captured [X]?
[X] was sent to [Y]'s PC. / someone's / Bill's
[X]'s data was added to the Pokédex!
It is raining. / A sandstorm is raging. (weather-affects-catch-rate flavor lines, same bank)
The Box is full! You can't catch any more!
```
This is byte-for-byte the standard FRLG/CFRU catch message bank (not reworded), which is a good sign for risk #1 in the plan (Unbound's catch subsystem may not have diverged much from a CFRU-shape compile, at least at the message layer). **Next step**: once Ghidra analysis completes, find XREFs to `0x083FD7A2` ("Gotcha!") and `0x083FD86x` ("Box is full") — those functions are the real catch-success/catch-overflow handlers we need to hook for the "off-roster catch fails" enforcement.

## Mystery Gift — STRING ANCHOR (strong lead)

File offset `0x1A6317`–`0x1A6385` decodes to Mystery Gift explanation dialogue ("...you must know about the MYSTERY GIFT... From now on, you should be receiving MYSTERY GIFTS!... Once you save your game, you can access the MYSTERY GIFT... Thank you for accessing the MYSTERY GIFT System..."). Corroborated by Phase-1's earlier debug-string find: the ROM retains original GameFreak assert strings naming `mevent.c` and `mevent_server.c` (Mystery Event/Gift source files in the pret/pokefirered decomp) — those files are the known real implementation this dialogue belongs to. **Next step**: XREF from these string addresses once Ghidra is done, cross-reference against pokefirered's `mevent.c`/`mevent_server.c` structure for the species-assignment call site.

## Trade sequence — STRING ANCHOR (strong lead, corrected from earlier pass)

Earlier pass mischaracterized this as link-trade dialogue — a wider read proved it wrong. File offset `~0x1F8590`–`0x1F85BBA`+ is **Unbound's actual "Borrius Trade Quest" NPC in-game trade table** — a self-contained sidequest with real, named, Unbound-specific trade pairs:
```
"It looks like there are still residents of Borrius that are willing to trade.
 Trade with all of them, and then I'll give you a nice reward."
...
Alolan Sandshrew  <->  Quacker the Ducklett
Onix              <->  Roly-Poly the Electrode
Lickitung         <->  Top the Hitmontop
Manectric         <->  Squirry the Pachirisu
Amoonguss         <->  Shiinotic  (two-way, both directions listed)
... (table continues past what's been read so far)
```
"Borrius" is Unbound's custom region name, confirming this is genuinely Unbound-authored content, not a leftover vanilla string. This is a much better hook-point candidate than the original guess — it's a clean, self-contained table of species-for-species swaps, exactly the shape of code the plan needs to find (something that reads an incoming species and assigns an outgoing one). **Next step**: XREF from these string addresses (once Ghidra is done) to find the actual trade-handler function; also read further past `0x1F85BBA` to capture the rest of the trade table (this dump was truncated mid-table).

## Starter give sites — FOUND, all three, + givemon handler fully decoded (2026-07-17 v9)

**Unbound's starters are Larvitar (246) / Beldum (398) / Gible (496)** (ids per the live species-name table; names never appear in dialogue text — the pickers buffer them dynamically, which is why string search failed for two sessions).

**givemon (opcode 0x79) handler = `0x0806BFD1`**, fully decoded: operands are species:u16 (VarGet-resolved — var ids work), level:u8 (raw), item:u16 (VarGet-resolved), then 3 raw bytes = `unused1`, `customGivePokemon`, `ballType`. Marshals into **CFRU `ScriptGiveMon(u16 species, u8 level, u16 item, u32 unused1, u32 customGivePokemon, u8 ballType)`** (`build_pokemon.c:4007`) via **`bl 0x080A011C` at `0x0806C030`** (orig bytes `34 F0 74 F8`), result stored to `gSpecialVar_Result` (0x800D @ 0x020370D0). `customGivePokemon != 0` makes it read vars 0x8000-0x800B as move/nature/IV overrides — every real give site sets the no-override defaults (0x8000-3=0xFFFF, 0x8004=0xFF, 0x8005=0) first. giveegg (0x7A) handler `0x0806C051` → `ScriptGiveEgg 0x080A01AC` (separate function, not hooked).

**Unbound's gift convention**: native picker writes the chosen species into **var 0x4001**, script does `givemon 0x4001` (seen at the Sinnoh-caretaker and neglected-companions NPCs too). The three starter-give scripts:
1. **`0x1E6E73A`** — branch on 0x8000∈{1,2,3} → setvar 0x4001 Larvitar/Beldum/Gible → `givemon 0x4001, lv 1` @ 0x1E6E77A.
2. **`0x1E90C68`** — NPC (faceplayer), `copyvar 0x8000 ← var 0x5012` (a stored earlier choice), shifted branch → yesno confirm → `givemon 0x4001, lv 10, item 44` @ 0x1E90CC5.
3. **`0x75CD3F`** — the prologue/escape scene (see corrected section below): three snippets `setvar 0x8000 <species>` + preview op 0x85 → `givemon 0x8000, lv 10` @ 0x75CB8F.

**Character Mode starter grant hooks here**: the single `bl` at `0x0806C030` is retargeted (via an 8-byte near veneer at **`0x081B2940`** — the handler is ~11MB from the injection block, out of Thumb bl range; veneer = `ldr r3,[pc,#0]; bx r3; .word wrapper|1`, and r3 = `unused1` which CFRU's own comment says is the hook-in arg, "don't use it for anything" — clobber-safe) to `CharacterMode_ScriptGiveMon`: first mon ever given while Character Mode is active becomes the character's roster[0] (signature-first ordering), name re-buffered into gStringVar1 (scripts buffer the species name BEFORE givemon). Covers all three starter scripts and every other first-give path uniformly; live-verified (starter_test 7/7).

## Starter selection — ~~RULED OUT~~ CORRECTED 2026-07-17: the escape scene IS a starter-give site

File offset `0x75CB20` ("Go ahead, choose a Pokémon.") was ruled out as "a mid-story escape sequence, not starter selection" — **half right, half wrong (corrected 2026-07-17)**: the scene is indeed the escape sequence, but its script (`0x75CD3F`+) sets var 0x8000 to exactly Larvitar/Beldum/Gible and feeds `givemon 0x8000, lv 10` @ 0x75CB8F — it IS one of the three starter-give sites (the prologue pick). The v7-era conclusion "don't hook here" still stands for a different reason: the Character Mode starter grant hooks the shared givemon-handler `bl` instead (see the section above), which covers this site and both others without touching any script.

Still potentially useful as a **generic gift-item/gift-Pokémon message lead**: "[X] received a [Y] from [Z]!" reads like shared vanilla-shape infrastructure (the standard FRLG "received an item/Pokémon from" message format), which could be the same underlying print routine used across many gift scenarios, not just this one cutscene. Not yet pointer-searched — worth trying once the true string start is pinned down (this one also needs the careful backward-scan-to-real-boundary treatment other leads required).

Real starter-selection dialogue is still **UNKNOWN** — not yet found by any technique. Candidate search terms tried and failed: generic "starter" substring (too many false positives, see below).

False leads ruled out during this search (recorded so they aren't re-tried): plain `"starter"` substring-matched unrelated dialogue about "starters" (ferry/ocean traffic flavor text) — too generic a search term. `"was caught"` substring-matched a battle move effect message ("was caught in a sticky web!" — String Shot/Sticky Web) as well as the real catch text — needs the fuller surrounding-context check every time, not just a raw hit count.

## Pointer-reference technique (no Ghidra needed for this class of finding)

Discovered a technique that works without waiting for Ghidra: GBA code and data reference strings via plain 4-byte little-endian pointers (`file_offset + 0x08000000`) — this is true both for data tables *and* for ARM/Thumb literal pools and compiled script bytecode, since none of those embed the address as a relative/encoded value. `tools/find_pointer_refs.py` searches the raw ROM bytes for a given string's pointer value directly. Important nuance learned the hard way: the pointer always targets the **true start** of the enclosing string, not wherever a keyword search happened to match mid-sentence — back up to the preceding `0xFF` terminator first (with caution: `0xFF` also appears in non-text binary/script data, so a long backtrack distance is a red flag that the heuristic wandered into non-text bytes, not a real string boundary; short, plausible backtracks like the mystery-gift case below are trustworthy, the trade-table case's 3.7 KB backtrack was not and needs a different approach).

Results:
- **Catch message ("Gotcha!") — table fully bounded, real code now inspected via Ghidra (upgraded twice this session).** File offset `0x3FD7A2`'s pointer is referenced at `0x3FE338`, inside a table now fully bounded by scanning outward for the full run of valid `0x08xxxxxx`-range pointers: starts at `0x3FDF3C`, ends (exclusive) at `0x3FE514` — **374 entries**, a size right in line with pret's known `gBattleStringsTable`. Searching for pointer references to the table's *base* (`0x3FDF3C`) found **26 hits**, densely clustered in file offsets `0xCEFEC`–`0xD8494` (~57 KB), plus 3 outliers.
  - Ghidra's full-ROM auto-analysis (headless, `-analysisTimeoutPerFile 3600`) ran for the full hour and **timed out** before reaching this region — its own `getReferencesTo()` found zero refs here, confirming the timeout genuinely left large parts of the ROM unanalyzed, not just slow. Full auto-analysis is not a reliable way to reach specific regions of a ROM this size in one pass.
  - Worked around it with a **targeted-disassembly script** (`tools/ghidra_scripts/InspectRegions.java`) that force-disassembles small windows around known addresses directly, using the FlatProgramAPI — much faster than a full re-analysis for a handful of known sites. Caught and fixed a real pitfall: the default `disassemble()` call decodes in **ARM mode**, producing plausible-looking but wrong 32-bit instructions ("adcs r8,r0,#0x4000001" nonsense) for what's actually **Thumb (16-bit)** GBA code — had to explicitly set the `TMode` context register to 1 before disassembling. Also had to `clearListing()` first to undo the bad ARM-mode analysis from the first attempt.
  - With Thumb mode forced, 4 of the 26 sites (`0x080CF068`, `0x080CF328`, `0x080CF3F0`, `0x080CFE50`) show real, sensible code, and 2 more (`0x080CFB28`, `0x080D8494`) turned out to be thunks (`b <target>`) pointing elsewhere, not inspected further yet.
  - **Ran Ghidra's Decompiler on the 4 real functions — this REVISES the earlier hypothesis, not just refines it.** The decompiled C shows a `get-a-value → validate via a lookup function → branch` pattern, e.g. (from `FUN_080cf328`):
    ```c
    uVar3 = FUN_0803fbe8();          // get some 16-bit value (a candidate id?)
    uVar3 = uVar3 & 0xffff;
    iVar4 = func_0x080441b8(uVar3);   // validate/look up that id
    if (iVar4 != 0) {                 // valid: print a fixed message, bump a per-slot counter, done
        FUN_080d77f4(*(ptr)(table_base + offset));
        ...
    } else {                          // invalid: build a message with the id embedded via a TEXT PLACEHOLDER
        *buf = 0xFD;      // Gen3 CHAR_DYNAMIC control code
        buf[1] = 2;        // placeholder-kind byte
        buf[2] = (char)uVar3; buf[3] = (char)(uVar3 >> 8);   // the id itself, LE
        buf[4] = 0xFF;
        StringExpandPlaceholders_equivalent(); print_equivalent();
        ...
    }
    ```
    This is a **validate-a-candidate-and-report-if-invalid** shape, not a generic "print battle message N" dispatcher. Given this sits right next to code the Species Randomizer plausibly needs (validate a randomly-picked species id, report if it's not a legal candidate), **these 4 functions more likely belong to the Species Randomizer's own internals than to the catch-message system** — even though the STRING CONTENT identification of the 374-entry table (containing "Gotcha!"/"Box is full!" etc., matching `gBattleStringsTable`'s size) is still solid and unchanged. What's revised is the earlier claim about what the 26 *code* cross-references to the table's base are for — "26 generic battle-message call sites" was an oversimplification, and for at least these 4, likely an incorrect one.
  - **Net effect on risk #1**: still de-risked (this is real, coherent, sensibly-structured ARM/Thumb code — not something exotic), but the *specific* claim "found the catch handler's neighborhood" needs walking back. The catch-success/catch-failure handler is still genuinely unconfirmed.
  - **Decompiled 5 more of the 26 sites** (`0x080CF148`, `0x080CF3A8`, `0x080CF438`, `0x080CF46C`, `0x080CF498`) — all show the same family shape: write a few fields into a `(bank_index)*8 + base` struct (offsets `+0x14`/`+0x16`/`+0x18` recur — plausibly per-active-script-instance state, stride 8 bytes per instance), sometimes call `FUN_080d77f4`/`func_0x080d87bc` (print-adjacent calls, same two functions recur across sites), and return via a **shared tail-branch epilogue at `0x080cf526`–`0x080cf536`** (`pop {r3,r4,r5} / mov r8,r3 / ... / pop {r0} / bx r0`). Ghidra's decompiler mislabeled this shared epilogue as an "UNRECOVERED_JUMPTABLE" (its switch-table heuristic misfired on it) — **corrected**: it's an ordinary function return sequence multiple nearby functions tail-branch into to share code size, not a script-command dispatch table. No opcode-to-handler mapping has actually been found yet.
  - **Working theory (still not fully confirmed)**: this whole `0xCEFEC`–`0xD8494` region is very plausibly the compiled `scrcmd.c`-equivalent (many small per-command handler functions, each touching a per-script-instance state struct and calling shared print helpers) — this would line up with the *retained debug-assert string* naming `scrcmd.c` as a real source file in this ROM (found earlier this session, see the strings-dump section above). If true, this is exactly the right neighborhood for catch/gift/trade script commands generally, just not confirmed to be reached via "battle string table" specifically — the 374-entry table may be a broader shared text bank used by many different script commands (of which catching is one), not something exclusively battle-specific.
  - Two remaining avenues: (a) find the actual opcode→handler dispatch mechanism (not yet located — would let us map a known opcode byte value, like the `0x2B`/`0x16` found in the enhancement-menu script, directly to its handler function address); (b) fall back to the plan's originally-envisioned technique — live mGBA watchpoint tracing while the built-in Species Randomizer or an actual catch attempt is exercised interactively, which needs the user's involvement per the ROWE precedent (Phase 5 territory, not attempted this session).
- **Mystery Gift dialogue — confirmed to be script-invoked.** True string start (after backing up past a plausible preceding terminator) is `0x1A62D3` ("Oh, hello! You know those words? That means you must know about the MYSTERY GIFT..."). Its one pointer reference is at file offset `0x1A7770`, embedded directly in what looks like compiled map-script bytecode (single-byte opcodes interleaved with a handful of 2-4 byte operands, e.g. `... D3 62 1A 08 09 04 ...` — the 4 bytes `D3 62 1A 08` are exactly our pointer in LE form). This confirms Mystery Gift's intro dialogue is triggered from a scripted event, as expected, but the actual native routine (invoked from the script via a `special`-style call, most likely) hasn't been isolated yet — that needs either Ghidra's script/special-function-table cross-referencing or manually decoding more of the surrounding script bytes against pret's `scrcmd.c` opcode table (which we already have a real anchor for, from the retained debug-assert filename).
- **Trade table — pointer search inconclusive so far.** The naive backward-terminator-scan landed implausibly far back (3.7 KB), a sign the heuristic crossed into non-text bytes rather than finding a real string boundary; needs a smarter string-start detection (e.g. reuse `dump_all_strings.py`'s decode-forward validator to find the previous *valid* decoded run's start, not just the previous raw `0xFF` byte) before trusting a pointer search here.

### Splice-site structural facts (2026-07-14, v8.1 — established while wiring the opt-in prompt)

- **The spliced 8 bytes at `0x1E70003` sit on a clean jump-target boundary**: `0x09E70003` is itself the target of a `goto_if` at `0x1E6FF3D` (`21 DF 50 02 00 / 06 00 03 00 E7 09` — `compare(VAR_UNBOUND_GAME_DIFFICULTY 0x50DF, 2); goto_if(0, 0x09E70003)`) and a plain `goto` at `0x1E6FFA3`. Execution therefore *enters* exactly at our replacement `call` opcode — no mid-instruction landing risk, and the `compare 0x800D` at `0x1E7000B` is only reached by fall-through.
- **The script's entry is `0x1E70000`** (3 bytes before the splice), referenced as `0x09E70000` from three native/data tables at file `0x0253FDE`, `0x038F94A`, `0x0A7A19E` (record shape not yet decoded — this is how the new-game difficulty flow is invoked from code). The whole difficulty spaghetti `0x1E6FF00`–`0x1E70003` gates on `0x50DF` compares and funnels into the enhancement prompt.
- Practical probe: `VAR_UNBOUND_GAME_DIFFICULTY 0x50DF` (EWRAM `0x0203B532`) is written by the difficulty selection just upstream of the splice — nonzero is strong evidence the intro reached our region (but 0 is inconclusive: the default choice may map to 0).

### Scrolling multichoice (special 0x158) — MAPPED, and why it must NOT be extended (2026-07-16, v8.2)

Full contract (from Unbound's own scripts, 54 call sites): `setvar 0x8000 <set>`, `setvar 0x8001 <rows>`, `setvar 0x8004 <initial cursor — MUST be set, stale value crashes>`, `special 0x158`, `waitstate` → selection index in `0x800D` (`0x7F` observed as cancel from the vanilla-side path; scripts also compare `0xFFFF`/`0xFFFE`). Machinery: vanilla handler `0x080CB7C4` + task `0x080CB904`, CFRU hooks at `080CB94C/080CB82A/80CBAC8` feeding lists via `GetSizeOfMultiList` **0x09EB48B8** / `GetScrollingMultiList` **0x09EB48D4** (both clamp idx>31→0), `gScrollingSets` = **0x09FB196C** with **31 real entries** (slot "31" is already the next sibling structure — two consecutive 0x09FCxxxx pointers). Sets 9/11 look script-unreferenced by nearby-setvar scanning but are the BP-shop menus (distant setvar/goto chains).

**Do not extend/relocate this table.** gScrollingSets has at least 3 more pool references in Unbound-custom code (`0x9EB7C6C`, `0x9EB80B4`, `0x9ED4FD8`) that index with raw unclamped Var8000 and sit among sibling-table pointer pools; an out-of-range magic index produced run-dependent chaos (SIGILL wedges, one spurious trainer battle from garbage data), and relocating the table (all 5 exact-base pool refs repointed) intermittently froze the game — consistent with iterators using separate end-pointer constants that exact-word scanning cannot find. The character-select uses ChooseNumberScreen instead (below).

### Character-select v3 wiring (2026-07-16, v8.2)

- `special 0x0B3` = CFRU `sp0B3_DoChooseNumberScreen` (0x08A0926D in this ROM): naming screen in number mode, result → `0x800D` (`0xFFFF` on empty/cancel). 11 existing script uses.
- `gSpecials[0x1B6]` (file `0x160438`, stale `0x081537C1`) repointed by the build to injected `CharacterMode_BufferNameSpecial` — copies `gCharacterNamePtrs[0x800D - 1]` to `gStringVar1` for `{STR_VAR_1}` text.
- Test-harness facts: gMain key fields (`heldKeysRaw +0x28 = 0x03003118`, `newKeysRaw +0x2A`, `newKeys +0x2E`, `newAndRepeated +0x30`); naming screens drop poked new-key writes ~half the time (input processed before the stop point) — use real host input verified by heldKeysRaw readback. High EWRAM (`0x0203FC00+`) is clobbered by live list-menu buffers (donor symbols end at `sBerryPouchListMenuItems 0x203F37C` but buffers grow upward) — never stage runtime code/scripts there; audited-clean expanded vars: `0x51F8/0x51F9/0x51FA` (0 hits), `0x51FB` (1 probable-false hit).

### Specials table — FOUND + hijack slot reserved (2026-07-14, v8.1)

Opcode `0x25` (`special`) handler `0x08069EFD` / `0x26` (`special2`) `0x08069F3D` validate the id then fetch `gSpecials[id]`:
- **`gSpecials` = `0x0815FD60`, 444 entries (ids `0x000`–`0x1BB`)**, table ends at `0x08160450` (= `gStdScripts`, consistent). Out-of-range ids hit an error path (literals `0x083A725C`/`0x083A7290`).
- 31 ids are dummied (all → vanilla `SpecialDummy` `0x080CADC1`).
- 20 ids have **zero** `25 xx xx`/`26 vv vv xx xx` byte-pattern hits anywhere in the 32MB ROM (a deliberately over-matching scan — so zero means definitely script-unreachable): `0x159 0x15F 0x189 0x18A 0x18E 0x195 0x19A 0x1A1 0x1A2 0x1A4 0x1A6 0x1A9 0x1AB 0x1AF 0x1B6` (highest 15 shown). The table is only read by the two opcode handlers, so repointing such an id's entry cannot affect anything else.
- **RESERVED for Character Mode: `special 0x1B6`** (entry at file `0x160438`, currently stale-pointing to `0x081537C1`). The future native character-select menu (and/or debug entry points) will be wired by repointing this entry to injected code in `tools/build_patch.py`, then invoked from the opt-in script as `25 B6 01`.

## Intro "enhancement options" menu — FOUND (major win, was the last big unknown for Phase 4's menu hook)

The exhaustive full-ROM string dump (`tools/dump_all_strings.py`, ~210K lines, ran ~40 min in the background) found exactly what the plan predicted would be the best precedent for Character Mode's own opt-in intro menu — Unbound's real new-game setup flow, starting at file offset `~0x1F1060`:

```
Expert / Insane / Challenging / Back          (difficulty sub-menu options)
"Would you like to view game enhancement options?"
"Would you like to view [randomizer] options?"
"Would you like to enable the [species] randomizer?"
"The [species] randomizer has been enabled."
"Would you like to enable the [level-up moveset] randomizer?" / enabled confirmation
"Would you like to enable the [Ability] randomizer?" / enabled confirmation
"Note that the randomizer will be temporarily disabled during boss battles."
"Would you like to play a variant with stat rebalancing?" / enabled confirmation
  + a full paragraph explaining the rebalancing math (BST ~600, Shedinja/Huge Power exceptions)
```

This is a real, working, **multi-step opt-in toggle system** exposed at new-game setup — a near-ideal structural precedent (or literal insertion point — a "Character Mode" toggle could plausibly be added as one more entry in this same sequence) for where Character Mode's own character-select menu should hook in.

The true string start ("Would you like to view game enhancement options?") is at file offset `0x1F1065C`. Its pointer is referenced once, at file offset `0x1E70005`, embedded in what reads as compiled script bytecode (small-opcode-plus-operand rhythm matching what we saw for the Mystery Gift reference: `... 5C 06 F1 09 ...` — `5C 06 F1 09` is exactly this pointer in LE form, `0x09F1065C`). Confirms this menu is script-driven, same mechanism as other dialogue flows.

### Script opcodes decoded — CONFIRMED (independently cross-validated, not guessed)

Scanned the raw script bytes for `0x1E6FF80`–`0x1E70120` (covering the species/moveset/ability randomizer toggle sequence) for a repeating pattern, since three near-identical "would you like to enable the X randomizer?" prompts should compile to near-identical script snippets differing only in which flag they set:

```
0x01E700AA: 2B FD 09   -> flag op on 0x09FD   [v8 correction: this is CHECKFLAG, not setflag]
0x01E700B3: 2B FE 09   -> flag op on 0x09FE   [v8: checkflag]
0x01E700BC: 2B 22 15   -> flag op on 0x1522   [v8: checkflag]
```

**`0x09FD` is an exact match for `FLAG_UNBOUND_SPECIES_RANDOMIZER`**, the one flag ID the plan's original research already had documented (via Unbound-Cloud's reverse-engineered save format). This independently confirms the script-decoding approach and the flag id — but the original conclusion "`0x2B` is `setflag`" was **wrong** (corrected in v8 via the dispatch table: `0x29`=setflag, `0x2B`=checkflag; these sites are checkflag→goto_if chains). `0x09FE` and `0x1522` remain two more real, in-use flag IDs.

Also found the companion `setvar` pattern:
```
0x01E70042 / 0x01E7006B: 16 00 80 ...  -> setvar(VAR=0x8000, ...)
0x01E700DB / 0x01E700E9 / 0x01E700F7: 16 06 80 ...  -> setvar(VAR=0x8006, ...)
```
`0x8000`/`0x8006` land exactly in pret's standard "special var" range (`VAR_RESULT = 0x8000` is the classic convention) — another independent confirmation that Unbound's scripting engine hasn't diverged from the vanilla/CFRU shape.

**Practical takeaway for Phase 4**: `FLAG_CHARACTER_MODE`/`VAR_CHARACTER_ID` must avoid at least `0x09FD`, `0x09FE`, `0x1522`, `0x8000`, `0x8006` (now confirmed in-use) plus the previously-known `VAR_UNBOUND_GAME_DIFFICULTY 0x50DF` — still not a complete unused-range map, but real, growing, confirmed exclusions rather than the empty list Phase 4 started with.

### Yes/No branch mechanism decoded — CONFIRMED (2026-07-12 v7)

Hand-decoded the raw bytes at `0x1E6FF80`–`0x1E70140` to find the actual conditional-branch pair gating each `setflag`, cross-checked across all three randomizer prompts (species/moveset/ability) for consistency — all three follow the identical pattern, byte-for-byte:

```
0x1E70003: 0F 00 5C 06 F1 09      loadword(bank=0, ptr=0x09F1065C)   ; load "enhancement options?" text
0x1E70009: 09 05                  callstd(5)                          ; MSGBOX_YESNO — display + wait for Yes/No
0x1E7000B: 21 0D 80 00 00         compare_var_to_value(VAR=0x800D, value=0)
0x1E70010: 06 01 48 01 E7 09      goto_if(cond=1/EQ, ptr=0x09E70148)  ; if answer==0 (No), skip enabling
0x1E7003F: 29 FD 09               setflag(0x09FD)                     ; [corrected in v8: 0x29 IS setflag]
  ...                             loadword+callstd for "enabled" confirmation message
0x1E700A6: 16 00 80 00 00         setvar(VAR=0x8000, 0) / setvar(VAR=0x8006, {0,1,2})  ; per-prompt bookkeeping var, not the answer
```

**Real, useful findings**:
- The Yes/No answer from `callstd(5)` (`MSGBOX_YESNO`) lands in **VAR `0x800D`** — a new, previously-unidentified scratch var. This (not `0x8000`/`0x8006`, which are written separately via `setvar` and are probably per-prompt bookkeeping, e.g. a running enabled-count) is the actual condition variable Character Mode's own Yes/No or character-select prompt would need to read.
- Confirms opcode `0x21` = `compare_var_to_value` (5 bytes: opcode + u16 var + u16 value) and opcode `0x06` = `goto_if` (6 bytes: opcode + u8 cond + u32 pointer) — both consistent with the standard XSE/pret Gen3 script command shapes, another independent cross-validation of the opcode table (in addition to `0x16`=`setvar`/`0x2B`=`setflag` from the prior session).
- ~~**Caveat, not yet resolved**: opcode `0x29` vs `0x2B`~~ **RESOLVED in v8 (see top section): `0x29`=setflag, `0x2A`=clearflag, `0x2B`=checkflag** — this v7 section's `setflag`/`goto_if` reading of the control flow still holds, but every `setflag` label in the byte listing above actually refers to opcode `0x29`'s sites, and the `2B` sites are checkflags. The dispatch table proved it.
- New flag ids seen via opcode `0x29` early in this same script region (before the difficulty/randomizer prompts even start): **`0x16E4`, `0x1503`, `0x170E`** — real, flag-touching, in-use ids regardless of `0x29`'s exact semantics. Added to the exclusion list below.
- Root "difficulty" prompt that starts the whole flow: **not fully pinned down this pass** — the window inspected (`0x1E6FF80` onward) starts mid-flow; a few bytes at the very start (`0x1E6FF80`–`0x1E6FF9F`) don't cleanly parse against the opcodes confirmed so far and need a slightly wider backward read to resolve. Low priority — the practical hook point (the enhancement-options entry, `0x1E70003` onward) is already well understood.

**Updated Phase 4 exclusion list**: `0x09FD`, `0x09FE`, `0x1522`, `0x16E4`, `0x1503`, `0x170E` (flags), `0x8000`, `0x8006`, `0x800D` (vars), plus `VAR_UNBOUND_GAME_DIFFICULTY 0x50DF`.

## Battle-string-table xref cluster — CATCH HANDLER RULED OUT (2026-07-12 v7, full 26/26 survey)

Completed decompiling every one of the 26 xref sites to the battle-string-table base (`0x3FDF3C`) found in the previous session — 9 had been decompiled before, the remaining 17 (really: the containing functions for the 2 remaining un-inspected raw xrefs plus resolution of the 2 known thunks' real targets) were done this session via the same `InspectRegions.java` → `DecompileFunc.java` pipeline. One gotcha hit along the way: the scripts' own comments about whether to include the `0x08` ROM-base prefix in the hex address argument are inconsistent/wrong (`InspectRegions.java`'s comment example, `000CEFEC`, omits it; `FindXrefs.java`'s, `083FD7A2`, includes it) — the correct, working convention is **always include the `08` prefix** (e.g. `080CEFEC`), confirmed by `toAddr()` resolving the un-prefixed form to an unmapped address (`MemoryBlock` null) rather than throwing. Worth fixing the misleading comment in `InspectRegions.java`/`DecompileFunc.java` next time either is touched.

**Result: every single one of the 26 sites (all now resolved to a real, decompiled function) is the same `scrcmd.c`-equivalent per-instance-state-write family** — write a small tag/counter into a `(bank_index)*8 + base` struct at offsets `+0x14`/`+0x16`/`+0x18`, call one of a small set of shared helpers (`FUN_080d77f4`, `func_0x08054508`, `func_0x080d87bc`), and return via one of (at least) two shared tail-branch epilogues (`0x080cf536`, `0x080d0044` — refines the earlier single-epilogue claim: there appear to be multiple, not one). `FUN_080cfe50` (previously flagged) re-confirms the "get-candidate → validate → placeholder-embed-on-failure" shape tied to Species Randomizer internals. The 3 outlier sites (`0x08883520`, `0x088c0dbc`, `0x089a3288`, scattered far from the main cluster) are tiny unrelated call-forwarding stubs, not catch-related either.

**This is a definitive negative result, not just "still unconfirmed" as before**: with full 26/26 coverage and zero sites showing catch-success/catch-failure/PC-routing logic, this specific xref cluster can be ruled out as the catch handler's location. The 374-entry string table's *content* identification (containing "Gotcha!"/"Box is full!", matching `gBattleStringsTable`'s known size) still stands — it's genuinely referenced by this `scrcmd.c`-equivalent region — but the actual code that prints from it on a real catch attempt must live elsewhere, reached through a mechanism not yet found (most likely the actual opcode dispatch table, still not located, which would let a known opcode value be mapped straight to its handler; or requires live mGBA tracing during an actual catch, per the plan's original Phase 5 approach).

## Gift-Pokémon-from-NPC handler — FOUND, two distinct instances (2026-07-12 v7)

Found via `tools/search_gametext.py` searches for phrases like "willing to trade" / "take good care" / "raise it well", which also turned up several *more* instances of the already-known Borrius Trade Quest NPC template (creature-for-creature swap dialogue at `0x007C2D0B`, `0x01F03BDD`, `0x01F29A7D`, all using the same "Would you be willing to trade one for my ___?" phrasing as the documented trade table) — not new findings, just confirms the trade-quest mechanic recurs at multiple map locations, all likely sharing one handler.

Two genuinely distinct **gift-Pokémon** (not trade, not Mystery Gift) events found, both with a real multi-choice "pick one of several Pokémon" structure:

1. **The "exhausted Sinnoh caretaker" NPC.** True string start `0x1EFB6F8` ("Yawn… Raising so many Pokémon from the Sinnoh region is exhausting… Oh! You seem like a strong Trainer! How would you like to raise one for me?" → "Which of my Pokémon would you like?" → offers a `Turtwig`/`Chimchar`/`Piplup` multichoice → "Please raise it well! If you come back when you have [N] Badges, I'll give you another."). Confirmed script-invoked: one pointer reference at file offset `0x1E63745`.
2. **The "neglected companions" NPC.** True string start `0x1F6B534` ("My husband is a very well known businessman from Cube Corp… I brought along three Pokémon with me… now that my husband returns home earlier, I've begun to neglect them… entrust them to a caring Trainer… would you like one of these Pokémon?" → repeat-visit variant: "You came back! … Which of my Pokémon would you like today?"). Confirmed script-invoked: one pointer reference at file offset `0x1E8E8C6`.

Both are real candidates for a "player receives a Pokémon directly from a script, not a trade/gift-code system" enforcement hook (Character Mode would need to gate/reject the choice if it's off-roster, same as catching). **Ruled out as a false positive for this category**: a third, superficially similar "Which of my Pokémon..." hit (`0x1F8DF45`/`0x1F8E0AB`, the "Milo" NPC) is actually a **battle ally/partner-selection** picker ("Which of my Pokémon should I use?" to join a double battle), not a permanent gift — don't conflate it with the two real finds above.

Neither has been traced to its native handler code yet (same next step as Mystery Gift/trade: XREF the script bytecode's `special`-style call, or targeted Ghidra decompilation once a code-level lead narrows which routine actually creates/assigns the resulting Pokémon).

## Not yet found / not yet searched

- **Correction**: the `0x4162E8`/`0x417713` Deposit/Withdraw/Storage text clusters are the **Bag's item-storage PC box** ("Store items in the PC", "Withdraw Item", item pocket categories) — NOT the Pokémon Storage System. Not relevant to Character Mode's party/PC-routing enforcement.
- **Correction**: the `0x4162E8`/`0x417713` Deposit/Withdraw/Storage text clusters are the **Bag's item-storage PC box** ("Store items in the PC", "Withdraw Item", item pocket categories) — NOT the Pokémon Storage System. Not relevant to Character Mode's party/PC-routing enforcement.
- The actually-relevant "route to PC" message for Character Mode enforcement is **already found**: it's part of the catch-message string bank (`0x3FD790`+ — "[X] was sent to [Y]'s PC", "someone's", "Bill's", "The Box is full!"), already tied into the 26-xref battle-string-table finding above. No separate search needed for this.
- ~~Intro menu / opt-in mode hook point~~ **FOUND** — see the "Intro enhancement options menu" section above.
- Overworld sprite table, trainer-card asset table, battle-intro pic table — not started (these are binary data tables, not findable via text search; need Ghidra's data-type analysis or manual structure hunting once available).
- Entry point / boot sequence address for a "hello world" injection hook — the injection MECHANISM is now built and verified (`tools/inject_code.py`, tested clean against a confirmed-free ROM block, exactly the right bytes changed), but no hook site has been wired yet — still need a call site to branch into injected code, not just a place to put it.

## Free space

See `docs/FREE_SPACE.md` — resolved, ~1.46 MiB confirmed free (0xFF-padded), not a blocker.

## Toolchain status

See `CLAUDE.md` — `arm-none-eabi-gcc`, `armips`, `mgba-qt` (Lua scripting compiled in) all verified working. **Ghidra 12.0.2 + `pudii/gba-ghidra-loader` 1.1.0 now installed** at `tools/ghidra/` (matched-version pair, confirmed the loader auto-detects the ROM as `GBA Loader` / `ARM:LE:32:v4t:default` on import). Full auto-analysis of the imported ROM is running (headless, `ghidra_project/UnboundCM`) — this is a genuinely long-running job on a 32MB binary; check `docs/ghidra_analysis.log` and process status before assuming it's done. Once complete, the next concrete step is running XREF queries against the string anchors above to convert them from "string anchor" to "confirmed routine."
