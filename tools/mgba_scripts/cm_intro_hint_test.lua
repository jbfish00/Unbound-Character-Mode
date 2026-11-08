-- Live layer: the wild-intro roster hint (QoL B9, 2026-11-08; src/character_mode.c
-- CharacterMode_MarkedIntro). Same route as cm_sure_catch_test.lua: from the free-roam
-- checkpoint a queued script gives a Pikachu lead, sets Character Mode as CM_CHAR (CM_ON=1)
-- and starts a wild battle with SPECIES (Snorlax, on Red's roster (1), off Leaf's (2)).
-- It reads r0 at the expander wrapper 0x080D77F4 (the decision in a real battle) and the
-- displayed battle string after the intro, decoded:
--   EXPECT=marker    -> "destined for <NAME>"
--   EXPECT=offroster -> "It is not on your roster."
--   EXPECT=vanilla   -> neither line (CM off, or the CM_NO_OFFROSTER control ROM)
-- Env: CM_ON 1/0, CM_CHAR, SPECIES, EXPECT, CM_EXPECT_CHECKS, SHOTS (dir).
local A, B, RIGHT, LEFT, UP, DOWN = 0, 1, 4, 5, 6, 7
local QUEUE = tonumber(os.getenv("QUEUE_CB1"))           -- CharacterMode_QueueScriptCb1|1
local SPECIES = tonumber(os.getenv("SPECIES") or "143")
local CM_ON = os.getenv("CM_ON") == "1"
local CHAR = tonumber(os.getenv("CM_CHAR") or "1")
local EXPECT = os.getenv("EXPECT") or "offroster"
local SEED = tonumber(os.getenv("SEED") or "1")
local SHOTS = os.getenv("SHOTS")
local SCRATCH, SLOT, CB1 = 0x0203FD00, 0x0203B764, 0x030030F0
local INBATTLE, PARTY_COUNT, RNG = 0x03003529, 0x02024029, 0x03005000   -- gRngValue (FireRed)
local odds, f, passes, fails, battleAt, keys, bagAt = nil, 0, 0, {}, nil, {}, nil
local battleCb2, bagOpenAt, throwAt = nil, nil, nil

local function u16(v) return string.char(v & 0xFF, (v >> 8) & 0xFF) end
local s = ""
s = s .. string.char(0x79) .. u16(25) .. string.char(50) .. u16(0) .. string.rep("\0", 9)  -- givemon Pikachu L50
s = s .. string.char(0x44) .. u16(4) .. u16(10)                                              -- additem POKE_BALL x10
if CM_ON then
    s = s .. string.char(0x29) .. u16(0x18F8)                                                -- setflag CM
    s = s .. string.char(0x16) .. u16(0x51FC) .. u16(CHAR)                                   -- setvar char
end
s = s .. string.char(0xB6) .. u16(SPECIES) .. string.char(30) .. u16(0)                      -- setwildbattle
s = s .. string.char(0xB7, 0x27, 0x02)                                                       -- dowildbattle; waitstate; end


local WRAPPER = 0x080D77F4
local DISPLAYED = emu:read32(0x080D7800)        -- the wrapper's literal: gDisplayedStringBattle
local INTROS = {[0x08A4C5C8] = true, [0x08A4C5A3] = true}
local MARKER_LO, MARKER_HI = 0x09630000, 0x09634000
local introR0, introAt = nil, nil
emu:setBreakpoint(function()
    if introR0 ~= nil or battleAt == nil then return end
    local r0 = emu:readRegister("r0")
    if INTROS[r0] or (r0 >= MARKER_LO and r0 < MARKER_HI) then introR0 = r0; introAt = f end
end, WRAPPER)

local function check(name, ok)
    if ok then passes = passes + 1 else table.insert(fails, name) end
    console:log(string.format("HINT %s %s", ok and "PASS" or "FAIL", name))
end
local function shot(n) if SHOTS then emu:screenshot(string.format("%s/%05d_%s.png", SHOTS, f, n)) end end
local function decode(addr, n)
    local out = {}
    for i = 0, n - 1 do
        local b = emu:read8(addr + i)
        if b == 0xFF then break
        elseif b >= 0xBB and b <= 0xD4 then out[#out + 1] = string.char(65 + b - 0xBB)
        elseif b >= 0xD5 and b <= 0xEE then out[#out + 1] = string.char(97 + b - 0xD5)
        elseif b == 0x00 then out[#out + 1] = " "
        elseif b == 0xAB then out[#out + 1] = "!"
        elseif b == 0xAD then out[#out + 1] = "."
        elseif b == 0xB8 then out[#out + 1] = ","
        elseif b == 0xFE then out[#out + 1] = "/"
        else out[#out + 1] = string.format("{%02X}", b) end
    end
    return table.concat(out)
end

callbacks:add("frame", function()
    f = f + 1
    if f == 5 then
        for i = 1, #s do emu:write8(SCRATCH + i - 1, s:byte(i)) end
        emu:write32(SLOT, SCRATCH)
        emu:write32(CB1, QUEUE)
    end
    if battleAt == nil and f > 10 and (emu:read8(INBATTLE) >> 1) & 1 == 1 then
        battleAt = f
        console:log("HINT battle started at frame " .. f)
    end
    if introAt and f == introAt + 90 then shot("intro") end
    if (introAt and f == introAt + 100) or f == 6000 then
        local text = decode(DISPLAYED, 80)
        console:log(string.format("HINT intro r0=%s text=[%s]",
            introR0 and string.format("%08X", introR0) or "nil", text))
        check("the wild intro was expanded in a real battle", introR0 ~= nil)
        local destined = text:find("destined for", 1, true) ~= nil
        local off = text:find("It is not on your roster.", 1, true) ~= nil
        if EXPECT == "marker" then check("the intro names the character", destined and not off)
        elseif EXPECT == "offroster" then check("the intro says 'It is not on your roster.'", off and not destined)
        else check("the vanilla intro (no roster line)", introR0 ~= nil and not off and not destined) end
        local want = tonumber(os.getenv("CM_EXPECT_CHECKS") or "2")
        local ran = passes + #fails
        console:log(string.format("HINT RESULT: %s (%d passed, %d failed, %d ran, want %d)",
            (#fails == 0 and ran == want) and "PASS" or "FAIL", passes, #fails, ran, want))
        emu:pause()
    end
end)
