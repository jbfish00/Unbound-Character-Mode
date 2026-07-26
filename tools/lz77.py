#!/usr/bin/env python3
"""Minimal GBA BIOS LZ77 (type 0x10) encoder + decoder.

Needed because a couple of staged assets arrived with an UNCOMPRESSED palette
(`trainer_pal.gbapal`) while the engine's LoadCompressedSpritePalette wants an
LZ77 stream, and nothing in this repo could produce one -- every existing .lz
was compressed upstream by gbagfx.

The encoder is deliberately STORE-ONLY: it emits a well-formed LZ77 stream in
which every token is a literal. That is valid input to the BIOS decompressor
(and to the engine's own), just not space-efficient -- which is irrelevant for
a 32-byte palette, and much easier to be sure is correct than a real matcher.
`roundtrip_ok` re-decodes whatever it produced, so a malformed stream cannot
reach the ROM.

Format: u8 type(0x10) + u24 decompressed size, then blocks of one flag byte
followed by 8 tokens, MSB first. Flag bit 0 = literal byte; bit 1 = back
reference (unused here).
"""
import sys


def decompress(data):
    if not data or data[0] != 0x10:
        raise ValueError("not an LZ77 (type 0x10) stream")
    size = data[1] | (data[2] << 8) | (data[3] << 16)
    out = bytearray()
    pos = 4
    while len(out) < size:
        if pos >= len(data):
            raise ValueError("truncated LZ77 stream")
        flags = data[pos]
        pos += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                if pos + 1 >= len(data):
                    raise ValueError("truncated back reference")
                b0, b1 = data[pos], data[pos + 1]
                pos += 2
                length = (b0 >> 4) + 3
                disp = (((b0 & 0xF) << 8) | b1) + 1
                if disp > len(out):
                    raise ValueError("back reference before start of output")
                for _ in range(length):
                    out.append(out[-disp])
            else:
                if pos >= len(data):
                    raise ValueError("truncated literal")
                out.append(data[pos])
                pos += 1
    return bytes(out[:size])


def compress(raw):
    """Store-only: valid LZ77, every token a literal."""
    if len(raw) >= 1 << 24:
        raise ValueError("input too large for a 24-bit LZ77 size field")
    out = bytearray([0x10, len(raw) & 0xFF, (len(raw) >> 8) & 0xFF,
                     (len(raw) >> 16) & 0xFF])
    for i in range(0, len(raw), 8):
        out.append(0x00)              # 8 literals
        out += raw[i:i + 8]
    return bytes(out)


def roundtrip_ok(raw):
    """Compress then decompress; True only if the bytes come back identical."""
    try:
        return decompress(compress(raw)) == raw
    except ValueError:
        return False


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in ("compress", "decompress"):
        raise SystemExit("usage: lz77.py compress|decompress <in> <out>")
    with open(sys.argv[2], "rb") as f:
        data = f.read()
    if sys.argv[1] == "compress":
        if not roundtrip_ok(data):
            raise SystemExit("refusing to write: the stream does not round-trip")
        result = compress(data)
    else:
        result = decompress(data)
    with open(sys.argv[3], "wb") as f:
        f.write(result)
    print("%s: %d -> %d bytes" % (sys.argv[1], len(data), len(result)))
