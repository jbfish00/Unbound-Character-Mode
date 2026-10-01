-- LIVE e2e for the PC second guard (CM_PSSLastMonGuard; src/character_mode.c;
-- verify_artifacts [G]), headless. Ported 2026-09-29 from the RR layer.
--
-- From the free-roam checkpoint (mk_checkpoint_field.lua), queue the PC debug
-- script baked into the SHIPPED build by build_patch.py (the same one
-- pc_exit_test.gdb uses): with Character Mode OFF it gives Pikachu and
-- Hitmontop (the ROM's own givemon), then turns the mode ON for the case's
-- character and jumps into the SHIPPED PC access script. Party [Pikachu,
-- Hitmontop], both alive. Then: DEPOSIT, slot 0 (Pikachu), the deposit entry,
-- confirm.
--
-- ⭐ With an alive Hitmontop beside it VANILLA ALLOWS depositing Pikachu, so
-- only the guard can refuse:
--   swept char (Pikachu ON, Hitmontop OFF) -> refused
--   stays char (both ON)                   -> deposited: another on-roster
--                                             mon remains, so nothing is
--                                             "last" (discrimination)
--   CM off (flag cleared once the PC opens) -> deposited (control)
-- and the no-guard ROM must FAIL this layer on the deposit.
--
-- Env: CM_SCRIPT (debug script address), CM_QUEUE (CharacterMode_QueueScriptCb1),
-- CM_PSS_ADDR, CM_GUARD_ADDR, CM_OFF=1 for the control, EXPECT refused|deposited,
-- CM_CHECKPOINT, CM_SHOT_PREFIX. Needs MGBA_HEADLESS_DEBUGGER=1.
local K = { A = 0, B = 1, START = 3, RIGHT = 4, LEFT = 5, UP = 6, DOWN = 7 }
local STATE = os.getenv("CM_CHECKPOINT") or "/tmp/ub_ss_field.ss"
local function envaddr(n)
    local v = os.getenv(n)
    if not v then error("missing env " .. n) end
    return tonumber(v)
end
local SCRIPT = envaddr("CM_SCRIPT")
local QUEUE  = envaddr("CM_QUEUE") & ~1
local PSS    = envaddr("CM_PSS_ADDR") & ~1
local GUARD  = tonumber(os.getenv("CM_GUARD_ADDR") or "0")
local CM_OFF = os.getenv("CM_OFF") == "1"
local EXPECT = os.getenv("EXPECT") or "refused"
local PREFIX = os.getenv("CM_SHOT_PREFIX") or "/tmp/ub_pcguard"
local PARTY, PARTY_COUNT, MON = 0x02024284, 0x02024029, 100
local CB1, SCRIPT_VAR = 0x030030F0, 0x0203B764
local FLAG_BYTE = 0x0203B373   -- flag 0x18F8 = bit 0 (same byte the roster layer reads)
local STORAGE_PTR, STORAGE_SCAN = 0x03005010, 0x8600

local passes, fails = 0, {}
local function check(what, ok, detail)
    if ok then passes = passes + 1; console:log("HARNESS PASS " .. what)
    else fails[#fails + 1] = what; console:log("HARNESS FAIL " .. what .. " " .. tostring(detail or "")) end
end
local function finish()
    local want = tonumber(os.getenv("CM_EXPECT_CHECKS") or "")
    local ran = passes + #fails
    if ran == 0 then fails[#fails + 1] = "ZERO assertions ran" end
    if want and ran ~= want then fails[#fails + 1] = ("TALLY CHANGED: expected %d, ran %d"):format(want, ran) end
    console:log(("HARNESS RESULT: %s (%d passed, %d failed)"):format(#fails == 0 and "PASS" or "FAIL", passes, #fails))
    os.exit(#fails == 0 and 0 or 1)
end
local function inStorage(pers)
    local base = emu:read32(STORAGE_PTR)
    if pers == 0 or base < 0x02000000 or base >= 0x02040000 then return nil end
    for off = 0, STORAGE_SCAN - 4 do
        if emu:read32(base + off) == pers then return off end
    end
end
local function inParty(pers)
    for i = 0, 5 do if emu:read32(PARTY + i * MON) == pers then return i end end
end
local function shot(n) emu:screenshot(("%s_%s.png"):format(PREFIX, n)) end
local pressing = {}
local function press(k, n, f) emu:addKey(k); pressing[k] = f + n end

local pssAt, guardHits, slot0 = nil, 0, nil
emu:setBreakpoint(function()
    if pssAt == nil then pssAt = -1 end
end, PSS)
if GUARD ~= 0 then
    emu:setBreakpoint(function()
        guardHits = guardHits + 1
        console:log(("HARNESS guard entered slot(r0)=%d lr=0x%08X"):format(
            emu:readRegister("r0"), emu:readRegister("lr")))
    end, GUARD & ~1)
end

-- ⚠️ Unbound reorders the PC menu: Move Pokemon / Move Items / Withdraw /
-- DEPOSIT / See Ya (measured from the screenshot) -- three DOWNs, not one.
local STEPS = {
    {60,  nil,    "1_pc_menu"},
    {10,  K.DOWN, nil},
    {20,  K.DOWN, nil},
    {20,  K.DOWN, "1b_on_deposit"},
    {40,  K.A,    "2_deposit_mode"},
    {160, K.A,    "3_party"},
    {60,  K.A,    "4_store_menu"},
    {90,  K.A,    "5_after_store"},
    {150, nil,    "6_result"},
}
local f, phase, at, stepI, stepAt = 0, "load", 0, 1, nil
callbacks:add("frame", function()
    f = f + 1
    for k, untilF in pairs(pressing) do
        if f >= untilF then emu:clearKey(k); pressing[k] = nil end
    end
    if phase == "load" and f == 5 then
        emu:loadStateFile(STATE); phase, at = "settle", f
    elseif phase == "settle" and f - at == 90 then
        emu:write32(SCRIPT_VAR, SCRIPT)
        emu:write32(CB1, QUEUE | 1)
        console:log(("HARNESS queued debug script 0x%08X"):format(SCRIPT))
        phase, at = "running", f
    elseif phase == "running" then
        if not slot0 and emu:read8(PARTY_COUNT) == 2 then
            slot0 = emu:read32(PARTY)
            console:log(("HARNESS party of 2 f=%d slot0=0x%08X"):format(f, slot0))
        end
        if pssAt == -1 then
            pssAt = f
            console:log(("HARNESS storage system opened f=%d"):format(f))
            if CM_OFF then
                emu:write8(FLAG_BYTE, emu:read8(FLAG_BYTE) & ~1)
                console:log("HARNESS CM flag cleared (control)")
            end
            phase, stepAt = "pc", f
        elseif f - at > 3000 then
            check("the storage system opened (timeout)", false); finish()
        end
    elseif phase == "pc" then
        local s = STEPS[stepI]
        if s == nil then
            local box, slot = inStorage(slot0 or 0), inParty(slot0 or 0)
            console:log(("HARNESS RESULT slot0 box=%s partySlot=%s guardHits=%d"):format(
                tostring(box), tostring(slot), guardHits))
            check("the debug script built a party of 2 and the PC opened", slot0 ~= nil)
            if EXPECT == "refused" then
                check("the deposit reached CM_PSSLastMonGuard", guardHits > 0)
                check("slot 0 (the last on-roster mon) is still in the party", slot ~= nil)
                check("...and NOT in the PC", box == nil)
            else
                check("slot 0 was deposited into the PC", box ~= nil)
                check("...and left the party", slot == nil)
            end
            finish()
        elseif f >= stepAt + s[1] then
            if s[3] then shot(s[3]) end
            if s[2] then press(s[2], 8, f) end
            stepI = stepI + 1; stepAt = f
        end
    end
end)
