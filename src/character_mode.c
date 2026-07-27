/*
 * Character Mode enforcement — Pokemon Unbound v2.1.1.1 binary port.
 *
 * Ported from ROWE's src/character_mode.c (the reference implementation);
 * same enforcement semantics, read from ROWE source 2026-07-12:
 *   1. handleballthrow: off-roster species cannot be caught (ball is
 *      dodged, reusing CFRU's existing FLAG_NO_CATCHING block path).
 *   2. GiveMonToPlayer: off-roster non-egg gifts go straight to the PC.
 *   3. Trades/storage: post-event party sweep (CharacterMode_SweepPartyToPC).
 *
 * Differences from ROWE (deliberate, documented):
 *   - Rosters are pre-expanded to full evolution families at emit time
 *     (tools/character_mode/emit_characters.py), so the membership check is
 *     a flat scan — no evolution-table walking in injected code.
 *   - Reads the raw binary character tables injected into free space, not a
 *     compiled-in C array.
 *
 * Hook wiring (tools/build_patch.py):
 *   - CharacterMode_CatchFlagGet: `bl` retarget at ROM 0x089C8CA6 (inside
 *     CFRU's atkEF_handleballthrow, replacing its FlagGet(FLAG_NO_CATCHING)
 *     call). Receives the flag id in r0 exactly like FlagGet.
 *   - CharacterMode_GiveMonToPlayer: 8-byte entry trampoline at 0x089C905C
 *     fully replaces CFRU's GiveMonToPlayer (semantics-identical
 *     reimplementation + the roster check; every callee is pinned in
 *     unbound.ld).
 *
 * Flag/var allocation (empirical zero-usage scan, 2026-07-12):
 *   FLAG_CHARACTER_MODE = 0x18F8 (CFRU expanded flags 0x900-0x18FF)
 *   VAR_CHARACTER_ID    = 0x51FC (CFRU expanded vars 0x5000-0x51FF)
 * Both routed through the vanilla FlagGet/VarGet entry points, which CFRU
 * trampolines to its expanded-save handlers (verified: GetFlagPointer ->
 * 0x089A2F6C, GetVarPointer -> 0x089A2F44).
 */

#include "unbound_rom.h"

#define FLAG_CHARACTER_MODE 0x18F8
#define VAR_CHARACTER_ID 0x51FC

/* ---- injected data (tools/character_mode binaries; addresses via unbound.ld) ---- */

struct CharacterRecordBin
{
    u32 nameOffset;
    u32 rosterOffset;
    u16 spriteAssetId;
    u8 generation;
    u8 flags;         /* bit0 = hasSignature (ace at roster[0])
                       * bit1 = hidden (below the playability threshold) */
    u8 starterCount;  /* roster[0..starterCount) eligible as starters */
    u8 reserved;
    u16 pad;
};

#define CHAR_FLAG_HAS_SIGNATURE 0x1
#define CHAR_FLAG_HIDDEN        0x2

extern const struct CharacterRecordBin gCharacterTable[];
extern const u16 gCharacterRosters[]; /* rosters.bin viewed as u16 */
extern const u8 gCharacterNames[];
extern const u16 gCharacterCount;

/* ---- core (mirrors ROWE's API names) ---- */

u16 GetCharacterCount(void)
{
    return gCharacterCount;
}

bool8 InCharacterMode(void)
{
    u16 id;

    if (!FlagGet(FLAG_CHARACTER_MODE))
        return FALSE;
    id = VarGet(VAR_CHARACTER_ID);
    return id != 0 && id <= gCharacterCount;
}

static const struct CharacterRecordBin *GetActiveCharacter(void)
{
    if (!InCharacterMode())
        return 0;
    return &gCharacterTable[VarGet(VAR_CHARACTER_ID) - 1];
}

/* Flat roster scan — families are pre-expanded at emit time, so no
 * base-form reduction is needed here (unlike ROWE). */
bool8 IsSpeciesAllowedForCharacter(u16 species)
{
    const struct CharacterRecordBin *character = GetActiveCharacter();
    const u16 *roster;
    u32 i;

    if (character == 0)
        return TRUE;
    if (species == SPECIES_NONE)
        return FALSE;

    roster = (const u16 *)((const u8 *)gCharacterRosters + character->rosterOffset);
    for (i = 0; roster[i] != SPECIES_NONE; i++)
    {
        if (roster[i] == species)
            return TRUE;
    }
    return FALSE;
}

bool8 CharacterMode_PartyHasAllowedMon(void)
{
    u32 i;

    for (i = 0; i < PARTY_SIZE; i++)
    {
        u16 species = GetMonData(&gPlayerParty[i], MON_DATA_SPECIES, 0);

        if (species != SPECIES_NONE
            && !GetMonData(&gPlayerParty[i], MON_DATA_IS_EGG, 0)
            && IsSpeciesAllowedForCharacter(species))
            return TRUE;
    }
    return FALSE;
}

/* Move every off-roster party member to the PC. Never leaves the party
 * empty: if all members are off-roster, one is kept. Mons stay in the
 * party if the boxes are full. Eggs are exempt. (ROWE semantics.) */
void CharacterMode_SweepPartyToPC(void)
{
    u32 i;
    bool8 keptOne = FALSE;

    if (!InCharacterMode())
        return;

    for (i = 0; i < PARTY_SIZE; i++)
    {
        u16 species = GetMonData(&gPlayerParty[i], MON_DATA_SPECIES, 0);

        if (species == SPECIES_NONE)
            continue;
        if (GetMonData(&gPlayerParty[i], MON_DATA_IS_EGG, 0)
            || IsSpeciesAllowedForCharacter(species))
        {
            keptOne = TRUE;
        }
    }

    for (i = 0; i < PARTY_SIZE; i++)
    {
        u16 species = GetMonData(&gPlayerParty[i], MON_DATA_SPECIES, 0);

        if (species == SPECIES_NONE
            || GetMonData(&gPlayerParty[i], MON_DATA_IS_EGG, 0)
            || IsSpeciesAllowedForCharacter(species))
            continue;
        if (!keptOne)
        {
            keptOne = TRUE; /* never empty the party */
            continue;
        }
        if (SendMonToPC(&gPlayerParty[i]) != MON_CANT_GIVE)
            ZeroMonData(&gPlayerParty[i]);
    }

    CompactPartySlots();
    CalculatePlayerPartyCount();
}

/* ---- hook bodies ---- */

/*
 * Replaces the `bl FlagGet` for FLAG_NO_CATCHING inside CFRU's
 * atkEF_handleballthrow (ROM 0x089C8CA6). Called with r0 = FLAG_NO_CATCHING
 * exactly as the original; a nonzero return takes the existing
 * BattleScript_DodgedBall branch — the ball visibly fails, using a complete,
 * already-working code path (no new battle strings or states).
 */
u8 CharacterMode_CatchFlagGet(u16 flagId)
{
    if (FlagGet(flagId))
        return TRUE;
    if (InCharacterMode()
        && !IsSpeciesAllowedForCharacter(BATTLEMON_SPECIES(gBankTarget)))
        return TRUE;
    return FALSE;
}

/*
 * Full replacement for CFRU's GiveMonToPlayer (entry trampoline at
 * 0x089C905C). Reimplements the original exactly (every callee pinned in
 * unbound.ld; layout facts from docs/ROUTINE_MAP.md v8) and adds ROWE's
 * rule: off-roster non-egg gifts go straight to the PC.
 *
 * Original semantics being preserved (CFRU src/catching.c:600):
 *   TryFormRevert, TryRevertMega, TryRevertGigantamax
 *   SetMonData(OT_NAME/OT_GENDER/OT_ID from gSaveBlock2)
 *   free slot scan; multi-battle partner forces PC
 *   full party -> TryRevertOriginFormes + SendMonToPC
 *   else CopyMon into slot, bump gPlayerPartyCount, MON_GIVEN_TO_PARTY
 */
