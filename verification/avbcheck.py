"""Minimal AVB 2.0 verifier: checks vbmeta signatures (incl. chained partitions) and that
each image matches the digest vbmeta commits to. Usage: python3 -I avbcheck.py <images_dir>"""
import hashlib, os, struct, sys
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

D = sys.argv[1]
ok = True


def tree_root(path, image_size, block, salt, algname):
    dsz = hashlib.new(algname).digest_size
    pad = b"\0" * ((1 << (dsz - 1).bit_length()) - dsz)  # avbtool pads digests to a power of 2
    hf = lambda b: hashlib.new(algname, salt + b).digest() + pad
    level = bytearray()
    with open(path, "rb") as f:
        left = image_size
        while left > 0:
            blk = f.read(min(block, left))
            left -= len(blk)
            level += hf(blk.ljust(block, b"\0"))
    while True:
        if len(level) % block:
            level += b"\0" * (block - len(level) % block)
        if len(level) == block:
            return hashlib.new(algname, salt + bytes(level)).digest()
        level = bytearray(b"".join(hf(bytes(level[i:i + block]))
                                   for i in range(0, len(level), block)))


def footer_vbmeta(path):
    with open(path, "rb") as f:
        f.seek(-64, 2)
        foot = f.read(64)
        assert foot[:4] == b"AVBf", f"{path}: no AVB footer"
        _, _, _, _, vbo, vbs = struct.unpack(">4sLLQQQ", foot[:36])
        f.seek(vbo)
        return f.read(vbs)


def verify(vb, label, expected_pk=None, indent=""):
    global ok
    assert vb[:4] == b"AVB0"
    maj, mnr, auth_sz, aux_sz, alg = struct.unpack(">LLQQL", vb[4:32])
    hash_off, hash_sz, sig_off, sig_sz, pk_off, pk_sz, pkm_off, pkm_sz, desc_off, desc_sz = \
        struct.unpack(">10Q", vb[32:112])
    rb_idx, flags = struct.unpack(">QL", vb[112:124])
    hdr, auth = vb[:256], vb[256:256 + auth_sz]
    aux = vb[256 + auth_sz:256 + auth_sz + aux_sz]
    print(f"{indent}== {label}: vbmeta v{maj}.{mnr} alg={alg} flags={flags} rollback_index={rb_idx}")
    pk = aux[pk_off:pk_off + pk_sz]
    bits, = struct.unpack(">L", pk[:4])
    print(f"{indent}   key RSA-{bits} sha1={hashlib.sha1(pk).hexdigest()}")
    if expected_pk is not None:
        same = pk == expected_pk
        ok &= same
        print(f"{indent}   key matches chain descriptor: {same}")
    n = int.from_bytes(pk[8:8 + bits // 8], "big")
    halg = hashes.SHA256() if alg <= 3 else hashes.SHA512()
    signed = hdr + aux
    rsa.RSAPublicNumbers(65537, n).public_key().verify(
        auth[sig_off:sig_off + sig_sz], signed, padding.PKCS1v15(), halg)
    hfn = hashlib.sha256 if alg <= 3 else hashlib.sha512
    assert auth[hash_off:hash_off + hash_sz] == hfn(signed).digest()
    print(f"{indent}   signature VALID")

    descs, p = aux[desc_off:desc_off + desc_sz], 0
    while p < len(descs):
        tag, nbf = struct.unpack(">QQ", descs[p:p + 16])
        body = descs[p + 16:p + 16 + nbf]
        p += 16 + nbf
        if tag == 0:  # property
            kl, vl = struct.unpack(">QQ", body[:16])
            print(f"{indent}   [prop] {body[16:16 + kl].decode()} = {body[17 + kl:17 + kl + vl].decode(errors='replace')}")
        elif tag == 1:  # hashtree
            _, image_size, _, _, dbs, _, _, _, _ = struct.unpack(">LQQQLLLQQ", body[:56])
            algname = body[56:88].rstrip(b"\0").decode()
            pl, sl, rl, _ = struct.unpack(">LLLL", body[88:104])
            rest = body[164:]
            name, salt, root = rest[:pl].decode(), rest[pl:pl + sl], rest[pl + sl:pl + sl + rl]
            got = tree_root(os.path.join(D, name + ".img"), image_size, dbs, salt, algname)
            ok &= got == root
            print(f"{indent}   [hashtree {algname}] {name} ({image_size} bytes): {'MATCH' if got == root else 'MISMATCH'}")
        elif tag == 2:  # hash
            image_size, = struct.unpack(">Q", body[:8])
            algname = body[8:40].rstrip(b"\0").decode()
            pl, sl, dl, _ = struct.unpack(">LLLL", body[40:56])
            rest = body[116:]
            name, salt, dig = rest[:pl].decode(), rest[pl:pl + sl], rest[pl + sl:pl + sl + dl]
            with open(os.path.join(D, name + ".img"), "rb") as f:
                got = hashlib.new(algname, salt + f.read(image_size)).digest()
            ok &= got == dig
            print(f"{indent}   [hash {algname}] {name}: {'MATCH' if got == dig else 'MISMATCH'}")
        elif tag == 4:  # chain
            _, pl, pkl, _ = struct.unpack(">LLLL", body[:16])
            name = body[76:76 + pl].decode()
            cpk = body[76 + pl:76 + pl + pkl]
            print(f"{indent}   [chain] {name}")
            verify(footer_vbmeta(os.path.join(D, name + ".img")), name, cpk, indent + "    ")


verify(open(os.path.join(D, "vbmeta.img"), "rb").read(), "vbmeta.img")
print("ALL OK" if ok else "SOME CHECKS FAILED")
