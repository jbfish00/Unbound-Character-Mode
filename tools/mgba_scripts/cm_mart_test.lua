-- Live layer: Mart evolution items (QoL A1, 2026-10-24; src/character_mode.c
-- CharacterMode_CreatePokemartMenu). From the free-roam checkpoint
-- (mk_checkpoint_field.lua), a script is queued through CharacterMode_QueueScriptCb1:
-- set (or clear) the Character Mode flag + character var, then `pokemart <MART>`
-- (a real list from the ROM). A breakpoint on SetShopItemsForSale reads the list the
-- shop receives; it must equal WANT_LIST (comma ids). Then A opens Buy, the list is
-- scrolled to its end and photographed (SHOT).
-- Env: QUEUE_CB1, MART (hex list address), CHAR (0 = mode off), WANT_LIST, SHOT,
--      CM_EXPECT_CHECKS.
local A, DOWN = 0, 7
local QUEUE = tonumber(os.getenv("QUEUE_CB1"))
local MART = tonumber(os.getenv("MART"), 16)
local CHAR = tonumber(os.getenv("CHAR") or "0")
local WANT = os.getenv("WANT_LIST")
local SHOT = os.getenv("SHOT")
local SCRATCH, SLOT, CB1 = 0x0203FD00, 0x0203B764, 0x030030F0
local f, got, gotAt, passes, fails = 0, nil, nil, 0, {}
local function u16(v) return string.char(v & 0xFF, (v >> 8) & 0xFF) end
local function u32(v) return u16(v & 0xFFFF) .. u16((v >> 16) & 0xFFFF) end

local s = ""
if CHAR > 0 then
    s = s .. string.char(0x29) .. u16(0x18F8) .. string.char(0x16) .. u16(0x51FC) .. u16(CHAR)   -- setflag CM; setvar char
else
    s = s .. string.char(0x2A) .. u16(0x18F8) .. string.char(0x16) .. u16(0x51FC) .. u16(0)      -- clearflag; setvar 0
end
s = s .. string.char(0x86) .. u32(MART) .. string.char(0x02)                                      -- pokemart; end

emu:setBreakpoint(function()
    local p, t = emu:readRegister("r0"), {}
    for i = 0, 100 do
        local v = emu:read16(p + 2 * i)
        if v == 0 then break end
        t[#t + 1] = v
    end
    got = table.concat(t, ","); gotAt = gotAt or f
end, 0x0809ABD8)

local function check(name, ok)
    if ok then passes = passes + 1 else table.insert(fails, name) end
    console:log(string.format("MART %s %s", ok and "PASS" or "FAIL", name))
end

local keys = {}
local function press(k, at, len) keys[#keys + 1] = {k, at, at + (len or 8)} end

callbacks:add("frame", function()
    f = f + 1
    for _, k in ipairs(keys) do
        if f == k[2] then emu:addKey(k[1]) elseif f == k[3] then emu:clearKey(k[1]) end
    end
    if f == 5 then
        for i = 1, #s do emu:write8(SCRATCH + i - 1, s:byte(i)) end
        emu:write32(SLOT, SCRATCH)
        emu:write32(CB1, QUEUE)
    end
    if gotAt and f == gotAt + 120 then press(A, f + 1) end                       -- Buy
    if gotAt and f == gotAt + 220 then for i = 1, 20 do press(DOWN, f + i * 14, 6) end end
    if (gotAt and f == gotAt + 560) or f == 3000 then
        if SHOT then emu:screenshot(SHOT) end
        console:log("MART list=" .. tostring(got))
        check("SetShopItemsForSale ran", got ~= nil)
        check("the Mart's list is " .. tostring(WANT), got == WANT)
        local want = tonumber(os.getenv("CM_EXPECT_CHECKS") or "2")
        local ran = passes + #fails
        console:log(string.format("MART RESULT: %s (%d passed, %d failed, %d ran, want %d)",
            (#fails == 0 and ran == want) and "PASS" or "FAIL", passes, #fails, ran, want))
        os.exit((#fails == 0 and ran == want) and 0 or 1)
    end
end)