u8 CharacterMode_GiveMonToPlayer(struct Pokemon *mon)
{
    u8 *sb2;
    u32 i;

    TryFormRevert(mon);
    TryRevertMega(mon);
    TryRevertGigantamax(mon);

    sb2 = gSaveBlock2Ptr;
    SetMonData(mon, MON_DATA_OT_NAME, sb2 + 0);   /* playerName */
    SetMonData(mon, MON_DATA_OT_GENDER, sb2 + 8); /* playerGender */
    SetMonData(mon, MON_DATA_OT_ID, sb2 + 10);    /* playerTrainerId */

    for (i = 0; i < PARTY_SIZE; i++)
    {
        if (*(u16 *)(gPlayerParty[i].raw + 0x20) == SPECIES_NONE)
            break;
    }

    /* Character Mode: off-roster gifts/statics go straight to the PC —
     * unless the party is empty (i == 0: no mon in slot 0 means no mons at
     * all, slots are kept compacted). Without this guard the intro starter
     * would be PC-routed and the player would leave the lab with an empty
     * party: a softlock. Mirrors ROWE's never-empty-party sweep rule. */
    if (i != 0
        && InCharacterMode()
        && !GetMonData(mon, MON_DATA_IS_EGG, 0)
        && !IsSpeciesAllowedForCharacter(GetMonData(mon, MON_DATA_SPECIES, 0)))
    {
        TryRevertOriginFormes(mon, TRUE);
        return SendMonToPC(mon);
    }

    if (i >= PARTY_SIZE
        || ((gMainInBattleByte & GMAIN_INBATTLE_BIT)
            && (gBattleTypeFlags & BATTLE_TYPE_INGAME_PARTNER)))
    {
        TryRevertOriginFormes(mon, TRUE);
        return SendMonToPC(mon);
    }

    CopyMon(&gPlayerParty[i], mon, POKEMON_SIZE);
    gPlayerPartyCount = i + 1;
    return MON_GIVEN_TO_PARTY;
}

/* Script-callable: returns whether Character Mode is active. Wired into a
 * spare specials slot later (Phase 4 menu work); also handy for the
 * in-game debug script. */
u8 IsPlayerInCharacterMode(void)
{
    return InCharacterMode();
}

/* ---- starter grant ----
 *
 * Unbound's starter (Larvitar/Beldum/Gible) is granted by script via
 * givemon: three sites found (docs/ROUTINE_MAP.md v9: multichoice ->
 * setvar 0x4001,<species> -> givemon 0x4001 at 0x1E6E77A lv1 / 0x1E90CC5
 * lv10 / prologue 0x75CB8F via 0x8000 lv10). Rather than patching each
 * script, the single `bl ScriptGiveMon` inside the givemon(0x79) handler
 * (0x0806C030) is retargeted to the wrapper below: the FIRST mon the
 * player ever receives while Character Mode is active becomes the
 * character's own starter — roster[0], which the emitter orders
 * signature-first. Level/item/overrides are the script's own; the engine
 * builds the mon natively for the substituted species (moves, ability,
 * stats), because substitution happens before CreateMon runs. */

u16 CharacterMode_GetStarterSpecies(void)
{
    const struct CharacterRecordBin *character = GetActiveCharacter();

    if (character == 0)
        return SPECIES_NONE;
    /* roster[0]: signature-first starter ordering; every emitted roster is
     * non-empty (verified at build time) */
    return *(const u16 *)((const u8 *)gCharacterRosters + character->rosterOffset);
}

/* Decision core (factored out so the self-test can exercise it): which
 * species should a scripted givemon actually deliver? Party slots are kept
 * compacted, so an empty slot 0 means the player owns no mons yet. */
u16 CharacterMode_SubstituteGiftSpecies(u16 species)
{
    u16 starter;

    if (*(u16 *)(gPlayerParty[0].raw + 0x20) != SPECIES_NONE)
        return species; /* not the first mon — gift rules handle the rest */
    if (!InCharacterMode())
        return species;
    starter = CharacterMode_GetStarterSpecies();
    if (starter == SPECIES_NONE)
        return species;
    return starter;
}

/* Wrapper the givemon handler's bl is retargeted to. On substitution the
 * species name is re-buffered into gStringVar1: giving scripts buffer the
 * name BEFORE givemon runs (bufferspecies from the same var), so the
 * "received X!" follow-up text would otherwise show the pre-substitution
 * species. */
u8 CharacterMode_ScriptGiveMon(u16 species, u8 level, u16 item,
                               u32 unused1, u32 customGivePokemon, u8 ballType)
{
    u16 substituted = CharacterMode_SubstituteGiftSpecies(species);

    if (substituted != species)
    {
        species = substituted;
        GetSpeciesName(gStringVar1, species);
    }
    return ScriptGiveMon(species, level, item, unused1, customGivePokemon, ballType);
}

/* ---- wild-encounter roster override ----
 *
 * Spec: after CFRU's normal wild-encounter species+level roll, there is a
 * 10% chance to replace the rolled species with a member of the active
 * character's roster, picking whichever evolution stage best matches the
 * rolled level (legendaries/mythicals excluded entirely). Covers every
 * table-rolled encounter type (grass/cave, surf, rock smash, fishing) in
 * one hook, because every one of them funnels through the same real
 * CreateWildMon (docs/ROUTINE_MAP.md v17: real body 0x08A14838, 7 internal
 * `bl` call sites inside the same compiled unit — all 7 retargeted by
 * tools/build_patch.py to CharacterMode_CreateWildMon below, which does the
 * override then tail-calls the real, byte-for-byte-untouched CreateWildMon).
 * Static/scripted encounters (setwildbattle -> CreateScriptedWildMon) are a
 * completely separate function this never touches, so they are
 * unaffected by construction, matching the "never touch gift/scripted
 * encounters" requirement.
 *
 * Per-species metadata (tools/character_mode/emit_wild_meta.py,
 * wild_species_meta.bin, injected alongside the character/roster tables):
 * a dense array indexed by species id, one record per species covering the
 * donor's entire species range, giving each species' canon level range for
 * ITS evolutionary stage (derived from the DPE donor's real Evolution
 * Table.c) plus its evolution-line "family root" id and a legendary/
 * mythical flag (the exact same LEGENDARY_BASES set emit_characters.py
 * already uses for starter eligibility, expanded to full families, so wild-
 * encounter exclusion and starter exclusion never disagree).
 */

/* Freestanding build (-ffreestanding -fno-builtin, no libgcc linked) has no
 * __aeabi_uidivmod/__aeabi_idivmod — the wild-encounter picker only ever
 * needs small moduli (<=100), so a plain subtract loop avoids that
 * dependency entirely rather than pulling in libgcc. */
static u32 CharacterMode_UMod(u32 value, u32 modulus)
{
    if (modulus == 0)
        return 0;
    while (value >= modulus)
        value -= modulus;
    return value;
}

#define WILD_META_COUNT 1294 /* donor include/species.h NUM_SPECIES, 2026-07-17 */
#define WILD_META_LEGENDARY 0x1
#define WILD_OVERRIDE_CHANCE_PERCENT 10
/* Independent of the 10% roll above, not carved out of it: carving would
 * change the feel of an already-shipped feature. */
#define WILD_LEGENDARY_CHANCE_PERCENT 1
/* Supplied by the injector (-DMAX_WILD_FAMILY_ROOTS), computed from the real
 * rosters with margin. It was a hardcoded 48 described as "generous: no roster
 * has this many distinct lines" -- which stopped being true: Goh reaches 83,
 * Ash 53, Oak 50. The overflow is SILENT (the `rootCount < MAX` guard just
 * stops adding), so those characters quietly lost evolution lines from the
 * wild-encounter override with no error anywhere. */
#ifndef MAX_WILD_FAMILY_ROOTS
#define MAX_WILD_FAMILY_ROOTS 96
#endif

struct WildSpeciesMetaBin
{
    u8 levelMin;
    u8 levelMax;
    u8 flags; /* bit0 = legendary/mythical family */
    u8 reserved;
    u16 familyRoot;
};

extern const struct WildSpeciesMetaBin gWildSpeciesMeta[]; /* WILD_META_COUNT entries */

/* ---- Pokedex "already caught" filter (game_plans/legendary_encounters.md
 *      §1.3) ----
 *
 * Both addresses RE-VERIFIED byte-exact in THIS ROM by disassembly rather than
 * copied from the sibling project: SpeciesToNationalPokedexNum reads a u16 from
 * the table at 0x09A41FEC indexed by (species-1) and returns 0 for species 0;
 * GetSetPokedexFlag does `movs r2,#0` before tail-calling its worker, which is
 * exactly what makes it take a NATIONAL DEX NUMBER rather than a species id.
 *
 * ⚠️ Species id != national dex number in this ROM (species 386 is Volbeat,
 * natdex 313). Passing a species id here would silently filter the wrong
 * Pokemon, and would look like the feature just never firing. */
