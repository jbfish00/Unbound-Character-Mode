# LIVE PC-exit e2e (../game_plans/rowe_parity.md §13.33 item 1).
#
# The PC-exit hook shipped in all four GBA games on STATIC evidence alone.
# Seaglass got the first live layer on 2026-09-10, Radical Red and Lazarus
# followed, and this is the port to the one repo with no Lua harness at all --
# here it is GDB over the mGBA stub, the same primitives trade_test.gdb uses.
# §13.20 is why it matters: four live layers in three repos were once found dead
# behind a fully green static suite.
#
# The fixture is baked into the ROM by tools/build_patch.py (pc_debug_script):
# with Character Mode OFF, givemon Pikachu (the keeper) + Hitmontop (the mon
# under test); then setflag CM, setvar the character, and `goto 0x081A6A22` --
# the REAL PC access script, with the shipped splice. Everything from that goto
# on is shipped: the overlay, the replayed special 0x3C + waitstate that opens
# the storage system and waits for it to close, and the sweep that runs when it
# does.
#
# ⚠️ The keeper is not decoration: CharacterMode_SweepPartyToPC never empties the
# party, so with Hitmontop alone it would be kept for EVERY character and the two
# cases would be identical -- green, discriminating nothing.
# ⚠️ And the mode is OFF for the givemons on purpose: an off-roster gift is
# PC-routed on the way in, so with the mode already on Hitmontop would never
# reach the party and there would be nothing to sweep.
#
# Case selected by env PC_CASE:
#   swept (character DERIVED at build time): Hitmontop off-roster -> boxed when
#          the PC closes. Party ends [Pikachu]; 237 present in PC storage.
#   stays (character DERIVED at build time): Hitmontop on-roster  -> kept.
#          Party ends [Pikachu, Hitmontop]; 237 NOT in PC storage.
#
# ⭐ T2b IS WHAT MAKES THIS A PC TEST AT ALL. It presses NOTHING for two seconds
# after the script is queued and requires the script context to still be WAITING
# -- held open by a menu only input can dismiss. If `special 0x3C` did nothing,
# its waitstate would release on the next frame, the sweep would still run, and
# every other check here would pass while no PC had ever been involved.
# ⚠️ It deliberately does NOT test gMain.callback2: `special 0x3C` opens a FIELD
# MULTICHOICE over the live map here, not a full-screen takeover, so CB2 never
# moves. See the note at the check itself.

set confirm off
set pagination off
set remotetimeout 10
target remote localhost:2345

python
import gdb, os, signal, threading, struct, json

inf = gdb.selected_inferior()
ROOT = "/home/jbfish00/Documents/Character Hacks/Unbound-Character-Mode"

def rd(addr, n):
    return int.from_bytes(inf.read_memory(addr, n).tobytes(), "little")
def rdbuf(addr, n):
    return inf.read_memory(addr, n).tobytes()
def wr(addr, data):
    inf.write_memory(addr, bytes(data))
def run(sec):
    threading.Timer(sec, lambda: os.kill(os.getpid(), signal.SIGINT)).start()
    try:
        gdb.execute("continue", to_string=True)
    except gdb.error:
        pass
def reg(name):
    return int(gdb.parse_and_eval(f"(unsigned int)${name}")) & 0xFFFFFFFF

CASE = os.environ.get("PC_CASE", "swept")

PARTY = 0x02024284      # gPlayerParty, stride 100, species u16 at +0x20
PARTY_COUNT = 0x02024029
CB1 = 0x030030F0
CB2 = 0x030030F4
CB1_OVERWORLD = 0x08056535
CB2_OVERWORLD = 0x080565B5
CTX2 = 0x03000F9C       # sScriptContext2Enabled: 0 = no script running
STORAGE_PTR = 0x03005010

def party_species(i):
    return rd(PARTY + 100 * i + 0x20, 2)

def pc_box_has(species, boxes=14):
    storage = rd(STORAGE_PTR, 4)
    if not (0x02000000 <= storage < 0x02040000):
        return -1
    buf = rdbuf(storage, boxes * 30 * 80)
    for slot in range(boxes * 30):
        if struct.unpack_from("<H", buf, slot * 80 + 0x20)[0] == species:
            return 1
    return 0

