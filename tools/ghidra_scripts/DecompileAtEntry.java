// Force-disassemble (Thumb) starting at EXACT function entry points, create the
// function there if Ghidra doesn't know it yet, then print the decompiled C.
// Unlike InspectRegions.java (which guesses a window start), this takes real
// entry addresses — e.g. handler pointers from a dispatch table, with or
// without the Thumb bit (it is stripped automatically).
//
// Run via: analyzeHeadless <project> <name> -process <file> -noanalysis
//   -scriptPath <this dir> -postScript DecompileAtEntry.java <addr1> <addr2> ...
// Addresses are hex WITH the 0x08000000 GBA ROM base included, e.g. 0806A82D
// (toAddr() resolves an un-prefixed offset to an unmapped address and silently no-ops).
// @category CharacterMode
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.lang.RegisterValue;
import ghidra.program.model.listing.Function;
import ghidra.util.task.ConsoleTaskMonitor;
import java.math.BigInteger;

public class DecompileAtEntry extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length == 0) {
            println("USAGE: DecompileAtEntry.java <hexaddr1> <hexaddr2> ...");
            return;
        }

        Register tmode = currentProgram.getProgramContext().getRegister("TMode");
        DecompInterface ifc = new DecompInterface();
        ifc.openProgram(currentProgram);

        for (String hexaddr : args) {
            long raw = Long.parseLong(hexaddr, 16) & ~1L; // strip Thumb bit
            Address entry = toAddr(raw);
            println("=== entry 0x" + Long.toHexString(raw) + " ===");

            Function func = getFunctionAt(entry);
            if (func == null) {
                // assume a Thumb function of bounded size; clear + set TMode + disassemble
                Address end = entry.add(0x200);
                try {
                    clearListing(entry, end);
                } catch (Exception e) {
                    // fine if nothing to clear
                }
                currentProgram.getProgramContext().setRegisterValue(
                    entry, end, new RegisterValue(tmode, BigInteger.ONE));
                disassemble(entry);
                func = createFunction(entry, null);
            }
            if (func == null) {
                func = getFunctionContaining(entry);
            }
            if (func == null) {
                println("  could not create/find function here");
                continue;
            }

            DecompileResults res = ifc.decompileFunction(func, 60, new ConsoleTaskMonitor());
            if (res.decompileCompleted()) {
                println(res.getDecompiledFunction().getC());
            } else {
                println("  decompile failed: " + res.getErrorMessage());
            }
            println("");
        }
        ifc.dispose();
    }
}
