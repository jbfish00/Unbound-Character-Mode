-- Live layer: party-wide Exp. Share with Character Mode OFF (user, 2026-10-21).
-- Unbound's party-wide Exp. Share is native: the Options menu's "Exp. Gain"
-- (Regular / Exp. Share / Capped Exp. Share); CM never touches it. From the
-- free-roam checkpoint (mk_checkpoint_field.lua: a fresh new game, CM answered
-- No) a script is queued through CharacterMode_QueueScriptCb1: Pikachu L50
-- lead + Caterpie L5 benched, then a wild Magikarp L2. The wild mon's HP is
-- poked to 1 and the lead's first move to Tackle; A is mashed until the battle
-- ends. The benched Caterpie never battles, so any Exp. it gains is the share.
--   EXPECT=share -> the benched mon gained Exp. (party-wide share is on)
--   EXPECT=none  -> it gained none (CLEAR_FLAG=9F2 cleared first: the flag the exp
--                   award reads, set unconditionally by the new-game init script
--                   0x09E70DB0; CFRU's 0x906 does nothing here, measured 2026-10-24)
-- Env: QUEUE_CB1, EXPECT, CLEAR_FLAG (hex, optional), CM_EXPECT_CHECKS, SHOTS.
local A = 0
local QUEUE = tonumber(os.getenv("QUEUE_CB1"))
local EXPECT = os.getenv("EXPECT") or "share"
local CLEAR = os.getenv("CLEAR_FLAG"); if CLEAR == "" then CLEAR = nil end
local SHOTS = os.getenv("SHOTS")
local SCRATCH, SLOT, CB1 = 0x0203FD00, 0x0203B764, 0x030030F0
local INBATTLE, PARTY_COUNT, PARTY = 0x03003529, 0x02024029, 0x02024284
local BMONS = 0x02023BE4            -- gBattleMons (FireRed), stride 0x58
local f, passes, fails, battleAt, endAt, poked, n0, done = 0, 0, {}, nil, nil, false, nil, false
local function u16(v) return string.char(v & 0xFF, (v >> 8) & 0xFF) end

-- party EXP. ⚠️ Unbound's party mons are NOT encrypted and the substructure
-- order is fixed: Growth sits at +32 in plain text (species u16, item u16, exp
-- u32). Measured 2026-10-24 by dumping a fresh givemon Pikachu L50: +32 = 25,
-- +36 = 125000. The vanilla PID^OTID decrypt this probe first used read garbage.
local function expOf(slot)
    local base = PARTY + 100 * slot
    return emu:read16(base + 32), emu:read32(base + 36)
end

local s = ""
if CLEAR then s = s .. string.char(0x2A) .. u16(tonumber(CLEAR, 16)) end                     -- clearflag
s = s .. string.char(0x79) .. u16(25) .. string.char(50) .. u16(0) .. string.rep("\0", 9)  -- givemon Pikachu L50
s = s .. string.char(0x79) .. u16(10) .. string.char(5) .. u16(0) .. string.rep("\0", 9)   -- givemon Caterpie L5
s = s .. string.char(0xB6) .. u16(129) .. string.char(2) .. u16(0)                         -- setwildbattle Magikarp L2
s = s .. string.char(0xB7, 0x27, 0x02)                                                     -- dowildbattle; waitstate; end

local function check(name, ok)
    if ok then passes = passes + 1 else table.insert(fails, name) end
    console:log(string.format("EXPSHARE %s %s", ok and "PASS" or "FAIL", name))
end

callbacks:add("frame", function()
    f = f + 1
    if f == 5 then
        n0 = emu:read8(PARTY_COUNT)
        for i = 1, #s do emu:write8(SCRATCH + i - 1, s:byte(i)) end
        emu:write32(SLOT, SCRATCH)
        emu:write32(CB1, QUEUE)
    end
    local inb = (emu:read8(INBATTLE) >> 1) & 1 == 1
    if battleAt == nil and f > 10 and inb then
        battleAt = f
        console:log("EXPSHARE battle started at frame " .. f .. ", party " .. emu:read8(PARTY_COUNT))
    end
    if battleAt and not endAt then
        if f > battleAt + 60 and f < battleAt + 600 then          -- both battlers are set up by now
            emu:write16(BMONS + 0x58 + 0x28, 1)                   -- wild HP 1
            emu:write16(BMONS + 0x0C, 33); emu:write8(BMONS + 0x24, 35)   -- lead move 1 = Tackle, PP
        end
        if (f - battleAt) % 40 == 0 then emu:addKey(A) elseif (f - battleAt) % 40 == 8 then emu:clearKey(A) end
        if SHOTS and (f - battleAt) % 200 == 0 then emu:screenshot(string.format("%s/%05d.png", SHOTS, f)) end
        if f > battleAt + 120 and not inb then endAt = f; emu:clearKey(A) end
    end
    if not done and ((endAt and f == endAt + 30) or f == 12000) then
        done = true
        local n = emu:read8(PARTY_COUNT)
        local sp1, e1 = expOf(n - 2)
        local sp2, e2 = expOf(n - 1)
        local base = 125   -- Caterpie L5 (medium fast: 5^3)
        console:log(string.format("EXPSHARE party %d->%d lead sp=%d exp=%d bench sp=%d exp=%d (L5 base %d)",
            n0, n, sp1, e1, sp2, e2, base))
        check("the battle started and ended", battleAt ~= nil and endAt ~= nil)
        check("the bench slot is the Caterpie (species 10)", sp2 == 10)
        if EXPECT == "share" then
            check("the benched Caterpie gained Exp. (party-wide share)", e2 > base)
        else
            check("the benched Caterpie gained no Exp. (share off)", e2 == base)
        end
        local want = tonumber(os.getenv("CM_EXPECT_CHECKS") or "3")
        local ran = passes + #fails
        console:log(string.format("EXPSHARE RESULT: %s (%d passed, %d failed, %d ran, want %d)",
            (#fails == 0 and ran == want) and "PASS" or "FAIL", passes, #fails, ran, want))
        os.exit((#fails == 0 and ran == want) and 0 or 1)
    end
end)
