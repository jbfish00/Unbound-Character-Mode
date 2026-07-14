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

    /* leave the expanded save state clean */
    FlagClear(FLAG_CHARACTER_MODE);
    VarSet(VAR_CHARACTER_ID, 0);

    SELFTEST_COUNT = n;
    SELFTEST_MAGIC = 0xC0DED00D;
    CharacterMode_SelfTestDone();
}
