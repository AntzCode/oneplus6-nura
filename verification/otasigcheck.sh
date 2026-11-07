#!/usr/bin/env bash
# Verify an Android OTA zip's whole-file signature (signapk -w) against a certificate.
# Usage: otasigcheck.sh <ota.zip> <cert.pem>
set -euo pipefail
zip=$1 cert=$2
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

python3 -I - "$zip" "$tmp" <<'EOF'
import os, struct, sys
z, t = sys.argv[1], sys.argv[2]
size = os.path.getsize(z)
with open(z, "rb") as f:
    f.seek(size - 6)
    sig_start, magic, comment_size = struct.unpack("<HHH", f.read(6))
    assert magic == 0xFFFF, "no whole-file signature footer"
    f.seek(size - sig_start)
    open(os.path.join(t, "sig.p7b"), "wb").write(f.read(sig_start - 6))
open(os.path.join(t, "len"), "w").write(str(size - comment_size - 2))
EOF

openssl cms -verify -inform DER -in "$tmp/sig.p7b" -binary \
    -content <(head -c "$(cat "$tmp/len")" "$zip") \
    -CAfile "$cert" -purpose any -out /dev/null
echo "Whole-file signature VALID for $(openssl x509 -in "$cert" -noout -subject)"
