-- Live test of the in-game roster display in UNBOUND: a START menu row
-- (2026-09-27). The first headless Lua/screenshot layer in this repo; the GDB
-- harness is unchanged.
--
-- Loads /tmp/ub_ss_field.ss (tools/mgba_scripts/mk_checkpoint_field.lua: a
-- fresh game driven to free-roam, CM opt-in answered No), presets CM in the
-- CFRU expanded-save EWRAM (flag 0x18F8 = bit 0 of 0x0203B373, var 0x51FC at
-- 0x0203B76C -- the persistence test's addresses), then opens START.
--
--   MODE=roster  CM on as CM_CHAR: START must contain action 6 (the dead
--                "Costume Box" slot, now Roster). Move the cursor onto it
--                closed-loop, press A: CM_StartMenuRosterCallback runs, the
--                rows are EXACTLY the character's roots (read out of the
--                list's own item array, species AND name pointer, against
--                CM_EXPECT_ROOTS from the manifest), the icon comes from CFRU's
--                icon table and matches VRAM and palette, one DOWN hands the
--                cursor callback the SECOND root's species ("ID, not index"),
--                B closes it all, and the player can walk again.
--   MODE=off     CM off: START must NOT contain action 6 -- with CM off the
--                menu is what it was.
local K = { A = 0, B = 1, START = 3, RIGHT = 4, LEFT = 5, UP = 6, DOWN = 7 }
local MODE = os.getenv("MODE") or "roster"
local CM_CHAR = tonumber(os.getenv("CM_CHAR") or "10")
local STATE = os.getenv("CM_CHECKPOINT") or "/tmp/ub_ss_field.ss"
local function envaddr(n)
    local v = os.getenv(n)
    if not v then error("missing env " .. n) end
    return tonumber(v)
