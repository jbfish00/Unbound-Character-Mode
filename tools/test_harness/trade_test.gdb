# Live in-game trade enforcement test: reach free-roam on a fresh save,
# queue the ROM-baked trade debug script (build_patch.py): with Character
# Mode OFF, givemon Pikachu + Lickitung; enable Character Mode for the case's
# character; execute Borrius trade 2 (The Top the Hitmontop for Lickitung)
# through the REAL patched shared junction (call 0x09E9459C -> special 0xFD;
# goto tail -> special 0xFE; waitstate; special 0x1AF sweep).
#
# Case selected by env TRADE_CASE:
#   red   (char 1): Hitmontop off-roster -> swept to the PC. Party ends
#                   [Pikachu]; 237 present in PC storage.
#   bruno (char 6): Hitmontop on-roster -> stays. Party ends
#                   [Pikachu, Hitmontop]; 237 NOT in PC storage.
#
# Same primitives as starter_test.gdb: ROM-resident script queued via
# CharacterMode_QueueScriptCb1, state readback over the mGBA gdb stub.

set confirm off
set pagination off
set remotetimeout 10
target remote localhost:2345

python
import gdb, os, signal, threading, struct, json

inf = gdb.selected_inferior()

def rd(addr, n):
    return int.from_bytes(inf.read_memory(addr, n).tobytes(), "little")
def rdbuf(addr, n):
    return inf.read_memory(addr, n).tobytes()
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

CASE = os.environ.get("TRADE_CASE", "red")

PARTY = 0x02024284      # gPlayerParty, stride 100, species u16 at +0x20
PARTY_COUNT = 0x02024029
CB1 = 0x030030F0
CB2 = 0x030030F4
CB1_OVERWORLD = 0x08056535
CB2_OVERWORLD = 0x080565B5
CTX2 = 0x03000F9C       # sScriptContext2Enabled: 0 = no script running
STORAGE_PTR = 0x03005010  # gPokemonStoragePtr (vanilla FR, CFRU dynamic saveblocks)

def party_species(i):
    return rd(PARTY + 100 * i + 0x20, 2)

def pc_box_has(species, boxes=14):
    """Scan the PC boxes (30 slots x 80 bytes, species u16 at +0x20 of each
    unencrypted BoxPokemon) for a species."""
    storage = rd(STORAGE_PTR, 4)
    if not (0x02000000 <= storage < 0x02040000):
        return -1  # pointer not sane — report as diagnostic
    # boxes start at storage+0 in this ROM's (CFRU dynamic-saveblock)
    # storage struct — no leading currentBox byte (confirmed live: swept
    # mon's species lands at storage+0x20 = box 0 slot 0 + 0x20)
    buf = rdbuf(storage, boxes * 30 * 80)
    for slot in range(boxes * 30):
        if struct.unpack_from("<H", buf, slot * 80 + 0x20)[0] == species:
            return 1
    return 0

def pc_raw_scan(species):
    """Diagnostic: raw byte-scan of the whole storage struct for the species
    u16 — reports offsets so a wrong stride/base assumption shows itself."""
    storage = rd(STORAGE_PTR, 4)
    if not (0x02000000 <= storage < 0x02040000):
        return f"storage ptr insane: {storage:08x}"
    buf = rdbuf(storage, 14 * 30 * 80 + 0x100)
    pat = struct.pack("<H", species)
    hits = []
    i = buf.find(pat)
    while i != -1 and len(hits) < 12:
        hits.append(hex(i))
        i = buf.find(pat, i + 1)
    return f"storage={storage:08x} raw hits at storage+{hits}"

print(f"case: {CASE}")
print("phase1: playing through opening...")
run(170)

ok = False
for attempt in range(30):
    cb2 = rd(CB2, 4)
    pc = reg("pc")
    cpsr = reg("cpsr")
    ctx2 = rd(CTX2, 1)
    if (cb2 == CB2_OVERWORLD and ctx2 == 0 and 0x08000000 <= pc < 0x0A000000
            and (cpsr & 0x1F) == 0x1F and (cpsr & 0x20) == 0x20):
        ok = True
        break
    run(4)
print(f"T0 reached hijackable overworld state (want 1): {1 if ok else 0}")

if ok:
    print(f"T1 party empty before test (want 1): {1 if party_species(0) == 0 else 0}")

    dbg = json.load(open("/home/jbfish00/Documents/Character Hacks/Unbound-Character-Mode/build/debug_addrs.json"))
    script_addr = dbg[f"trade_test_script_{CASE}"]
    QUEUE_SHIM = int(gdb.parse_and_eval("(unsigned int)CharacterMode_QueueScriptCb1")) & ~1
    wr(0x0203B764, struct.pack("<I", script_addr))
    wr(CB1, struct.pack("<I", QUEUE_SHIM | 1))

    # the trade scene is a full CB2 takeover (~40s of animation) with
    # several press-A message prompts (state 71 of the anim state machine
    # polls gMain.newKeys & A_BUTTON) — the driver script runs a second
    # masher until we touch the sentinel file below. Poll for completion:
    # script context idle again, overworld CB2 back, party populated.
    done = False
    for attempt in range(40):
        run(4)
        if (rd(CTX2, 1) == 0 and rd(CB2, 4) == CB2_OVERWORLD
                and rd(PARTY_COUNT, 1) != 0):
            done = True
            break
    open("/home/jbfish00/Documents/Character Hacks/Unbound-Character-Mode/build/.trade_done", "w").close()
    print(f"T2 trade script + scene completed (want 1): {1 if done else 0}")

    sp0 = party_species(0)
    sp1 = party_species(1)
    cnt = rd(PARTY_COUNT, 1)
    in_pc = pc_box_has(237)
    print(f"diag: party=[{sp0},{sp1}] count={cnt} hitmontop_in_pc={in_pc}")
    print(f"diag: {pc_raw_scan(237)}")
    print(f"T3 party[0] is Pikachu (want 1): {1 if sp0 == 25 else 0}")
    if CASE == "red":
        print(f"T4 party count post-sweep (want 1): {cnt}")
        print(f"T5 off-roster Hitmontop out of party (want 1): {1 if sp1 == 0 else 0}")
        print(f"T6 Hitmontop delivered to PC storage (want 1): {1 if in_pc == 1 else 0}")
    else:
        print(f"T4 party count control (want 2): {cnt}")
        print(f"T5 on-roster Hitmontop stays in party (want 1): {1 if sp1 == 237 else 0}")
        print(f"T6 Hitmontop not PC-routed (want 1): {1 if in_pc == 0 else 0}")

    # game still healthy: CB1 restored, overworld CB2, PC in an executable
    # region (ROM, IWRAM — audio engine runs there — EWRAM, or BIOS: any of
    # these is normal; requiring ROM specifically was a flake source)
    healthy = False
    for attempt in range(3):
        run(3)
        cb1 = rd(CB1, 4)
        cb2 = rd(CB2, 4)
        pc = reg("pc")
        pc_ok = (pc < 0x4000 or 0x02000000 <= pc < 0x02040000
                 or 0x03000000 <= pc < 0x03008000 or 0x08000000 <= pc < 0x0A000000)
        if cb1 == CB1_OVERWORLD and cb2 == CB2_OVERWORLD and pc_ok:
            healthy = True
            break
        print(f"diag: health retry cb1={cb1:08x} cb2={cb2:08x} pc={pc:08x}")
    print(f"T7 game healthy after test (want 1): {1 if healthy else 0}")
end

echo \n=== TESTS DONE ===\n
disconnect
quit
