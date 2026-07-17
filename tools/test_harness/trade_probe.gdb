# Diagnostic probe for the trade live test: queue the red trade script,
# then periodically dump engine state to see where the scene wedges.
set confirm off
set pagination off
set remotetimeout 10
target remote localhost:2345

python
import gdb, os, signal, threading, struct, json

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

PARTY = 0x02024284
CB1 = 0x030030F0
CB2 = 0x030030F4
CTX2 = 0x03000F9C
SCTX1_STATUS = 0x03000EA8
SCTX1 = 0x03000EB0   # scriptPtr at +8
VBLANK = 0x030030F8  # vblank counter area (from boot smoke: counter2 nearby)

print("phase1: playing through opening...")
run(170)
for attempt in range(30):
    if (rd(CB2, 4) == 0x080565B5 and rd(CTX2, 1) == 0):
        break
    run(4)
print("reached overworld")

dbg = json.load(open("/home/jbfish00/Documents/Character Hacks/Unbound-Character-Mode/build/debug_addrs.json"))
QUEUE_SHIM = int(gdb.parse_and_eval("(unsigned int)CharacterMode_QueueScriptCb1")) & ~1
wr(0x0203B764, struct.pack("<I", dbg["trade_test_script_red"]))
wr(CB1, struct.pack("<I", QUEUE_SHIM | 1))

for i in range(10):
    run(6)
    cb2 = rd(CB2, 4)
    pc = reg("pc")
    sptr = rd(SCTX1 + 8, 4)
    sp1 = rd(PARTY + 100 + 0x20, 2)
    tdp = rd(0x02031DAC, 4)   # sTradeData pointer
    if 0x02000000 <= tdp < 0x02040000:
        tstate = rd(tdp + 0x94, 2)
        tflag = rd(tdp + 0x108, 1)
    else:
        tstate = tflag = -1
    gmain_state = rd(0x030030F0 + 0x438, 1)
    print(f"t+{(i+1)*6}s cb2={cb2:08x} pc={pc:08x} sptr={sptr:08x} party1={sp1} "
          f"td={tdp:08x} td.state={tstate} td.flag108={tflag} gMain.state={gmain_state}")
end

echo \n=== PROBE DONE ===\n
disconnect
quit
