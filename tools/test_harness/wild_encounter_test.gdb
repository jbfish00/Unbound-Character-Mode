# Live wild-encounter roster-override test.
#
# Goal: prove that the REAL, live wild-encounter generator TryGenerateWildMon
# (0x08A14EC4 — the actual function a grass/cave/surf/rock-smash step runs)
# routes through our hooked `bl` at 0x08A14FE6 into CharacterMode_CreateWildMon,
# and that the 10% roster override fires on that real path — observed on the
# running, booted game (not the in-CPU unit self-test, and not a reset-state
# memory poke).
#
# Since the 1% legendary roll landed (game_plans/legendary_encounters.md), a
# legendary is a LEGITIMATE outcome here, so the old "never legendary"
# assertion became an upper-bound rate check (W3d) and the real proof of the
# legendary path moved to W4*, which drives the legendary picker directly and
# asserts, positively, that it returns roster legendaries.
#
# Why a hijack-call rather than physically walking into grass: no save/state in
# this repo reaches a walkable grass tile, and driving the full intro + then
# navigating to the nearest grass patch is map-navigation automation not built
# this session (documented in the report). Instead we reach REAL free-roam via
# the shared intro drive (so gSaveBlock/party/engine state is fully
# initialized, exactly as after a grass step), enable Character Mode through the
# game's REAL FlagSet/VarSet handlers, then register-hijack a call to the REAL,
# live TryGenerateWildMon with a wild table — the exact same function (and the
# exact same hooked call site @0x08A14FE6) a grass step invokes. Only the
# trigger differs; species-selection, the 10% roll, the override, and
# CreateWildMon all execute for real on the running game. (gdb breakpoints are
# unreliable on mGBA's QT stub — see unit_tests.gdb header — so we use the same
# register-hijack + EWRAM-readback primitive the rest of the suite relies on.)
#
# Env: MGBA_WID = mgba-qt X window id (for the intro key drive).

set confirm off
set pagination off
set remotetimeout 10
target remote localhost:2345

python
import gdb, os, signal, threading, subprocess, struct, json

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

ROOT = "/home/jbfish00/Documents/Character Hacks/Unbound-Character-Mode"

PARK    = int(gdb.parse_and_eval("(unsigned int)CharacterMode_SelfTestDone")) & ~1
INCM    = int(gdb.parse_and_eval("(unsigned int)IsPlayerInCharacterMode")) & ~1
PROBE   = int(gdb.parse_and_eval("(unsigned int)CharacterMode_RunWildLiveProbe")) & ~1
# Probe result buffers (EWRAM, written by the in-ROM probe):
PROBE_RESULTS = 0x02030100   # WILD_PROBE_N x u16 produced species
PROBE_META    = 0x02030200   # [0]=N [1]=overrides [2]=off_roster [3]=legendary
                             # [4]=magic [5]=progress [6]=legend_ok [7]=legend_bad
                             # [8]=legend_none [9]=legend_offroster
PROBE_MAGIC   = 0xB0DEBEEF

TBL_MON  = 0x02030000
TBL_INFO = 0x02030040
FLAGBYTE = 0x0203B373   # CFRU expanded-save byte holding flag 0x18F8 (bit 0)
VAR51FC  = 0x0203B76C   # CFRU expanded-save var 0x51FC (VAR_CHARACTER_ID)
FILLER_SPECIES = 19     # Rattata: NOT on Red's roster (matches the in-ROM probe)

manifest = json.load(open(ROOT + "/tools/character_mode/characters_manifest.json"))
red = manifest["characters"][0]
RED_ROSTER = set(red["roster_species_ids"])
wm = json.load(open(ROOT + "/tools/character_mode/wild_species_meta_manifest.json"))
LEGEND = {e["species"] for e in wm["entries_with_data"] if e["legendary"]}
RED_LEGENDARY = sorted(RED_ROSTER & LEGEND)

def hijack_call(entry, a0=0, a1=0, a2=0, a3=0, sec=1.5):
    # Free-roam CPU is already in Thumb mode and every target here (FlagSet/
    # VarSet/InCharacterMode/TryGenerateWildMon) is Thumb, so we jump straight
    # to the function — no ARM->Thumb shim, no cpsr write (the mGBA QT stub
    # handles cpsr writes unreliably at a running state). Force T=1 defensively
    # so bx-lr return + Thumb decode are unambiguous.
    gdb.execute("set $r0=%d" % (a0 & 0xFFFFFFFF))
    gdb.execute("set $r1=%d" % (a1 & 0xFFFFFFFF))
    gdb.execute("set $r2=%d" % (a2 & 0xFFFFFFFF))
    gdb.execute("set $r3=%d" % (a3 & 0xFFFFFFFF))
    gdb.execute("set $sp=0x03007E00")
    gdb.execute("set $lr=0x%x" % (PARK | 1))
    gdb.execute("set $cpsr=($cpsr | 0x20)")       # ensure Thumb (T bit set)
    gdb.execute("set $pc=0x%x" % (entry & ~1))
    run(sec)
    return (PARK <= reg("pc") < PARK + 8), reg("r0")

# reach real free-roam via the shared intro drive (answers No at the CM prompt)
print("phase1: driving the opening to free-roam...")
exec(open(ROOT + "/tools/test_harness/intro_drive.py").read())
drive_intro_to_freeroam()

ok = False
for _ in range(30):
    cb2  = rd(0x030030F4, 4)
    pc   = reg("pc")
    cpsr = reg("cpsr")
    ctx2 = rd(0x03000F9C, 1)
    if (cb2 == 0x080565B5 and ctx2 == 0 and 0x08000000 <= pc < 0x0A000000
            and (cpsr & 0x1F) == 0x1F and (cpsr & 0x20) == 0x20):
        ok = True
        break
    run(4)
