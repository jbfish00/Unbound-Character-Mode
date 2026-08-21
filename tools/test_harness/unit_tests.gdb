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

python
# The character count is DERIVED from characters_manifest.json (path exported by
# the runner as CM_MANIFEST). It used to be a literal 179 in the assertions
# below, which failed as "want 179, got 208" the moment the 2026-07-25 roster
# audit landed -- a message that reads like a roster bug rather than a test that
# had not been told the roster grew.
import json, os
_p = os.environ.get("CM_MANIFEST", "tools/character_mode/characters_manifest.json")
try:
    NUM_CHARS = len(json.load(open(_p))["characters"])
except Exception as _e:
    raise SystemExit("cannot derive the character count from %s: %s" % (_p, _e))
gdb.execute("set $want_chars = %d" % NUM_CHARS)
end
echo \n=== results ===\n
printf "MAGIC ok (want 1): %d\n", (*(unsigned int*)0x0203FEFC == 0xC0DED00D)
printf "COUNT checks ran (want 71): %d\n", *(unsigned int*)0x0203FEF8
printf "A1 InCharacterMode mode-off (want 0): %d\n", *(unsigned char*)(0x0203FE00 + 0)
printf "A2 IsSpeciesAllowed(27) mode-off (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 1)
printf "A3 CatchFlagGet mode-off (want 0): %d\n", *(unsigned char*)(0x0203FE00 + 2)
printf "B1 InCharacterMode Red (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 3)
printf "B2 GetCharacterCount (want %d): %d\n", $want_chars, *(unsigned char*)(0x0203FE00 + 4)
printf "B3 IsSpeciesAllowed(25) Pikachu (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 5)
printf "B4 IsSpeciesAllowed(6) Charizard-expansion (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 6)
printf "B5 IsSpeciesAllowed(27) Sandshrew, off-roster (want 0): %d\n", *(unsigned char*)(0x0203FE00 + 7)
printf "B6 IsSpeciesAllowed(0) SPECIES_NONE (want 0): %d\n", *(unsigned char*)(0x0203FE00 + 8)
printf "C1 CatchFlagGet target=Sandshrew (want 1=blocked): %d\n", *(unsigned char*)(0x0203FE00 + 9)
printf "C2 CatchFlagGet target=Pikachu (want 0=allowed): %d\n", *(unsigned char*)(0x0203FE00 + 10)
printf "C3 CatchFlagGet target=Charizard (want 0=allowed): %d\n", *(unsigned char*)(0x0203FE00 + 11)
printf "D1 CatchFlagGet no-catching-flag mode-off (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 12)
printf "E1 InCharacterMode var=999 (want 0): %d\n", *(unsigned char*)(0x0203FE00 + 13)
printf "E2 IsSpeciesAllowed(27) var=999 (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 14)
printf "F1 GiveMon(Pikachu) to party (want 0): %d\n", *(unsigned char*)(0x0203FE00 + 15)
printf "F2 party[0] is Pikachu (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 16)
printf "F3 party count (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 17)
printf "G1 GiveMon(Sandshrew, off-roster) kept out of party (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 18)
printf "H1 GiveMon(Mewtwo) empty party accepted (want 0): %d\n", *(unsigned char*)(0x0203FE00 + 19)
printf "H2 party[0] is Mewtwo (softlock guard) (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 20)
printf "I1 buffer name id=1 nonempty (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 21)
printf "I2 buffer name id=1 first char R (want 204): %d\n", *(unsigned char*)(0x0203FE00 + 22)
printf "I3 buffer name id=%d (last) nonempty (want 1): %d\n", $want_chars, *(unsigned char*)(0x0203FE00 + 23)
printf "I4 buffer name id=0 empty (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 24)
printf "I5 buffer name id=999 empty (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 25)
printf "J1 GetStarterSpecies Red (want 25): %d\n", *(unsigned char*)(0x0203FE00 + 26)
printf "J2 substitute Larvitar empty party (want 25): %d\n", *(unsigned char*)(0x0203FE00 + 27)
printf "J3 substitute passthrough non-empty party (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 28)
printf "J4 substitute passthrough mode off (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 29)
printf "J5 GetStarterSpecies mode off is 0 (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 30)
printf "K1 sweep no-op mode off (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 31)
printf "K2 sweep never-empty guard (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 32)
printf "K3 sweep on-roster untouched (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 33)
printf "K4 sweep keeps on-roster in mixed party (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 34)
printf "K5 sweep egg exemption (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 35)
printf "K6 hatched off-roster egg IS swept (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 36)
printf "L1 wild override passthrough mode-off (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 37)
printf "L2 wild pick none mode-off (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 38)
printf "L3 meta Charmander levelMin/Max (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 39)
printf "L4 meta Charmeleon levelMin/Max (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 40)
printf "L5 meta Charizard levelMin/Max (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 41)
printf "L6 meta family root shared (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 42)
printf "L7 meta Mewtwo legendary flag (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 43)
printf "L8 meta Pikachu not legendary (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 44)
printf "L9 wild pick never legendary x200 Red (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 45)
printf "L10 wild override empirical rate in band (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 46)
printf "M1 selectable character is selectable (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 47)
printf "M2 hidden character is NOT selectable (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 48)
printf "M3 id 0 rejected (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 49)
printf "M4 id count+1 rejected (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 50)
printf "M5 native writes 1 for selectable (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 51)
printf "M6 native writes 0 for hidden (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 52)
printf "M7 hidden character still loads from a save (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 53)
printf "M8 hidden character still resolves its roster (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 54)
printf "N1 species 386 -> natdex 313 (id != dex num) (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 55)
printf "N2 species 0 -> natdex 0 (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 56)
printf "N3 legendary picker DOES return roster legendaries x50 (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 57)
printf "N4 uncaught legendary not filtered (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 58)
printf "N5 no-legendary character gets no legendary (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 59)
printf "N6 no-legendary character keeps its 10%% override (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 60)
printf "N6b no-legendary character has no legendary family (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 61)
printf "N7 all-legendary roster has no non-legendary family (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 62)
printf "N8 all-legendary roster is repeatable, not empty (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 63)
printf "R1 randomizer flag cleared in Character Mode (want 0): %d\n", *(unsigned char*)(0x0203FE00 + 64)
printf "R2 control: randomizer untouched with mode off (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 65)
printf "M1 marker case 1 (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 66)
printf "M2 marker case 2 (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 67)
printf "M3 marker case 3 (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 68)
printf "M4 marker case 4 (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 69)
printf "M5 marker case 5 (want 1): %d\n", *(unsigned char*)(0x0203FE00 + 70)

echo \n=== TESTS DONE ===\n
# mGBA's stub doesn't implement the detach packet (E07) — just drop the link
disconnect
quit