#define FLAG_GET_CAUGHT 1

extern u16 SpeciesToNationalPokedexNum(u16 species);
/* Really returns s8 (the ROM sign-extends r0 with lsls/asrs #24); this header
 * has no s8 typedef and the value is only ever tested against zero. */
extern int GetSetPokedexFlag(u16 nationalDexNo, u8 caseId);

static bool8 CharacterMode_AlreadyCaught(u16 species)
{
    u16 dexNum = SpeciesToNationalPokedexNum(species);

    /* No dex entry of its own -> never offer it. The engine's own
     * FixPokedexCheckNullSpeciesHook already guards natdex 0, but a species
     * the dex cannot represent is not something to spawn as a "catch this
     * once" reward either, so this is filtered here too and does not depend
     * on that hook staying in place. */
    if (dexNum == 0)
        return TRUE;
    return GetSetPokedexFlag(dexNum, FLAG_GET_CAUGHT) != 0;
}

/* Does this character have anything NON-legendary to find? Drives the §1.2
 * exemption: a roster that is entirely legendary (Cogita, Tobias) keeps its
 * legendaries repeatable, because otherwise catching the one family would
 * leave that character able to catch nothing at all for the rest of the run --
 * while still being selectable, since the playability threshold exempts them
 * precisely FOR having a legendary.
 *
 * Deliberately does not reuse the picker to answer this: the picker consumes
 * Random(), and a probe that perturbs the RNG stream would change encounter
 * behaviour just by being asked a question. */
static bool8 CharacterMode_HasFamilyOfKind(const struct CharacterRecordBin *character,
                                           bool8 wantLegendary)
{
    const u16 *roster;
    u32 i;

    if (character == 0)
        return FALSE;
    roster = (const u16 *)((const u8 *)gCharacterRosters + character->rosterOffset);
    for (i = 0; roster[i] != SPECIES_NONE; i++)
    {
        u16 sp = roster[i];

        if (sp >= WILD_META_COUNT)
            continue;
        if (((gWildSpeciesMeta[sp].flags & WILD_META_LEGENDARY) != 0) == wantLegendary)
            return TRUE;
    }
    return FALSE;
}

static bool8 CharacterMode_HasNonLegendaryFamily(const struct CharacterRecordBin *character)
{
    return CharacterMode_HasFamilyOfKind(character, FALSE);
}

/* Decision core (factored out so the self-test can drive it directly, same
 * pattern as CharacterMode_SubstituteGiftSpecies). Picks a random evolution
 * LINE present in the active character's roster whose legendary-ness matches
 * `wantLegendary`, then within that line the stage whose canon level range
 * best matches rolledLevel (exact containment first, else nearest boundary).
 * When skipCaught is set, members already recorded as caught in the Pokedex
 * are excluded -- that is what makes a legendary a once-each reward.
 *
 * ONE family buffer, selected by flag, deliberately: a second parallel array
 * would double a 192-byte stack allocation against the stack assert in
 * tools/build_patch.py. Returns SPECIES_NONE if there is no character active,
 * the roster is empty, or nothing matches -- which the caller treats as
 * "leave the vanilla roll alone", never as a substitution to species 0. */
static u16 CharacterMode_PickWildFamily(u16 rolledLevel, bool8 wantLegendary,
                                        bool8 skipCaught)
{
    const struct CharacterRecordBin *character = GetActiveCharacter();
    const u16 *roster;
    u16 roots[MAX_WILD_FAMILY_ROOTS];
    u8 rootCount = 0;
    u32 i;
    u16 chosenRoot;
    u16 best = SPECIES_NONE;
    int bestDist = 0;

    if (character == 0)
        return SPECIES_NONE;

    roster = (const u16 *)((const u8 *)gCharacterRosters + character->rosterOffset);

    for (i = 0; roster[i] != SPECIES_NONE; i++)
    {
        u16 sp = roster[i];
        u16 root;
        u32 j;
        bool8 dup;

        if (sp >= WILD_META_COUNT)
            continue;
        if (((gWildSpeciesMeta[sp].flags & WILD_META_LEGENDARY) != 0) != wantLegendary)
            continue;
        if (skipCaught && CharacterMode_AlreadyCaught(sp))
            continue;
        root = gWildSpeciesMeta[sp].familyRoot;
        dup = FALSE;
        for (j = 0; j < rootCount; j++)
        {
            if (roots[j] == root)
            {
                dup = TRUE;
                break;
            }
        }
        if (!dup && rootCount < MAX_WILD_FAMILY_ROOTS)
            roots[rootCount++] = root;
    }

    if (rootCount == 0)
        return SPECIES_NONE;

    chosenRoot = roots[CharacterMode_UMod(Random(), rootCount)];

    for (i = 0; roster[i] != SPECIES_NONE; i++)
    {
        u16 sp = roster[i];
        int dist;

        if (sp >= WILD_META_COUNT)
            continue;
        if (((gWildSpeciesMeta[sp].flags & WILD_META_LEGENDARY) != 0) != wantLegendary)
            continue;
        if (skipCaught && CharacterMode_AlreadyCaught(sp))
            continue;
        if (gWildSpeciesMeta[sp].familyRoot != chosenRoot)
            continue;

        if (rolledLevel >= gWildSpeciesMeta[sp].levelMin && rolledLevel <= gWildSpeciesMeta[sp].levelMax)
            dist = 0;
        else if (rolledLevel < gWildSpeciesMeta[sp].levelMin)
            dist = gWildSpeciesMeta[sp].levelMin - rolledLevel;
        else
            dist = rolledLevel - gWildSpeciesMeta[sp].levelMax;

        if (best == SPECIES_NONE || dist < bestDist)
        {
            best = sp;
            bestDist = dist;
        }
    }
    return best;
}

/* The existing 10% override's picker: NON-legendary only, unchanged
 * behaviour. Kept as its own entry point rather than folded into the
 * legendary one -- unit check L9 asserts across 200 picks that this never
 * returns a legendary, and sharing one function would make that check fail
 * the moment legendaries became pickable at all. */
u16 CharacterMode_PickWildRosterSpecies(u16 rolledLevel)
{
    return CharacterMode_PickWildFamily(rolledLevel, FALSE, FALSE);
}

/* The 1% roll's picker: legendary families only, filtered by the Pokedex so
 * each is offered until it is caught -- except for an all-legendary roster,
 * which stays repeatable (§1.2). */
u16 CharacterMode_PickWildLegendarySpecies(u16 rolledLevel)
{
    const struct CharacterRecordBin *character = GetActiveCharacter();
    bool8 repeatable;

    if (character == 0)
        return SPECIES_NONE;
    repeatable = !CharacterMode_HasNonLegendaryFamily(character);
    return CharacterMode_PickWildFamily(rolledLevel, TRUE, !repeatable);
}

/* Gate: mode off -> untouched passthrough; else two INDEPENDENT rolls, the
 * legendary one first (game_plans/legendary_encounters.md §1.1):
 *
 *     1%  -> a legendary from this character's roster
 *     10% -> a non-legendary roster member  (the existing feature, unchanged)
 *     else   the game's own wild table
 *
 * Net ~1% legendary / ~9.9% roster / ~89% vanilla. A character with no
 * legendary is unaffected: the 1% roll finds nothing to offer and falls
 * through to exactly the behaviour it had before, at exactly the same rate.
 * Only replace on a successful pick -- SPECIES_NONE means "leave the vanilla
 * species alone". */
u16 CharacterMode_MaybeOverrideWildSpecies(u16 species, u8 level)
{
    u16 replacement;

    if (!InCharacterMode())
        return species;

    /* The DATA CHECK comes before the roll, and that ordering is load-bearing:
     * Random() is the game's own LCG, so consuming one extra value per wild
     * encounter would shift the whole downstream RNG stream (shininess, IVs,
     * every later roll) for the ~115 characters that have no legendary at all.
     * Testing "does this character even have one" first means those characters
     * consume exactly the RNG they did before this feature existed, which is
     * what "a character with no legendary is completely unaffected" has to
     * mean to be true. */
    if (CharacterMode_HasFamilyOfKind(GetActiveCharacter(), TRUE)
        && CharacterMode_UMod(Random(), 100) < WILD_LEGENDARY_CHANCE_PERCENT)
    {
        replacement = CharacterMode_PickWildLegendarySpecies(level);
        if (replacement != SPECIES_NONE)
            return replacement;
    }

    if (CharacterMode_UMod(Random(), 100) >= WILD_OVERRIDE_CHANCE_PERCENT)
        return species;
    replacement = CharacterMode_PickWildRosterSpecies(level);
    if (replacement == SPECIES_NONE)
        return species;
    return replacement;
}