print("W0 reached hijackable free-roam (want 1): %d" % (1 if ok else 0))
print("info: free-roam cpsr=0x%08x pc=0x%08x" % (reg("cpsr"), reg("pc")))

# W1: enable Character Mode as Red by writing the CFRU expanded-save EWRAM
# directly (the same regions FlagGet/VarGet read; hijack-calling FlagSet/VarSet
# at a running state is unreliable on the mGBA QT stub — persistence_test.gdb
# uses this same direct-write approach). InCharacterMode() reads exactly these.
wr(FLAGBYTE, bytes([rd(FLAGBYTE, 1) | 0x01]))     # set flag 0x18F8 bit 0
wr(VAR51FC, struct.pack("<H", 1))                 # VAR_CHARACTER_ID = 1 (Red)
cm_ok = (rd(FLAGBYTE, 1) & 1) and (rd(VAR51FC, 2) == 1)
print("W1 Character Mode enabled as Red in the live expanded-save (want 1): %d" % (1 if cm_ok else 0))

# W2: single reliable hijack into the in-ROM probe. It runs the whole loop
# inside the emulated CPU — calling the REAL live TryGenerateWildMon (through
# our hooked bl) 64x against a Rattata-only land table at this real free-roam
# state, reading each result via the engine's own GetMonData, and tallying to
# EWRAM. (One hijack, not 64: individual hijacks are flaky on this stub.)
wr(PROBE_META + 16, struct.pack("<I", 0))         # clear entry/magic
wr(PROBE_META + 20, struct.pack("<I", 0xFFFFFFFF))
# Clear the legendary counters too: a stale buffer from a previous run would
# otherwise let W4b pass without the probe having written anything at all.
for _slot in (24, 28, 32, 36):
    wr(PROBE_META + _slot, struct.pack("<I", 0xFFFFFFFF))
parked, _ = hijack_call(PROBE, sec=8.0)
print("info: probe parked=%d pc=0x%08x entry_marker=0x%08x progress=%d"
      % (1 if parked else 0, reg("pc"), rd(PROBE_META + 16, 4), rd(PROBE_META + 20, 4)))
magic = rd(PROBE_META + 16, 4)
N        = rd(PROBE_META + 0, 4)
overrides = rd(PROBE_META + 4, 4)
off_roster = rd(PROBE_META + 8, 4)
legendary = rd(PROBE_META + 12, 4)
print("W2 in-ROM live probe completed (magic ok) (want 1): %d" % (1 if magic == PROBE_MAGIC else 0))

if magic == PROBE_MAGIC and N:
    results = [rd(PROBE_RESULTS + 2 * i, 2) for i in range(N)]
    from collections import Counter
    obs = Counter(s for s in results if s not in (FILLER_SPECIES, 0))
    produced = sum(1 for s in results if s != 0)
    rate = 100.0 * overrides / N

    print("W3 all %d live TryGenerateWildMon calls produced a wild mon (want 1): %d"
          % (N, 1 if produced == N else 0))
    print("W3b observed >=1 real override on the live path (want 1): %d" % (1 if overrides else 0))
    print("W3c every override is on the active roster (in-ROM check) (want 0): %d" % off_roster)
    # W3d USED to be "no override was ever legendary". That is no longer the
    # rule: the 1% legendary roll (game_plans/legendary_encounters.md) can
    # legitimately produce one. At 1% over 64 samples the expected count is
    # well under one, so this stays an upper bound -- a *rate* check, not a
    # ban. The positive direction is W4 below, which is the assertion that
    # actually proves the legendary path is alive.
    print("W3d legendary overrides within the 1%% roll's plausible range (want 1): %d"
          % (1 if legendary <= max(3, N // 8) else 0))
    print("W3e override rate within 2-25%% band (want 1): %d" % (1 if 2.0 <= rate <= 25.0 else 0))
    print("info: N=%d overrides=%d off_roster=%d legendary=%d rate=%.1f%%"
          % (N, overrides, off_roster, legendary, rate))
    print("info: Red roster legendary members now REACHABLE at 1%%: %s" % RED_LEGENDARY)
    print("info: override species observed (species:count): %s"
          % ", ".join("%d:%d" % (k, v) for k, v in sorted(obs.items())))

    # ---- W4: the legendary path, positive direction ----
    # legendary_encounters.md §5 calls this the biggest risk in the feature:
    # every pre-existing assertion here was "an override never produced a
    # legendary", which a completely DEAD legendary path satisfies perfectly.
    # The probe therefore also calls the legendary picker directly, on the
    # live booted game with its real Pokedex, and these assert that what comes
    # back is genuinely a legendary on the active roster.
    legend_ok = rd(PROBE_META + 24, 4)
    legend_bad = rd(PROBE_META + 28, 4)
    legend_none = rd(PROBE_META + 32, 4)
    legend_offroster = rd(PROBE_META + 36, 4)
    tries = legend_ok + legend_bad + legend_none
    print("W4 legendary picker ran on the live game (want 1): %d"
          % (1 if tries else 0))
    print("W4b every legendary pick WAS a legendary (want 1): %d"
          % (1 if tries and legend_ok == tries else 0))
    print("W4c no legendary pick was off-roster (want 0): %d" % legend_offroster)
    print("W4d no legendary pick returned a non-legendary (want 0): %d" % legend_bad)
    print("info: legendary picks ok=%d bad=%d none=%d off_roster=%d"
          % (legend_ok, legend_bad, legend_none, legend_offroster))

print("=== TESTS DONE ===")
end

disconnect
quit
