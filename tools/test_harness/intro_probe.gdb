# Probe loop for the automated intro playthrough (run_intro_playthrough.sh).
# Repeats: run the game ~8s, interrupt (timed self-SIGINT, same technique as
# unit_tests.gdb), read Character Mode state from fixed EWRAM, resume.
# Succeeds when FLAG_CHARACTER_MODE 0x18F8 (byte 0x0203B373 bit0) is set by
# the real script engine while the key-masher answers the intro prompts.

set confirm off
set pagination off
set remotetimeout 10
target remote localhost:2345

python
import gdb, os, signal, threading

inf = gdb.selected_inferior()
def rd(addr, n):
    return int.from_bytes(inf.read_memory(addr, n).tobytes(), "little")

success = False
dead = False
for cycle in range(90):
    threading.Timer(8.0, lambda: os.kill(os.getpid(), signal.SIGINT)).start()
    try:
        gdb.execute("continue", to_string=True)
    except gdb.error:
        pass
    try:
        flag = rd(0x0203B373, 1) & 1      # FLAG_CHARACTER_MODE 0x18F8
        var = rd(0x0203B76C, 2)           # VAR_CHARACTER_ID 0x51FC
        vb = rd(0x03003114, 4)            # gMain.vblankCounter2
        cb2 = rd(0x030030F4, 4)           # gMain.callback2
    except gdb.MemoryError:
        print(f"probe {cycle:02d}: emulator gone (memory read failed) — aborting")
        dead = True
        break
    print(f"probe {cycle:02d}: flag18F8={flag} var51FC={var} vblank={vb} cb2=0x{cb2:08x}")
    if flag:
        success = True
        # two more short cycles to prove the game stays alive after the prompt
        vb_before = vb
        for _ in range(2):
            threading.Timer(4.0, lambda: os.kill(os.getpid(), signal.SIGINT)).start()
            try:
                gdb.execute("continue", to_string=True)
            except gdb.error:
                pass
        vb_after = rd(0x03003114, 4)
        var = rd(0x0203B76C, 2)
        print(f"I1 opt-in flag set by script engine (want 1): 1")
        print(f"I2 var 0x51FC is Red id 1 (want 1): {1 if var == 1 else 0}")
        print(f"I3 game alive after prompt (want 1): {1 if vb_after > vb_before else 0}")
        break

if not success:
    print("I1 opt-in flag set by script engine (want 1): 0")
print("=== TESTS DONE ===")
end

disconnect
quit
