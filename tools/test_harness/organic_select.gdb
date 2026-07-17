# Full organic character-select test (gold path): on a FRESH save, drive the
# real new-game intro with verified key presses — Welcome speech, appearance,
# player naming, questionnaire, difficulty — until the game's own flow
# reaches the Character Mode block (new splice at the checkflag gate,
# 0x1E6FF2D), then: Yes -> type '1' on ChooseNumberScreen -> confirm Yes ->
# assert flag 0x18F8 + var 0x51FC set BY THE ORGANIC FLOW, then keep playing
# and assert the intro continues to the overworld with mode intact.
#
# Supersedes number_select_test.gdb (whose 0x09E70000 entry no longer
# carries the prompt after the splice moved to the first-run gate).
# Env: MGBA_WID.

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

KEYMASK = {"x": 1, "z": 2, "n": 4, "q": 8, "l": 0x10, "j": 0x20, "i": 0x40, "k": 0x80}
def press(key):
    m = KEYMASK[key]
    for attempt in range(3):
        subprocess.run(f"xdotool keydown --window {WID} {key}", shell=True)
        run(0.25)
        held = rd(0x03003118, 2)
        if held & m:
            run(0.25)
            subprocess.run(f"xdotool keyup --window {WID} {key}", shell=True)
            run(0.5)
            return True
        subprocess.run(f"xdotool keyup --window {WID} {key}", shell=True)
        subprocess.run(f"xdotool windowfocus --sync {WID}", shell=True)
        run(0.2)
    b = struct.pack("<H", m)
    wr(0x0300311A, b)   # gMain.newKeysRaw
    wr(0x0300311E, b)   # gMain.newKeys
    wr(0x03003120, b)   # gMain.newAndRepeatedKeys
    run(0.8)
    return False
def shot():
    subprocess.run(f"xdotool key --window {WID} F12", shell=True)
    run(0.3)

TYPE_SENTINEL = "/home/jbfish00/Documents/Character Hacks/Unbound-Character-Mode/build/.type_now"
BLOCK = rd(0x09E6FF2E, 4)          # call target baked into the new splice
BREADCRUMB = 0x0203B768            # var 0x51FA (0xCA11 once block entered)
FLAG18F8 = 0x0203B373
VAR51FC = 0x0203B76C
CTX2 = 0x03000F9C
CB2 = 0x030030F4
VBLANK = 0x03003114
OVERWORLD_CB2 = 0x080565B5

def block_pos():
    vals = [rd(0x03000EB8, 4)]
    depth = rd(0x03000EB0, 1)
    for i in range(min(depth, 20)):
        vals.append(rd(0x03000EBC + 4*i, 4))
    for v in vals:
        if BLOCK <= v < BLOCK + 130:
            return v - BLOCK
    return -1

print(f"block @ 0x{BLOCK:08x}")
print("phase1: driving the intro to the Character Mode prompt...")

# blind-drive the pre-questionnaire intro (title, speech, appearance, player
# naming — mash-A escapes the naming screen via buffer-full -> OK)
reached = False
for step in range(120):
    press("x")
    if step % 15 == 0:
        shot()
    if block_pos() >= 0 or rd(BREADCRUMB, 2) == 0xCA11:
        reached = True
        break
print(f"G1 organic flow entered the CM block (want 1): {1 if reached else 0}")

typed = 0
done = False
if reached:
    # state-machine drive inside the block (offsets: layout in optin_script.py)
    #   13  parked in opt-in yesno            -> A (Yes)
    #   32  parked in number-prompt msgbox    -> A
    #   36  parked on waitstate: ChooseNumberScreen up -> right,'1',Start,OK
    #   85  parked in confirm yesno           -> A (Yes)
    #  107  parked in enabled msgbox          -> A
    for step in range(60):
        pos = block_pos()
        if step % 5 == 0:
            print(f"  step {step:02d}: pos={pos} flag={rd(FLAG18F8,1)&1} var={rd(VAR51FC,2)}")
        if pos == 36:
            # The naming screen mishandles gdb-sliced key presses (keys
            # register in heldKeysRaw but the screen ignores/garbles them —
            # SIGINT stop/resume around each press breaks its input timing).
            # So: signal the driver script's background typer and run one
            # long UNINTERRUPTED continue while it presses l,x,q,x with
            # clean wall-clock timing.
            open(TYPE_SENTINEL, "w").close()
            print(f"  typing round {typed}: handed to wall-clock typer")
            typed += 1
            run(14)
            shot()
        elif pos < 0:
            if rd(FLAG18F8, 1) & 1:
                done = True
                break
            press("x")      # not in block (yet/anymore): advance
        else:
            press("x")      # any open msgbox/yesno in the block: A
        if typed > 4:
            break           # wedged in the validation loop — bail to asserts
    flag = rd(FLAG18F8, 1) & 1
    var = rd(VAR51FC, 2)
    crumb = rd(BREADCRUMB, 2)
    shot()
    print(f"G2 mode enabled by the organic flow (want 1): {flag}")
    print(f"info: chosen character id = {var}, typed rounds = {typed}")
    print(f"G3 character id valid 1-156 (want 1): {1 if 1 <= var <= 156 else 0}")

    # keep playing: the intro must continue (story cutscene) and reach the
    # overworld with the mode state intact
    alive_ok = False
    for step in range(180):
        press("x")
        if step % 20 == 0:
            shot()
        if rd(CTX2, 1) == 0 and rd(CB2, 4) == OVERWORLD_CB2:
            alive_ok = True
            break
    flag2 = rd(FLAG18F8, 1) & 1
    var2 = rd(VAR51FC, 2)
    print(f"G4 intro continued to overworld (want 1): {1 if alive_ok else 0}")
    print(f"G5 mode state intact at overworld (want 1): {1 if (flag2 == flag and var2 == var) else 0}")
    vb1 = rd(VBLANK, 4)
    run(4)
    vb2 = rd(VBLANK, 4)
    print(f"G6 game alive (want 1): {1 if vb2 > vb1 else 0}")
end

echo \n=== TESTS DONE ===\n
disconnect
quit
