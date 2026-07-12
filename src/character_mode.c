/*
 * Character Mode enforcement logic — Pokemon Unbound port.
 *
 * Ported from the ROWE Character Mode project's src/character_mode.c, which
 * this file mirrors in spirit (same core algorithm: roster membership check
 * by evolution-family base stage, party sweep to PC for off-roster mons).
 * ROWE reads `const struct CharacterInfo gCharacters[]`, a C array compiled
 * straight into its build from src/data/characters.h. Unbound has no build
 * step for us — this file instead reads the RAW BINARY tables produced by
 * tools/character_mode/emit_characters.py (characters.bin / rosters.bin /
 * names.bin) directly, once they're injected into ROM free space.
 *
 * BUILD: compiled standalone with arm-none-eabi-gcc (freestanding, no libc),
 * NOT linked against any Unbound/CFRU source tree (we don't have one). Every
 * external symbol below that isn't defined in this file is expected to be
 * resolved by the Phase-1-informed insert script, which patches in the real
 * ROM addresses once Phase 1 locates them. This file is written NOW so the
 * core algorithm is ready — the extern declarations are literally the
 * project's remaining to-do list for Phase 1/4.
 *
 * STATUS: compiles conceptually, NOT YET BUILT OR TESTED (no real addresses
 * to link against yet). See docs/PHASE4_DEPENDENCIES.md for what each
 * extern needs and why.
 */

#include <stdint.h>

typedef uint8_t bool8;
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
#define TRUE 1
#define FALSE 0
#define SPECIES_NONE 0

/* ---- Binary table layout (must match tools/character_mode/emit_characters.py) ---- */

struct CharacterRecordBin
{
    u32 nameOffset;      /* offset into the injected names blob */
    u32 rosterOffset;    /* offset into the injected rosters blob (u16 species ids, SPECIES_NONE-terminated) */
    u16 spriteAssetId;   /* 0xFFFF = "TBD", Phase 3 not yet wired */
    u8 generation;
    u8 flags;            /* bit0 = hasSignature (signature ace is rosterOffset[0]) */
};

#define FLAG_HAS_SIGNATURE 0x1

/* ---- Injected data — addresses patched in by the insert script once known (Phase 1/2) ---- */
/* TODO(Phase 1/2): these three symbols must be given real ROM addresses by the
 * insert script once characters.bin/rosters.bin/names.bin are placed in free
 * space (candidates: the 337 KiB block @ file offset 0x015FBC90, or the
 * 147 KiB block @ 0x00B2B280 — see docs/FREE_SPACE.md). Until then this file
 * builds as an object with unresolved symbols; it is not link-complete. */
extern const struct CharacterRecordBin gCharacterTable[];
extern const u16 gCharacterRosters[];   /* rosters.bin, viewed as u16 */
extern const u8 gCharacterNames[];      /* names.bin, Gen3-charmap-encoded, 0xFF-terminated per name */
extern const u16 gCharacterCount;       /* NOTE: record count, patched in as a constant by the insert script */

/* ---- Unbound engine glue — NOT YET LOCATED (Phase 1). Every one of these is
 * a placeholder prototype; the insert script must repoint them at Unbound's
 * real functions/flag-var storage once Phase 1 confirms the addresses. See
 * docs/PHASE4_DEPENDENCIES.md. Assumed CFRU/vanilla-shaped signatures based
 * on the battle-string-table finding (docs/ROUTINE_MAP.md) — Unbound's
 * battle-message plumbing hasn't diverged structurally, which is our best
 * evidence these signatures are still a reasonable bet, NOT confirmation. */
extern bool8 FlagGet(u16 flagId);
extern u16 VarGet(u16 varId);
extern u16 GetMonData(void *mon, u8 field, void *unused);   /* real struct Pokemon type unknown here yet */
extern bool8 GetMonDataIsEgg(void *mon);                    /* MON_DATA_IS_EGG field id unknown yet */
extern u16 GetFirstEvolution(u16 species);                  /* walks the evolution table backward to base stage */
extern u16 GetBaseFormSpeciesId(u16 species);                /* strips regional/alt forms to the base form id */
extern int SendMonToPC(void *mon);                          /* PC-deposit routine; return convention TBD (MON_CANT_GIVE equivalent unknown) */
extern void ZeroMonData(void *mon);
extern void CompactPartySlots(void);
extern void CalculatePlayerPartyCount(void);
extern void *gPlayerParty;                                   /* base address of the party array; stride/size TBD */

#define PARTY_SIZE 6
#define MON_DATA_SPECIES 0    /* PLACEHOLDER field id — Unbound's real MON_DATA_* enum not yet confirmed */

