# GDB batch unit tests for the injected Character Mode code, run against a
# live mgba-qt --gdb instance emulating build/unbound-cm.gba.
#
# Strategy (v3):
#   v1 used gdb `call` — hung (dummy-frame return breakpoints don't survive
#     the reset-state ARM/Thumb interworking on mGBA's stub).
#   v2 used `break` + `continue` — the breakpoint never hit (either a stub
#     Z-packet limitation on ROM addresses, or a crash before the park).
#   v3 depends on NOTHING but memory/register access + interrupt: the whole
#   test matrix runs inside the emulated CPU (CharacterMode_RunSelfTest in
#   src/character_mode.c writes one result byte per check to 0x0203FE00 and
#   parks in CharacterMode_SelfTestDone's infinite loop), and gdb just runs
#   the target free for a few seconds, interrupts via a timed SIGINT to
#   itself (the Ctrl-C equivalent that works in batch mode), then reads PC +
#   the result buffer. The final PC doubles as the diagnostic: parked in
#   SelfTestDone = clean run; anywhere else = where it actually went.
#
# Safe at reset: IME=0 (no interrupts), CFRU expanded flag/var arrays are
# fixed EWRAM addresses needing no save init, and nothing else executes.

set confirm off
set pagination off
set remotetimeout 10
target remote localhost:2345

# known-good stack (standard user SP region)
set $sp = 0x03007E00

# clear result magic/count so a stale buffer can't fake a pass
set {unsigned int}0x0203FEFC = 0
set {unsigned int}0x0203FEF8 = 0

# ARM->Thumb entry shim in EWRAM: ldr r12,[pc,#0]; bx r12; .word entry|1
set {unsigned int}0x02000000 = 0xE59FC000
set {unsigned int}0x02000004 = 0xE12FFF1C
set {unsigned int}0x02000008 = ((unsigned int)CharacterMode_RunSelfTest) | 1
set $pc = 0x02000000

echo \n=== shim readback ===\n
x/3wx 0x02000000

# arm a 5s self-SIGINT, then run free; SIGINT stops the target and continue
# returns (the test itself finishes in emulated microseconds)
python
import threading, os, signal
threading.Timer(5.0, lambda: os.kill(os.getpid(), signal.SIGINT)).start()
end
continue

echo \n=== state after run ===\n
printf "PC after stop: 0x%08x\n", (unsigned int)$pc
printf "SelfTestDone at: 0x%08x\n", ((unsigned int)CharacterMode_SelfTestDone) & ~1
printf "parked in SelfTestDone (want 1): %d\n", ((unsigned int)$pc >= (((unsigned int)CharacterMode_SelfTestDone) & ~1)) && ((unsigned int)$pc < ((((unsigned int)CharacterMode_SelfTestDone) & ~1) + 8))

echo \n=== results ===\n
printf "MAGIC ok (want 1): %d\n", (*(unsigned int*)0x0203FEFC == 0xC0DED00D)
printf "COUNT checks ran (want 26): %d\n", *(unsigned int*)0x0203FEF8
printf "A1 InCharacterMode mode-off (want 0): %d\n", *(unsigned char*)(0x0203FE00 + 0)
printf "A2 IsSpeciesAllowed(150) mode-off (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 1)
printf "A3 CatchFlagGet mode-off (want 0): %d\n", *(unsigned char*)(0x0203FE00 + 2)
printf "B1 InCharacterMode Red (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 3)
printf "B2 GetCharacterCount (want 156): %d\n", *(unsigned char*)(0x0203FE00 + 4)
printf "B3 IsSpeciesAllowed(25) Pikachu (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 5)
printf "B4 IsSpeciesAllowed(6) Charizard-expansion (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 6)
printf "B5 IsSpeciesAllowed(150) Mewtwo (want 0): %d\n", *(unsigned char*)(0x0203FE00 + 7)
printf "B6 IsSpeciesAllowed(0) SPECIES_NONE (want 0): %d\n", *(unsigned char*)(0x0203FE00 + 8)
printf "C1 CatchFlagGet target=Mewtwo (want 1=blocked): %d\n", *(unsigned char*)(0x0203FE00 + 9)
printf "C2 CatchFlagGet target=Pikachu (want 0=allowed): %d\n", *(unsigned char*)(0x0203FE00 + 10)
printf "C3 CatchFlagGet target=Charizard (want 0=allowed): %d\n", *(unsigned char*)(0x0203FE00 + 11)
printf "D1 CatchFlagGet no-catching-flag mode-off (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 12)
printf "E1 InCharacterMode var=999 (want 0): %d\n", *(unsigned char*)(0x0203FE00 + 13)
printf "E2 IsSpeciesAllowed(150) var=999 (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 14)
printf "F1 GiveMon(Pikachu) to party (want 0): %d\n", *(unsigned char*)(0x0203FE00 + 15)
printf "F2 party[0] is Pikachu (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 16)
printf "F3 party count (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 17)
printf "G1 GiveMon(Mewtwo) kept out of party (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 18)
printf "H1 GiveMon(Mewtwo) empty party accepted (want 0): %d\n", *(unsigned char*)(0x0203FE00 + 19)
printf "H2 party[0] is Mewtwo (softlock guard) (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 20)
printf "I1 buffer name id=1 nonempty (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 21)
printf "I2 buffer name id=1 first char R (want 204): %d\n", *(unsigned char*)(0x0203FE00 + 22)
printf "I3 buffer name id=156 nonempty (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 23)
printf "I4 buffer name id=0 empty (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 24)
printf "I5 buffer name id=999 empty (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 25)

echo \n=== TESTS DONE ===\n
# mGBA's stub doesn't implement the detach packet (E07) — just drop the link
disconnect
quit
