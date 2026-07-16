# Live catch-gate test, phase A (exploratory): reach free-roam, inject a
# debug script into EWRAM scratch (0x0203FD00) that enables Character Mode
# (Red), grants a Pikachu + Master Balls, and forces a wild Mewtwo battle.
# Then advance dialogs and capture screenshots of the battle menu so the
# ball-throw key sequence can be learned.
#
# The EWRAM script-injection primitive: the script engine follows any
# addressable pointer, so poking bytecode into scratch RAM + one hijacked
# ScriptContext1_SetupScript call = run arbitrary script without a rebuild
# (the binary-hack equivalent of ROWE's debug menu).
#
# Env: MGBA_WID = mgba-qt X window id (for key presses / F12 screenshots).

set confirm off
set pagination off
set remotetimeout 10
target remote localhost:2345

python
import gdb, os, signal, threading, subprocess, struct

inf = gdb.selected_inferior()
WID = os.environ.get("MGBA_WID", "")

def rd(addr, n):
    return int.from_bytes(inf.read_memory(addr, n).tobytes(), "little")
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
def press(key):
    subprocess.run(f"xdotool keydown --window {WID} {key}", shell=True)
    # target must be RUNNING to poll the key: hold it across a short run
    threading.Timer(0.35, lambda: subprocess.run(
        f"xdotool keyup --window {WID} {key}", shell=True)).start()
    run(0.8)
def shot():
    press("F12")

TRIG = int(gdb.parse_and_eval("(unsigned int)CharacterMode_TriggerIntroScript")) & ~1
PARK = int(gdb.parse_and_eval("(unsigned int)CharacterMode_SelfTestDone")) & ~1
REGS = [f"r{i}" for i in range(13)] + ["sp", "lr", "pc", "cpsr"]
SCRATCH = 0x0203FD00
INBATTLE = 0x03003529   # gMain + 0x439, bit 1

# debug script: zero move-override vars, enable Character Mode as Red,
# 10 Master Balls, give Pikachu lvl 5, wild Mewtwo lvl 5
script = bytearray()
for v in range(0x8000, 0x8008):
    script += bytes([0x16]) + struct.pack("<HH", v, 0)      # setvar v, 0
script += bytes([0x29]) + struct.pack("<H", 0x18F8)         # setflag
script += bytes([0x16]) + struct.pack("<HH", 0x51FC, 1)     # setvar char=Red
script += bytes([0x44]) + struct.pack("<HH", 1, 10)         # additem MASTER_BALL x10
script += bytes([0x79]) + struct.pack("<HBH", 25, 30, 0) + b"\x00" * 9  # givemon Pikachu L30
TEST_SPECIES = int(os.environ.get("TEST_SPECIES", "150"))   # default wild Mewtwo
TEST_WANT = os.environ.get("TEST_WANT", "block")            # block | catch
script += bytes([0xB6]) + struct.pack("<HBH", TEST_SPECIES, 5, 0)  # setwildbattle
script += bytes([0xB7, 0x27, 0x02])                         # dowildbattle; waitstate; end

print("phase1: playing through opening...")
run(170)

ok = False
for attempt in range(30):
    cb2 = rd(0x030030F4, 4)
    pc = reg("pc")
    cpsr = reg("cpsr")
    ctx2 = rd(0x03000F9C, 1)   # sScriptContext2Enabled: 0 = player has control
    if (cb2 == 0x080565B5 and ctx2 == 0 and 0x08000000 <= pc < 0x0A000000
            and (cpsr & 0x1F) == 0x1F and (cpsr & 0x20) == 0x20):
        ok = True
        break
    run(4)
print(f"B0 reached hijackable overworld state (want 1): {1 if ok else 0}")

