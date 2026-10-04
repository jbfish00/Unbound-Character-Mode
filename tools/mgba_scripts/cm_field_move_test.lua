-- LIVE e2e for field moves (src/character_mode.c CharacterMode_FieldMoveCanLearn;
-- verify_artifacts [H]), headless. 2026-10-04.
--
-- From the free-roam checkpoint (mk_checkpoint_field.lua), queue a debug script
-- baked into the SHIPPED build by build_patch.py: it sets the mode (ON as
-- Brandon, or OFF) and callnatives CharacterMode_FieldMoveProbe. The probe
-- makes the party one Magikarp that knows only Splash (it learns no HM), gives
-- all eight badges, then calls the REAL PartyHasMonWithFieldMovePotential for
-- each field move without and with the HM in the bag, and builds the REAL
-- party menu for Fly without and with HM02.
--   on      -> no HM: nobody (6); HM in bag: slot 0; Fly listed only with HM02
--   off     -> 6 / 6, Fly never listed (vanilla: Magikarp learns nothing)
--   nohook ROM, on -> the layer must FAIL (the three bls restored)
--
-- Env: CM_SCRIPT, CM_QUEUE, EXPECT on|off, CM_EXPECT_CHECKS, CM_CHECKPOINT.
-- Needs MGBA_HEADLESS_DEBUGGER=1.
local STATE = os.getenv("CM_CHECKPOINT") or "/tmp/ub_ss_field.ss"
local function envaddr(n)
    local v = os.getenv(n)
    if not v then error("missing env " .. n) end
    return tonumber(v)
end
local SCRIPT = envaddr("CM_SCRIPT")
local QUEUE  = envaddr("CM_QUEUE") & ~1
local EXPECT = os.getenv("EXPECT") or "on"
local CB1, SCRIPT_VAR = 0x030030F0, 0x0203B764
local PROBE, MAGIC = 0x02030300, 0xF1E1D000
local NAMES = { "Cut", "Surf", "Strength", "Dive", "Rock Smash", "Waterfall",
                "Rock Climb", "Flash" }

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
        emu:write32(SCRIPT_VAR, SCRIPT)
        emu:write32(CB1, QUEUE | 1)
        console:log(("HARNESS queued debug script 0x%08X"):format(SCRIPT))
        phase, at = "running", f
    elseif phase == "running" then
        local m = emu:read32(PROBE)
        if (m & 0xFFFFFF00) == MAGIC then
            local n = m & 0xFF
            check("the probe ran and covered all eight field moves", n == #NAMES, n)
            for i = 1, #NAMES do
                local r = emu:read32(PROBE + 4 * i)
                local without, with = r & 0xFF, (r >> 8) & 0xFF
                console:log(("HARNESS %-10s without HM -> %d, with HM -> %d"):format(NAMES[i], without, with))
                check(NAMES[i] .. ": the HM is still required (none without it)", without == 6, without)
                if EXPECT == "on" then
                    check(NAMES[i] .. ": the Magikarp can use it with the HM in the bag", with == 0, with)
                else
                    check(NAMES[i] .. ": vanilla, the Magikarp can't use it", with == 6, with)
                end
            end
            local fly = emu:read32(PROBE + 40)
            console:log(("HARNESS Fly in the party menu: %d"):format(fly))
            check("Fly isn't listed without HM02", (fly & 2) == 0, fly)
            if EXPECT == "on" then
                check("Fly is listed for the Magikarp with HM02", (fly & 1) == 1, fly)
            else
                check("vanilla: Fly isn't listed for the Magikarp", (fly & 1) == 0, fly)
            end
            finish()
        elseif f - at > 600 then
            check("the probe ran (timeout)", false); finish()
        end
    end
end)
