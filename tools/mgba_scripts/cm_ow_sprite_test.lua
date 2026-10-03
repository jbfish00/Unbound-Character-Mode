-- Live test: the player's overworld sprite follows the character (2026-10-03).
--
-- Loads a free-roam checkpoint (mk_checkpoint_cm.lua: CM turned on through the
-- real opt-in block; or mk_checkpoint_field.lua: CM off), then reads the
-- player's sprite straight out of OBJ VRAM and the UNFADED palette buffer and
-- compares them with the expected art (tools/tests/ow_sprite_env.py writes it
-- from the source sheet, not from the built ROM).
--
--   MODE=on   standing, then walking and running in all four directions: every
--             frame seen in VRAM must be one of THAT direction's frames for
--             that gait, and a step frame must show up. Sideways running is
--             the case that caught RR's frame order (a running player's back).
--   MODE=off  CM off: the sprite must NOT be any of the character's frames.
--
-- Env: MODE, CM_CHECKPOINT, CM_OW_EXPECT, CM_OW_FRAME_BYTES, CM_OW_KIND
--      (sheet | costume), CM_EXPECT_CHECKS, CM_SHOTS (screenshot prefix).
local MODE = os.getenv("MODE") or "on"
local STATE = os.getenv("CM_CHECKPOINT")
local FB = tonumber(os.getenv("CM_OW_FRAME_BYTES") or "512")
local KIND = os.getenv("CM_OW_KIND") or "sheet"
local SHOTS = os.getenv("CM_SHOTS") or "/tmp/ub_ow"
local K = { A = 0, B = 1, RIGHT = 4, LEFT = 5, UP = 6, DOWN = 7 }

local fh = assert(io.open(os.getenv("CM_OW_EXPECT"), "rb"))
local blob = fh:read("a"); fh:close()
local FRAMES, PAL = {}, {}
for i = 0, 17 do FRAMES[i] = blob:sub(i * FB + 1, (i + 1) * FB) end
for k = 0, 15 do PAL[k] = string.unpack("<I2", blob, 18 * FB + 2 * k + 1) end

