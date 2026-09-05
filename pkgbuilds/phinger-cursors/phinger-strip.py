#!/usr/bin/env python3
"""Rewrite an Xcursor file in place so it only contains 24px images.

Xcursor wire format (libXcursor src/file.c):
  file:  "Xcur" magic(4) + header: hsz(4=16) version(4) ntoc(4)
  toc:   ntoc x { type u32, subtype u32 (size px), position u32 }
  chunk: { header_length u32 (36), type u32, subtype u32, version u32 }
         + { width u32, height u32, xhot u32, yhot u32, delay u32 }
         + width*height x { u32 RGBA pixel }
  chunk byte length = 36 + width*height*4
Compositors pick the embedded size closest to the requested one; keeping only
the 24px images forces the small cursor everywhere.
"""
import struct
import sys

MAGIC = b'Xcur'
IMAGE = 0xFFFD0002
KEEP_SIZE = 24


def read(file, offset, count):
    return struct.unpack_from('<%dI' % count, file, offset)


def chunk_len(file, t, off):
    if t == IMAGE:
        width, height = read(file, off + 16, 2)
        if width == 0 or height == 0 or width > 1024 or height > 1024:
            raise SystemExit('implausible image in %s' % path)
        return 36 + width * height * 4
    return 16 + 4 + read(file, off + 16, 1)[0]


def main(path):
    raw = bytearray(open(path, 'rb').read())
    if raw[:4] != MAGIC:
        raise SystemExit('not an Xcursor file: %s' % path)
    ntoc = read(raw, 12, 1)[0]
    tocs = [read(raw, 16 + 12 * i, 3) for i in range(ntoc)]

    for t, size, off in tocs:
        if off + chunk_len(raw, t, off) > len(raw):
            raise SystemExit('truncated chunk in %s' % path)

    kept = [c for c in tocs if c[0] != IMAGE or c[1] == KEEP_SIZE]
    if not any(t == IMAGE for t, _s, _o in kept):
        raise SystemExit('no %dpx image in %s' % (KEEP_SIZE, path))
    if len(kept) == ntoc:
        return

    out = bytearray(raw[:16])
    out += struct.pack('<I', len(kept))
    out += b'\0' * (12 * len(kept))
    offset = len(out)
    for i, (t, size, off) in enumerate(kept):
        clen = chunk_len(raw, t, off)
        struct.pack_into('<III', out, 16 + 12 * i, t, size, offset)
        out += raw[off:off + clen]
        offset += clen

    with open(path, 'wb') as f:
        f.write(out)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise SystemExit('usage: phinger-strip.py FILE...')
    for path in sys.argv[1:]:
        main(path)