/* Retarget of the 4 real random-table-roll `bl CreateWildMon` call sites
 * inside the compiled wild_encounter.c unit (tools/build_patch.py). Runs the
 * override, then tail-calls the real CreateWildMon — which is never itself
 * modified, so nature/ability/shiny-lock/custom-move/hidden-ability logic all
 * still run exactly as vanilla, just against the (possibly) substituted
 * species. */
void CharacterMode_CreateWildMon(u16 species, u8 level, u8 monHeaderIndex, bool8 purgeParty)
{
    species = CharacterMode_MaybeOverrideWildSpecies(species, level);
    CreateWildMon(species, level, monHeaderIndex, purgeParty);
}

/* ---- live-gameplay probe (tools/test_harness/run_wild_encounter_test.sh) ----
 *
 * Reliability note: driving hundreds of individual GDB register-hijacks at a
 * running free-roam state is flaky on mGBA's QT stub (the same limitation
 * unit_tests.gdb documents). So the live test enables Character Mode in the
 * real save, then makes ONE hijack into this routine, which runs the whole
 * observation loop INSIDE the emulated CPU: it calls the REAL, live
 * TryGenerateWildMon (0x08A14EC4 — the actual grass/cave/surf generator, which
 * physically contains our hooked `bl` at 0x08A14FE6) against a controlled land
 * table, reads back each produced wild mon via the engine's own GetMonData,
 * and tallies the results into EWRAM. Every override therefore travels the
 * exact live code path a grass step does: TryGenerateWildMon -> hooked bl ->
 * CharacterMode_CreateWildMon -> override -> real CreateWildMon.
 *
 * Filler species 19 (Rattata) is off every character's roster, so any produced
 * species other than 19/SPECIES_NONE is unambiguously our override; the routine
 * self-verifies each override is on the active roster and non-legendary. */

struct CMWildPokemon
{
    u8 minLevel;
    u8 maxLevel;
    u16 species;
};

/* NOTE: in this ROM's build TryGenerateWildMon reads wildMonInfo->wildPokemon
 * at OFFSET 0 (confirmed by disasm: `ldr r0,[r5,#0]` feeding the ability-index
 * helper), i.e. the pointer is the struct's first field — not the donor's
 * {encounterRate; wildPokemon}. encounterRate is consumed earlier by the
 * caller's rate test, not by TryGenerateWildMon, so we only need the pointer. */
struct CMWildPokemonInfo
{
    const struct CMWildPokemon *wildPokemon;
    u8 encounterRate;
    u8 pad0;
    u8 pad1;
    u8 pad2;
};

extern struct Pokemon gEnemyParty[];
extern bool8 TryGenerateWildMon(const struct CMWildPokemonInfo *info, u8 area, u8 flags);
void CharacterMode_SelfTestDone(void);   /* defined in the self-test section below */

#define WILD_PROBE_FILLER 19   /* Rattata: on no character's roster */
#define WILD_PROBE_LEVEL 25
#define WILD_PROBE_N 64
#define WILD_PROBE_LEGEND_N 32 /* direct legendary-picker calls (positive check) */
#define WILD_PROBE_RESULTS ((volatile u16 *)0x02030100)  /* N result species */
#define WILD_PROBE_META    ((volatile u32 *)0x02030200)  /* [0]=N [1]=overrides
                              [2]=off_roster_hits [3]=legendary_hits [4]=magic
                              [5]=progress [6]=legend_ok [7]=legend_bad
                              [8]=legend_none [9]=legend_offroster */

void CharacterMode_RunWildLiveProbe(void)
{
    struct CMWildPokemon mons[12];
    struct CMWildPokemonInfo info;
    u32 overrides = 0, off_roster = 0, legendary = 0;
    u32 legend_ok = 0, legend_bad = 0, legend_none = 0, legend_offroster = 0;
    u32 i;

    for (i = 0; i < 12; i++)
    {
        mons[i].minLevel = WILD_PROBE_LEVEL;
        mons[i].maxLevel = WILD_PROBE_LEVEL;
        mons[i].species = WILD_PROBE_FILLER;
    }
    info.encounterRate = 10;
    info.pad0 = info.pad1 = info.pad2 = 0;
    info.wildPokemon = mons;

    WILD_PROBE_META[4] = 0xE47E5ED0; /* entry marker */
    for (i = 0; i < WILD_PROBE_N; i++)
    {
        u16 species;

        WILD_PROBE_META[5] = i;      /* progress marker */
        /* the REAL live generator; area 0 = WILD_AREA_LAND, flags 0 = no
         * repel/keen-eye gate. Builds the mon into gEnemyParty[0]. */
        TryGenerateWildMon(&info, 0, 0);
        species = GetMonData(&gEnemyParty[0], MON_DATA_SPECIES, 0);
        WILD_PROBE_RESULTS[i] = species;

        if (species != WILD_PROBE_FILLER && species != SPECIES_NONE)
        {
            overrides++;
            if (!IsSpeciesAllowedForCharacter(species))
                off_roster++;
            if (species < WILD_META_COUNT
                && (gWildSpeciesMeta[species].flags & WILD_META_LEGENDARY))
                legendary++;
        }
    }

    /* ---- positive direction for the legendary path ----
     *
     * The tally above cannot prove the 1% feature works: at 64 samples it
     * expects well under one hit, and "no legendary appeared" is satisfied
     * just as well by the legendary path being completely dead. So drive the
     * legendary picker directly and require that what it returns really is a
     * legendary on this character's roster. Same live ROM, same real Pokedex
     * reads -- only the 1-in-100 roll is bypassed.
     *
     * This is the assertion legendary_encounters.md §5 calls the biggest risk
     * in the whole feature. */
    {
        u32 k;

        for (k = 0; k < WILD_PROBE_LEGEND_N; k++)
        {
            u16 sp = CharacterMode_PickWildLegendarySpecies(WILD_PROBE_LEVEL);

            if (sp == SPECIES_NONE)
                legend_none++;
            else if (sp < WILD_META_COUNT
                     && (gWildSpeciesMeta[sp].flags & WILD_META_LEGENDARY))
            {
                legend_ok++;
                if (!IsSpeciesAllowedForCharacter(sp))
                    legend_offroster++;
            }
            else
                legend_bad++;
        }
    }

    WILD_PROBE_META[0] = WILD_PROBE_N;
    WILD_PROBE_META[1] = overrides;
    WILD_PROBE_META[2] = off_roster;
    WILD_PROBE_META[3] = legendary;
    /* [5] is the in-loop progress marker -- do not reuse it */
    WILD_PROBE_META[6] = legend_ok;
    WILD_PROBE_META[7] = legend_bad;
    WILD_PROBE_META[8] = legend_none;
    WILD_PROBE_META[9] = legend_offroster;
    WILD_PROBE_META[4] = 0xB0DEBEEF;
    CharacterMode_SelfTestDone();
}

/* ---- GDB-driven self-test (tools/test_harness) ----
 *
 * ROWE tests via an in-game debug menu; the binary-hack equivalent is this
 * in-ROM test runner. The whole unit matrix executes inside the emulated
 * CPU — every check goes through the real engine calls (FlagSet/VarSet ->
 * CFRU expanded-save handlers, etc.), so it exercises the exact code paths
 * the hooks use. The harness (tools/test_harness/unit_tests.gdb) starts it
 * at the reset state via a tiny ARM->Thumb shim poked into EWRAM, breaks on
 * CharacterMode_SelfTestDone, then reads the result bytes back.
 *
 * Dead code in normal play: nothing in the ROM calls it. Safe at reset
 * because IME=0 (no interrupts) and only our own callees run — the CFRU
 * expanded flag/var arrays are fixed EWRAM addresses needing no save init.
 */

#define FLAG_NO_CATCHING 0x9F8
#define SELFTEST_BUF ((volatile u8 *)0x0203FE00)
#define SELFTEST_COUNT (*(volatile u32 *)0x0203FEF8)
#define SELFTEST_MAGIC (*(volatile u32 *)0x0203FEFC)

