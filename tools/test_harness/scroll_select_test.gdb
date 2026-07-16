# Live character-list test: inject a minimal script that opens the scrolling
# multichoice on the MAGIC character set (0xFE -> 156 names via our
# trampolined getters), scroll down 3, select, and verify 0x800D == 3.
# Also exercises cancel (B) on a second pass -> 0x800D == 0xFFFF.
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
def reg(name):
    return int(gdb.parse_and_eval(f"(unsigned int)${name}")) & 0xFFFFFFFF
def press(key):
    subprocess.run(f"xdotool keydown --window {WID} {key}", shell=True)
    threading.Timer(0.35, lambda: subprocess.run(
        f"xdotool keyup --window {WID} {key}", shell=True)).start()
    run(0.9)
def shot():
    press("F12")

PARK = int(gdb.parse_and_eval("(unsigned int)CharacterMode_SelfTestDone")) & ~1
REGS = [f"r{i}" for i in range(13)] + ["sp", "lr", "pc", "cpsr"]
SCRATCH = 0x0203FD00

# menu script: magic set, 6 rows, cursor 0 (stale cursor crashes!). A message
# box MUST be on screen first — every ROM usage of special 0x158 shows one,
# and without it the list task crashes. preparemsg+waitmsg shows text and
# lets the script continue without an A-press.
SET_INDEX = int(os.environ.get("SCROLL_SET", "32"), 0)
script = bytearray()
script += bytes([0x67]) + struct.pack("<I", 0x09F1065C)  # preparemsg (any text)
script += bytes([0x66])                                  # waitmsg
script += bytes([0x16]) + struct.pack("<HH", 0x8000, SET_INDEX)
script += bytes([0x16]) + struct.pack("<HH", 0x8001, 6)
script += bytes([0x16]) + struct.pack("<HH", 0x8004, 0)
script += bytes([0x25]) + struct.pack("<H", 0x158)
script += bytes([0x27])                                  # waitstate
script += bytes([0x68])                                  # closemessage
script += bytes([0x02])                                  # end

SHIM = 0x0203FC00
CB1 = 0x030030F0          # gMain.callback1 — invoked every frame via bx
SETUP = 0x08069AE4

def inject():
    # Deterministic script queuing WITHOUT touching pc/registers (direct
    # `set $pc` hijacks flake — the stub sometimes drops Thumb state).
    # A Thumb shim in EWRAM becomes gMain.callback1 for exactly one frame:
    # it restores the original callback1, loads r0 = script, and tail-calls
    # ScriptContext1_SetupScript; the game itself enters it via bx with
    # correct interworking.
    #   ldr r3,=0x030030F0 ; ldr r2,=orig_cb1 ; str r2,[r3]
    #   ldr r0,=script     ; ldr r1,=Setup|1  ; bx r1
    orig_cb1 = rd(CB1, 4)
    if not (0x08000000 <= orig_cb1 < 0x0A000000 and (orig_cb1 & 1)):
        print(f"  inject: callback1 not hijackable (0x{orig_cb1:08x})")
        return False
    wr(SCRATCH, script)
    shim = struct.pack("<6H", 0x4B03, 0x4A04, 0x601A, 0x4804, 0x4904, 0x4708)
    shim += b"\x00\x00\x00\x00"  # pad to pool at +16
    shim += struct.pack("<4I", CB1, orig_cb1, SCRATCH, SETUP | 1)
    wr(SHIM, shim)
    wr(CB1, struct.pack("<I", SHIM | 1))
    run(2)   # one frame is enough; run a couple of seconds
    cb1_now = rd(CB1, 4)
    sptr = rd(0x03000EB8, 4)   # sScriptContext1.scriptPtr
    okq = (cb1_now == orig_cb1)
    print(f"  inject: cb1 restored={okq} scriptPtr=0x{sptr:08x}")
    return okq

print("phase1: playing through opening...")
run(170)
# phase 1.5: keep advancing dialogue until true free-roam. The overworld cb2
# alone is NOT enough — the opening cutscene runs under it too; the real
# "player has control" signal is sScriptContext2Enabled == 0 (0x03000F9C).
ok = False
for attempt in range(70):
    cb2 = rd(0x030030F4, 4)
    pc = reg("pc")
    cpsr = reg("cpsr")
    ctx2 = rd(0x03000F9C, 1)
    if (cb2 == 0x080565B5 and ctx2 == 0
            and 0x08000000 <= pc < 0x0A000000
            and (cpsr & 0x1F) == 0x1F and (cpsr & 0x20) == 0x20):
        ok = True
        break
    press("x")      # advance whatever script/cutscene is still running
    run(2.0)
print(f"M0 hijackable free-roam (want 1): {1 if ok else 0}")

def task_dump():
    # gTasks @0x03005090, 16 entries, stride 40: func u32 @+0, isActive @+4
    act = []
    for i in range(16):
        f = rd(0x03005090 + 40*i, 4)
        a = rd(0x03005090 + 40*i + 4, 1)
        if a:
            act.append(f"{i}:0x{f:08x}")
    print(f"  active tasks: {act}")

if ok:
    q = inject()
    print(f"M1 menu script queued (want 1): {1 if q else 0}")
    run(4)              # menu draws
    print(f"  post-menu-open pc=0x{reg('pc'):08x}")
    task_dump()
    # key-delivery sanity: hold START (inert in list menus) and verify the
    # game polls it (gMain.heldKeysRaw bit 3)
    subprocess.run(f"xdotool windowfocus --sync {WID}", shell=True)
    subprocess.run(f"xdotool keydown --window {WID} q", shell=True)
    run(1.0)
    held = rd(0x03003118, 2)
    subprocess.run(f"xdotool keyup --window {WID} q", shell=True)
    run(0.5)
    print(f"MK key delivery live (want 1): {(held >> 3) & 1}")
    shot()              # should show the first 6 character names
    import os.path
    print(f"MS screenshot saved (want 1): {1 if os.path.exists('/home/jbfish00/Documents/Character Hacks/Unbound-Character-Mode/build/unbound-cm-0.png') else 0}")
    press("k"); press("k"); press("k")   # scroll to index 3
    shot()
    press("x")          # select
    run(2)
    sel = rd(0x020370D0, 2)
    print(f"M2 selection index (want 3): {sel}")
    run(2)

    q = inject()
    print(f"M3 second menu queued (want 1): {1 if q else 0}")
    run(4)
    press("z")          # cancel
    run(2)
    sel = rd(0x020370D0, 2)
    print(f"M4 cancel result (want 65535): {sel}")
    # game still alive?
    vb1 = rd(0x03003114, 4)
    run(4)
    vb2 = rd(0x03003114, 4)
    print(f"M5 game alive (want 1): {1 if vb2 > vb1 else 0}")
    shot()

print("=== TESTS DONE ===")
end

disconnect
quit
