#!/usr/bin/env python3
"""Print `export` lines for the overworld sprite layer (cm_ow_sprite_test.lua).

The expected art comes from the SOURCE sheet (sprites/ow_player/) or, for a
native costume, from Unbound's own base-ROM costume set -- never from the built
ROM's injected data, so the live test cannot agree with the build by
construction. Writes the 18 expected frames + the 32-byte palette to
CM_OW_EXPECT (default /tmp/ub_ow_expect.bin).

Usage: eval "$(python3 tools/tests/ow_sprite_env.py <character id, 1-based>)"
"""
import json
import os
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "character_mode"))
import unbound_ow_player as owp  # noqa: E402

char = int(sys.argv[1]) if len(sys.argv) > 1 else 10
out = os.environ.get("CM_OW_EXPECT", "/tmp/ub_ow_expect.bin")
man = json.loads(owp.CHAR_MANIFEST.read_text())["characters"]
name = man[char - 1]["character"]
dbg = json.loads((ROOT / "build" / "debug_addrs.json").read_text())
o = dbg["optin_offsets"]
print(f"export CM_OPTIN_BLOCK={dbg['optin_block']:#x}")
print(f"export CM_OFF_NUMTEXT={o['NUMTEXT_MSGBOX']} CM_OFF_GATE={o['GATE']} CM_OFF_TEXT={o['TEXT']}")

base = (ROOT / "rom" / "Pokemon Unbound (v2.1.1.1).gba").read_bytes()
sheets = owp.sheets()
if name in owp.NATIVE_COSTUMES:
    gid = owp.NATIVE_COSTUMES[name]
    info = owp._info(base, gid >> 8, gid & 0xFF)
    images = struct.unpack_from("<I", info, 0x1C)[0]
    fb = 512
    frames = b""
    for f in range(18):
        p = struct.unpack_from("<I", base, owp.R(images) + 8 * f)[0]
        frames += base[owp.R(p):owp.R(p) + fb]
    tag = struct.unpack_from("<H", info, 2)[0]
    pal = next(base[owp.R(p):owp.R(p) + 32] for p, t in owp.pal_entries(base) if t == tag)
    kind = "costume"
elif name in sheets:
    e = sheets[name]
    fb = e["width"] * e["height"] // 2
    frames = (owp.SHEETS / f"{e['stem']}.4bpp").read_bytes()
    pal = (owp.SHEETS / f"{e['stem']}.gbapal").read_bytes()
    kind = "sheet"
else:
    sys.exit(f"ow_sprite_env: {name} has no overworld sprite")
Path(out).write_bytes(frames + pal)
print(f"export CM_OW_EXPECT={out} CM_OW_FRAME_BYTES={fb} CM_OW_KIND={kind}")
print(f"# {name}: {kind}, {fb}-byte frames", file=sys.stderr)