/* noinline so the harness's parked-PC check can match this symbol's range */
__attribute__((noinline)) void CharacterMode_SelfTestDone(void)
{
    for (;;)
        ;
}

/* ---- character-select menu: scrolling-multichoice list hooks ----
 *
 * Unbound ships CFRU's scrolling multichoice (special 0x158): the vanilla
 * list machinery at 0x080CB7C4 asks two tiny CFRU getters for the list.
 * We trampoline BOTH getters (0x09EB48B8 / 0x09EB48D4, wired in
 * tools/build_patch.py) to these replacements: a magic set index returns
 * the 179 character names; anything else reproduces the originals exactly
 * (including Unbound's own idx>31 clamp-to-0), so every existing menu in
 * the game behaves identically.
 *
 * Script contract (decoded from Unbound's own scripts, docs/ROUTINE_MAP.md):
 *   setvar 0x8000, <set>; setvar 0x8001, <rows>; setvar 0x8004, <cursor>;
 *   special 0x158; waitstate -> 0x800D = picked index, 0xFFFF on cancel.
 *   (0x8004 MUST be set: a stale value crashes the vanilla task.)
 */

/* ---- character-select support (see docs/ROUTINE_MAP.md v8.2 for why the
 * scrolling-multichoice approaches were abandoned: the sets table is read
 * by unknown Unbound-custom code with raw indices AND likely end-pointer
 * loop bounds, so neither magic indices nor relocation are safe). The v3
 * select flow uses CFRU's ChooseNumberScreen (special 0x0B3) + this
 * name-buffering special, wired into the reserved gSpecials[0x1B6]. ---- */

extern const u8 *const gCharacterNamePtrs[];

/* special 0x1B6: copy the character name for the id currently in VAR_RESULT
 * (0x800D — the number the player just entered, validated 1..count by the
 * script BEFORE this special runs) into gStringVar1 so the confirmation
 * msgbox can say "play as {STR_VAR_1}?". Invalid id -> empty string. */
void CharacterMode_BufferNameSpecial(void)
{
    u16 id = VarGet(0x800D);
    u8 *dst = gStringVar1;

    if (id >= 1 && id <= gCharacterCount)
    {
        const u8 *src = gCharacterNamePtrs[id - 1];

        while ((*dst++ = *src++) != 0xFF)
            ;
    }
    else
        *dst = 0xFF;
}

/* ---- playability-threshold gating (../push_rosters.md §3) ----
 *
 * A character with fewer than six fully-evolved Pokemon obtainable in this
 * game's dex (and no legendary to exempt it) is not worth offering: the wild
 * override and the catch gate would leave the player with almost nothing to
 * find. emit_characters.py sets CHAR_FLAG_HIDDEN on those records from
 * character_drops.json.
 *
 * ONLY the selection path consults this. Enforcement deliberately does not:
 * a save that already stores a hidden character's index must keep working
 * exactly as before, because the id in the save IS the table index. That is
 * also why hiding never renumbers anyone -- the emitted table keeps all 208
 * records and the hidden ones simply stop being choosable. */
bool8 CharacterMode_IsCharacterSelectable(u16 id)
{
    if (id < 1 || id > gCharacterCount)
        return FALSE;
    return (gCharacterTable[id - 1].flags & CHAR_FLAG_HIDDEN) == 0;
}

/* callnative target for the number-entry validation loop. ScrCmd_callnative
 * discards the C return value, so the verdict is handed back through a var:
 * VAR_SELECTABLE_RESULT = 1 when the id in VAR_RESULT may be chosen, 0 when it
 * is out of range or hidden. The script compares and re-asks on 0.
 *
 * 0x800C is used rather than one of 0x8000-0x800B: those are givemon's own
 * override channel, and nothing else in this project reads or writes 0x800C. */
void CharacterMode_CheckSelectableNative(void)
{
    VarSet(0x800C, CharacterMode_IsCharacterSelectable(VarGet(0x800D)) ? 1 : 0);
}

/* Debug/test primitive (the ROWE debug-menu equivalent for a binary hack):
 * queue the new-game difficulty script (entry 0x09E70000 — flows through our
 * opt-in splice at 0x09E70003) on the game's own script engine, then park in
 * SelfTestDone so the harness can restore the interrupted CPU context. The
 * overworld CB1 picks the queued script up on the next frame. Never called
 * by the game itself. */
void CharacterMode_TriggerIntroScript(void)
{
    ScriptContext1_SetupScript((const u8 *)0x09E70000);
    CharacterMode_SelfTestDone();
}

/* One-frame gMain.callback1 stand-in for the live test harness: restores
 * the overworld CB1 and queues the new-game difficulty script (which flows
 * through the opt-in splice). Constants only — earlier harness versions
 * poked shim code into high EWRAM at runtime, which intermittently got
 * clobbered by live list-menu buffers (0x0203F37C+) and crashed/reset the
 * game. ROM-resident code + zero runtime RAM = deterministic. The harness
 * installs it by writing gMain.callback1 (0x030030F0) once while stopped;
 * the game itself calls it next frame with correct interworking. Never
 * called by the game otherwise. */
void CharacterMode_QueueIntroScriptCb1(void)
{
    *(volatile u32 *)0x030030F0 = 0x08056535;      /* CB1_Overworld|1 */
    ScriptContext1_SetupScript((const u8 *)0x09E70000);
}

/* Parameterized variant: the script pointer is read from expanded vars
 * 0x51F8/0x51F9 (EWRAM 0x0203B764 — audited unused; 4 bytes of DATA there
 * is safe where poked CODE was not). Debug scripts themselves live in ROM
 * (baked by tools/build_patch.py). Never called by the game. */
void CharacterMode_QueueScriptCb1(void)
{
    *(volatile u32 *)0x030030F0 = 0x08056535;      /* CB1_Overworld|1 */
    ScriptContext1_SetupScript((const u8 *)*(volatile u32 *)0x0203B764);
}

/* OFF_ROSTER_SPECIES: the self-test's control for "not on Red's roster".
 *
 * This was Mewtwo (150) until the 2026-07-25 roster audit, whose wave 5
 * explicitly KEPT Mewtwo for Red -- Pokemon Origins, where he weakens it with
 * Mega Charizard X and catches it with an Ultra Ball (the Adventures Mewtwo is
 * Blaine's, which is why it looks wrong at first glance). Three checks went red
 * (B5/C1/G1) and, worse, four more (H1/H2/K1/K2) kept PASSING while no longer
 * testing anything, because their expected outcome is "kept" either way.
 *
 * Re-picked BY FAMILY BASE, the documented rule: Sandshrew's whole family is
 * absent from Red's roster, so no evolution or regional form can quietly put it
 * back. Verify with tools/character_mode/rosters_mapped.json before changing.
 */
#define OFF_ROSTER_SPECIES 27   /* Sandshrew */

