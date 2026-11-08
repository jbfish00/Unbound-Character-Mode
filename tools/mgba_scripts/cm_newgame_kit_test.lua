-- Live layer: QoL C11/C16 starter kit (2026-11-07; src/character_mode.c CharacterMode_NewGameKit, hooked at
-- NewGameInitData's last BL). From a free-roam checkpoint made from a FRESH new game on the same ROM
-- (mk_checkpoint_field.lua; Character Mode answered No), a script is queued through CharacterMode_QueueScriptCb1:
-- checkitem 633 (Shiny Charm) -> 0x8004, checkitem 632 (Oval Charm) -> 0x8005. The Running Shoes flag 0x82F is read.
--   EXPECT=granted -> both items and the flag;  EXPECT=none (the CM_NO_STARTKIT build) -> no items
-- (Unbound's own intro may set 0x82F itself, so the flag is asserted only for "granted".)
local QUEUE = tonumber(os.getenv("QUEUE_CB1"))
local EXPECT = os.getenv("EXPECT") or "granted"
local SCRATCH, SLOT, CB1 = 0x0203FD00, 0x0203B764, 0x030030F0
local VAR8004, VAR8005 = 0x020370C0, 0x020370C2
local f, passes, fails = 0, 0, {}
local function u16(v) return string.char(v & 0xFF, (v >> 8) & 0xFF) end
local function flag(id) return (emu:read8(emu:read32(0x03005008) + 0xEE0 + (id >> 3)) >> (id & 7)) & 1 end
local s = string.char(0x16) .. u16(0x8004) .. u16(0xFFFF) .. string.char(0x16) .. u16(0x8005) .. u16(0xFFFF)
s = s .. string.char(0x47) .. u16(633) .. u16(1) .. string.char(0x19) .. u16(0x8004) .. u16(0x800D)
s = s .. string.char(0x47) .. u16(632) .. u16(1) .. string.char(0x19) .. u16(0x8005) .. u16(0x800D)
s = s .. string.char(0x02)
local function check(name, ok)
    if ok then passes = passes + 1 else table.insert(fails, name) end
    console:log(string.format("KIT %s %s", ok and "PASS" or "FAIL", name))
end
callbacks:add("frame", function()
    f = f + 1
    if f == 5 then
        emu:write16(VAR8004, 0xEEEE); emu:write16(VAR8005, 0xEEEE)
        for i = 1, #s do emu:write8(SCRATCH + i - 1, s:byte(i)) end
        emu:write32(SLOT, SCRATCH)
        emu:write32(CB1, QUEUE)
    end
    if f == 300 then
        local sh, ov, shoes = emu:read16(VAR8004), emu:read16(VAR8005), flag(0x82F)
        console:log(string.format("KIT checkitem 633 -> %d, checkitem 632 -> %d, flag 0x82F -> %d", sh, ov, shoes))
        local want = EXPECT == "granted" and 1 or 0
        check("the queued script ran (0x8004/0x8005 written)", sh ~= 0xEEEE and ov ~= 0xEEEE)
        check("Shiny Charm (633) in the bag = " .. want, sh == want)
        check("Oval Charm (632) in the bag = " .. want, ov == want)
        if EXPECT == "granted" then check("Running Shoes flag 0x82F", shoes == 1) end
        local n = tonumber(os.getenv("CM_EXPECT_CHECKS") or "0")
        if passes + #fails ~= n then table.insert(fails, "TALLY " .. (passes + #fails) .. " want " .. n) end
        console:log("KIT RESULT: " .. (#fails == 0 and "PASS" or ("FAIL " .. table.concat(fails, "; "))))
        os.exit(0)
    end
end)
