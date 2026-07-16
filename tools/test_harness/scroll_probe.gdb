# Empirical probe of special 0x158 (CFRU scrolling multichoice): invoke it
# on Unbound's own set 0 from an injected script, scroll+select, and find
# where the result var lands (and the cancel value). One-off diagnostic.

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
def vars_snapshot():
    return [rd(0x020370B8 + 2*i, 2) for i in range(16)]   # vars 0x8000-0x800F

PARK = int(gdb.parse_and_eval("(unsigned int)CharacterMode_SelfTestDone")) & ~1
REGS = [f"r{i}" for i in range(13)] + ["sp", "lr", "pc", "cpsr"]
SCRATCH = 0x0203FD00

# script: set0, 6 rows, scrolling multichoice, waitstate, end
script = bytearray()
script += bytes([0x16]) + struct.pack("<HH", 0x8000, 0)
script += bytes([0x16]) + struct.pack("<HH", 0x8001, 6)
script += bytes([0x25]) + struct.pack("<H", 0x158)
script += bytes([0x27, 0x02])

print("phase1: playing through opening...")
run(170)
ok = False
for attempt in range(30):
    cb2 = rd(0x030030F4, 4)
    pc = reg("pc")
    cpsr = reg("cpsr")
    if (cb2 == 0x080565B5 and 0x08000000 <= pc < 0x0A000000
            and (cpsr & 0x1F) == 0x1F and (cpsr & 0x20) == 0x20):
        ok = True
        break
    run(4)
print(f"S0 hijackable (want 1): {1 if ok else 0}")

if ok:
    wr(SCRATCH, script)
    saved = {r: reg(r) for r in REGS}
    gdb.execute(f"set $r0 = {SCRATCH}")
    gdb.execute(f"set $lr = {PARK | 1}")
    gdb.execute("set $pc = 0x08069AE4")
    run(3)
    parked = PARK <= reg("pc") < PARK + 8
    print(f"S1 queued (want 1): {1 if parked else 0}")
    for r in REGS:
        gdb.execute(f"set ${r} = {saved[r]}")

    run(4)              # let the menu appear
    shot()              # what does set 0 look like?
    pre = vars_snapshot()
    print("vars pre-select: ", [hex(v) for v in pre])
    press("k")          # scroll down 2
    press("k")
    shot()
    press("x")          # select entry index 2
    run(3)
    shot()
    post = vars_snapshot()
    print("vars post-select:", [hex(v) for v in post])
    for i, (a, b) in enumerate(zip(pre, post)):
        if a != b:
            print(f"  var 0x{0x8000+i:04X} changed 0x{a:04x} -> 0x{b:04x}")

    # second pass: cancel semantics
    wr(SCRATCH, script)
    saved = {r: reg(r) for r in REGS}
    gdb.execute(f"set $r0 = {SCRATCH}")
    gdb.execute(f"set $lr = {PARK | 1}")
    gdb.execute("set $pc = 0x08069AE4")
    run(3)
    for r in REGS:
        gdb.execute(f"set ${r} = {saved[r]}")
    run(4)
    pre = vars_snapshot()
    press("z")          # B = cancel
    run(3)
    shot()
    post = vars_snapshot()
    print("vars post-cancel:", [hex(v) for v in post])
    for i, (a, b) in enumerate(zip(pre, post)):
        if a != b:
            print(f"  var 0x{0x8000+i:04X} changed 0x{a:04x} -> 0x{b:04x}")

print("=== TESTS DONE ===")
end

disconnect
quit