void CharacterMode_RunSelfTest(void)
{
    volatile u8 *r = SELFTEST_BUF;
    u32 n = 0;
    u32 i;

    /* A: mode off */
    FlagClear(FLAG_CHARACTER_MODE);
    VarSet(VAR_CHARACTER_ID, 0);
    FlagClear(FLAG_NO_CATCHING);
    r[n++] = InCharacterMode();                      /* A1 want 0 */
    r[n++] = IsSpeciesAllowedForCharacter(OFF_ROSTER_SPECIES); /* A2 want 1 */
    r[n++] = CharacterMode_CatchFlagGet(FLAG_NO_CATCHING); /* A3 want 0 */

    /* B: mode on as character 1 (Red) */
    FlagSet(FLAG_CHARACTER_MODE);
    VarSet(VAR_CHARACTER_ID, 1);
    r[n++] = InCharacterMode();                      /* B1 want 1 */
    r[n++] = (u8)GetCharacterCount();                /* B2 want 179 */
    r[n++] = IsSpeciesAllowedForCharacter(25);       /* B3 Pikachu want 1 */
    r[n++] = IsSpeciesAllowedForCharacter(6);        /* B4 Charizard (family expansion) want 1 */
    r[n++] = IsSpeciesAllowedForCharacter(OFF_ROSTER_SPECIES); /* B5 want 0 */
    r[n++] = IsSpeciesAllowedForCharacter(0);        /* B6 SPECIES_NONE want 0 */

    /* C: catch gate against live battle state */
    gBankTarget = 0;
    BATTLEMON_SPECIES(0) = OFF_ROSTER_SPECIES;
    r[n++] = CharacterMode_CatchFlagGet(FLAG_NO_CATCHING); /* C1 want 1 (blocked) */
    BATTLEMON_SPECIES(0) = 25;
    r[n++] = CharacterMode_CatchFlagGet(FLAG_NO_CATCHING); /* C2 want 0 (allowed) */
    BATTLEMON_SPECIES(0) = 6;
    r[n++] = CharacterMode_CatchFlagGet(FLAG_NO_CATCHING); /* C3 want 0 (allowed) */

    /* D: FLAG_NO_CATCHING passthrough with mode off */
    FlagClear(FLAG_CHARACTER_MODE);
    FlagSet(FLAG_NO_CATCHING);
    r[n++] = CharacterMode_CatchFlagGet(FLAG_NO_CATCHING); /* D1 want 1 */
    FlagClear(FLAG_NO_CATCHING);

    /* E: out-of-range character id behaves as mode off */
    FlagSet(FLAG_CHARACTER_MODE);
    VarSet(VAR_CHARACTER_ID, 999);
    r[n++] = InCharacterMode();                      /* E1 want 0 */
    r[n++] = IsSpeciesAllowedForCharacter(OFF_ROSTER_SPECIES); /* E2 want 1 */

    /* F/G: GiveMonToPlayer routing. Built from a zeroed stack mon with the
     * species written at raw+0x20 (the unencrypted CFRU layout the shipped
     * binary itself uses). G deliberately only asserts the off-roster mon
     * did NOT join the party — the PC path runs against a null storage
     * pointer at reset, so its return value is not meaningful here. */
    FlagSet(FLAG_CHARACTER_MODE);
    VarSet(VAR_CHARACTER_ID, 1);
    for (i = 0; i < PARTY_SIZE; i++)
        ZeroMonData(&gPlayerParty[i]);
    gPlayerPartyCount = 0;
    {
        struct Pokemon m;
        u32 j;

        for (j = 0; j < POKEMON_SIZE; j++)
            m.raw[j] = 0;
        *(u16 *)(m.raw + 0x20) = 25;                         /* Pikachu */
        r[n++] = CharacterMode_GiveMonToPlayer(&m);          /* F1 want 0 (party) */
        r[n++] = *(u16 *)(gPlayerParty[0].raw + 0x20) == 25; /* F2 want 1 */
        r[n++] = gPlayerPartyCount;                          /* F3 want 1 */

        for (j = 0; j < POKEMON_SIZE; j++)
            m.raw[j] = 0;
        *(u16 *)(m.raw + 0x20) = OFF_ROSTER_SPECIES;          /* off-roster */
        CharacterMode_GiveMonToPlayer(&m);
        r[n++] = (gPlayerPartyCount == 1
                  && *(u16 *)(gPlayerParty[1].raw + 0x20) == SPECIES_NONE); /* G1 want 1 */

        /* H: empty-party softlock guard — an off-roster gift into an EMPTY
         * party (the intro starter case) must be accepted, not PC-routed. */
        for (i = 0; i < PARTY_SIZE; i++)
            ZeroMonData(&gPlayerParty[i]);
        gPlayerPartyCount = 0;
        for (j = 0; j < POKEMON_SIZE; j++)
            m.raw[j] = 0;
        *(u16 *)(m.raw + 0x20) = OFF_ROSTER_SPECIES;          /* off-roster */
        r[n++] = CharacterMode_GiveMonToPlayer(&m);          /* H1 want 0 (party) */
        r[n++] = *(u16 *)(gPlayerParty[0].raw + 0x20) == OFF_ROSTER_SPECIES; /* H2 want 1 */
    }

    /* I: character-name buffering for the select flow (special 0x1B6) */
    VarSet(0x800D, 1);
    CharacterMode_BufferNameSpecial();
    r[n++] = gStringVar1[0] != 0xFF;   /* I1 want 1: char 1 has a name */
    r[n++] = gStringVar1[0];           /* I2 want 204 ('R' of Red) */
    VarSet(0x800D, GetCharacterCount());   /* last character id */
    CharacterMode_BufferNameSpecial();
    r[n++] = gStringVar1[0] != 0xFF;   /* I3 want 1: last char has a name */
    VarSet(0x800D, 0);
    CharacterMode_BufferNameSpecial();
    r[n++] = gStringVar1[0] == 0xFF;   /* I4 want 1: 0 -> empty */
    VarSet(0x800D, 999);
    CharacterMode_BufferNameSpecial();
    r[n++] = gStringVar1[0] == 0xFF;   /* I5 want 1: out of range -> empty */
    VarSet(0x800D, 0);

    /* J: starter grant — first-mon species substitution */
    FlagSet(FLAG_CHARACTER_MODE);
    VarSet(VAR_CHARACTER_ID, 1);                        /* Red */
    for (i = 0; i < PARTY_SIZE; i++)
        ZeroMonData(&gPlayerParty[i]);
    gPlayerPartyCount = 0;
    r[n++] = (u8)CharacterMode_GetStarterSpecies();      /* J1 want 25 (Pikachu) */
    r[n++] = (u8)CharacterMode_SubstituteGiftSpecies(246); /* J2 empty party: Larvitar->25 */
    *(u16 *)(gPlayerParty[0].raw + 0x20) = 25;
    r[n++] = CharacterMode_SubstituteGiftSpecies(246) == 246; /* J3 non-empty: passthrough, want 1 */
    *(u16 *)(gPlayerParty[0].raw + 0x20) = 0;
    FlagClear(FLAG_CHARACTER_MODE);
    r[n++] = CharacterMode_SubstituteGiftSpecies(246) == 246; /* J4 mode off: passthrough, want 1 */
    r[n++] = CharacterMode_GetStarterSpecies() == 0;     /* J5 mode off: no starter, want 1 */

    /* K: trade sweep (CharacterMode_SweepPartyToPC, special 0x1AF).
     * Only reset-deterministic assertions here: the actual PC delivery of a
     * swept mon is proven by the live trade test (SendMonToPC's return at
     * reset state is not meaningful, same caveat as G1). Party mons are
     * built raw: species u16 at +0x20 (growth substruct), egg bit is IV
     * word bit 30 at +0x48 (misc substruct) — CFRU unencrypted layout. */
    {
        /* K1: mode off -> sweep is a no-op even with an off-roster mon */
        FlagClear(FLAG_CHARACTER_MODE);
        VarSet(VAR_CHARACTER_ID, 0);
        for (i = 0; i < PARTY_SIZE; i++)
            ZeroMonData(&gPlayerParty[i]);
        *(u16 *)(gPlayerParty[0].raw + 0x20) = OFF_ROSTER_SPECIES; /* off-roster */
        gPlayerPartyCount = 1;
        CharacterMode_SweepPartyToPC();
        r[n++] = *(u16 *)(gPlayerParty[0].raw + 0x20) == OFF_ROSTER_SPECIES; /* K1 want 1 */

        /* K2: never-empty guard — sole off-roster mon is kept (this path
         * never even calls SendMonToPC, so it's fully deterministic) */
        FlagSet(FLAG_CHARACTER_MODE);
        VarSet(VAR_CHARACTER_ID, 1);                          /* Red */
        CharacterMode_SweepPartyToPC();
        r[n++] = *(u16 *)(gPlayerParty[0].raw + 0x20) == OFF_ROSTER_SPECIES; /* K2 want 1 */

        /* K3: all-on-roster party untouched */
        for (i = 0; i < PARTY_SIZE; i++)
            ZeroMonData(&gPlayerParty[i]);
        *(u16 *)(gPlayerParty[0].raw + 0x20) = 25;            /* Pikachu */
        gPlayerPartyCount = 1;
        CharacterMode_SweepPartyToPC();
        r[n++] = (*(u16 *)(gPlayerParty[0].raw + 0x20) == 25
                  && gPlayerPartyCount == 1);                 /* K3 want 1 */

        /* K4: mixed party — the on-roster mon survives in slot 0 whatever
         * SendMonToPC returned for the off-roster one (swept -> compacted
         * to [Pikachu]; boxes-full path -> [Pikachu, Mewtwo]) */
        for (i = 0; i < PARTY_SIZE; i++)
            ZeroMonData(&gPlayerParty[i]);
        *(u16 *)(gPlayerParty[0].raw + 0x20) = 25;
        *(u16 *)(gPlayerParty[1].raw + 0x20) = OFF_ROSTER_SPECIES;
        gPlayerPartyCount = 2;
        CharacterMode_SweepPartyToPC();
        r[n++] = *(u16 *)(gPlayerParty[0].raw + 0x20) == 25;  /* K4 want 1 */

        /* K5: egg exemption — an off-roster egg is never swept */
        for (i = 0; i < PARTY_SIZE; i++)
            ZeroMonData(&gPlayerParty[i]);
        *(u16 *)(gPlayerParty[0].raw + 0x20) = 25;
        *(u16 *)(gPlayerParty[1].raw + 0x20) = OFF_ROSTER_SPECIES;
        *(u32 *)(gPlayerParty[1].raw + 0x48) |= (1u << 30);   /* isEgg */
        gPlayerPartyCount = 2;
        CharacterMode_SweepPartyToPC();
        r[n++] = *(u16 *)(gPlayerParty[1].raw + 0x20) == OFF_ROSTER_SPECIES; /* K5 want 1 */

        /* K6: ...but ONCE IT HATCHES it is swept. This is the exact state the
         * egg-hatch hook creates: the same party slot, off-roster, with the egg
         * bit now clear. K5 alone made the exemption look like a permanent
         * licence to keep an off-roster Pokemon, which is what a gift egg used
         * to do. The hook appends the sweep special to the hatch script's tail,
         * so this is the state the sweep sees when it runs. */
        *(u32 *)(gPlayerParty[1].raw + 0x48) &= ~(1u << 30);  /* hatched */
        CharacterMode_SweepPartyToPC();
        r[n++] = *(u16 *)(gPlayerParty[1].raw + 0x20) != OFF_ROSTER_SPECIES; /* K6 want 1 */

        for (i = 0; i < PARTY_SIZE; i++)
            ZeroMonData(&gPlayerParty[i]);
        gPlayerPartyCount = 0;
    }

    /* L: wild-encounter roster override (CharacterMode_CreateWildMon /
     * CharacterMode_MaybeOverrideWildSpecies / CharacterMode_PickWildRosterSpecies).
     * L1-L2 exercise the gate; L3-L7 verify the injected per-species metadata
     * table (levelMin/levelMax/familyRoot/legendary flag) round-tripped
     * correctly through the build+injection pipeline for a known family
     * (Charmander(4)/Charmeleon(5)/Charizard(6)) and a known legendary
     * (Mewtwo, 150) vs. non-legendary (Pikachu, 25); L8-L9 are live
     * invariant/statistical checks against Red's real roster (character 1,
     * whose family-expanded roster genuinely includes legendary members —
     * Articuno/Raikou/Entei/Suicune/among others — so the exclusion path is
     * actually exercised, not vacuously true). */
    FlagClear(FLAG_CHARACTER_MODE);
    VarSet(VAR_CHARACTER_ID, 0);
    r[n++] = CharacterMode_MaybeOverrideWildSpecies(150, 50) == 150; /* L1 mode off: passthrough, want 1 */
    r[n++] = CharacterMode_PickWildRosterSpecies(50) == SPECIES_NONE; /* L2 mode off: no pick, want 1 */

    r[n++] = (gWildSpeciesMeta[4].levelMin == 1 && gWildSpeciesMeta[4].levelMax == 15);   /* L3 Charmander want 1 */
    r[n++] = (gWildSpeciesMeta[5].levelMin == 16 && gWildSpeciesMeta[5].levelMax == 35);  /* L4 Charmeleon want 1 */
    r[n++] = (gWildSpeciesMeta[6].levelMin == 36 && gWildSpeciesMeta[6].levelMax == 100); /* L5 Charizard want 1 */
    r[n++] = (gWildSpeciesMeta[4].familyRoot == 4 && gWildSpeciesMeta[5].familyRoot == 4
              && gWildSpeciesMeta[6].familyRoot == 4);                                   /* L6 same line want 1 */
    r[n++] = (gWildSpeciesMeta[150].flags & WILD_META_LEGENDARY) != 0;                    /* L7 Mewtwo legendary want 1 */
    r[n++] = (gWildSpeciesMeta[25].flags & WILD_META_LEGENDARY) == 0;                      /* L8 Pikachu not want 1 */

    FlagSet(FLAG_CHARACTER_MODE);
    VarSet(VAR_CHARACTER_ID, 1); /* Red: roster genuinely includes legendary family members */
    {
        u32 pick;
        u32 neverLegendary = 1;
        u32 overrideHits = 0;
        const u32 trials = 200;

        for (pick = 0; pick < trials; pick++)
        {
            u16 lvl = 1 + CharacterMode_UMod(pick * 7, 100); /* deterministic spread 1..100 */
            u16 sp = CharacterMode_PickWildRosterSpecies(lvl);

            if (sp != SPECIES_NONE
                && (sp >= WILD_META_COUNT || (gWildSpeciesMeta[sp].flags & WILD_META_LEGENDARY)))
                neverLegendary = 0;

            if (CharacterMode_MaybeOverrideWildSpecies(9999, lvl) != 9999)
                overrideHits++;
        }
        r[n++] = neverLegendary; /* L9: 200 picks, none ever legendary, want 1 */
        /* L10: empirical override rate near 10% (species 9999 can never be a
         * real roster member, so any change is definitely our 10% path).
         * Wide band (2%-25% of 200 = 4-50 hits) — this is a real RNG
         * consumer (CFRU's LCG), not a mocked/seeded one, so the band is
         * deliberately generous to avoid flaking while still catching a
         * badly wrong rate (e.g. always-on or never-firing). */
        r[n++] = (overrideHits >= 4 && overrideHits <= 50);
    }
    FlagClear(FLAG_CHARACTER_MODE);
    VarSet(VAR_CHARACTER_ID, 0);

    /* ---- M: playability-threshold gating ----
     * Both ids are derived by build_patch.py from characters_manifest.json and
     * passed in as defines, so a roster change cannot leave these pointing at
     * the wrong character. */
    r[n++] = CharacterMode_IsCharacterSelectable(TEST_SHOWN_ID) == TRUE;   /* M1 want 1 */
    r[n++] = CharacterMode_IsCharacterSelectable(TEST_HIDDEN_ID) == FALSE; /* M2 want 1 */
    r[n++] = CharacterMode_IsCharacterSelectable(0) == FALSE;              /* M3 want 1 */
    r[n++] = CharacterMode_IsCharacterSelectable(GetCharacterCount() + 1)
             == FALSE;                                                     /* M4 want 1 */

    /* The native hands its verdict back through 0x800C, which is what the
     * script actually branches on -- checking only the bool above would leave
     * the var plumbing (the part that can silently break) untested. */
    VarSet(0x800D, TEST_SHOWN_ID);
    VarSet(0x800C, 0xFFFF);
    CharacterMode_CheckSelectableNative();
    r[n++] = VarGet(0x800C) == 1;                                          /* M5 want 1 */
    VarSet(0x800D, TEST_HIDDEN_ID);
    VarSet(0x800C, 0xFFFF);
    CharacterMode_CheckSelectableNative();
    r[n++] = VarGet(0x800C) == 0;                                          /* M6 want 1 */

    /* M7/M8: a hidden character must remain fully PLAYABLE from a save that
     * already stores its index -- only SELECTION is gated. push_rosters.md §3
     * requires this be tested explicitly, because getting it wrong would brick
     * an existing save rather than merely hiding a menu entry. */
    FlagSet(FLAG_CHARACTER_MODE);
    VarSet(VAR_CHARACTER_ID, TEST_HIDDEN_ID);
    r[n++] = InCharacterMode() == TRUE;                                    /* M7 want 1 */
    r[n++] = CharacterMode_GetStarterSpecies() != SPECIES_NONE;            /* M8 want 1 */
    FlagClear(FLAG_CHARACTER_MODE);
    VarSet(VAR_CHARACTER_ID, 0);
    VarSet(0x800C, 0);
    VarSet(0x800D, 0);

    /* ---- N: 1% legendary wild encounters ----
     * All three character ids are derived by build_patch.py from the real
     * rosters and passed in as defines. */

    /* N1/N2: the dex conversion. Species id != national dex number in this
     * ROM, and getting that wrong would filter the WRONG species -- which
     * looks exactly like the feature never firing. 386 -> 313 (Volbeat) is
     * the documented proof that the conversion is real and not identity. */
    r[n++] = SpeciesToNationalPokedexNum(386) == 313;   /* N1 want 1 */
    r[n++] = SpeciesToNationalPokedexNum(0) == 0;       /* N2 want 1 */

    FlagSet(FLAG_CHARACTER_MODE);
    VarSet(VAR_CHARACTER_ID, TEST_LEGEND_CHAR_ID);
    {
        /* N3 is the POSITIVE direction, and it is the one that matters:
         * legendary_encounters.md §5 warns that every existing assertion here
         * is of the form "an override never produced a legendary", which a
         * completely dead legendary path satisfies perfectly. Assert instead
         * that the picker DOES produce legendaries, and that they are on the
         * roster. Nothing is caught at reset, so none are filtered out. */
        u32 k, ok = 0, bad = 0;

        for (k = 0; k < 50; k++)
        {
            u16 sp = CharacterMode_PickWildLegendarySpecies(30);

            if (sp != SPECIES_NONE && sp < WILD_META_COUNT
                && (gWildSpeciesMeta[sp].flags & WILD_META_LEGENDARY)
                && IsSpeciesAllowedForCharacter(sp))
                ok++;
            else
                bad++;
        }
        r[n++] = (ok == 50 && bad == 0);                /* N3 want 1 */
    }
    /* N4: an already-caught legendary is filtered. Read through the same
     * helper the picker uses, on a species the fresh save has not caught. */
    r[n++] = CharacterMode_AlreadyCaught(150) == FALSE; /* N5-> N4 want 1 */

    /* N5: a character with NO legendary gets nothing from the 1% roll, so it
     * falls through to exactly its previous behaviour. */
    VarSet(VAR_CHARACTER_ID, TEST_NOLEGEND_CHAR_ID);
    r[n++] = CharacterMode_PickWildLegendarySpecies(30) == SPECIES_NONE; /* N5 want 1 */
    r[n++] = CharacterMode_PickWildRosterSpecies(30) != SPECIES_NONE;    /* N6 want 1 */
    /* N6b: the predicate that gates the 1% roll. It is what keeps a
     * no-legendary character from consuming an extra Random() per encounter
     * and shifting the game's whole downstream RNG stream. */
    r[n++] = CharacterMode_HasFamilyOfKind(GetActiveCharacter(), TRUE) == FALSE; /* want 1 */

    /* N7/N8: the §1.2 exemption. An all-legendary roster has no non-legendary
     * family, so its legendaries stay repeatable -- without this, Cogita
     * catches her one family and can then catch nothing for the rest of the
     * run, while remaining selectable precisely BECAUSE she has a legendary.
     * N8 is the case that used to return SPECIES_NONE forever. */
#if TEST_ALLLEGEND_CHAR_ID
    VarSet(VAR_CHARACTER_ID, TEST_ALLLEGEND_CHAR_ID);
    r[n++] = CharacterMode_HasNonLegendaryFamily(GetActiveCharacter()) == FALSE; /* N7 want 1 */
    r[n++] = CharacterMode_PickWildLegendarySpecies(30) != SPECIES_NONE;         /* N8 want 1 */
#else
    r[n++] = 1;   /* N7 want 1: no all-legendary character in this build */
    r[n++] = 1;   /* N8 want 1 */
#endif

    /* leave the expanded save state clean */
    FlagClear(FLAG_CHARACTER_MODE);
    VarSet(VAR_CHARACTER_ID, 0);

    SELFTEST_COUNT = n;
    SELFTEST_MAGIC = 0xC0DED00D;
    CharacterMode_SelfTestDone();
}

