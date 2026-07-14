# Key-delivery diagnostic: which xdotool method actually reaches mgba-qt?
# Holds the A key (bound to 'x') via two methods while the game runs, then
# reads gMain.heldKeysRaw (0x03003118, GBA A = bit 0) at the pause.
# Env: MGBA_WID = X window id of the mgba-qt instance.

set confirm off
set pagination off
set remotetimeout 10
target remote localhost:2345

python
import gdb, os, signal, threading, subprocess

inf = gdb.selected_inferior()
def rd(addr, n):
    return int.from_bytes(inf.read_memory(addr, n).tobytes(), "little")
def run(sec):
    threading.Timer(sec, lambda: os.kill(os.getpid(), signal.SIGINT)).start()
    try:
        gdb.execute("continue", to_string=True)
    except gdb.error:
        pass

run(8)  # boot to title/intro
wid = os.environ.get("MGBA_WID", "")
methods = [
    ("xtest_after_windowfocus",
     f"xdotool windowfocus --sync {wid} 2>/dev/null; xdotool keydown x; sleep 2.5; xdotool keyup x"),
    ("xsendevent_to_window",
     f"xdotool keydown --window {wid} x; sleep 2.5; xdotool keyup --window {wid} x"),
]
for label, cmd in methods:
    p = subprocess.Popen(cmd, shell=True)
    run(1.8)          # emulator runs while the key is held
    held = rd(0x03003118, 2)
    p.wait()
    run(1.0)          # let the keyup land before the next method
    print(f"KEYTEST {label}: heldKeysRaw=0x{held:04x} A-pressed (want 1): {held & 1}")
print("=== TESTS DONE ===")
end

disconnect
quit
