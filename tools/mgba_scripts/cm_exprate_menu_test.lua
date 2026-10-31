-- Live layer: START > Extras > Exp. Rate (2026-10-30, src/exp_rate.c + src/roster_display.c).
-- From the free-roam checkpoint (mk_checkpoint_field.lua), preset Character Mode (MODE=on: flag 0x18F8 + CM_CHAR;
-- MODE=off: flag cleared) and the rate var 0x51FD (START_RATE), open START, put the cursor on action 6 ("Extras",
-- record 6) closed-loop and press A. Then:
--   MODE=on   the Extras list must open (its task); EXTRAS_KEYS are pressed in it (comma list, e.g. "DOWN,A" = Exp.
--             Rate, "A" = Roster, "B" = close). WANT_NEXT = rate | roster | field: what must open next.
--   MODE=off  the rate chooser must open straight away (no Extras list).
-- In the rate chooser LIST_KEYS are pressed; var 0x51FD must then read WANT_RATE, every task must be gone and the
-- player must walk. Screenshots: SHOTS=<prefix>.
-- Env: EXTRAS_INPUT, RATE_INPUT, ROSTER_INPUT (task funcs from the ELF), CM_EXPECT_CHECKS.
local K = { A = 0, B = 1, START = 3, RIGHT = 4, LEFT = 5, UP = 6, DOWN = 7 }
local MODE = os.getenv("MODE") or "off"
local CM_CHAR = tonumber(os.getenv("CM_CHAR") or "10")
local STATE = os.getenv("CM_CHECKPOINT") or "/tmp/ub_ss_field.ss"
local START_RATE = tonumber(os.getenv("START_RATE") or "0")
local WANT_RATE = tonumber(os.getenv("WANT_RATE") or "-1")
local WANT_NEXT = os.getenv("WANT_NEXT") or "rate"
local SHOTS = os.getenv("SHOTS")
local function envaddr(n) local v = os.getenv(n); if not v then error("missing env " .. n) end; return tonumber(v) & ~1 end
local EXTRAS, RATE, ROSTER = envaddr("EXTRAS_INPUT"), envaddr("RATE_INPUT"), envaddr("ROSTER_INPUT")
local function keylist(s)
    local t = {}
    for k in (s or ""):gmatch("[A-Z]+") do t[#t + 1] = K[k] end
    return t
end
local EXTRAS_KEYS, LIST_KEYS = keylist(os.getenv("EXTRAS_KEYS")), keylist(os.getenv("LIST_KEYS"))

local FLAG_BYTE, VAR_CHAR, VAR_RATE = 0x0203B373, 0x0203B76C, 0x0203B76E
local NUM_ITEMS, ACTIONS, CURSOR = 0x020370F5, 0x020370F6, 0x020370F4
local gTasks, TASK_SIZE = 0x03005090, 0x28

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
local function task(fn)
    for i = 0, 15 do
        local t = gTasks + i * TASK_SIZE
        if emu:read8(t + 4) ~= 0 and (emu:read32(t) & ~1) == fn then return t end
    end
end
local function has6()
    for i = 0, emu:read8(NUM_ITEMS) - 1 do if emu:read8(ACTIONS + i) == 6 then return true end end
    return false
end
local function pos()
    local sb1 = emu:read32(0x03005008)
    return emu:read16(sb1), emu:read16(sb1 + 2)
end
local function shot(name) if SHOTS then emu:screenshot(("%s_%s.png"):format(SHOTS, name)) end end

local f, step, at, holdKey, holdUntil, ki = 0, "load", 0, nil, 0, 1
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
        emu:write16(VAR_RATE, START_RATE)
        hold(K.START, 15); step, at = "menu", f
    elseif step == "menu" and f - at == 90 then
        t.row = has6(); shot("start")
        if t.row then step, at = "seek", f else step = "done" end
    elseif step == "seek" then
        if emu:read8(ACTIONS + emu:read8(CURSOR)) == 6 then step, at = "on6", f
        elseif f - at > 900 then step = "done"
        elseif (f - at) % 30 == 0 then hold(K.RIGHT, 10) end
    elseif step == "on6" and f - at == 40 then
        hold(K.A, 12); step, at = "opened", f
    elseif step == "opened" and f - at == 60 then
        t.extras = task(EXTRAS) ~= nil; t.rate = task(RATE) ~= nil
        shot("opened"); ki = 1
        if MODE == "on" and t.extras then step, at = "extras", f
        elseif t.rate then step, at = "list", f; ki = 1
        else step = "done" end
    elseif step == "extras" and (f - at) % 30 == 0 then
        if ki <= #EXTRAS_KEYS then hold(EXTRAS_KEYS[ki], 8); ki = ki + 1
        elseif f - at > 30 * (#EXTRAS_KEYS + 2) then
            t.extrasGone = task(EXTRAS) == nil
            t.next = task(RATE) and "rate" or task(ROSTER) and "roster" or "field"
            shot("after_extras")
            if t.next == "rate" then step, at, ki = "list", f, 1
            elseif t.next == "roster" then step, at = "close_roster", f
            else step, at = "walk", f end
        end
    elseif step == "close_roster" then
        if task(ROSTER) == nil then step, at = "walk", f
        elseif f - at > 600 then step = "done"
        elseif (f - at) % 20 == 0 then hold(K.B, 8) end
    elseif step == "list" and (f - at) % 30 == 0 and f > at then
        if ki <= #LIST_KEYS then
            if ki == #LIST_KEYS then shot("list") end
            hold(LIST_KEYS[ki], 8); ki = ki + 1
        elseif f - at > 30 * (#LIST_KEYS + 2) then
            t.rateGone = task(RATE) == nil; step, at = "walk", f
        end
    elseif step == "walk" and f - at == 60 then
        t.x0, t.y0 = pos(); hold(K.DOWN, 16); step, at = "walked", f
    elseif step == "walked" and f - at == 60 then
        local x, y = pos()
        t.walked = (x ~= t.x0 or y ~= t.y0)
        if not t.walked then hold(K.UP, 16); step, at = "walked2", f else step = "done" end
    elseif step == "walked2" and f - at == 60 then
        local x, y = pos()
        t.walked = (x ~= t.x0 or y ~= t.y0)
        step = "done"
    end
    if step == "done" then
        step = "finished"
        shot("end")
        local rate = emu:read16(VAR_RATE)
        console:log(("mode=%s start=%d rate=%d next=%s"):format(MODE, START_RATE, rate, tostring(t.next)))
        check("START contains the Extras row (action 6)", t.row == true)
        if MODE == "on" then
            check("A on it opened the Extras list (not the chooser)", t.extras == true and t.rate == false)
            check("after EXTRAS_KEYS the list is gone and " .. WANT_NEXT .. " opened", t.extrasGone == true and t.next == WANT_NEXT, t.next)
        else
            check("CM off: A on it opened the rate chooser straight away", t.rate == true and t.extras == false)
        end
        if WANT_NEXT == "rate" then
            check("the chooser closed", t.rateGone == true)
            check("var 0x51FD == " .. WANT_RATE, rate == WANT_RATE, rate)
        else
            check("var 0x51FD unchanged", rate == START_RATE, rate)
        end
        check("the field is back: the player walked", t.walked == true)
        finish()
    end
    if f > 6000 and step ~= "finished" then step = "done" end
end)