/* TODO(Phase 4): flag/var ids for FLAG_CHARACTER_MODE / VAR_CHARACTER_ID must
 * be chosen from a confirmed-unused range. Known-real Unbound ids collected
 * so far (Unbound-Cloud, see the plan's technical-approach section):
 *   FLAG_UNBOUND_SPECIES_RANDOMIZER 0x9FD
 *   VAR_UNBOUND_GAME_DIFFICULTY     0x50DF
 * These two placeholders are NOT verified unused — an empirical scan (diff a
 * fully-played save, or find a fuller community flag/var list) is required
 * before picking real values. */
#define FLAG_CHARACTER_MODE 0     /* PLACEHOLDER */
#define VAR_CHARACTER_ID 0        /* PLACEHOLDER */

/* ---- Core algorithm (this part IS ready — pure logic, no ROM addresses needed) ---- */

static const struct CharacterRecordBin *GetCharacterRecord(u16 index)
{
    return &gCharacterTable[index];
}

bool8 InCharacterMode(void)
{
    u16 charId = VarGet(VAR_CHARACTER_ID);
    return FlagGet(FLAG_CHARACTER_MODE) && charId != 0 && charId <= gCharacterCount;
}

static const struct CharacterRecordBin *GetActiveCharacter(void)
{
    if (!InCharacterMode())
        return (void *)0;
    return GetCharacterRecord(VarGet(VAR_CHARACTER_ID) - 1);
}

/* A species is allowed if the base stage of its evolution family is on the
 * active character's roster (rosters store base stages only, so whole
 * families are always allowed together). Mirrors ROWE's
 * IsSpeciesAllowedForCharacter() exactly, just reading a raw u16 array
 * instead of a compiled struct's `.roster` member. */
bool8 IsSpeciesAllowedForCharacter(u16 species)
{
    const struct CharacterRecordBin *character = GetActiveCharacter();
    u16 base;
    u32 i;

    if (character == (void *)0)
        return TRUE;
    if (species == SPECIES_NONE)
        return FALSE;

    base = GetFirstEvolution(GetBaseFormSpeciesId(species));
    for (i = 0; gCharacterRosters[character->rosterOffset / 2 + i] != SPECIES_NONE; i++)
    {
        if (gCharacterRosters[character->rosterOffset / 2 + i] == base)
            return TRUE;
    }
    return FALSE;
}

bool8 CharacterMode_PartyHasAllowedMon(void)
{
    /* TODO(Phase 1): party array indexing (gPlayerParty[i]) needs the real
     * struct Pokemon size/stride once located — placeholder arithmetic below
     * assumes a flat array of opaque mon structs, real size unknown. */
    u32 i;

    for (i = 0; i < PARTY_SIZE; i++)
    {
        void *mon = (u8 *)gPlayerParty + i * 0 /* TODO: real sizeof(struct Pokemon) */;
        u16 species = GetMonData(mon, MON_DATA_SPECIES, (void *)0);

        if (species != SPECIES_NONE && !GetMonDataIsEgg(mon) && IsSpeciesAllowedForCharacter(species))
            return TRUE;
    }
    return FALSE;
}

/* Move every off-roster party member to the PC. Never leaves the party
 * empty: if all members are off-roster, slot 0 is kept. Mons stay in the
 * party if the boxes are full. Mirrors ROWE's CharacterMode_SweepPartyToPC(). */
void CharacterMode_SweepPartyToPC(void)
{
    u32 i;
    bool8 keptOne = FALSE;

    if (!InCharacterMode())
        return;

    for (i = 0; i < PARTY_SIZE; i++)
    {
        void *mon = (u8 *)gPlayerParty + i * 0 /* TODO: real sizeof(struct Pokemon) */;
        u16 species = GetMonData(mon, MON_DATA_SPECIES, (void *)0);

        if (species == SPECIES_NONE)
            continue;
        if (GetMonDataIsEgg(mon) || IsSpeciesAllowedForCharacter(species))
        {
            keptOne = TRUE;
            continue;
        }
    }

    for (i = 0; i < PARTY_SIZE; i++)
    {
        void *mon = (u8 *)gPlayerParty + i * 0 /* TODO: real sizeof(struct Pokemon) */;
        u16 species = GetMonData(mon, MON_DATA_SPECIES, (void *)0);

        if (species == SPECIES_NONE || GetMonDataIsEgg(mon) || IsSpeciesAllowedForCharacter(species))
            continue;
        if (!keptOne)
        {
            keptOne = TRUE;
            continue;
        }
        if (SendMonToPC(mon) /* TODO: confirm MON_CANT_GIVE-equivalent return value */)
            ZeroMonData(mon);
    }

    CompactPartySlots();
    CalculatePlayerPartyCount();
}