_dbg0 = json.load(open(ROOT + "/build/debug_addrs.json"))
print(f"case: {CASE} (character: {_dbg0.get('pc_test_' + CASE + '_char', '?')})")
print("phase1: driving the opening (answers No at the CM prompt)...")
exec(open(ROOT + "/tools/test_harness/intro_drive.py").read())
drive_intro_to_freeroam()

ok = False
for attempt in range(30):
    cb2 = rd(CB2, 4)
    pc = reg("pc")
    cpsr = reg("cpsr")
    ctx2 = rd(CTX2, 1)
    if (cb2 == CB2_OVERWORLD and ctx2 == 0 and 0x08000000 <= pc < 0x0A000000
            and (cpsr & 0x1F) == 0x1F and (cpsr & 0x20) == 0x20):
        ok = True
        break
    run(4)
print(f"T0 reached hijackable overworld state (want 1): {1 if ok else 0}")

if ok:
    print(f"T1 party empty before test (want 1): {1 if party_species(0) == 0 else 0}")

    dbg = json.load(open(ROOT + "/build/debug_addrs.json"))
    script_addr = dbg[f"pc_test_script_{CASE}"]
    QUEUE_SHIM = int(gdb.parse_and_eval("(unsigned int)CharacterMode_QueueScriptCb1")) & ~1
    wr(0x0203B764, struct.pack("<I", script_addr))
    wr(CB1, struct.pack("<I", QUEUE_SHIM | 1))

    # ⭐ PHASE A -- LET THE PC OPEN WITH NO INPUT AT ALL, AND WATCH THE SCRIPT
    # STAY BLOCKED. This is what makes the layer a PC test rather than a
    # "something ran" test: if `special 0x3C` were a no-op, its `waitstate`
    # would release on the very next frame, the sweep would run, the script
    # would finish, and every roster assertion below would pass with no PC ever
    # involved. So press nothing for two seconds and require the script context
    # to still be WAITING -- held open by a menu only input can dismiss.
    #
    # ⚠️⚠️ AND DO NOT USE gMain.callback2 FOR THIS. The first version did, on the
    # assumption that the storage system is a full CB2 takeover. It is not: in
    # this engine `special 0x3C` opens a FIELD MULTICHOICE drawn over the live
    # map (Withdraw / Deposit / Move / Move Items / See Ya!), so CB2 stays the
    # overworld callback the whole time. Measured here: 23 consecutive polls with
    # cb2 = 0x080565B5, ctx2 = 1, party already [Pikachu, Hitmontop] -- the
    # script plainly blocked, while the CB2 check read 0 and called it a
    # no-op. CB2 only moves if a submenu is entered, which this layer never does.
    #
    # ⚠️ The masher must also stay asleep until phase A is over. Woken with the
    # script (as the trade test does), B is already being pressed when the menu
    # appears, the menu is dismissed inside one poll, and the window this layer
    # exists to observe never happens.
    blocked = 0
    saw_other_cb2 = 0
    other_cb2 = 0
    for attempt in range(8):
        run(0.25)
        cb2now = rd(CB2, 4)
        if cb2now != CB2_OVERWORLD and 0x08000000 <= cb2now < 0x0A000000:
            saw_other_cb2 = 1
            other_cb2 = cb2now
    blocked = 1 if (rd(CTX2, 1) == 1 and rd(PARTY_COUNT, 1) == 2) else 0
    print(f"T2b the PC held the script open with no input (want 1): {blocked}  "
          f"[ctx2={rd(CTX2,1)} count={rd(PARTY_COUNT,1)} cb2={rd(CB2,4):#010x} "
          f"other_cb2={other_cb2:#010x}]")

    # PHASE B -- now wake the driver's masher to close it. ⚠️ It presses B, not
    # A: B backs out of the storage system, where A would dive INTO a box with
    # no scripted route back.
    open(ROOT + "/build/.mash_now", "w").close()

    # Poll to completion while the masher closes the PC.
    #   saw_other_cb2 -- the storage system is a full CB2 takeover, so if the PC
    #                    really opened, gMain.callback2 must leave the overworld
    #                    callback at some point. A no-op special would never
    #                    show one.
    #   keys_seen     -- proves input is actually reaching the emulator. If the
    #                    masher dies (the classic: the runner invoked with `sh`,
    #                    so $SECONDS is unset under set -u), the PC simply stays
    #                    open forever and every check below fails in a way that
    #                    looks like a broken ROM. Assert the input path.
    def scene_done():
        return (rd(CTX2, 1) == 0 and rd(CB2, 4) == CB2_OVERWORLD
                and rd(PARTY_COUNT, 1) != 0)

    # keys_seen proves input actually reached the emulator. If the masher dies
    # (the classic: the runner invoked with `sh`, so $SECONDS is unset under
    # set -u), the menu simply stays open forever and every check below fails in
    # a way that looks like a broken ROM. Assert the input path, don't assume it.

    # ⚠️ Poll FINELY here. heldKeysRaw is transient -- it reads whatever is down
    # at the instant the stub halts -- and the menu closes on the FIRST press, so
    # there is exactly one press to catch. Sampling every 2 s (which is what the
    # trade test does, where the scene lasts ~40 s and takes dozens of presses)
    # missed it every time and reported a dead input path on a run that plainly
    # had one.
    done = False
    keys_seen = 0
    for attempt in range(200):
        run(0.25)
        keys_seen |= rd(0x03003118, 2)
        if scene_done():
            done = True
            break
    # ⚠️ "key bits seen" is worded so the tally regex COUNTS it: the pattern
    # anchors on a literal "(want", and the trade test's version of this line
    # reads "(key bits seen, want 1)" -- which silently sits outside its own
    # layer's tally.
    print(f"T2a input path alive, key bits seen (want 1): "
          f"{1 if keys_seen else 0}  [{keys_seen:#06x}]")
    if not done:
        print(f"diag stuck: cb1={rd(CB1,4):#010x} cb2={rd(CB2,4):#010x} "
              f"ctx2={rd(CTX2,1)} heldRaw={rd(0x03003118,2):#06x} "
              f"newKeys={rd(0x0300311E,2):#06x} count={rd(PARTY_COUNT,1)}")
    open(ROOT + "/build/.pc_done", "w").close()
    print(f"T2 PC opened and closed again (want 1): {1 if done else 0}")

    sp0 = party_species(0)
    sp1 = party_species(1)
    cnt = rd(PARTY_COUNT, 1)
    in_pc = pc_box_has(237)
    print(f"diag: party=[{sp0},{sp1}] count={cnt} hitmontop_in_pc={in_pc}")
    print(f"T3 party[0] is Pikachu, the keeper (want 1): {1 if sp0 == 25 else 0}")
    if CASE == "swept":
        print(f"T4 party count post-sweep (want 1): {cnt}")
        print(f"T5 off-roster Hitmontop out of party (want 1): {1 if sp1 == 0 else 0}")
        print(f"T6 Hitmontop delivered to PC storage (want 1): {1 if in_pc == 1 else 0}")
    else:
        print(f"T4 party count control (want 2): {cnt}")
        print(f"T5 on-roster Hitmontop stays in party (want 1): {1 if sp1 == 237 else 0}")
        print(f"T6 Hitmontop not PC-routed (want 1): {1 if in_pc == 0 else 0}")

    healthy = False
    for attempt in range(3):
        run(3)
        cb1 = rd(CB1, 4)
        cb2 = rd(CB2, 4)
        pc = reg("pc")
        pc_ok = (pc < 0x4000 or 0x02000000 <= pc < 0x02040000
                 or 0x03000000 <= pc < 0x03008000 or 0x08000000 <= pc < 0x0A000000)
        if cb1 == CB1_OVERWORLD and cb2 == CB2_OVERWORLD and pc_ok:
            healthy = True
            break
        print(f"diag: health retry cb1={cb1:08x} cb2={cb2:08x} pc={pc:08x}")
    print(f"T7 game healthy after test (want 1): {1 if healthy else 0}")
end

echo \n=== TESTS DONE ===\n
disconnect
quit
