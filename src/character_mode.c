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
    u8 flags;         /* bit0 = hasSignature (ace at roster[0]) */
    u8 starterCount;  /* roster[0..starterCount) eligible as starters */
    u8 reserved;
    u16 pad;
};

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
 * the 156 character names; anything else reproduces the originals exactly
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
    r[n++] = IsSpeciesAllowedForCharacter(150);      /* A2 want 1 */
    r[n++] = CharacterMode_CatchFlagGet(FLAG_NO_CATCHING); /* A3 want 0 */

    /* B: mode on as character 1 (Red) */
    FlagSet(FLAG_CHARACTER_MODE);
    VarSet(VAR_CHARACTER_ID, 1);
    r[n++] = InCharacterMode();                      /* B1 want 1 */
    r[n++] = (u8)GetCharacterCount();                /* B2 want 156 */
    r[n++] = IsSpeciesAllowedForCharacter(25);       /* B3 Pikachu want 1 */
    r[n++] = IsSpeciesAllowedForCharacter(6);        /* B4 Charizard (family expansion) want 1 */
    r[n++] = IsSpeciesAllowedForCharacter(150);      /* B5 Mewtwo want 0 */
    r[n++] = IsSpeciesAllowedForCharacter(0);        /* B6 SPECIES_NONE want 0 */

    /* C: catch gate against live battle state */
    gBankTarget = 0;
    BATTLEMON_SPECIES(0) = 150;
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
    r[n++] = IsSpeciesAllowedForCharacter(150);      /* E2 want 1 */

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
        *(u16 *)(m.raw + 0x20) = 150;                        /* Mewtwo, off-roster */
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
        *(u16 *)(m.raw + 0x20) = 150;                        /* Mewtwo, off-roster */
        r[n++] = CharacterMode_GiveMonToPlayer(&m);          /* H1 want 0 (party) */
        r[n++] = *(u16 *)(gPlayerParty[0].raw + 0x20) == 150; /* H2 want 1 */
    }

    /* I: character-name buffering for the select flow (special 0x1B6) */
    VarSet(0x800D, 1);
    CharacterMode_BufferNameSpecial();
    r[n++] = gStringVar1[0] != 0xFF;   /* I1 want 1: char 1 has a name */
    r[n++] = gStringVar1[0];           /* I2 want 204 ('R' of Red) */
    VarSet(0x800D, 156);
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
        *(u16 *)(gPlayerParty[0].raw + 0x20) = 150;          /* Mewtwo */
        gPlayerPartyCount = 1;
        CharacterMode_SweepPartyToPC();
        r[n++] = *(u16 *)(gPlayerParty[0].raw + 0x20) == 150; /* K1 want 1 */

        /* K2: never-empty guard — sole off-roster mon is kept (this path
         * never even calls SendMonToPC, so it's fully deterministic) */
        FlagSet(FLAG_CHARACTER_MODE);
        VarSet(VAR_CHARACTER_ID, 1);                          /* Red */
        CharacterMode_SweepPartyToPC();
        r[n++] = *(u16 *)(gPlayerParty[0].raw + 0x20) == 150; /* K2 want 1 */

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
        *(u16 *)(gPlayerParty[1].raw + 0x20) = 150;
        gPlayerPartyCount = 2;
        CharacterMode_SweepPartyToPC();
        r[n++] = *(u16 *)(gPlayerParty[0].raw + 0x20) == 25;  /* K4 want 1 */

        /* K5: egg exemption — an off-roster egg is never swept */
        for (i = 0; i < PARTY_SIZE; i++)
            ZeroMonData(&gPlayerParty[i]);
        *(u16 *)(gPlayerParty[0].raw + 0x20) = 25;
        *(u16 *)(gPlayerParty[1].raw + 0x20) = 150;
        *(u32 *)(gPlayerParty[1].raw + 0x48) |= (1u << 30);   /* isEgg */
        gPlayerPartyCount = 2;
        CharacterMode_SweepPartyToPC();
        r[n++] = *(u16 *)(gPlayerParty[1].raw + 0x20) == 150; /* K5 want 1 */

        for (i = 0; i < PARTY_SIZE; i++)
            ZeroMonData(&gPlayerParty[i]);
        gPlayerPartyCount = 0;
    }

    /* leave the expanded save state clean */
    FlagClear(FLAG_CHARACTER_MODE);
    VarSet(VAR_CHARACTER_ID, 0);

    SELFTEST_COUNT = n;
    SELFTEST_MAGIC = 0xC0DED00D;
    CharacterMode_SelfTestDone();
}
