# Live opt-in script test: once the game reaches overworld free-roam, hijack
# the CPU to CharacterMode_TriggerIntroScript (queues the difficulty script —
# which flows through our splice at 0x09E70003 — on the game's own script
# engine), restore the interrupted context, and watch the masher answer the
# prompts. Verifies the ENTIRE live chain: script engine -> spliced call ->
# our block -> msgbox_yesno -> setflag/setvar through CFRU's handlers.
#
# Hijack safety: only performed when the interrupt landed in stable
# ROM-executing system-mode Thumb code (not mid-IRQ, not BIOS), and the full
# register file incl. cpsr/sp/lr is saved and restored afterwards.

set confirm off
set pagination off
set remotetimeout 10
target remote localhost:2345

python
import gdb, os, signal, threading

inf = gdb.selected_inferior()
def rd(addr, n):
    return int.from_bytes(inf.read_memory(addr, n).tobytes(), "little")
def run(sec):
    threading.Timer(sec, lambda: os.kill(os.getpid(), signal.SIGINT)).start()
    try:
        gdb.execute("continue", to_string=True)
    except gdb.error:
        pass
def reg(name):
    return int(gdb.parse_and_eval(f"(unsigned int)${name}")) & 0xFFFFFFFF

TRIG = int(gdb.parse_and_eval("(unsigned int)CharacterMode_TriggerIntroScript")) & ~1
PARK = int(gdb.parse_and_eval("(unsigned int)CharacterMode_SelfTestDone")) & ~1
REGS = [f"r{i}" for i in range(13)] + ["sp", "lr", "pc", "cpsr"]

# phase 1: let the masher play through the opening (~3 min)
print("phase1: playing through opening...")
run(170)

# phase 2: find a hijackable stop (overworld cb2, system-mode Thumb in ROM)
ok = False
for attempt in range(30):
    cb2 = rd(0x030030F4, 4)
    pc = reg("pc")
    cpsr = reg("cpsr")
    ctx2 = rd(0x03000F9C, 1)   # sScriptContext2Enabled: 0 = player has control
    good = (cb2 == 0x080565B5
            and ctx2 == 0
            and 0x08000000 <= pc < 0x0A000000
            and (cpsr & 0x1F) == 0x1F
            and (cpsr & 0x20) == 0x20)
    print(f"stop {attempt}: pc=0x{pc:08x} cpsr=0x{cpsr:08x} cb2=0x{cb2:08x} hijackable={good}")
    if good:
        ok = True
        break
    run(4)
print(f"H0 reached hijackable overworld state (want 1): {1 if ok else 0}")

def script_state():
    # sScriptContext1Status u8 @0x03000EA8; struct ScriptContext @0x03000EB0:
    # stackDepth(0) mode(1) comparisonResult(2) nativePtr(4) scriptPtr(8)
    st = rd(0x03000EA8, 1)
    mode = rd(0x03000EB1, 1)
    sptr = rd(0x03000EB8, 4)
    ctx2 = rd(0x03000F9C, 1)
    cb1 = rd(0x030030F0, 4)
    return f"st={st} mode={mode} scriptPtr=0x{sptr:08x} ctx2en={ctx2} cb1=0x{cb1:08x}"

if ok:
    saved = {r: reg(r) for r in REGS}
    print(f"pre-trigger:  {script_state()}")
    gdb.execute(f"set $pc = {TRIG}")
    run(3)
    pc = reg("pc")
    parked = PARK <= pc < PARK + 8
    print(f"H1 trigger parked cleanly (want 1): {1 if parked else 0}")
    for r in REGS:
        gdb.execute(f"set ${r} = {saved[r]}")
    print(f"post-trigger: {script_state()}")

    # phase 3: the queued script runs on the next frame; the masher's A
    # presses answer our prompt (Yes) then the replayed enhancement prompt
    got = 0
    for cycle in range(25):
        run(6)
        try:
            flag = rd(0x0203B373, 1) & 1
            var = rd(0x0203B76C, 2)
            vb = rd(0x03003114, 4)
            ss = script_state()
        except gdb.MemoryError:
            print(f"cycle {cycle}: emulator gone")
            break
        print(f"cycle {cycle:02d}: flag18F8={flag} var51FC={var} vblank={vb} | {ss}")
        if flag and var == 1:
            got = 1
            break
    print(f"I1 opt-in flag set via live script engine (want 1): {got}")
    if got:
        vb1 = rd(0x03003114, 4)
        run(5)
        vb2 = rd(0x03003114, 4)
        print(f"I2 game alive after opt-in (want 1): {1 if vb2 > vb1 else 0}")

print("=== TESTS DONE ===")
end

disconnect
quit
