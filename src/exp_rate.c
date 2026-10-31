/* EXP rate (QoL, user 2026-10-29): battle EXP x0.5 / x1 / x1.5 / x2 / x3, every save (Character Mode on or off).
 * ../../game_plans/EXP_RATE_PLAN.md. Ported from the Radical Red port's src/exp_rate.c (same CFRU code).
 *
 * Storage: expanded var 0x51FD (save-persistent; zero setvar/addvar/subvar/copyvar/compare/literal hits in the base
 * ROM, unused by this repo; 0x51FC is VAR_CHARACTER_ID, 0x51FA the opt-in breadcrumb, 0x51F8/9 the test-script
 * pointer): 0 = x1 (every existing save), 1 = x1.5, 2 = x2, 3 = x3, 4 = x0.5.
 *
 * Multiply: CFRU's atk23_getexp computes the award, then `MathMin(0x190640, exp)` (BL at 0x089E2006, byte-for-byte
 * RR's 0x09094A82) and `MathMax(1, ...)`. The hard-level-cap path (award 1) jumps past the MathMin to the MathMax,
 * so CM_ExpRateMin scales only real awards: min(cap, award * N / 2), never 0.
 *
 * Control (user 2026-10-30: "share the Roster slot"): Unbound's START bar has no spare record, so record 6 (the dead
 * Costume Box, Roster since 2026-09-27) is now "Extras" and always shown. With Character Mode on and a roster to
 * show it asks Roster / Exp. Rate (src/roster_display.c); otherwise it opens this chooser straight away. The field
 * is frozen by the START callback; closing the chooser gives it back. */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed short s16;
typedef signed int s32;

#define TEXT __attribute__((section(".text")))

#define VAR_EXP_RATE        0x51FD
#define EXP_CAP             0x190640
#define EOS 0xFF

#define VarGet                  ((u16 (*)(u16))      0x0806E569)
#define VarSet                  ((u8 (*)(u16, u16))  0x0806E585)
#define ScriptContext2_Disable  ((void (*)(void))    0x0806994D)
#define ClearPlayerHeldMovementAndUnfreezeEventObjects ((void (*)(void)) 0x080696C1)
#define AddWindow               ((u8 (*)(const void *)) 0x08003CE5)
#define RemoveWindow            ((void (*)(u8))      0x08003E3D)
#define DrawStdWindowFrame      ((void (*)(u8, u8))  0x080F6F1D)
#define ClearStdWindowAndFrame  ((void (*)(u8, u8))  0x080F6F9D)
#define FillWindowPixelBuffer   ((void (*)(u8, u8))  0x0800445D)
#define CopyWindowToVram        ((void (*)(u8, u8))  0x08003F21)
#define AddTextPrinterParameterized ((u16 (*)(u8, u8, const u8 *, u8, u8, u8, void *)) 0x08002C49)
#define LoadStdWindowFrameGfx   ((void (*)(void))    0x080F6E9D)
#define ListMenuInit            ((u8 (*)(const void *, u16, u16)) 0x08106FF9)
#define ListMenu_ProcessInput   ((s32 (*)(u8))       0x08107079)
#define DestroyListMenuTask     ((void (*)(u8, u16 *, u16 *)) 0x0810713D)
#define ListMenuDefaultCursorMoveFunc ((void *)      0x08107AED)
#define CreateTask              ((u8 (*)(void (*)(u8), u8)) 0x0807741D)
#define DestroyTask             ((void (*)(u8))      0x08077509)
#define FONT_NORMAL 2
#define LIST_NOTHING_CHOSEN (-1)

struct Task { void (*func)(u8); u8 isActive, prev, next, priority; s16 data[16]; };
#define gTasks ((struct Task *) 0x03005090)
struct WindowTemplate { u8 bg, tilemapLeft, tilemapTop, width, height, paletteNum; u16 baseBlock; };
struct ListMenuItem { const u8 *name; s32 id; };
struct ListMenuTemplate {
    const struct ListMenuItem *items;
    void *moveCursorFunc;
    void *itemPrintFunc;
    u16 totalItems;
    u16 maxShowed;
    u8 windowId, header_X, item_X, cursor_X;
    u8 upText_Y:4, cursorPal:4;
    u8 fillValue:4, cursorShadowPal:4;
    u8 lettersSpacing:3, itemVerticalPadding:3, scrollMultiple:2;
    u8 fontId:6, cursorKind:2;
};

