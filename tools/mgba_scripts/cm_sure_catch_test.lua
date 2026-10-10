-- Live layer: 100% catch for on-roster species (2026-10-09).
-- From the free-roam checkpoint (tools/mgba_scripts/mk_checkpoint_field.lua, CM
-- answered No): a script written to EWRAM scratch is queued through the
-- build's own debug hook CharacterMode_QueueScriptCb1 (the same route
-- battle_catch_test.gdb uses). It gives a Pikachu L50 lead, 10 POKE Balls,
-- then sets Character Mode as CM_CHAR (or leaves it off) and starts a wild
-- battle with SPECIES at level 30 (full HP). One Poke Ball is thrown through
-- the real bag UI. Breakpoints on both successors of the hooked decision
-- (0x089C8D5C caught, 0x089C8E24 shake path) read r5, the odds the game
-- decides on, the first time either is reached:
--   EXPECT=sure    -> odds 255 and the battle ends (caught)
--   EXPECT=miss    -> odds below 255 and the throw fails (not caught)
--   EXPECT=dodged  -> off-roster with CM on: CharacterMode_CatchFlagGet dodges
--                     the ball before any odds are computed (never reached)
-- Snorlax (143, catch rate 25) is on Red's roster (1) and off Leaf's (2).
-- Env: CM_ON 1/0, CM_CHAR, SPECIES, SEED, EXPECT, CM_EXPECT_CHECKS, SHOTS (dir).
local A, B, RIGHT, LEFT, UP, DOWN = 0, 1, 4, 5, 6, 7
local QUEUE = tonumber(os.getenv("QUEUE_CB1"))           -- CharacterMode_QueueScriptCb1|1
local SPECIES = tonumber(os.getenv("SPECIES") or "143")
local CM_ON = os.getenv("CM_ON") == "1"
local CHAR = tonumber(os.getenv("CM_CHAR") or "1")
local EXPECT = os.getenv("EXPECT") or "sure"
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

local function grab() if odds == nil then odds = emu:readRegister("r5") end end
emu:setBreakpoint(grab, 0x089C8D5C)
emu:setBreakpoint(grab, 0x089C8E24)

local function check(name, ok)
    if ok then passes = passes + 1 else table.insert(fails, name) end
    console:log(string.format("SURE %s %s", ok and "PASS" or "FAIL", name))
end
local function press(k, at, len) keys[#keys + 1] = {k, at, at + (len or 20)} end
local function shot(n) if SHOTS then emu:screenshot(string.format("%s/%05d_%s.png", SHOTS, f, n)) end end

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
    if battleAt == nil and f > 10 and (emu:read8(INBATTLE) >> 1) & 1 == 1 then
        battleAt = f
        console:log("SURE battle started at frame " .. f)
        -- the intro text ends ~900 frames in; then Cube (the bag, right of Fight)
        bagAt = f + 300   -- from here, poll: see below
    end
    -- The intro's length varies. Until the bag opens (gMain.callback2 leaves the
    -- battle's), every 120 frames: gActionSelectionCursor[0] = 1 (Cube, as
    -- battle_catch_test.gdb does) and a 20-frame A.
    if bagAt and f == bagAt then battleCb2 = emu:read32(0x030030F4) end
    if bagAt and f > bagAt and not bagOpenAt then
        if emu:read32(0x030030F4) ~= battleCb2 then
            bagOpenAt = f
            console:log("SURE bag opened at frame " .. f)
            press(RIGHT, f + 60); press(RIGHT, f + 120)       -- Items -> Key Items -> Poke Balls
            press(A, f + 300)                                 -- Poke Ball x10
            throwAt = f + 380
            press(A, throwAt)                                 -- Use
            for t = f + 800, f + 3400, 80 do press(B, t) end -- the messages after it
        elseif (f - bagAt) % 120 == 0 then
            emu:write8(0x02023FF8, 1); press(A, f + 1)
        end
    end
    if throwAt and f == throwAt - 2 then
        emu:write32(RNG, (SEED * 0x9E3779B9 + 0x7F4A7C15) & 0xFFFFFFFF)   -- the shake rolls
    end
    if bagOpenAt and SHOTS and (f - bagOpenAt) % 40 == 0 and f - bagOpenAt <= 1600 then shot("g") end
    if f == 9000 then
        -- Caught = the battle is over (gMain.inBattle clear). Nothing else can end
        -- it in this window: the lead never attacks, the wild mon can't KO a
        -- L50 lead in a few turns, and B never picks Run. A failed throw leaves
        -- the battle running. (gBattleOutcome's vanilla address reads garbage
        -- here, so it is not used.)
        local caught = (emu:read8(INBATTLE) >> 1) & 1 == 0
        console:log(string.format("SURE odds at the decision=%s battle over=%s", tostring(odds), tostring(caught)))
        check("a wild battle started", battleAt ~= nil)
        if EXPECT == "sure" then
            check("odds at the caught/shake decision are 255", odds == 255)
            check("caught on the first throw at full HP (the battle ended)", caught)
        elseif EXPECT == "miss" then
            check("odds are the ball's own (below 255)", odds ~= nil and odds < 255)
            check("this seed's vanilla roll breaks out (not caught)", not caught)
        elseif EXPECT == "dodged" then
            check("the ball never reaches the odds (dodged by the catch gate)", odds == nil)
            check("not caught", not caught)
        else
            check("the throw reached the decision", odds ~= nil)
            check("odds are the ball's own (below 255)", odds ~= nil and odds < 255)
        end
        local want = tonumber(os.getenv("CM_EXPECT_CHECKS") or "3")
        local ran = passes + #fails
        console:log(string.format("SURE RESULT: %s (%d passed, %d failed, %d ran, want %d)",
            (#fails == 0 and ran == want) and "PASS" or "FAIL", passes, #fails, ran, want))
        emu:pause()
    end
end)
