/*
 * unbound.ld — Pokemon Unbound v2.1.1.1 symbol addresses for the injected
 * Character Mode code. Every address here was reverse-engineered and
 * double-confirmed in Phase 1 (docs/ROUTINE_MAP.md v8: decompiled handler
 * shape + CFRU BPRE.ld name match). Thumb functions carry the |1 bit.
 *
 * The injected code/data base addresses (ORIGIN below) are chosen by
 * tools/build_patch.py and passed with --defsym CM_INJECT_BASE=...;
 * this file only pins the ENGINE symbols.
 */

/* ---- vanilla FRLG engine core (live in this ROM, CFRU hooks route
 *      expanded flag/var ids transparently) ---- */
FlagGet   = 0x0806E6D0 | 1;
FlagSet   = 0x0806E680 | 1;
FlagClear = 0x0806E6A8 | 1;
VarGet    = 0x0806E568 | 1;
VarSet    = 0x0806E584 | 1;

GetMonData  = 0x0803FBE8 | 1;
SetMonData  = 0x0804037C | 1;
ZeroMonData = 0x0803D994 | 1;
CopyMon     = 0x08040B08 | 1;
CalculatePlayerPartyCount = 0x08040C3C | 1;
CompactPartySlots         = 0x080937DC | 1;

/* ---- CFRU-compiled functions (Unbound's high-ROM blob) ---- */
SendMonToPC          = 0x08A04CB0 | 1;  /* CFRU's replacement, not vanilla 0x08040B90 */
TryFormRevert        = 0x089E5E00 | 1;
TryRevertMega        = 0x089F77B0 | 1;
TryRevertGigantamax  = 0x089D9D34 | 1;
TryRevertOriginFormes = 0x089E5D08 | 1;

/* ---- engine data ---- */
gPlayerParty      = 0x02024284;
gPlayerPartyCount = 0x02024029;
gBankTarget       = 0x02023D6C;
gBattleMons       = 0x02023BE4;
gBattleTypeFlags  = 0x02022B4C;
gMainInBattleByte = 0x030030F0 + 0x439; /* gMain.inBattle byte */
gSaveBlock2Ptr    = 0x0300500C;
