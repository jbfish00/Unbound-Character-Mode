-- LIVE e2e for the link-trade sweep (CharacterMode_LinkTradeSweepThenExpand,
-- src/character_mode.c; verify_artifacts [L]; rowe_parity.md §13.53), headless.
-- Added 2026-09-30; same design as Radical Red's layer (byte-identical code).
--
-- A real link trade needs two consoles. What CAN be run for real is the code
-- the hook lives in: CB2_SaveAndEndTrade (0x08053E8C), the one callback
-- FireRed's trade installs after its animation and evolution, wired or
-- wireless. From the free-roam checkpoint, queue the SHIPPED PC debug script
-- (party [Pikachu, Hitmontop], the mode on for the case's character, the real
-- PC open), then install that callback at state 0 as CB2_TryLinkTradeEvolution
-- does and stop at the return of its hooked BL (0x080540F0).
--
-- ⭐ The SWAP is asserted (which personality went where):
--   swept char (Pikachu ON, Hitmontop OFF) -> Hitmontop boxed, Pikachu stays
--   stays char (both ON)                   -> nothing moves (discrimination)
--   CM off (flag cleared once the PC opens) -> nothing moves (vanilla)
-- and the no-hook ROM must FAIL the swept case. The expansion must still
-- happen ("Comm..." in gStringVar4).
--
-- Env: CM_SCRIPT, CM_QUEUE, CM_PSS_ADDR, CM_SHIM_ADDR (0 on the no-hook ROM),
-- CM_OFF=1 for the control, EXPECT box1|none, CM_CHECKPOINT, CM_SHOT_PREFIX.
-- Needs MGBA_HEADLESS_DEBUGGER=1.
local STATE = os.getenv("CM_CHECKPOINT") or "/tmp/ub_ss_field.ss"
local function envaddr(n)
    local v = os.getenv(n)
    if not v then error("missing env " .. n) end
    return tonumber(v)
end
local SCRIPT = envaddr("CM_SCRIPT")
local QUEUE  = envaddr("CM_QUEUE") & ~1
local PSS    = envaddr("CM_PSS_ADDR") & ~1
local SHIM   = tonumber(os.getenv("CM_SHIM_ADDR") or "0")
local CM_OFF = os.getenv("CM_OFF") == "1"
local EXPECT = os.getenv("EXPECT") or "box1"
local PREFIX = os.getenv("CM_SHOT_PREFIX") or "/tmp/ub_linksweep"
local PARTY, PARTY_COUNT, MON = 0x02024284, 0x02024029, 100
local CB1, SCRIPT_VAR = 0x030030F0, 0x0203B764
local CB2, MAIN_STATE = 0x030030F4, 0x030030F0 + 0x438
local CB2_SaveAndEndTrade, EXPAND_RETURN = 0x08053E8D, 0x080540F0
local gStringVar4 = 0x02021D18
local FLAG_BYTE = 0x0203B373   -- flag 0x18F8 = bit 0
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

local pssAt, p0, p1, installed, shimHits, done = nil, nil, nil, nil, 0, false
emu:setBreakpoint(function() if pssAt == nil then pssAt = -1 end end, PSS)
if SHIM ~= 0 then
    emu:setBreakpoint(function() shimHits = shimHits + 1 end, SHIM & ~1)
end
-- At the hooked BL's return: snapshot only. The checks and the exit run on
-- the next frame callback: os.exit from inside a breakpoint callback hung this
-- layer (2026-09-30), and Unbound's other layers only exit from frames.
local snap = nil
emu:setBreakpoint(function()
    if snap or not installed then return end
    snap = {
        count = emu:read8(PARTY_COUNT),
        p0party = inParty(p0), p0pc = inStorage(p0),
        p1party = inParty(p1), p1pc = inStorage(p1),
        s = {emu:read8(gStringVar4), emu:read8(gStringVar4 + 1),
             emu:read8(gStringVar4 + 2), emu:read8(gStringVar4 + 3)},
        hits = shimHits,
    }
end, EXPAND_RETURN)

local function report()
    done = true
    emu:screenshot(PREFIX .. "_after.png")
    local x = snap
    console:log(("HARNESS RESULT shimHits=%d party=%d p0 party=%s pc=%s  p1 party=%s pc=%s  str=%d,%d,%d,%d"):format(
        x.hits, x.count, tostring(x.p0party), tostring(x.p0pc),
        tostring(x.p1party), tostring(x.p1pc), x.s[1], x.s[2], x.s[3], x.s[4]))
    check("state 0 of CB2_SaveAndEndTrade reached the expand BL", true)
    check("gStringVar4 was still expanded (\"Comm\")",
        x.s[1] == 0xBD and x.s[2] == 0xE3 and x.s[3] == 0xE1 and x.s[4] == 0xE1)
    if EXPECT == "box1" then
        check("Pikachu (on the roster) stayed in the party", x.p0party ~= nil)
        check("Hitmontop (off the roster) left the party", x.p1party == nil)
        check("...and is in the PC", x.p1pc ~= nil)
    else
        check("Pikachu stayed in the party", x.p0party ~= nil)
        check("Hitmontop stayed in the party", x.p1party ~= nil)
        check("party count is still 2", x.count == 2)
    end
    finish()
end

local f, phase, at = 0, "load", 0
callbacks:add("frame", function()
    f = f + 1
    if phase == "load" and f == 5 then
        emu:loadStateFile(STATE); phase, at = "settle", f
    elseif phase == "settle" and f - at == 90 then
        emu:write32(SCRIPT_VAR, SCRIPT)
        emu:write32(CB1, QUEUE | 1)
        phase, at = "running", f
    elseif phase == "running" then
        if snap and not done then
            report()
        elseif pssAt == -1 then
            pssAt = f
            if CM_OFF then
                emu:write8(FLAG_BYTE, emu:read8(FLAG_BYTE) & ~1)
                console:log("HARNESS CM flag cleared (control)")
            end
        elseif pssAt and pssAt > 0 and f == pssAt + 60 then
            p0, p1 = emu:read32(PARTY), emu:read32(PARTY + MON)
            console:log(("HARNESS fixture f=%d party=%d p0=0x%08X p1=0x%08X flag=%d"):format(
                f, emu:read8(PARTY_COUNT), p0, p1, emu:read8(FLAG_BYTE) & 1))
            check("fixture: party of 2, the PC open",
                emu:read8(PARTY_COUNT) == 2 and p0 ~= 0 and p1 ~= 0)
            emu:screenshot(PREFIX .. "_before.png")
            emu:write8(MAIN_STATE, 0)
            emu:write32(CB2, CB2_SaveAndEndTrade)
            installed = f
        elseif f - at > 3000 and not done then
            check("reached CB2_SaveAndEndTrade's expand BL (timeout)", false); finish()
        end
    end
end)
