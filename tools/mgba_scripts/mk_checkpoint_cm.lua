-- Drive a FRESH save through Unbound's new-game intro, turn Character Mode ON
-- as CM_CHAR through the real opt-in block, continue to free-roam, and write a
-- savestate there (2026-10-03, for the overworld sprite layer).
--
-- mk_checkpoint_field.lua's state machine, with the opt-in answered YES. The
-- number screen can't be typed to an arbitrary id (a 5-wide grid that drops
-- presses), so -- as run_gate_test.sh does -- while the script is parked in the
-- "enter your number" msgbox, VAR_RESULT is preset to CM_CHAR and the script
-- pointer moved to the block's GATE label: from there the SHIPPED bytes run
-- (threshold check, copyvar, "Play as X?", setflag, sweep, "enabled" msgbox,
-- the replayed intro gate). The overworld sprite is never touched here: the
-- player object is created by the intro's own first map load.
--
-- Env: CM_CHAR (1-based id), CM_CHECKPOINT (output), CM_OPTIN_BLOCK,
--      CM_OFF_NUMTEXT, CM_OFF_GATE, CM_OFF_TEXT (tools/tests/ow_sprite_env.py).
local OUT = os.getenv("CM_CHECKPOINT") or "/tmp/ub_ss_cm.ss"
local CHAR = tonumber(os.getenv("CM_CHAR") or "10")
local BLOCK = tonumber(os.getenv("CM_OPTIN_BLOCK"))
local OFF_NUMTEXT = tonumber(os.getenv("CM_OFF_NUMTEXT"))
local OFF_GATE = tonumber(os.getenv("CM_OFF_GATE"))
local OFF_TEXT = tonumber(os.getenv("CM_OFF_TEXT"))
local A, B, START, DOWN = 0, 1, 3, 7
local SCRIPT_PTR, DEPTH, STACK = 0x03000EB8, 0x03000EB0, 0x03000EBC
local VAR_RESULT = 0x020370D0
local FLAG_BYTE, VAR_CHAR = 0x0203B373, 0x0203B76C

local function blockPos()
    local vals = { emu:read32(SCRIPT_PTR) }
    local depth = emu:read8(DEPTH)
    for i = 0, math.min(depth, 20) - 1 do vals[#vals + 1] = emu:read32(STACK + 4 * i) end
    for _, v in ipairs(vals) do
        if v >= BLOCK and v < BLOCK + OFF_TEXT then return v - BLOCK end
    end
    return -1
end
local function freeRoam()
    return emu:read8(0x03000F9C) == 0 and emu:read32(0x030030F4) == 0x080565B5
end

local f, phase, holdKey, holdUntil, nextAt, queue = 0, "title", nil, 0, 700, {}
local jumped = false
local function press(k) queue[#queue + 1] = k end

callbacks:add("frame", function()
    f = f + 1
    if holdKey and f >= holdUntil then emu:clearKey(holdKey); holdKey = nil; nextAt = f + 24 end
    if holdKey or f < nextAt then return end
    if #queue > 0 then
        holdKey = table.remove(queue, 1); emu:addKey(holdKey); holdUntil = f + 12
        return
    end
    if phase == "title" then
        press(START); press(START); phase = "intro"
    elseif phase == "intro" then
        if blockPos() >= 0 then phase = "block" else press(A) end
    elseif phase == "block" then
        local pos = blockPos()
        if pos < 0 then
            if not jumped then console:log("CHECKPOINT FAILED: left the block without the gate jump"); os.exit(1) end
            phase = "story"
        elseif pos == OFF_NUMTEXT and not jumped then
            if not WAITED then WAITED = true; nextAt = f + 90; return end
            emu:write16(VAR_RESULT, CHAR)
            emu:write32(SCRIPT_PTR, BLOCK + OFF_GATE)
            jumped = true
            console:log(("gate jump: VAR_RESULT=%d -> %#x"):format(CHAR, BLOCK + OFF_GATE))
            press(A)
        else press(A) end
    elseif phase == "story" then
        if freeRoam() then nextAt = f + 120; phase = "settle" else press(A) end
    elseif phase == "settle" then
        if freeRoam() then
            local on = (emu:read8(FLAG_BYTE) & 1) == 1
            local id = emu:read16(VAR_CHAR)
            if not on or id ~= CHAR then
                console:log(("CHECKPOINT FAILED: CM flag %s, char %d (want %d)"):format(tostring(on), id, CHAR))
                os.exit(1)
            end
            emu:saveStateFile(OUT)
            emu:screenshot(OUT .. ".png")
            console:log(("CHECKPOINT %s at frame %d (CM on, char %d)"):format(OUT, f, id))
            os.exit(0)
        end
        phase = "story"
    end
    if f > 60 * 60 * 30 then console:log("CHECKPOINT FAILED phase=" .. phase); os.exit(1) end
end)
