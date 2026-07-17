# Flag-persistence test, phase A (save): drive a fresh save to free-roam
# (intro_drive answers No at the CM prompt), set Character Mode state
# directly in the CFRU expanded-save EWRAM (flag 0x18F8 bit, var 0x51FC=42,
# var 0x51FA=0x1234 as a second sentinel), then hijack the CPU to vanilla
# FR TrySavingData(SAVE_NORMAL) (0x080DA364, BPRE.ld) with lr parked at
# CharacterMode_SelfTestDone, verify the save completed undamaged, restore
# registers. Phase B (persistence_load.gdb) reboots and checks the state
# survived the load.

set confirm off
set pagination off
set remotetimeout 10
target remote localhost:2345

python
import gdb, os, signal, threading, struct

inf = gdb.selected_inferior()
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

TRYSAVE = 0x080DA364            # vanilla TrySavingData (BPRE.ld)
PARK = int(gdb.parse_and_eval("(unsigned int)CharacterMode_SelfTestDone")) & ~1
REGS = [f"r{i}" for i in range(13)] + ["sp", "lr", "pc", "cpsr"]

FLAGBYTE = 0x0203B373           # byte holding flag 0x18F8 (bit 0)
VAR51FC = 0x0203B76C
VAR51FA = 0x0203B768

print("phase1: driving the opening (answers No at the CM prompt)...")
exec(open("/home/jbfish00/Documents/Character Hacks/Unbound-Character-Mode/tools/test_harness/intro_drive.py").read())
drive_intro_to_freeroam()

ok = False
for attempt in range(30):
    cb2 = rd(0x030030F4, 4)
    pc = reg("pc")
    cpsr = reg("cpsr")
    ctx2 = rd(0x03000F9C, 1)
    if (cb2 == 0x080565B5 and ctx2 == 0 and 0x08000000 <= pc < 0x0A000000
            and (cpsr & 0x1F) == 0x1F and (cpsr & 0x20) == 0x20):
        ok = True
        break
    run(4)
print(f"P0 reached hijackable overworld state (want 1): {1 if ok else 0}")

if ok:
    # set Character Mode state in the expanded-save EWRAM regions
    wr(FLAGBYTE, bytes([rd(FLAGBYTE, 1) | 1]))
    wr(VAR51FC, struct.pack("<H", 42))
    wr(VAR51FA, struct.pack("<H", 0x1234))
    print(f"P1 state set (flag/var/sentinel) (want 1): "
          f"{1 if (rd(FLAGBYTE,1)&1)==1 and rd(VAR51FC,2)==42 and rd(VAR51FA,2)==0x1234 else 0}")

    # hijack: TrySavingData(SAVE_NORMAL=0), return into the park loop
    saved = {r: reg(r) for r in REGS}
    gdb.execute("set $r0 = 0")
    gdb.execute(f"set $lr = {PARK + 1}")
    gdb.execute(f"set $pc = {TRYSAVE}")
    parked = False
    for attempt in range(5):
        run(4)
        pc = reg("pc")
        if PARK <= pc < PARK + 8:
            parked = True
            break
    print(f"P2 save call parked cleanly (want 1): {1 if parked else 0}")
    damaged = rd(0x0300538C, 4)     # gDamagedSaveSectors
    print(f"P3 no damaged save sectors (want 0): {damaged}")
    for r in REGS:
        gdb.execute(f"set ${r} = {saved[r]}")
    run(3)
    vb1 = rd(0x03003114, 4)
    run(3)
    vb2 = rd(0x03003114, 4)
    print(f"P4 game alive after save (want 1): {1 if vb2 > vb1 else 0}")
end

echo \n=== PHASE A DONE ===\n
disconnect
quit