/* ---- character mugshot (Phase 3 render surface, 2026-07-25) ----
 *
 * 136 character front pics are injected at gCharacterSpritePtrs (an additive
 * blob + pointer table that touches no engine table), but until now nothing
 * read them. These two are called from the opt-in script via `callnative`
 * (script command 0x23 — confirmed in this ROM's own command table at
 * 0x0815F9B4, and it takes an ABSOLUTE pointer, so there is no branch-range
 * constraint) and bracket the "Play as {NAME}?" confirmation, so the player
 * sees the character before committing:
 *
 *     special 0x1B6                  <- buffers the name into gStringVar1
 *     callnative CharacterMode_ShowMugshot
 *     loadword <"Play as {NAME}?">; callstd MSGBOX_YESNO   <- blocks
 *     callnative CharacterMode_HideMugshot
 *
 * Ported from RadicalRed-Character-Mode/src/character_sprite.c, which proved
 * the technique. Every address it relies on was re-verified in THIS ROM.
 *
 * Failure is silent and safe throughout: an out-of-range id, a character with
 * no staged art, or a full OBJ palette all leave the prompt looking exactly as
 * it did before this existed.
 */

#define CM_TILE_TAG 0xC0DE
#define CM_PALETTE_TAG 0xC0DF
#define MUGSHOT_GFX_SIZE 2048   /* 64x64 4bpp, decompressed */

