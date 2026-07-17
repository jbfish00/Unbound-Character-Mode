# Organic intro-reach test: run a fresh save with a blind A-masher through
# Unbound's new-game intro (Welcome speech -> name -> difficulty
# questionnaire -> level cap -> [our spliced Character Mode prompt] ->
# opening) and read the breadcrumb var the opt-in block sets at entry
# (0x51FA = 0xCA11, written BEFORE any prompt). Proves the splice runs
# in the real un-hijacked flow no matter how the mash answers it.

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

BREADCRUMB = 0x0203B768   # var 0x51FA
FLAG18F8 = 0x0203B373     # FLAG_CHARACTER_MODE byte (bit 0)
VAR51FC = 0x0203B76C      # VAR_CHARACTER_ID
DIFF = 0x0203B532         # VAR_UNBOUND_GAME_DIFFICULTY 0x50DF
CB2 = 0x030030F4
VBLANK = 0x03003114

print("running intro with masher...")
crumb_seen_at = -1
for cycle in range(30):
    run(8)
    crumb = rd(BREADCRUMB, 2)
    flag = rd(FLAG18F8, 1) & 1
    var = rd(VAR51FC, 2)
    diff = rd(DIFF, 2)
    cb2 = rd(CB2, 4)
    print(f"cycle {cycle:02d}: crumb={crumb:04x} flag18F8={flag} var51FC={var} "
          f"diff50DF={diff} cb2={cb2:08x}")
    if crumb == 0xCA11 and crumb_seen_at < 0:
        crumb_seen_at = cycle
        # keep going a few cycles to see the post-prompt outcome settle
    if crumb_seen_at >= 0 and cycle >= crumb_seen_at + 4:
        break

crumb = rd(BREADCRUMB, 2)
flag = rd(FLAG18F8, 1) & 1
var = rd(VAR51FC, 2)
vb1 = rd(VBLANK, 4)
run(4)
vb2 = rd(VBLANK, 4)
print(f"O1 splice reached organically (breadcrumb) (want 1): {1 if crumb == 0xCA11 else 0}")
print(f"O2 game alive after intro (want 1): {1 if vb2 > vb1 else 0}")
print(f"O3 mode state consistent (flag=>valid id) (want 1): "
      f"{1 if (flag == 0 or (1 <= var <= 156)) else 0}")
print(f"diag: final flag={flag} var51FC={var}")
end

echo \n=== TESTS DONE ===\n
disconnect
quit