end
local CALLBACK = envaddr("CM_ROSTER_CALLBACK") & ~1
local MOVE = envaddr("CM_ROSTER_MOVE") & ~1
local INPUT = envaddr("CM_ROSTER_INPUT") & ~1
local EXPECT = {}
for s in (os.getenv("CM_EXPECT_ROOTS") or ""):gmatch("%d+") do EXPECT[#EXPECT + 1] = tonumber(s) end

local FLAG_BYTE, VAR_CHAR, VAR_ORDER6 = 0x0203B373, 0x0203B76C, 0x0203B3F4
local NUM_ITEMS, ACTIONS, CURSOR = 0x020370F5, 0x020370F6, 0x020370F4
local gTasks, TASK_SIZE = 0x03005090, 0x28
local gSprites, SPRITE_SIZE = 0x0202063C, 0x44
local NAMES = emu:read32(0x08000144)
local ICONS = emu:read32(0x08000138)
local PALIDX = emu:read32(0x0800013C)
local PALTABLE = emu:read32(0x08000140)

-- ---- tally (CM_EXPECT_CHECKS pins the count, as every layer here does) ----
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

local cbHits, moves, selSeen = 0, 0, {}
emu:setBreakpoint(function() cbHits = cbHits + 1 end, CALLBACK)
emu:setBreakpoint(function()
    moves = moves + 1
    selSeen[#selSeen + 1] = emu:readRegister("r0")
end, MOVE)

local function actions()
    local n, t = emu:read8(NUM_ITEMS), {}
    for i = 0, n - 1 do t[#t + 1] = emu:read8(ACTIONS + i) end
    return t
end
local function has6(t) for _, v in ipairs(t) do if v == 6 then return true end end return false end
local function rosterTask()
    for i = 0, 15 do
        local t = gTasks + i * TASK_SIZE
        if emu:read8(t + 4) ~= 0 and (emu:read32(t) & ~1) == INPUT then return t end
    end
end
local function readRows()
    local t = rosterTask()
    if not t then return nil end
    local items = ((emu:read16(t + 8 + 8) & 0xFFFF) << 16) | (emu:read16(t + 8 + 10) & 0xFFFF)
    local ids, namesOk = {}, true
    for i = 0, #EXPECT - 1 do
        local id = emu:read32(items + i * 8 + 4)
        ids[#ids + 1] = tostring(id)
        if emu:read32(items + i * 8) ~= NAMES + id * 11 then namesOk = false end
    end
    return table.concat(ids, ","), namesOk
end
local function iconSpriteFor(s)
    local img = emu:read32(ICONS + s * 4)
    for i = 0, 63 do
        local b = gSprites + i * SPRITE_SIZE
        if (emu:read8(b + 0x3E) & 1) == 1 and emu:read32(b + 12) == img then return b end
    end
end
local function anyRosterIcon()
    for _, s in ipairs(EXPECT) do if iconSpriteFor(s) then return true end end
    return false
end
local function iconMatchesRom(b, s)
    local img = emu:read32(ICONS + s * 4)
    local vram = 0x06010000 + (emu:read16(b + 4) & 0x3FF) * 32
    local f0, f1 = true, true
    for k = 0, 511 do
        local v = emu:read8(vram + k)
        if v ~= emu:read8(img + k) then f0 = false end
        if v ~= emu:read8(img + 512 + k) then f1 = false end
    end
    -- ⚠️ Compare the UNFADED buffer (gPlttBufferUnfaded 0x020371F8 + 0x200),
    -- not palette RAM: Unbound's day/night system tints what reaches hardware.
    local pal = (emu:read16(b + 4) >> 12) & 15
    local src = emu:read32(PALTABLE + emu:read8(PALIDX + s) * 8)
    local palOk = true
    for k = 0, 15 do
        if emu:read16(0x020371F8 + 0x200 + pal * 32 + k * 2) ~= emu:read16(src + k * 2) then palOk = false end
    end
    return (f0 or f1), palOk
end
local function pos()
    local sb1 = emu:read32(0x03005008)
    return emu:read16(sb1), emu:read16(sb1 + 2)
end

local f, step, at, holdKey, holdUntil = 0, "load", 0, nil, 0
local t = {}
local function hold(k, n) holdKey = k; emu:addKey(k); holdUntil = f + n end
callbacks:add("frame", function()
    f = f + 1
    if holdKey and f >= holdUntil then emu:clearKey(holdKey); holdKey = nil end
    if step == "load" and f == 3 then
        emu:loadStateFile(STATE); step, at = "preset", f
    elseif step == "preset" and f - at == 30 then
        local b = emu:read8(FLAG_BYTE)
        if MODE == "off" then emu:write8(FLAG_BYTE, b & ~1)
        else emu:write8(FLAG_BYTE, b | 1); emu:write16(VAR_CHAR, CM_CHAR) end
        console:log(("order var 0x5040 = %d"):format(emu:read16(VAR_ORDER6)))
        hold(K.START, 15); step, at = "menu", f
    elseif step == "menu" and f - at == 90 then
        t.acts = actions()
        console:log("START actions: " .. table.concat(t.acts, ","))
        emu:screenshot(("build/roster_start_%s.png"):format(MODE))
        if MODE == "off" then step = "done" else step, at = "seek", f end
    elseif step == "seek" then
        local cur = emu:read8(ACTIONS + emu:read8(CURSOR))
        if cur == 6 then
            step, at = "on_roster", f
        elseif f - at > 900 then step = "done"
        elseif (f - at) % 30 == 0 then hold(K.RIGHT, 10) end
    elseif step == "on_roster" and f - at == 40 then
        emu:screenshot("build/roster_start_selected.png")
        hold(K.A, 12); step, at = "wait_list", f
    elseif step == "wait_list" then
        if cbHits > 0 and moves > 0 then step, at = "list_shot", f
        elseif f - at > 600 then step = "done" end
    elseif step == "list_shot" and f - at == 40 then
        t.rows, t.namesOk = readRows()
        local b = iconSpriteFor(EXPECT[1])
        t.firstIcon = b ~= nil
        if b then t.firstVram, t.firstPal = iconMatchesRom(b, EXPECT[1]) end
        emu:screenshot(("build/roster_list_c%d_row0.png"):format(CM_CHAR))
        -- the handler's fade-to-black must have been cancelled: BG palette 0
        -- colour 1 in palette RAM is the same as before START was opened
        t.visible = emu:read16(0x05000002) ~= 0 and emu:read8(0x02037AB8 + 7) & 0x80 == 0
        t.moveBase = moves; step, at = "down", f
    elseif step == "down" then
        if moves > t.moveBase then step, at = "down_shot", f
        elseif f - at > 600 then step, at = "close", f
        elseif (f - at) % 20 == 0 then hold(K.DOWN, 8) end
    elseif step == "down_shot" and f - at == 40 then
        local b = iconSpriteFor(EXPECT[2])
        t.secondIcon = b ~= nil
        t.secondPrio = b and ((emu:read8(b + 5) >> 2) & 3)
        emu:screenshot(("build/roster_list_c%d_row1.png"):format(CM_CHAR))
        step, at = "close", f
    elseif step == "close" then
        if rosterTask() == nil then step, at = "walk", f
        elseif f - at > 600 then step = "done"
        elseif (f - at) % 20 == 0 then hold(K.B, 8) end
    elseif step == "walk" and f - at == 60 then
        t.x0, t.y0 = pos(); hold(K.DOWN, 16); step, at = "walked", f
    elseif step == "walked" and f - at == 60 then
        local x, y = pos()
        t.walked = (x ~= t.x0 or y ~= t.y0)
        if not t.walked then hold(K.UP, 16); step, at = "walked2", f
        else step = "done" end
    elseif step == "walked2" and f - at == 60 then
        local x, y = pos()
        t.walked = (x ~= t.x0 or y ~= t.y0)
        step = "done"
    end
    if step == "done" then
        step = "finished"
        emu:screenshot(("build/roster_end_%s.png"):format(MODE))
        local s = {}
        for _, v in ipairs(selSeen) do s[#s + 1] = tostring(v) end
        console:log(("mode=%s char=%d callback=%d moves=%d sel=[%s] rows=[%s]"):format(
            MODE, CM_CHAR, cbHits, moves, table.concat(s, ","), tostring(t.rows)))
        if MODE == "roster" then
            check("START contains the Roster row (action 6)", t.acts and has6(t.acts), table.concat(t.acts or {}, ","))
            check("selecting it ran CM_StartMenuRosterCallback", cbHits == 1)
            check("rows == the character's family roots, in order", t.rows == table.concat(EXPECT, ","))
            check("every row's name points at gSpeciesNames[species]", t.namesOk == true)
            check("the screen is visible while the list is up (no leftover fade)", t.visible == true)
            check("first cursor callback got the first root's SPECIES", selSeen[1] == EXPECT[1], selSeen[1])
            check("the first root's icon sprite draws from CFRU's icon table", t.firstIcon == true)
            check("...its VRAM tiles are that icon's frame", t.firstVram == true)
            check("...and its OBJ palette is the table entry its index names", t.firstPal == true)
            check("after one DOWN, the callback got the SECOND root's species", selSeen[#selSeen] == EXPECT[2], selSeen[#selSeen])
            check("the second root's icon replaced it", t.secondIcon == true)
            check("the icon is above the window layer (oam priority)", t.secondPrio == 0, t.secondPrio)
            check("B closed it: no roster task, no roster icon", rosterTask() == nil and not anyRosterIcon())
            check("the field is back: the player walked after the close", t.walked == true)
        else
            check("CM off: START has no Roster row", t.acts and not has6(t.acts), table.concat(t.acts or {}, ","))
            check("CM off: the roster never opened", cbHits == 0)
        end
        finish()
    end
    if f > 6000 and step ~= "finished" then step = "done" end
end)