/* BL at 0x089E2006 (was MathMin 0x08A13BF0): r0 = the 0x190640 cap, r1 = the award. */
u32 CM_ExpRateMin(u32 cap, u32 exp)
{
#ifndef CM_NO_EXPRATE
    static const u8 sHalves[5] TEXT = { 2, 3, 4, 6, 1 };
    u16 rate = VarGet(VAR_EXP_RATE);

    if (rate >= 1 && rate <= 4 && exp != 0) {
        exp = (exp > EXP_CAP ? EXP_CAP : exp) * sHalves[rate] >> 1;
        if (exp == 0)
            exp = 1;
    }
#endif
    return exp < cap ? exp : cap;
}

/* "Exp. Rate" and the five rows, in the game charmap */
const u8 gCMExpRateText[] TEXT = { 0xBF, 0xEC, 0xE4, 0xAD, 0x00, 0xCC, 0xD5, 0xE8, 0xD9, EOS };
static const u8 sText_x0_5[] TEXT = { 0xEC, 0xA1, 0xAD, 0xA6, EOS };
static const u8 sText_x1[]   TEXT = { 0xEC, 0xA2, EOS };
static const u8 sText_x1_5[] TEXT = { 0xEC, 0xA2, 0xAD, 0xA6, EOS };
static const u8 sText_x2[]   TEXT = { 0xEC, 0xA3, EOS };
static const u8 sText_x3[]   TEXT = { 0xEC, 0xA4, EOS };

#define tRateList  data[0]
#define tRateWin   data[1]
#define tRateHead  data[2]
static const struct WindowTemplate sRateHeadWindow TEXT = { 0, 1, 1, 9, 2, 15, 1 };
static const struct WindowTemplate sRateListWindow TEXT = { 0, 1, 5, 9, 10, 15, 1 + 9 * 2 };
/* rows top to bottom: x0.5 x1 x1.5 x2 x3; the item id is the stored value */
static const struct ListMenuItem sRateItems[5] TEXT = {
    { sText_x0_5, 4 }, { sText_x1, 0 }, { sText_x1_5, 1 }, { sText_x2, 2 }, { sText_x3, 3 },
};
static const u8 sRateRow[5] TEXT = { 1, 2, 3, 4, 0 };   /* stored value -> row */

static void ExpRate_HandleInput(u8 taskId)
{
    s32 r = ListMenu_ProcessInput(gTasks[taskId].tRateList);

    if (r == LIST_NOTHING_CHOSEN)
        return;
    if (r >= 0)
        VarSet(VAR_EXP_RATE, (u16) r);          /* A; B (LIST_CANCEL) keeps the rate */
    DestroyListMenuTask(gTasks[taskId].tRateList, 0, 0);
    ClearStdWindowAndFrame(gTasks[taskId].tRateWin, 1);
    RemoveWindow(gTasks[taskId].tRateWin);
    ClearStdWindowAndFrame(gTasks[taskId].tRateHead, 1);
    RemoveWindow(gTasks[taskId].tRateHead);
    DestroyTask(taskId);
    ClearPlayerHeldMovementAndUnfreezeEventObjects();
    ScriptContext2_Disable();
}

/* Opens the chooser over a FROZEN field (the START callback froze it), cursor on the current rate. */
void CM_ExpRateOpen(void)
{
    struct ListMenuTemplate t;
    u16 rate = VarGet(VAR_EXP_RATE);
    u8 taskId, win, head;

    LoadStdWindowFrameGfx();
    head = AddWindow(&sRateHeadWindow);
    DrawStdWindowFrame(head, 0);
    FillWindowPixelBuffer(head, 0x11);
    AddTextPrinterParameterized(head, FONT_NORMAL, gCMExpRateText, 0, 1, 0, 0);
    CopyWindowToVram(head, 3);
    win = AddWindow(&sRateListWindow);
    DrawStdWindowFrame(win, 0);
    taskId = CreateTask(ExpRate_HandleInput, 3);
    gTasks[taskId].tRateWin = win;
    gTasks[taskId].tRateHead = head;

    t.items = sRateItems;
    t.moveCursorFunc = ListMenuDefaultCursorMoveFunc;
    t.itemPrintFunc = 0;
    t.totalItems = 5;
    t.maxShowed = 5;
    t.windowId = win;
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
    gTasks[taskId].tRateList = ListMenuInit(&t, 0, sRateRow[rate <= 4 ? rate : 0]);
    CopyWindowToVram(win, 3);
}

/* Build fingerprint (as the other units'): the values this unit compiled with, read back out of the BUILT ROM by
 * verify_artifacts [E]. GCC builds 0x51FD and 0x190640 with shifts, so they are not in any literal pool to pin. */
__attribute__((used, section(".rodata.cm_fingerprint")))
const u32 CM_ExpRateFingerprint[4] = {
    0x52505845u,                        /* 'EXPR' */
    VAR_EXP_RATE,
    EXP_CAP,
#ifdef CM_NO_EXPRATE
    0,
#else
    1,
#endif
};
