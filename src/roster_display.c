/* Character Mode in-game roster display for Pokemon Unbound (CFRU, FireRed).
 *
 * ../../game_plans/roster_display.md is the runbook: a read-only list of the
 * ACTIVE character's roster, one row per family ROOT, name + bordered icon.
 *
 * PORTED 2026-09-27 from the Radical Red port's src/roster_display.c (same
 * engine: ROWE's design -- a native task owning a header window, a ListMenu
 * window and ONE icon sprite in its own framed box). Every vanilla FireRed
 * entry it calls was compared against RR: 24 are byte-identical and the other
 * six are CFRU hook trampolines or the same code with different literals, so
 * calling the entry runs Unbound's own version.
 *
 * ENTRY: a START menu row (user decision 2026-09-27: "a menu option ... I would
 * like the START menu ... cheapest and least intrusive"). Unbound's START menu
 * is its own graphical icon bar built from a 12-record table (0x08A6D160).
 * Record 6, "Costume Box", is DEAD in this version -- the builder's case 6
 * never appends it -- so the Roster row takes its slot instead of growing any
 * table, loop or stack array:
 *   - record 6's callback/text/icon are patched in place
 *     -> CM_StartMenuRosterCallback, "Roster", the Pokemon List icon;
 *   - the builder's case-6 jump-table byte goes from "skip" to "append";
 *   - the order loops' VarGet literal -> CM_StartMenuVarGet, which returns
 *     the real VarGet for every var except record 6's (0x5040), and 0xFF
 *     (= not in the menu) for that one unless Character Mode is on. With CM
 *     off the START menu is exactly what it was.
 * The callback closes the menu with Unbound's own Exit routine, re-freezes the
 * field, and opens the screen; closing the screen unfreezes it again -- the
 * mirror of Exit.
 *
 * ⚠️ No mutable statics: all per-open state lives in the input task's data[].
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed short s16;
typedef signed int s32;
typedef volatile unsigned short vu16;

#define TEXT __attribute__((section(".text")))

#ifndef NUM_CHARACTERS
#error "compile with -DNUM_CHARACTERS=<from characters_manifest.json>"
#endif
/* The roots blob is placed by build_patch.py (--defsym gRosterRoots): this
 * build compiles before it lays out the block, so the address is a symbol. */
extern const u16 gRosterRoots[];
#ifndef ROSTER_ROOTS_OFF
#error "compile with -DROSTER_ROOTS_OFF=<roots_offset_bytes from the manifest>"
#endif
#define VAR_CHARACTER_ID    0x51FC
#define FLAG_CHARACTER_MODE 0x18F8
/* record 6's position var: the one var whose order the wrapper gates */
#define ROSTER_ORDER_VAR    0x5040
/* build_patch.py places the header names (already in ROM for the opt-in list) */
extern const u8 *const gCharacterNamePtrs[];
#define EOS 0xFF

/* --- CFRU redirect slots (include/new/rom_locs.h) --- */
#define gSpeciesNames ((const u8 *) *(const u32 *) 0x08000144)   /* 11 B per species */
#define SPECIES_NAME_STRIDE 11

/* --- vanilla FireRed, BPRE.ld --- */
#define GetVarPointer        ((u16 *(*)(u16)) 0x0806E455)
#define VarGet               ((u16 (*)(u16)) 0x0806E569)
#define FlagGet              ((u8 (*)(u16)) 0x0806E6D1)
#define ScriptContext2_Enable  ((void (*)(void)) 0x08069941)
#define ScriptContext2_Disable ((void (*)(void)) 0x0806994D)
#define FreezeEventObjects   ((void (*)(void)) 0x08068975)
#define ClearPlayerHeldMovementAndUnfreezeEventObjects ((void (*)(void)) 0x080696C1)
/* Unbound's own START-menu close (what its Exit callback 0x08A0BD85 runs):
 * PlaySE, item count 0, tear down the icon bar, unfreeze, ScriptContext2
 * off, ShowBg(0), flash fix-up. */
#define UnboundStartMenuClose ((void (*)(void)) 0x08A0BD35)
/* Stops the active palette fade: active = 0, level 0 (BPRE.ld, byte-identical
 * to RR's). BeginNormalPaletteFade cannot do this -- it refuses to start while
 * a fade is active, which the first version found out the hard way. */
