"""Extract partition images from a full (non-incremental) OTA zip's payload.bin.
Standard library only. Check the result afterwards with otacompare.py, which compares
each image's SHA-256 against the signed manifest.
Usage: python3 -I payloadextract.py <ota.zip> <out_dir>"""
import bz2, hashlib, lzma, os, struct, sys

ZIP, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
f = open(ZIP, "rb")


def get(start, length):
    f.seek(start)
    data = f.read(length)
    assert len(data) == length, (len(data), length)
    return data


size = os.path.getsize(ZIP)
tail = get(size - 65536, 65536)
eocd = tail.rfind(b"PK\x05\x06")
cd_size, cd_off = struct.unpack("<LL", tail[eocd + 12:eocd + 20])
cd = get(cd_off, cd_size)
entries, p = {}, 0
while cd[p:p + 4] == b"PK\x01\x02":
    method, = struct.unpack("<H", cd[p + 10:p + 12])
    nl, xl, cl = struct.unpack("<HHH", cd[p + 28:p + 34])
    lho, = struct.unpack("<L", cd[p + 42:p + 46])
    entries[cd[p + 46:p + 46 + nl].decode()] = (method, lho)
    p += 46 + nl + xl + cl

method, lho = entries["payload.bin"]
assert method == 0, "payload.bin must be stored"
nl, xl = struct.unpack("<HH", get(lho + 26, 4))
off = lho + 30 + nl + xl
hdr = get(off, 24)
assert hdr[:4] == b"CrAU"
ver, msize, sigsize = struct.unpack(">QQL", hdr[4:24])
assert ver == 2, ver
manifest = get(off + 24, msize)
blobs = off + 24 + msize + sigsize


def varint(buf, i):
    v = shift = 0
    while True:
        b = buf[i]; i += 1; v |= (b & 0x7F) << shift; shift += 7
        if b < 0x80: return v, i


def fields(buf):
    i = 0
    while i < len(buf):
        key, i = varint(buf, i)
        fn, wt = key >> 3, key & 7
        if wt == 0: v, i = varint(buf, i)
        elif wt == 2: ln, i = varint(buf, i); v = buf[i:i + ln]; i += ln
        elif wt == 1: v = buf[i:i + 8]; i += 8
        elif wt == 5: v = buf[i:i + 4]; i += 4
        else: raise ValueError(wt)
        yield fn, v


block = 4096
parts = []
for fn, v in fields(manifest):
    if fn == 3: block = v
    elif fn == 13: parts.append(v)

for part in parts:
    name, ops, psize = None, [], None
    for fn, v in fields(part):
        if fn == 1: name = v.decode()
        elif fn == 7: psize = dict(fields(v)).get(1)
        elif fn == 8: ops.append(v)
    path = os.path.join(OUT, name + ".img")
    with open(path, "wb") as out:
        for op in ops:
            typ, doff, dlen, dst, want = 0, 0, 0, [], None
            for fn, v in fields(op):
                if fn == 1: typ = v
                elif fn == 2: doff = v
                elif fn == 3: dlen = v
                elif fn == 6: e = dict(fields(v)); dst.append((e.get(1, 0), e.get(2, 0)))
                elif fn == 8: want = v
            if typ in (0, 1, 8):  # REPLACE, REPLACE_BZ, REPLACE_XZ
                data = get(blobs + doff, dlen)
                if want is not None:
                    assert hashlib.sha256(data).digest() == want, f"{name}: blob hash mismatch"
                if typ == 1: data = bz2.decompress(data)
                elif typ == 8: data = lzma.decompress(data)
            elif typ in (6, 7):  # ZERO, DISCARD
                data = b"\0" * sum(n for _, n in dst) * block
            else:
                sys.exit(f"{name}: operation type {typ} needs a source image (incremental OTA?)")
            for start, n in dst:
                out.seek(start * block)
                out.write(data[:n * block]); data = data[n * block:]
        if psize is not None:
            out.truncate(psize)
    print(f"{name:14} {os.path.getsize(path):>11} bytes, {len(ops)} operations")
print(f"Extracted {len(parts)} partitions to {OUT}")
