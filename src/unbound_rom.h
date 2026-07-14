/*
 * unbound_rom.h — extern surface of Pokemon Unbound v2.1.1.1 as reverse-
 * engineered in Phase 1 (docs/ROUTINE_MAP.md v8). Every symbol here is
 * given its real ROM/RAM address by src/unbound.ld at link time; nothing
 * is guessed. All function addresses were confirmed two independent ways
 * (decompiled handler shape + CFRU BPRE.ld name match) — see the routine
 * map before changing any of them.
 */
#ifndef UNBOUND_ROM_H
#define UNBOUND_ROM_H

#include <stdint.h>

typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint8_t bool8;

#define TRUE 1
#define FALSE 0

#define SPECIES_NONE 0
#define PARTY_SIZE 6
#define POKEMON_SIZE 100 /* sizeof(struct Pokemon), vanilla layout */

/* struct Pokemon is opaque to us — the engine functions do all field access */
struct Pokemon
{
    u8 raw[POKEMON_SIZE];
};

/* GetMonData/SetMonData field ids (vanilla pret FRLG values; CFRU only
 * appends new ids past the vanilla enum, it does not renumber) */
#define MON_DATA_OT_ID 1
#define MON_DATA_OT_NAME 7
#define MON_DATA_SPECIES 11
#define MON_DATA_IS_EGG 45
#define MON_DATA_OT_GENDER 49

/* GiveMonToPlayer / SendMonToPC return convention (vanilla FRLG) */
#define MON_GIVEN_TO_PARTY 0
#define MON_GIVEN_TO_PC 1
#define MON_CANT_GIVE 2

#define BATTLE_TYPE_INGAME_PARTNER 0x00400000
#define GMAIN_INBATTLE_BIT 0x2 /* bit 1 of gMain byte +0x439 */

/* ---- engine functions (addresses in unbound.ld) ---- */
u8 FlagGet(u16 flagId);
u8 FlagSet(u16 flagId);
u8 FlagClear(u16 flagId);
u16 VarGet(u16 varId);
bool8 VarSet(u16 varId, u16 value);
u32 GetMonData(struct Pokemon *mon, u32 field, void *data);
void SetMonData(struct Pokemon *mon, u32 field, const void *data);
void ZeroMonData(struct Pokemon *mon);
void CopyMon(void *dest, const void *src, u32 size);
u8 CalculatePlayerPartyCount(void);
void CompactPartySlots(void);
u8 SendMonToPC(struct Pokemon *mon); /* CFRU's compiled version (0x08A04CB0) */

/* CFRU form-handling calls GiveMonToPlayer performs before storing a mon —
 * our replacement must keep making them (docs/ROUTINE_MAP.md v8) */
void TryFormRevert(struct Pokemon *mon);
void TryRevertMega(struct Pokemon *mon);
void TryRevertGigantamax(struct Pokemon *mon);
void TryRevertOriginFormes(struct Pokemon *mon, bool8 keepChanges);

/* ---- engine data (addresses in unbound.ld) ---- */
extern struct Pokemon gPlayerParty[PARTY_SIZE];
extern u8 gPlayerPartyCount;
extern u8 gBankTarget;                /* CFRU name for gBattlerTarget */
extern u8 gBattleMons[];              /* stride 0x58, species u16 at +0 */
extern u32 gBattleTypeFlags;
extern u8 gMainInBattleByte;          /* gMain + 0x439 */
extern u8 *gSaveBlock2Ptr;            /* 0x0300500C holds the live pointer */

#define BATTLEMON_SPECIES(bank) (*(u16 *)(gBattleMons + (bank) * 0x58))

#endif /* UNBOUND_ROM_H */