#define ResetPaletteFadeControl ((void (*)(void)) 0x08070A85)
#define AddWindow            ((u8 (*)(const void *)) 0x08003CE5)
#define RemoveWindow         ((void (*)(u8)) 0x08003E3D)
#define DrawStdWindowFrame   ((void (*)(u8, u8)) 0x080F6F1D)
#define ClearStdWindowAndFrame ((void (*)(u8, u8)) 0x080F6F9D)
#define FillWindowPixelBuffer ((void (*)(u8, u8)) 0x0800445D)
#define CopyWindowToVram     ((void (*)(u8, u8)) 0x08003F21)
#define AddTextPrinterParameterized ((u16 (*)(u8, u8, const u8 *, u8, u8, u8, void *)) 0x08002C49)
#define LoadStdWindowFrameGfx ((void (*)(void)) 0x080F6E9D)
#define ListMenuInit         ((u8 (*)(const void *, u16, u16)) 0x08106FF9)
#define ListMenu_ProcessInput ((s32 (*)(u8)) 0x08107079)
#define DestroyListMenuTask  ((void (*)(u8, u16 *, u16 *)) 0x0810713D)
#define CreateTask           ((u8 (*)(void (*)(u8), u8)) 0x0807741D)
#define DestroyTask          ((void (*)(u8)) 0x08077509)
#define FindTaskIdByFunc     ((u8 (*)(void (*)(u8))) 0x08077689)
#define Malloc               ((void *(*)(u32)) 0x08002B9D)
#define Free                 ((void (*)(void *)) 0x08002BC5)
#define PlaySE               ((void (*)(u16)) 0x080722CD)
#define CreateMonIcon        ((u8 (*)(u16, void *, s16, s16, u8, u32, u32)) 0x08096E19)
#define DestroyMonIcon       ((void (*)(void *)) 0x08097071)
#define LoadMonIconPalette   ((void (*)(u16)) 0x080970E1)
#define FreeMonIconPalette   ((void (*)(u16)) 0x08097169)
#define UpdateMonIconFrame   ((void *) 0x08097229)   /* FireRed's SpriteCB_MonIcon body */

#define gTasks   ((struct Task *) 0x03005090)
#define gMainNewKeys (*(vu16 *) (0x030030F0 + 0x2E))
#define gSprites ((u8 *) 0x0202063C)
#define SPRITE_STRIDE 0x44
#define MAX_SPRITES 64
#define TASK_NONE 0xFF
#define NO_WINDOW 0xFF
#define A_BUTTON 0x0001
#define B_BUTTON 0x0002
#define SE_SELECT 5
#define LIST_NOTHING_CHOSEN (-1)
#define FONT_NORMAL 2

struct Task {
    void (*func)(u8);
    u8 isActive, prev, next, priority;
    s16 data[16];
};

struct WindowTemplate {
    u8 bg, tilemapLeft, tilemapTop, width, height, paletteNum;
    u16 baseBlock;
};

struct ListMenuItem {
    const u8 *name;
    s32 id;
};

struct ListMenuTemplate {
    const struct ListMenuItem *items;
    void (*moveCursorFunc)(s32, u8, void *);
    void (*itemPrintFunc)(u8, s32, u8);
    u16 totalItems;
    u16 maxShowed;
    u8 windowId, header_X, item_X, cursor_X;
    u8 upText_Y:4, cursorPal:4;
    u8 fillValue:4, cursorShadowPal:4;
    u8 lettersSpacing:3, itemVerticalPadding:3, scrollMultiple:2;
    u8 fontId:6, cursorKind:2;
};

/* Geometry: ROWE's, with a wider header (RR names reach 12 characters). */
#define MENU_WIDTH    13
#define MENU_ROWS      6
#define HEADER_WIDTH  18
#define ICON_WIN_LEFT 19
#define ICON_WIN_TOP   8
#define ICON_WIN_SIZE  5
/* 80, not the box's centre 84: icon art is bottom-weighted in its 32x32 frame
 * (ROWE measured it off the rendered screen). */
#define ICON_X 172
#define ICON_Y  80

#define tListTaskId  data[0]
#define tWindowId    data[1]
#define tHeaderId    data[2]
#define tIconSprite  data[3]
#define tItemsHi     data[4]
#define tItemsLo     data[5]
#define tIconWinId   data[6]
#define tIconSpecies data[7]

static const struct WindowTemplate sMenuWindow TEXT = {
    0, 1, 5, MENU_WIDTH, 2 * MENU_ROWS, 15, 1 };
static const struct WindowTemplate sHeaderWindow TEXT = {
    0, 1, 1, HEADER_WIDTH, 2, 15, 1 + MENU_WIDTH * 2 * MENU_ROWS };
static const struct WindowTemplate sIconWindow TEXT = {
    0, ICON_WIN_LEFT, ICON_WIN_TOP, ICON_WIN_SIZE, ICON_WIN_SIZE, 15,
    1 + MENU_WIDTH * 2 * MENU_ROWS + HEADER_WIDTH * 2 };

