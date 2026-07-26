# Live test of the playability-threshold gate (../push_rosters.md §3).
#
# The gate is three script instructions inside the opt-in block:
#     callnative CharacterMode_CheckSelectableNative   (verdict -> var 0x800C)
#     compare_var_to_value 0x800C, 1
#     goto_if NE -> the "not available" branch -> goto back to the number entry
#
# Driving it through the number screen is not workable: sp0B3 is a naming
# screen in number mode, it drops and reorders synthetic key presses, and every
# attempt to type a two-digit id landed on a different number entirely. So the
# harness presets VAR_RESULT and `goto`s straight into the gate, which runs the
# REAL shipped bytes of the REAL block -- only the typing is replaced.
#
# Two cases, chosen by TEST_CASE (hidden | shown):
#   hidden -> must land in the rejection msgbox and must NOT commit the id
#   shown  -> must fall through to the confirm prompt and DOES commit the id
# The shown case is the control: without it, "the script went somewhere other
# than the confirm prompt" would pass for the hidden case even if the gate
# rejected everything, including valid characters.
# Env: MGBA_WID, TEST_CASE.

set confirm off
set pagination off
set remotetimeout 10
target remote localhost:2345

python
import gdb, os, re, json, signal, threading, subprocess, struct

inf = gdb.selected_inferior()
WID = os.environ.get("MGBA_WID", "")
CASE = os.environ.get("TEST_CASE", "hidden")

def rd(addr, n):
    return int.from_bytes(inf.read_memory(addr, n).tobytes(), "little")
def wr(addr, data):
    inf.write_memory(addr, bytes(data))
def reg(name):
    return int(gdb.parse_and_eval(f"${name}")) & 0xFFFFFFFF
def run(sec):
    threading.Timer(sec, lambda: os.kill(os.getpid(), signal.SIGINT)).start()
    try:
        gdb.execute("continue", to_string=True)
    except gdb.error:
        pass

ROOT = "/home/jbfish00/Documents/Character Hacks/Unbound-Character-Mode"
dbg = json.load(open(os.path.join(ROOT, "build", "debug_addrs.json")))
OFF = dbg["optin_offsets"]
BLOCK = dbg["optin_block"]
CB1, CB2 = 0x030030F0, 0x030030F4   # gMain.callback1 / callback2
CB1_OVERWORLD = 0x08056535
FLAG18F8 = 0x0203B373
VAR51FC = 0x0203B76C          # VAR_CHARACTER_ID
VAR800C = None                # resolved below only for reporting

TEST_ID = dbg["gate_hidden_id"] if CASE == "hidden" else dbg["gate_shown_id"]
SCRIPT = dbg["gate_test_script_hidden"] if CASE == "hidden" \
    else dbg["gate_test_script_shown"]
print(f"case: {CASE} (character id {TEST_ID}), gate @ block+{OFF['GATE']}")

def block_pos():
    vals = [rd(0x03000EB8, 4)]
    depth = rd(0x03000EB0, 1)
    for i in range(min(depth, 20)):
        vals.append(rd(0x03000EBC + 4 * i, 4))
    for v in vals:
        if BLOCK <= v < BLOCK + OFF["TEXT"]:
            return v - BLOCK
    return -1

print("phase1: driving the opening (answers No at the CM prompt)...")
exec(open(os.path.join(ROOT, "tools", "test_harness", "intro_drive.py")).read())
drive_intro_to_freeroam()

ok = False
for attempt in range(30):
    cb2 = rd(CB2, 4)
    pc = reg("pc")
    cpsr = reg("cpsr")
    ctx2 = rd(0x03000F9C, 1)
    if (cb2 == 0x080565B5 and ctx2 == 0 and 0x08000000 <= pc < 0x0A000000
            and (cpsr & 0x1F) == 0x1F and (cpsr & 0x20) == 0x20):
        ok = True
        break
    run(4)
print(f"T0 reached hijackable overworld state (want 1): {1 if ok else 0}")

if ok:
    # The intro answered No, so mode must be OFF before the gate runs -- if it
    # were already on, "id not committed" would pass for the wrong reason.
    flag_before = rd(FLAG18F8, 1) & 1
    var_before = rd(VAR51FC, 2)
    print(f"T1 mode off before the gate runs (want 0): {flag_before}")
    print(f"T2 no character committed before the gate (want 0): {var_before}")

    QUEUE_SHIM = int(gdb.parse_and_eval("(unsigned int)CharacterMode_QueueScriptCb1")) & ~1
    wr(0x0203B764, struct.pack("<I", SCRIPT))
    wr(CB1, struct.pack("<I", QUEUE_SHIM | 1))

    # Watch where the script parks. The gate is synchronous, but the branch it
    # takes ends in a msgbox that waits for the player, so sampling over a few
    # seconds is what distinguishes the two outcomes.
    saw_hidden = 0
    saw_confirm = 0
    positions = []
    for step in range(14):
        run(1)
        pos = block_pos()
        if pos >= 0:
            positions.append(pos)
        if pos == OFF["HIDDEN_MSGBOX"]:
            saw_hidden += 1
        if pos == OFF["CONFIRM_YESNO"]:
            saw_confirm += 1
    print(f"info: block positions visited = {sorted(set(positions))}")
    print(f"info: hidden-msgbox samples = {saw_hidden}, confirm samples = {saw_confirm}")

    var_after = rd(VAR51FC, 2)
    flag_after = rd(FLAG18F8, 1) & 1

    if CASE == "hidden":
        # Landed in the rejection branch...
        print(f"T3 rejection msgbox reached (want 1): {1 if saw_hidden else 0}")
        # ...and NOT in the confirm prompt: a hidden character must never get
        # as far as "Play as X?", because that is the point of no return.
        print(f"T4 confirm prompt NOT reached (want 0): {saw_confirm}")
        # ...and the id was never committed to VAR_CHARACTER_ID. This is the
        # assertion that actually protects the save: the copyvar sits AFTER the
        # gate, so a rejected pick must leave the variable untouched.
        print(f"T5 hidden id not committed to VAR_CHARACTER_ID (want 1): "
              f"{1 if var_after != TEST_ID else 0}")
        print(f"T6 mode not enabled by a refused pick (want 0): {flag_after}")
    else:
        # Control: a selectable id must sail through the same gate.
        print(f"T3 confirm prompt reached (want 1): {1 if saw_confirm else 0}")
        print(f"T4 rejection msgbox NOT reached (want 0): {saw_hidden}")
        print(f"T5 selectable id committed to VAR_CHARACTER_ID (want 1): "
              f"{1 if var_after == TEST_ID else 0}")
    print(f"info: VAR_CHARACTER_ID after = {var_after}, flag = {flag_after}")

    healthy = False
    for attempt in range(3):
        run(3)
        pc = reg("pc")
        pc_ok = (pc < 0x4000 or 0x02000000 <= pc < 0x02040000
                 or 0x03000000 <= pc < 0x03008000 or 0x08000000 <= pc < 0x0A000000)
        if pc_ok:
            healthy = True
            break
    print(f"T7 game healthy after the gate (want 1): {1 if healthy else 0}")
end

echo \n=== TESTS DONE ===\n
disconnect
quit
