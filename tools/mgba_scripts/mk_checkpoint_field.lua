-- Headless (mgba-headless + Lua) port of tools/test_harness/intro_drive.py:
-- drive a FRESH save through Unbound's new-game intro, answer No at the
-- Character Mode opt-in, continue to free-roam, and write a savestate there.
-- 2026-09-27, for the roster display's live test (the first Lua/screenshot
-- layer in this repo -- the GDB harness stays as it is).
--
-- Same state machine as intro_drive.py, off the same RAM:
--   script pointer   sScriptContext1.scriptPtr 0x03000EB8, call stack
--                    depth 0x03000EB0, stack 0x03000EBC..
--   opt-in block     the call target of the splice at 0x09E6FF2D (read from
--                    ROM at 0x09E6FF2E); "pos 13" is its yes/no
--   free-roam        sScriptContext2Enabled 0x03000F9C == 0 and
--                    gMain.callback2 0x030030F4 == CB2_Overworld 0x080565B5
-- Presses are verified through heldKeysRaw 0x03003118 (mGBA drops short taps).
--
-- Usage: mgba-headless --script tools/mgba_scripts/mk_checkpoint_field.lua build/unbound-cm.gba
-- Env:   CM_CHECKPOINT (default /tmp/ub_ss_field.ss)
local OUT = os.getenv("CM_CHECKPOINT") or "/tmp/ub_ss_field.ss"
local A, B, START, DOWN = 0, 1, 3, 7
-- ⚠️ The operand is UNALIGNED (script bytes are not word-aligned) and
-- emu:read32 on an unaligned address does not return these four bytes -- the
-- first version read a wrong BLOCK, never saw the opt-in, A-mashed "Yes" and
-- wedged in the number-entry loop. Assemble it from bytes.
local function read32u(a)
    return emu:read8(a) | (emu:read8(a + 1) << 8) | (emu:read8(a + 2) << 16) | (emu:read8(a + 3) << 24)
end
local BLOCK = read32u(0x09E6FF2E)

local function blockPos()
    local vals = { emu:read32(0x03000EB8) }
    local depth = emu:read8(0x03000EB0)
    for i = 0, math.min(depth, 20) - 1 do vals[#vals + 1] = emu:read32(0x03000EBC + 4 * i) end
    for _, v in ipairs(vals) do
        if v >= BLOCK and v < BLOCK + 130 then return v - BLOCK end
    end
    return -1
end
local function freeRoam()
    return emu:read8(0x03000F9C) == 0 and emu:read32(0x030030F4) == 0x080565B5
end

local f, phase, holdKey, holdUntil, nextAt, queue = 0, "title", nil, 0, 700, {}
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
        if pos < 0 then phase = "story"
        -- Wait before answering: the yes/no and the number screen take time
        -- to come up, and a press that lands first is dropped. Measured: an
        -- immediate DOWN at pos 13 answered YES, then looped 32 <-> 36.
        elseif pos == 13 then
            if not WAITED13 then WAITED13 = true; nextAt = f + 90; return end
            press(DOWN); press(A)
        elseif pos == 36 then
            if not WAITED36 then WAITED36 = true; nextAt = f + 90; return end
            WAITED36 = false
            press(START); press(A)
        else press(A) end
    elseif phase == "story" then
        if freeRoam() then
            nextAt = f + 120; phase = "settle"
        else press(A) end
    elseif phase == "settle" then
        if freeRoam() then
            emu:saveStateFile(OUT)
            console:log(("CHECKPOINT %s at frame %d"):format(OUT, f))
            os.exit(0)
        end
        phase = "story"
    end
    if f > 60 * 60 * 30 then console:log("CHECKPOINT FAILED phase=" .. phase); os.exit(1) end
end)