if ok:
    wr(SCRATCH, script)
    # patch the trigger's script pointer: TriggerIntroScript loads 0x09E70000;
    # easier to just call SetupScript ourselves through the same trampoline?
    # No — reuse the trigger but override r0 AFTER the jump is not possible;
    # instead: set pc to SetupScript directly with r0=SCRATCH and lr=park.
    saved = {r: reg(r) for r in REGS}
    SETUP = 0x08069AE4
    gdb.execute(f"set $r0 = {SCRATCH}")
    gdb.execute(f"set $lr = {PARK | 1}")
    gdb.execute(f"set $pc = {SETUP}")
    run(3)
    pc = reg("pc")
    parked = PARK <= pc < PARK + 8
    print(f"B1 script queued (want 1): {1 if parked else 0}")
    for r in REGS:
        gdb.execute(f"set ${r} = {saved[r]}")

    # advance the givemon fanfare/messages with A, watching for battle start
    inb = 0
    for i in range(30):
        press("x")
        run(1.2)
        inb = (rd(INBATTLE, 1) >> 1) & 1
        if inb:
            break
    print(f"B2 wild battle started (want 1): {inb}")

    if inb:
        run(8)          # battle intro animation
        battle_cb2 = rd(0x030030F4, 4)
        # open the battle bag: poke the action cursor onto BAG (index 1) and
        # press A; retries self-correct through message boxes and stray turns
        opened = False
        for t in range(15):
            wr(0x02023FF8, b"\x01")     # gActionSelectionCursor[0] = BAG
            press("x")
            run(2)
            if rd(0x030030F4, 4) != battle_cb2:
                opened = True
                break
        print(f"B3 battle bag opened (want 1): {1 if opened else 0}")
        # confound check BEFORE throwing: is the game's own no-catching state
        # active in this story section? (would fake a "blocked" result)
        nc = rd(0x0203B193, 1) & 1            # FLAG_NO_CATCHING 0x9F8 (expanded)
        sb1 = rd(0x03005008, 4)               # FLAG_NO_CATCHING_AND_RUNNING 0x8E2
        ncr = (rd(sb1 + 0xEE0 + (0x8E2 >> 3), 1) >> (0x8E2 & 7)) & 1 \
            if 0x02000000 <= sb1 < 0x02040000 else 9
        print(f"B4 game's own FLAG_NO_CATCHING clear (want 0): {nc}")
        print(f"B5 FLAG_NO_CATCHING_AND_RUNNING clear (want 0): {ncr}")
        shot()
        # pockets cycle right: Items -> Key Items -> Poke Balls
        press("l"); run(1)
        press("l"); run(1); shot()
        press("x"); run(2); shot()   # select Master Ball -> context menu
        press("x"); run(2)           # Use -> throw
        run(12)                      # throw + dodge/shake/caught animation
        shot()
        if TEST_WANT == "block":
            press("x"); run(3)
            inb2 = (rd(INBATTLE, 1) >> 1) & 1
            pcount = rd(0x02024029, 1)
            outcome = rd(0x02023E8A, 1)
            print(f"info: inBattle={inb2} partyCount={pcount} outcome={outcome}")
            print(f"B6 still in battle after Master Ball vs {TEST_SPECIES} (want 1): {inb2}")
            print(f"B7 party count still 1 = NOT caught (want 1): {1 if pcount == 1 else 0}")
        else:
            # the caught mon joins the party only at the END of the catch
            # message chain (Gotcha -> exp -> dex -> nickname prompt); drive
            # it with A (advance) and B (decline nickname) while polling
            # Start+A escapes the naming screen if the nickname prompt got a
            # Yes; on plain messages Start is a no-op and A advances
            caught = 0
            for t in range(20):
                press("q"); run(1.2)
                press("x"); run(1.5)
                pcount = rd(0x02024029, 1)
                inb2 = (rd(INBATTLE, 1) >> 1) & 1
                outcome = rd(0x02023E8A, 1)
                if pcount == 2 or outcome == 7 or not inb2:
                    break
            caught = 1 if (pcount == 2 or outcome == 7) else 0
            print(f"info: inBattle={inb2} partyCount={pcount} outcome={outcome}")
            print(f"B6 Master Ball caught species {TEST_SPECIES} (want 1): {caught}")
            sp1 = rd(0x02024284 + 100 + 0x20, 2)
            print(f"B7 party[1] species (info): {sp1}")
        flag = rd(0x0203B373, 1) & 1
        print(f"B9 character mode on (want 1): {flag}")
        shot()

print("=== TESTS DONE ===")
end

disconnect
quit