/* "'s roster" in the game charmap: ' s space r o s t e r */
static const u8 sText_Suffix[] TEXT = { 0xB4, 0xE7, 0x00, 0xE6, 0xE3, 0xE7, 0xE8, 0xD9, 0xE6, EOS };

/* Record 6's START-menu label, "Roster" in the game charmap. */
const u8 gCMRosterMenuText[] TEXT = { 0xCC, 0xE3, 0xE7, 0xE8, 0xD9, 0xE6, EOS };

static void RosterMenu_HandleInput(u8 taskId);

static struct ListMenuItem *GetItems(u8 taskId)
{
    return (struct ListMenuItem *) (((u32) (u16) gTasks[taskId].tItemsHi << 16)
                                    | (u16) gTasks[taskId].tItemsLo);
}

static void DestroyIcon(u8 taskId)
{
    if (gTasks[taskId].tIconSprite != MAX_SPRITES) {
        DestroyMonIcon(gSprites + gTasks[taskId].tIconSprite * SPRITE_STRIDE);
        FreeMonIconPalette((u16) gTasks[taskId].tIconSpecies);
        gTasks[taskId].tIconSprite = MAX_SPRITES;
    }
}

/* ⚠️ THE FIRST PARAMETER IS THE ITEM'S ID, NOT ITS INDEX (ROWE's trap: indexing
 * items[] with it drew Scyther for Pikachu). The id IS the species here. */
static void RosterMenu_MoveCursor(s32 itemId, u8 onInit, void *list)
{
    u8 taskId = FindTaskIdByFunc(RosterMenu_HandleInput);
    u16 species = (u16) itemId;
    u8 id;
    (void) list;

    if (taskId == TASK_NONE || itemId <= 0)
        return;
    if (!onInit)
        PlaySE(SE_SELECT);
    DestroyIcon(taskId);
    /* One palette for the one icon: the field holds most sprite palette slots. */
    LoadMonIconPalette(species);
    id = CreateMonIcon(species, UpdateMonIconFrame, ICON_X, ICON_Y, 0, 0, 0);
    if (id >= MAX_SPRITES) {
        FreeMonIconPalette(species);
        return;
    }
    gSprites[id * SPRITE_STRIDE + 5] &= ~0x0C;   /* oam.priority = 0: above the window */
    gTasks[taskId].tIconSprite = id;
    gTasks[taskId].tIconSpecies = species;
}

#define HEADER_NAME_MAX 16

static void DrawHeader(u8 windowId, u16 charId)
{
    const u8 *name = gCharacterNamePtrs[charId - 1];
    u8 buf[HEADER_NAME_MAX + sizeof(sText_Suffix)];
    u32 n = 0, k;

    while (n < HEADER_NAME_MAX && name[n] != EOS) {
        buf[n] = name[n];
        n++;
    }
    for (k = 0; k < sizeof(sText_Suffix); k++)
        buf[n + k] = sText_Suffix[k];
    FillWindowPixelBuffer(windowId, 0x11);
    AddTextPrinterParameterized(windowId, FONT_NORMAL, buf, 0, 1, 0, 0);
    CopyWindowToVram(windowId, 3);
}

static void ReleaseField(void)
{
    ClearPlayerHeldMovementAndUnfreezeEventObjects();
    ScriptContext2_Disable();
}

/* Opens the screen over a FROZEN field. Anything that stops it opening gives
 * the field straight back, so the player can never be left locked. */
