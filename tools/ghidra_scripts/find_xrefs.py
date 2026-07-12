# Ghidra headless script: print incoming references to a list of ROM addresses.
# Run via: analyzeHeadless <project> <name> -process <file> -scriptPath <this dir> -postScript find_xrefs.py <addr1> <addr2> ...
# Addresses are hex strings WITHOUT the 0x08000000 GBA base offset already added, e.g. 083FD7A2
# @category CharacterMode

from ghidra.program.model.symbol import RefType

args = getScriptArgs()
if not args:
    print("USAGE: find_xrefs.py <hexaddr1> <hexaddr2> ...  (e.g. 083FD7A2)")
else:
    for hexaddr in args:
        addr = toAddr(hexaddr)
        print("=== XREFs to 0x%s ===" % hexaddr)
        refs = getReferencesTo(addr)
        count = 0
        for ref in refs:
            count += 1
            fromAddr = ref.getFromAddress()
            func = getFunctionContaining(fromAddr)
            funcName = func.getName() if func else "(no function)"
            funcEntry = ("0x%s" % func.getEntryPoint()) if func else "?"
            print("  from 0x%s  in function %s @ %s  type=%s" % (fromAddr, funcName, funcEntry, ref.getReferenceType()))
        if count == 0:
            print("  (no references found)")
        print("")
