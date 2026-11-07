"""Read the payload.bin manifest from an OTA zip and compare each partition's official
SHA-256 against local images. The zip can be a URL (fetched with HTTP range requests,
so only the manifest is downloaded) or a local file.
Usage: python3 -I otacompare.py <ota_url_or_zip_path> <images_dir>"""
import hashlib, os, struct, sys, urllib.request, zlib

URL, D = sys.argv[1], sys.argv[2]
LOCAL = os.path.isfile(URL)


def get(start, length):
    if LOCAL:
        with open(URL, "rb") as f:
            f.seek(start)
            data = f.read(length)
    else:
        req = urllib.request.Request(URL, headers={"Range": f"bytes={start}-{start + length - 1}"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
    assert len(data) == length, (len(data), length)
    return data


if LOCAL:
    size = os.path.getsize(URL)
else:
    size = int(urllib.request.urlopen(urllib.request.Request(URL, method="HEAD"), timeout=60).headers["Content-Length"])
tail = get(size - 65536, 65536)
eocd = tail.rfind(b"PK\x05\x06")
cd_size, cd_off = struct.unpack("<LL", tail[eocd + 12:eocd + 20])
cd = get(cd_off, cd_size)

entries, p = {}, 0
while cd[p:p + 4] == b"PK\x01\x02":
    method, = struct.unpack("<H", cd[p + 10:p + 12])
    csize, usize, nl, xl, cl = struct.unpack("<LLHHH", cd[p + 20:p + 34])
    lho, = struct.unpack("<L", cd[p + 42:p + 46])
    name = cd[p + 46:p + 46 + nl].decode()
    entries[name] = (method, csize, lho)
    p += 46 + nl + xl + cl
print("zip entries:", ", ".join(sorted(entries)))


def data_offset(name):
    method, csize, lho = entries[name]
    lh = get(lho, 30)
    nl, xl = struct.unpack("<HH", lh[26:30])
    return method, csize, lho + 30 + nl + xl


m, cs, off = data_offset("payload_properties.txt")
props = get(off, cs)
if m == 8:
    props = zlib.decompress(props, -15)
print(props.decode())

m, _, off = data_offset("payload.bin")
assert m == 0, "payload.bin must be stored"
hdr = get(off, 24)
assert hdr[:4] == b"CrAU"
ver, msize = struct.unpack(">QQ", hdr[4:20])
manifest = get(off + (24 if ver >= 2 else 20), msize)


def fields(buf):
    i = 0
    while i < len(buf):
        key = 0; shift = 0
        while True:
            b = buf[i]; i += 1; key |= (b & 0x7F) << shift; shift += 7
            if b < 0x80: break
        fn, wt = key >> 3, key & 7
        if wt == 0:
            v = 0; shift = 0
            while True:
                b = buf[i]; i += 1; v |= (b & 0x7F) << shift; shift += 7
                if b < 0x80: break
        elif wt == 2:
            ln = 0; shift = 0
            while True:
                b = buf[i]; i += 1; ln |= (b & 0x7F) << shift; shift += 7
                if b < 0x80: break
            v = buf[i:i + ln]; i += ln
        elif wt == 1:
            v = buf[i:i + 8]; i += 8
        elif wt == 5:
            v = buf[i:i + 4]; i += 4
        else:
            raise ValueError(wt)
        yield fn, v


official = {}
for fn, v in fields(manifest):
    if fn == 13:
        name, info = None, None
        for f2, v2 in fields(v):
            if f2 == 1: name = v2.decode()
            elif f2 == 7: info = dict(fields(v2))
        official[name] = (info.get(1), info.get(2))

allok = True
for name, (psize, phash) in sorted(official.items()):
    path = os.path.join(D, name + ".img")
    if not os.path.exists(path):
        print(f"{name:12} official size {psize}: (no local image)")
        continue
    h = hashlib.sha256()
    with open(path, "rb") as f:
        left = psize
        while left:
            chunk = f.read(min(1 << 22, left))
            if not chunk: break
            h.update(chunk); left -= len(chunk)
    match = left == 0 and h.digest() == phash
    allok &= match
    print(f"{name:12} {'MATCH' if match else 'MISMATCH'} {psize:>11} {phash.hex()}")
local_only = sorted(n[:-4] for n in os.listdir(D) if n.endswith(".img") and n[:-4] not in official)
print("local images not in official OTA:", ", ".join(local_only) or "none")
print("ALL OFFICIAL PARTITIONS MATCH" if allok else "SOME MISMATCH")