-- Which sheet frames each direction/gait may show. A sheet is pokeemerald's
-- player layout (run stands 9-11, then steps); a native costume is FireRed's
-- own (each direction's run stand + steps grouped).
local SETS
if KIND == "costume" then
    SETS = { walk = { DOWN = { 0, 3, 4 }, UP = { 1, 5, 6 }, LEFT = { 2, 7, 8 }, RIGHT = { 2, 7, 8 } },
             run = { DOWN = { 9, 10, 11 }, UP = { 12, 13, 14 }, LEFT = { 15, 16, 17 }, RIGHT = { 15, 16, 17 } } }
else
    SETS = { walk = { DOWN = { 0, 3, 4 }, UP = { 1, 5, 6 }, LEFT = { 2, 7, 8 }, RIGHT = { 2, 7, 8 } },
             run = { DOWN = { 9, 12, 13 }, UP = { 10, 14, 15 }, LEFT = { 11, 16, 17 }, RIGHT = { 11, 16, 17 } } }
end
-- the stand frame a gait returns to between steps (walk 0-2; a run may end on it too)
local STAND = { DOWN = 0, UP = 1, LEFT = 2, RIGHT = 2 }

local gPlayerAvatar, gSprites, SPRITE_SIZE = 0x02037078, 0x0202063C, 0x44
local UNFADED_OBJ = 0x020371F8 + 0x200

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

local function playerSprite() return gSprites + emu:read8(gPlayerAvatar + 4) * SPRITE_SIZE end
-- EVERY sheet frame whose bytes equal what is in VRAM: sheets often repeat a
-- frame (many reuse the walk steps as run steps), so "the first match" would
-- name the wrong one. nil when nothing matches.
local function vramFrames()
    local b = playerSprite()
    local at = 0x06010000 + (emu:read16(b + 4) & 0x3FF) * 32
    local t = {}
    for k = 0, FB - 1, 4 do t[#t + 1] = string.pack("<I4", emu:read32(at + k)) end
    local cur, hit = table.concat(t), {}
    for i = 0, 17 do if FRAMES[i] == cur then hit[#hit + 1] = i end end
    return #hit > 0 and hit or nil
end
local function vramFrame() local h = vramFrames(); return h and h[1] end
local function paletteOk()
    local pal = (emu:read16(playerSprite() + 4) >> 12) & 15
    for k = 1, 15 do   -- colour 0 is transparent
        if emu:read16(UNFADED_OBJ + pal * 32 + 2 * k) ~= PAL[k] then return false end
    end
    return true
end
local function contains(t, v) for _, x in ipairs(t) do if x == v then return true end end return false end
local function overlaps(a, b) for _, x in ipairs(a) do if contains(b, x) then return true end end return false end
local function dashing() return (emu:read8(gPlayerAvatar) & 0x80) ~= 0 end

-- ---- movement: Unbound auto-runs (a held direction dashes, B+direction
-- walks, measured 2026-10-03), so the gait of every sample is read from the
-- avatar's dash flag rather than assumed from the keys. The route is the one
-- the CM checkpoint's room allows: down the corridor, one tile left and back
-- at its foot, then up again. Every direction must show a STEP frame of its
-- own while dashing and while walking, and no sample may show another
-- direction's frame. ----
local steps = {
    { dir = "DOWN", b = false, hold = 64 }, { dir = "LEFT", b = false, hold = 24 },
    { dir = "RIGHT", b = false, hold = 24 }, { dir = "LEFT", b = true, hold = 40 },
    { dir = "RIGHT", b = true, hold = 40 }, { dir = "UP", b = false, hold = 40 },
    { dir = "UP", b = true, hold = 40 }, { dir = "DOWN", b = true, hold = 40 },
}
local GAP, TURN = 24, 3      -- ignore the first TURN samples: the turn lands a frame or two late
local got = {}               -- got[dir][gait] = a step frame of that gait was seen
local bad = {}               -- samples showing a frame outside their direction/gait set
local function stepOf(gait, dir, hit)
    local set = SETS[gait][dir]
    for _, v in ipairs(hit) do
        if contains(set, v) and v ~= set[1] and v ~= STAND[dir] then return true end
    end
    return false
end
local f, phase, si, t0 = 0, "boot", 1, 0
callbacks:add("frame", function()
    f = f + 1
    if phase == "boot" then
        if f < 3 then return end   -- as cm_roster_menu_test.lua: a load on frame 1 drops input
        if not emu:loadStateFile(STATE) then console:log("HARNESS FAIL no checkpoint"); os.exit(1) end
        phase, t0 = "settle", f
    elseif phase == "settle" then
        if f - t0 < 30 then return end
        local fr = vramFrame()
        emu:screenshot(SHOTS .. "_stand.png")
        if MODE == "off" then
            check("CM off: the player is not drawn with the character's art (want no match)", fr == nil, fr)
            check("CM off: the palette is not the character's (want mismatch)", not paletteOk())
            finish()
        end
        check("standing: VRAM holds one of the character's frames", fr ~= nil, "no frame matched")
        check("standing: the UNFADED palette is the character's", paletteOk())
        phase, t0 = "move", f + 1   -- dt == 0 on the NEXT frame
    elseif phase == "move" then
        local s = steps[si]
        local dt = f - t0
        if dt == 0 then
            emu:addKey(K[s.dir]); if s.b then emu:addKey(K.B) end
        elseif dt <= s.hold then
            if dt > TURN then
                local hit = vramFrames()
                local gait = dashing() and "run" or "walk"
                -- The direction is strict; the gait is not: the dash flag drops
                -- a frame before VRAM gets the next copy (VBlank), so the last
                -- run frame can sit under a walk flag (seen on Unbound's own
                -- Leaf costume too). The step checks below stay per gait.
                local ok = hit and (overlaps(hit, SETS.walk[s.dir]) or overlaps(hit, SETS.run[s.dir])
                                    or contains(hit, STAND[s.dir]))
                if not ok then bad[#bad + 1] = ("%s/%s:%s"):format(s.dir, gait, hit and table.concat(hit, "+") or "x") end
                if hit and stepOf(gait, s.dir, hit) then
                    got[s.dir] = got[s.dir] or {}; got[s.dir][gait] = true
                end
            end
            if dt == s.hold // 2 then emu:screenshot(("%s_%d_%s%s.png"):format(SHOTS, si, s.dir, s.b and "_B" or "")) end
        elseif dt == s.hold + 1 then
            emu:clearKey(K[s.dir]); emu:clearKey(K.B)
        elseif dt >= s.hold + GAP then
            si, t0 = si + 1, f + 1
            if si > #steps then
                check("every sample shows its own direction's frame (want no stray frame)",
                      #bad == 0, table.concat(bad, " "))
                for _, d in ipairs({ "DOWN", "UP", "LEFT", "RIGHT" }) do
                    for _, g in ipairs({ "walk", "run" }) do
                        check(("%s %s: a %s step frame was drawn (want one)"):format(g, d, g),
                              got[d] and got[d][g])
                    end
                end
                finish()
            end
        end
    end
    if f > 60 * 120 then console:log("HARNESS FAIL timeout"); finish() end
end)