static void CM_RosterOpen(void)
{
    u16 charId = *GetVarPointer(VAR_CHARACTER_ID);
    const u16 *entry, *roots;
    struct ListMenuItem *items;
    struct ListMenuTemplate t;
    u8 windowId, headerId, iconWinId, taskId;
    u32 i, count;

    if (charId < 1 || charId > NUM_CHARACTERS) {
        ReleaseField();
        return;
    }
    entry = gRosterRoots + (u32) (charId - 1) * 2;
    roots = (const u16 *) ((const u8 *) gRosterRoots + ROSTER_ROOTS_OFF) + entry[0];
    count = entry[1];
    items = count ? Malloc(count * sizeof(struct ListMenuItem)) : 0;
    if (items == 0) {                 /* no rows, or no memory: nothing to draw */
        ReleaseField();
        return;
    }
    for (i = 0; i < count; i++) {
        /* Point straight into the name table: fixed width, 0xFF-terminated. */
        items[i].name = gSpeciesNames + (u32) roots[i] * SPECIES_NAME_STRIDE;
        items[i].id = roots[i];
    }

    LoadStdWindowFrameGfx();
    headerId = AddWindow(&sHeaderWindow);
    DrawStdWindowFrame(headerId, 0);
    DrawHeader(headerId, charId);
    windowId = AddWindow(&sMenuWindow);
    DrawStdWindowFrame(windowId, 0);
    iconWinId = AddWindow(&sIconWindow);
    DrawStdWindowFrame(iconWinId, 0);
    FillWindowPixelBuffer(iconWinId, 0x11);
    CopyWindowToVram(iconWinId, 3);

    /* The task exists BEFORE ListMenuInit: its first moveCursor call (onInit)
     * needs somewhere to keep the sprite id. */
    taskId = CreateTask(RosterMenu_HandleInput, 3);
    gTasks[taskId].tListTaskId = TASK_NONE;
    gTasks[taskId].tWindowId = windowId;
    gTasks[taskId].tHeaderId = headerId;
    gTasks[taskId].tIconSprite = MAX_SPRITES;
    gTasks[taskId].tIconWinId = iconWinId;
    gTasks[taskId].tItemsHi = (s16) ((u32) items >> 16);
    gTasks[taskId].tItemsLo = (s16) ((u32) items & 0xFFFF);

    t.items = items;
    t.moveCursorFunc = RosterMenu_MoveCursor;
    t.itemPrintFunc = 0;
    t.totalItems = count;
    t.maxShowed = count < MENU_ROWS ? count : MENU_ROWS;
    t.windowId = windowId;
    t.header_X = 0;
    t.item_X = 8;
    t.cursor_X = 0;
    t.upText_Y = 1;
    t.cursorPal = 2;
    t.fillValue = 1;
    t.cursorShadowPal = 3;
    t.lettersSpacing = 1;
    t.itemVerticalPadding = 0;
    t.scrollMultiple = 0;
    t.fontId = FONT_NORMAL;
    t.cursorKind = 0;
    gTasks[taskId].tListTaskId = ListMenuInit(&t, 0, 0);
    CopyWindowToVram(windowId, 3);
}

static void RosterMenu_Destroy(u8 taskId)
{
    struct ListMenuItem *items = GetItems(taskId);

    DestroyListMenuTask(gTasks[taskId].tListTaskId, 0, 0);
    DestroyIcon(taskId);
    Free(items);
    ClearStdWindowAndFrame(gTasks[taskId].tWindowId, 1);
    RemoveWindow(gTasks[taskId].tWindowId);
    ClearStdWindowAndFrame(gTasks[taskId].tHeaderId, 1);
    RemoveWindow(gTasks[taskId].tHeaderId);
    ClearStdWindowAndFrame(gTasks[taskId].tIconWinId, 1);
    RemoveWindow(gTasks[taskId].tIconWinId);
    DestroyTask(taskId);
    ReleaseField();
}

/* Read-only: A and B both close it (ROWE's rule). */
static void RosterMenu_HandleInput(u8 taskId)
{
    if (ListMenu_ProcessInput(gTasks[taskId].tListTaskId) != LIST_NOTHING_CHOSEN
        || (gMainNewKeys & B_BUTTON))
        RosterMenu_Destroy(taskId);
}

/* Record 6's START-menu callback. Close the menu exactly as Exit does, then
 * take the field back and open the screen. TRUE = the menu is finished. */
u8 CM_StartMenuRosterCallback(void)
{
    /* ⚠️ The START handler starts a fade-to-black before calling any row it
     * does not know stays on the field (FireRed's
     * StartMenu_FadeScreenIfLeavingOverworld: only Save/Exit/Retire are
     * exempt). Measured: this callback runs in the SAME frame, fade active at
     * level 0, and without this the field stayed black forever -- the Pokedex
     * and Bag callbacks wait for that fade and change screen, this one is an
     * overlay. The fade is still at level 0 here (colours untouched), so
     * stopping it is enough. */
    ResetPaletteFadeControl();
    UnboundStartMenuClose();
    ScriptContext2_Enable();
    FreezeEventObjects();
    CM_RosterOpen();
    return 1;
}

/* Replaces VarGet in the START menu's two order loops (literal 0x08A0C1F4).
 * Every var but record 6's goes straight to VarGet. Record 6 is in the menu
 * only while Character Mode is on AND the active character has rows; 0xFF is
 * the loops' "not in the menu" value. */
u16 CM_StartMenuVarGet(u16 var)
{
    u16 id;
    if (var != ROSTER_ORDER_VAR)
        return VarGet(var);
    if (!FlagGet(FLAG_CHARACTER_MODE))
        return 0xFF;
    id = *GetVarPointer(VAR_CHARACTER_ID);
    if (id < 1 || id > NUM_CHARACTERS
        || gRosterRoots[(u32) (id - 1) * 2 + 1] == 0)
        return 0xFF;
    return VarGet(var);
}
