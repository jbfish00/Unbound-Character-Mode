# Live starter-grant test: reach free-roam on a fresh save, queue the
# ROM-baked starter debug script (build_patch.py: enable Character Mode as
# Red on an EMPTY party, then givemon Larvitar twice — the exact script
# shape Unbound's own starter scenes use). The retargeted givemon handler
# must deliver Pikachu (Red roster[0]) for the first give, and pass the
# second Larvitar through to the PC-routing gift rule (party stays at 1).
#
# Same primitives as battle_catch_test.gdb: ROM-resident script queued via
# CharacterMode_QueueScriptCb1 (script ptr in audited vars 0x51F8/F9), no
# EWRAM-staged code, state readback over the mGBA gdb stub.

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

PARTY = 0x02024284      # gPlayerParty, stride 100, species u16 at +0x20
PARTY_COUNT = 0x02024029
STRVAR1 = 0x02021CD0
CB1 = 0x030030F0
CB2 = 0x030030F4
CB1_OVERWORLD = 0x08056535

print("phase1: playing through opening...")
run(170)

ok = False
for attempt in range(30):
    cb2 = rd(CB2, 4)
    pc = reg("pc")
    cpsr = reg("cpsr")
    ctx2 = rd(0x03000F9C, 1)   # sScriptContext2Enabled: 0 = player has control
    if (cb2 == 0x080565B5 and ctx2 == 0 and 0x08000000 <= pc < 0x0A000000
            and (cpsr & 0x1F) == 0x1F and (cpsr & 0x20) == 0x20):
        ok = True
        break
    run(4)
print(f"S0 reached hijackable overworld state (want 1): {1 if ok else 0}")

if ok:
    party0_before = rd(PARTY + 0x20, 2)
    print(f"S1 party empty before test (want 1): {1 if party0_before == 0 else 0}")

    dbg = json.load(open("/home/jbfish00/Documents/Character Hacks/Unbound-Character-Mode/build/debug_addrs.json"))
    QUEUE_SHIM = int(gdb.parse_and_eval("(unsigned int)CharacterMode_QueueScriptCb1")) & ~1
    wr(0x0203B764, struct.pack("<I", dbg["starter_test_script"]))
    wr(CB1, struct.pack("<I", QUEUE_SHIM | 1))
    run(4)   # script has no waitstates; a few frames is plenty

    sp0 = rd(PARTY + 0x20, 2)
    sp1 = rd(PARTY + 100 + 0x20, 2)
    cnt = rd(PARTY_COUNT, 1)
    sv1 = rd(STRVAR1, 1)
    print(f"S2 party[0] species (want 25): {sp0}")
    print(f"S3 party count after both gives (want 1): {cnt}")
    print(f"S4 second Larvitar kept out of party (want 1): {1 if sp1 == 0 else 0}")
    print(f"S5 gStringVar1 rebuffered to Pikachu 'P' (want 202): {sv1}")

    # game still healthy: CB1 restored, overworld CB2, PC executing ROM
    run(3)
    cb1 = rd(CB1, 4)
    cb2 = rd(CB2, 4)
    pc = reg("pc")
    healthy = cb1 == CB1_OVERWORLD and cb2 == 0x080565B5 and 0x08000000 <= pc < 0x0A000000
    print(f"S6 game healthy after test (want 1): {1 if healthy else 0}")
end

echo \n=== TESTS DONE ===\n
disconnect
quit
