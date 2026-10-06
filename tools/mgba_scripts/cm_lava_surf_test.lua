-- LIVE e2e for Lava Surf (build_patch.py LAVA_*; src/character_mode.c
-- CharacterMode_LavaSurfSlot), headless. 2026-10-05.
--
-- From the free-roam checkpoint, queue a debug script baked into the SHIPPED
-- build: it sets the mode, has CharacterMode_LavaSurfSetup build a one-mon
-- party (Magikarp, or a Charmander for the Fire cases), all eight badges and
-- HM03 present or absent, then jumps into the REAL magma script (0x089A4A52).
-- The script copies the chosen party slot into 0x8004 only on its "surf on
-- it?" path; on the "magma glistens" dead end 0x8004 stays 6.
--
-- Env: CM_SCRIPT, CM_QUEUE, CM_LAVA_MODE (the fixture the setup must report),
-- WANT_SLOT (0 = can surf the lava, 6 = can't), CM_EXPECT_CHECKS, CM_CHECKPOINT,
-- CM_SHOT (optional: a screenshot path taken when the checks run).
local STATE = os.getenv("CM_CHECKPOINT") or "/tmp/ub_ss_field.ss"
local function envnum(n)
    local v = os.getenv(n)
    if not v then error("missing env " .. n) end
    return tonumber(v)
end
local SCRIPT = envnum("CM_SCRIPT")
local QUEUE  = envnum("CM_QUEUE") & ~1
local MODE   = envnum("CM_LAVA_MODE")
local WANT   = envnum("WANT_SLOT")
local CB1, SCRIPT_VAR = 0x030030F0, 0x0203B764
local PROBE, MAGIC, VAR_8004 = 0x02030340, 0x1A7A0000, 0x020370C0

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

local f, phase, at = 0, "load", 0
callbacks:add("frame", function()
    f = f + 1
    if phase == "load" and f == 5 then
        emu:loadStateFile(STATE); phase, at = "settle", f
    elseif phase == "settle" and f - at == 90 then
        emu:write32(PROBE, 0)
        emu:write16(VAR_8004, 0xBEEF)
        emu:write32(SCRIPT_VAR, SCRIPT)
        emu:write32(CB1, QUEUE | 1)
        console:log(("HARNESS queued lava script 0x%08X"):format(SCRIPT))
        phase, at = "running", f
    elseif phase == "running" then
        local m = emu:read32(PROBE)
        if (m & 0xFFFF0000) == MAGIC then
            phase, at = "script", f
        elseif f - at > 600 then
            check("the lava setup ran (timeout)", false); finish()
        end
    elseif phase == "script" and f - at == 120 then
        local m = emu:read32(PROBE) & 0xFFFF
        check("the setup built the fixture asked for", m == MODE, m)
        local shot = os.getenv("CM_SHOT")
        if shot then emu:screenshot(shot) end
        local slot = emu:read16(VAR_8004)
        console:log(("HARNESS magma script chose slot %d (want %d)"):format(slot, WANT))
        if WANT == 6 then
            check("the magma script dead-ends (nobody can surf the lava)", slot == 6, slot)
        else
            check("the magma script offers to surf with party slot " .. WANT, slot == WANT, slot)
        end
        finish()
    end
end)
