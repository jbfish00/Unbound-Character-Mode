# Flag-persistence test, phase B (load): the emulator was relaunched with
# the .sav written in phase A. Drive title -> CONTINUE -> overworld, then
# verify the Character Mode state survived the save/load round trip.

set confirm off
set pagination off
set remotetimeout 10
target remote localhost:2345

python
import gdb, os, signal, threading, subprocess

inf = gdb.selected_inferior()
WID = os.environ.get("MGBA_WID", "")
def rd(addr, n):
    return int.from_bytes(inf.read_memory(addr, n).tobytes(), "little")
def run(sec):
    threading.Timer(sec, lambda: os.kill(os.getpid(), signal.SIGINT)).start()
    try:
        gdb.execute("continue", to_string=True)
    except gdb.error:
        pass
def press(key):
    subprocess.run(f"xdotool keydown --window {WID} {key}", shell=True)
    run(0.25)
    subprocess.run(f"xdotool keyup --window {WID} {key}", shell=True)
    run(0.8)

FLAGBYTE = 0x0203B373
VAR51FC = 0x0203B76C
VAR51FA = 0x0203B768

print("driving title -> CONTINUE -> overworld...")
run(6)
loaded = False
for step in range(50):
    press("x")
    if rd(0x03000F9C, 1) == 0 and rd(0x030030F4, 4) == 0x080565B5:
        loaded = True
        break
print(f"P5 save loaded to overworld (want 1): {1 if loaded else 0}")

flag = rd(FLAGBYTE, 1) & 1
var = rd(VAR51FC, 2)
sent = rd(VAR51FA, 2)
print(f"P6 flag 0x18F8 survived save/load (want 1): {flag}")
print(f"P7 var 0x51FC survived save/load (want 1): {1 if var == 42 else 0}")
print(f"P8 var 0x51FA sentinel survived (want 1): {1 if sent == 0x1234 else 0}")
print(f"diag: flag={flag} var51FC={var} var51FA={sent:#x}")
end

echo \n=== PHASE B DONE ===\n
disconnect
quit