/* Sprite position is its CENTRE (CreateSprite applies the centre-to-corner
 * vector itself), so a 64x64 mugshot here spans x 160-224, y 2-66.
 *
 * Measured, not guessed: the confirm prompt's Yes/No window occupies
 * x >= 161, y >= 67 in this game, and the message box the bottom of the
 * screen. At y = 48 (Radical Red's value) the sprite's feet were clipped by
 * the top of that window -- see build/unbound-cm-6.png from the first pass.
 * This sits it directly above the choices instead. */
#define MUGSHOT_X 192
#define MUGSHOT_Y 34

/* attr0 = 0 (square shape, 4bpp, normal), attr1 = 0xC000 (size 3 -> 64x64),
 * attr2 = 0 (priority 0; CreateSprite fills tileNum/paletteNum from the tags) */
static const u32 sMugshotOam[2] = { 0xC0000000, 0x00000000 };

static const struct SpriteTemplate sMugshotTemplate = {
    CM_TILE_TAG,
    CM_PALETTE_TAG,
    sMugshotOam,
    gDummySpriteAnimTable,
    0,
    gDummySpriteAffineAnimTable,
    SpriteCallbackDummy,
};

void CharacterMode_HideMugshot(void)
{
    u8 *s = gSprites;
    u32 i;

    /* Identify our own sprite by template pointer: needs no save-block var
     * and no scratch RAM, and stays correct if it was never created. */
    for (i = 0; i < SPRITE_COUNT; i++, s += SPRITE_STRIDE)
    {
        if (!(s[SPRITE_OFF_INUSE] & 1))
            continue;
        if (*(const void **)(s + SPRITE_OFF_TEMPLATE) == (const void *)&sMugshotTemplate)
            DestroySprite(s);
    }

    FreeSpriteTilesByTag(CM_TILE_TAG);
    FreeSpritePaletteByTag(CM_PALETTE_TAG);
}

void CharacterMode_ShowMugshot(void)
{
    struct CompressedSpriteSheet sheet;
    struct CompressedSpritePalette pal;
    const u32 *entry;
    u16 id;

    id = VarGet(VAR_CHARACTER_ID);
    if (id < 1 || id > gCharacterCount)
        return;

    /* ids are 1-based in the var, 0-based in the table */
    entry = &gCharacterSpritePtrs[(u32)(id - 1) * 2];
    if (entry[0] == 0 || entry[1] == 0)
        return;                 /* no front pic staged for this character */

    /* Re-entry is normal here: the confirm prompt sits in a validation loop,
     * so answering No returns to the number entry and comes back through.
     * Without this, each pass would strand another tile/palette allocation. */
    CharacterMode_HideMugshot();

    pal.data = (const void *)entry[1];
    pal.tag = CM_PALETTE_TAG;
    if (LoadCompressedSpritePalette(&pal) == PALETTE_ALLOC_FAIL)
        return;                 /* all 16 OBJ palette slots in use */

    sheet.data = (const void *)entry[0];
    sheet.size = MUGSHOT_GFX_SIZE;
    sheet.tag = CM_TILE_TAG;
    LoadCompressedSpriteSheet(&sheet);

    if (CreateSprite(&sMugshotTemplate, MUGSHOT_X, MUGSHOT_Y, 0) == MAX_SPRITES_RETURN)
    {
        FreeSpriteTilesByTag(CM_TILE_TAG);
        FreeSpritePaletteByTag(CM_PALETTE_TAG);
    }
}
