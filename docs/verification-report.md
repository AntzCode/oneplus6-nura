# OnePlus 6 – OxygenOS 9.0.9 fastboot ROM verification report

- **Date:** 2026-10-17
- **Device:** OnePlus 6 (`enchilada`, product `sdm845`, serial `<serial>`), bootloader unlocked
- **Purpose:** Confirm the community fastboot ROM used to downgrade from OxygenOS 11 to 9.0.9 (needed for the Ubuntu Touch install) is unmodified official OnePlus firmware.

## Result

**Every partition image in the fastboot ROM is byte-for-byte identical to OnePlus's official OxygenOS 9.0.9 full OTA.** All 24 images match the official SHA-256 values in the OTA's `payload.bin` manifest. The ROM contains no images that aren't in the official OTA.

## Files examined

| File | SHA-256 |
|---|---|
| `9.0.9-OnePlus6Oxygen_22_OTA_034_all_1909112343_dd26-FASTBOOT.zip` (community repack, 2,014,749,140 bytes) | `c78055dba4126a46cdbde201e6f08941660f3d9b5ebc8e3e15931cc4259f3709` |
| `…-FASTBOOT/images.zip` (1,998,632,702 bytes) | `2daf68cd62061963c093409553c09b001b0f28b195d6431ea6cac7809a4e14ee` |
| `…-FASTBOOT/TWRP.img` (**not verified**, not flashed) | `76eddace77bd9181ef593309d11b95549449a757b93c0a471b3ff47bef3a58dd` |
| `…-FASTBOOT/persist.img` (**not verified**, not flashed, must never be flashed) | `6b4a6d6b2cb72d347ab53b88dbf5a58a8cdd6c520484cebc66a414b5a1120c71` |

The repack is by XDA user mauronofrio (credited in its `.bat` scripts). Both zips passed `unzip -t`. The bundled Windows tools (`adb.exe`, `fastboot.exe` and the rest) were not verified or used.

## Official reference

- **File:** `OnePlus6Oxygen_22_OTA_034_all_1909112343_31f86cec5f8d4c7b.zip`
- **Host:** OnePlus's own S3 bucket `oxygenos.oneplus.net`, fetched over HTTPS
- **HTTP headers (2026-10-17):** `Content-Length: 1681259811`, `Last-Modified: Sat, 05 Oct 2019 09:16:32 GMT`, `ETag: "e597a8e7840fb32216be0a11d98bca74-107"`
- **`payload_properties.txt`:**
  ```
  FILE_HASH=Ojv4GoAdV9+n/owPZye47NPFvWbann25Z2inpVTXS6s=
  FILE_SIZE=1681246681
  METADATA_HASH=NL3iAAmyxAyJKSXQtiMj7QeKu+1N64xIz5eRU/+CwIg=
  METADATA_SIZE=118555
  ```
- **`META-INF/com/android/metadata`** is saved as `verification/official-ota-metadata.txt`. Key fields:
  - `ota-id=OnePlus6Oxygen_22.O.34_GLO_034_1909112343` (global build)
  - `post-build=OnePlus/OnePlus6/OnePlus6:9/PKQ1.180716.001/1909112330:user/release-keys`
  - `post-security-patch-level=2019-08-01`
  - `ota-type=AB`

Only the zip's central directory, `payload_properties.txt`, `metadata`, `otacert` and the `payload.bin` header and manifest were downloaded, using HTTP range requests. The full 1.68 GB file was not downloaded.

## Check 1 – Official manifest hashes vs local images

`verification/otacompare.py` reads each partition's `new_partition_info` (size and SHA-256) from the official `payload.bin` manifest and hashes the matching local image in `…-FASTBOOT/images/`.

| Partition | Size (bytes) | Official SHA-256 | Local |
|---|---:|---|---|
| LOGO | 3,235,840 | `87f1f449e5d0e36cbd15ca21fc6fbc86edfebf6252c991636dd4648147314bf7` | MATCH |
| abl | 208,896 | `7e37a38083fda6d2b1e076076786e4ac53f2276e5d83d8ff07a15f18d4d21e5d` | MATCH |
| aop | 184,320 | `2c1da14a7549dc86778c4079d376d07a4e0a3266de23ee99f4ae5b9935c0895e` | MATCH |
| bluetooth | 765,952 | `0ce6441a572c08165b3c85686b4bc00cc46da0c99d47ba59b41c1190a3722c95` | MATCH |
| boot | 67,108,864 | `357a3e0c93b32d7960af4f98465c40310aeeb240e80eb9fa85e134aff4daf4e8` | MATCH |
| cmnlib | 376,832 | `9dab95863139647f74aba367d89d39bf37d885ab49aab118ae0b49bf4a919930` | MATCH |
| cmnlib64 | 495,616 | `97ece3ae13721e26616fffa56da184875a6eb9a6b36b86c9c7c03848dbe5dd17` | MATCH |
| devcfg | 40,960 | `f46f6944894f4f58f9f0613ff5d16becd5147254057f03f80d2b7e0b5ed322c4` | MATCH |
| dsp | 33,554,432 | `9ab0bf284c982f4e18039cf3283158e7312f5290c304f04b2d7eec72e6959b77` | MATCH |
| dtbo | 8,388,608 | `cadc2ee60e38444423f17cf5ee6dad5b84b10c9c79f91ee0f3287414d71201ff` | MATCH |
| fw_4j1ed | 352,256 | `b89c91add1dd791338eaadb3b95d2ed99404920636007836229826486f8302c5` | MATCH |
| fw_4u1ea | 352,256 | `eb18786518fd75a6797704bb523d40b76ec995458bfd9e3dfa3746812dce5352` | MATCH |
| hyp | 389,120 | `196361e0542de0be02da6d590d36313fe05cc1c3b1008d7fe22953c61077ec76` | MATCH |
| keymaster | 233,472 | `708738724f14976bfa26f7ceeea6b88b60ae6fe15e55c6fac187d0e34170c2a8` | MATCH |
| modem | 125,472,768 | `3a91c4ceec0565a9dd900307ccbdec0fc3769b22438865452b6ec7ac338b18a6` | MATCH |
| oem_stanvbk | 974,848 | `8d3f7a88880861bdb0962fa4048ef861b9e5341499f80db3b7b9516036aae1d2` | MATCH |
| qupfw | 65,536 | `d37f351cb4527ae1cc42f04ae9424fbb6f7be1a8f39bc0c0f2e8ab77c15e4f9f` | MATCH |
| storsec | 24,576 | `e6da3e1a82943ff7d1b3d54021278e65c3237d6be210c429f2bd46f9adcc5239` | MATCH |
| system | 2,998,927,360 | `81da1acb49d4b1fc86517e08977a455557bb7c0ea730db5aabf6d327c54fd994` | MATCH |
| tz | 2,056,192 | `ce34f98410cc83fd39e25235b37c1689867f71af4e25c63343d58ac712b60abb` | MATCH |
| vbmeta | 4,096 | `af3d10c43aab075c6e9afab333b4f1fe34bb78c8b2e7da106448d6e815795010` | MATCH |
| vendor | 1,073,741,824 | `1401a6938b993bb1b7c5ce78ed7ab15b81b43b132a5b571fb08911bf11a72a8d` | MATCH |
| xbl | 3,289,088 | `a169af22f70143d90cde48be09f5621efe26027de81f4578e98f2e2005790650` | MATCH |
| xbl_config | 98,304 | `b742f85707217f8df55e61483226c8092aa66fc6d28a6ce7a2232b651ab2f4a7` | MATCH |

## Check 2 – Android Verified Boot (AVB 2.0) signatures

`verification/avbcheck.py` checks each RSA signature and recomputes every hash and hashtree root from the image data.

| Item | Key | Algorithm | Result |
|---|---|---|---|
| `vbmeta.img` (top level) | RSA-4096, AVB pubkey SHA-1 `2597c218aae470a130f61162feaae70afd97f011`, SHA-256 `7728e30f50bfa5cea165f473175a08803f6a8346642b5aa10913e9d9e6defef6` | SHA256_RSA4096 | Signature valid |
| ↳ `boot` hash descriptor | – | sha256 | Match |
| ↳ `dtbo` hash descriptor | – | sha256 | Match |
| ↳ `vendor` hashtree (1,056,714,752 bytes) | – | sha1 dm-verity | Root match |
| ↳ chained `system` (vbmeta in `system.img` footer) | RSA-4096, AVB pubkey SHA-1 `5f8f2af16b17d9f8c082cb3a6cb648436a4e784a`; identical to the key in the chain descriptor | SHA256_RSA4096 | Signature valid |
| &nbsp;&nbsp;↳ `system` hashtree (2,951,528,448 bytes) | – | sha1 dm-verity | Root match |

All rollback indexes are 0 and all flags are 0.

**Important:** the top-level `vbmeta` key is the **public AOSP test key** `testkey_rsa4096`. Its private key is published, so anyone can sign with it. I confirmed this by downloading Google's `testkey_rsa4096.pem` and deriving its AVB pubkey SHA-1, which came out as `2597c218…f011`. (For comparison, `testkey_rsa2048` gives `cdbb77177f731920bbe0a0f94f84d9038ae0617d`.) This is how OnePlus shipped the OnePlus 6. It means the AVB check only shows the images are internally consistent; authenticity comes from Check 1.

## Check 3 – Build identity and OTA certificate

Read from `system.img` with `debugfs`:

```
ro.build.fingerprint=OnePlus/OnePlus6/OnePlus6:9/PKQ1.180716.001/1909112330:user/release-keys
ro.build.ota.versionname=OnePlus6Oxygen_22_1909112343
ro.build.version.security_patch=2019-08-01
ro.build.date=Wed Sep 11 23:40:47 CST 2019
ro.build.type=user
ro.build.tags=release-keys
ro.build.user=OnePlus
ro.build.host=ubuntu-11
```

These match the official OTA's `post-build`, `version_name` and `post-security-patch-level`.

**OTA signing certificate:** the copy in `system.img` (`/system/etc/security/otacerts.zip`) and the official OTA's `META-INF/com/android/otacert` are the **same certificate**. It is saved as `verification/official-ota-otacert.x509.pem`.

- Subject and issuer: `C=CN, ST=Guangdong, L=Shenzhen, O=OnePlus, OU=SW, CN=OnePlus, emailAddress=oneplus@oneplus.cn`
- Valid: 2015-05-07 to 2042-09-22
- SHA-256 fingerprint: `46:81:AD:50:CA:FC:58:0E:DF:E0:27:BD:3F:E5:93:25:4E:72:CD:2D:EF:1B:35:1F:EA:30:6C:CF:62:20:CF:07`

## Check 4 – Full official OTA download and OnePlus signature (added later on 2026-10-17)

The full official OTA was downloaded from the Wayback Machine's 2020 capture and saved in the project root as `OnePlus6Oxygen_22_OTA_034_all_1909112343_31f86cec5f8d4c7b.zip`.

| | Value |
|---|---|
| Size | 1,681,259,811 bytes, identical to OnePlus's S3 `Content-Length` |
| MD5 | `9f83a153c9760d8ef4c01a9bdcaff5bf` |
| SHA-256 | `184d71530300b9c17861147e09a71408c0cb0111f88178b8e46c9208bf86e548` |
| `unzip -t` | No errors |
| `payload.bin` SHA-256 (base64) | `Ojv4GoAdV9+n/owPZye47NPFvWbann25Z2inpVTXS6s=`, which equals `FILE_HASH` in `payload_properties.txt` |
| **Whole-file OTA signature** | **VALID.** It's a PKCS#7 signature over the first 1,681,258,278 bytes, made by the OnePlus OTA certificate (SHA-256 `46:81:AD:50:…:CF:07`). That's the same certificate the OnePlus 6 system image trusts for updates. |
| Manifest vs repack images | All 24 partitions MATCH (rerun of Check 1 against the local zip) |

**Why its MD5 differs from the repack's** (`c61a9b63964e1239541e95c738bf7483`): they are different packages. The official OTA holds a single compressed and signed `payload.bin`, while mauronofrio's repack holds the extracted raw `.img` files plus Windows tools. Their checksums can never match. What matters is that every image inside the repack is identical to what OnePlus's signed payload produces, and Checks 1 and 4 confirm that.

Together, the OnePlus signature, the payload hash, the manifest hashes and the repack images form an unbroken chain. That closes the main limitation of the first verification.

## Limitations

- **The `payload.bin` internal signature** (separate from the whole-file zip signature) was not checked. The whole-file signature already covers `payload.bin`, so this is redundant.
- **The signing certificate is anchored to OnePlus's own artifacts.** It's the cert inside the OTA and inside the OnePlus 6 system image; there's no external certificate authority behind it. This is how Android OTA trust works: phones accept only updates signed by this cert.
- **The official filename comes from third-party listings** (GetDroidTips and the XDA mirror thread). The file's location in OnePlus's bucket, the matching OnePlus OTA certificate and the matching build metadata support that it's genuine.
- **Some files can't be verified this way.** `TWRP.img`, `persist.img`, `file_contexts`, `mke2fs.conf` and the Windows binaries are not part of the official OTA.

## What was flashed (2026-10-17)

`flash-linux.sh` flashed these images to **both** slots:

- aop, bluetooth, boot, dsp, dtbo, fw_4j1ed, fw_4u1ea, modem, qupfw, storsec, system, vbmeta, vendor and LOGO
- plus `oem_stanvbk`, which has no a/b slots

It then ran `fastboot erase userdata`. The critical partitions (abl, xbl, xbl_config, tz, hyp, keymaster, cmnlib, cmnlib64 and devcfg) were **not** flashed and stay at their OxygenOS 11 versions. `persist` was not touched.

Fastboot printed `skip copying … avb footer` warnings for system and vendor. They're harmless: both raw images already fill their partitions exactly. The image sizes shown in those warnings are junk values caused by a known bug in Debian's fastboot 34.0.4.

## Reproducing

```
python3 -I verification/otacompare.py \
  https://s3.amazonaws.com/oxygenos.oneplus.net/OnePlus6Oxygen_22_OTA_034_all_1909112343_31f86cec5f8d4c7b.zip \
  9.0.9-OnePlus6Oxygen_22_OTA_034_all_1909112343_dd26-FASTBOOT/images
python3 -I verification/avbcheck.py 9.0.9-OnePlus6Oxygen_22_OTA_034_all_1909112343_dd26-FASTBOOT/images
```

The scripts need Python 3 and the `cryptography` package; `avbcheck.py` uses it. If OnePlus's URL ever stops working, the official SHA-256 table above is the reference.

## URLs used in the verification

1. https://s3.amazonaws.com/oxygenos.oneplus.net/OnePlus6Oxygen_22_OTA_034_all_1909112343_31f86cec5f8d4c7b.zip (official OTA, HTTPS, source of the manifest, cert and metadata)
2. http://oxygenos.oneplus.net.s3.amazonaws.com/OnePlus6Oxygen_22_OTA_034_all_1909112343_31f86cec5f8d4c7b.zip (same object, used for the first existence check)
3. https://oxygenos.oneplus.net/OnePlus6Oxygen_22_OTA_034_all_1909112343_31f86cec5f8d4c7b.zip (OnePlus's own domain for it; gave no response on 2026-10-17)
4. https://android.googlesource.com/platform/external/avb/+/refs/heads/main/test/data/testkey_rsa4096.pem (AOSP AVB test key, RSA-4096)
5. https://android.googlesource.com/platform/external/avb/+/refs/heads/main/test/data/testkey_rsa2048.pem (AOSP AVB test key, RSA-2048)
6. https://www.getdroidtips.com/download-oxygenos-9-0-9-9-0-17-update-for-oneplus-6-and-6t/ (source of the official OTA filename)
7. https://xdaforums.com/t/oneplus-6-rom-ota-oxygen-os-mirrors-for-official-oxygen-os-roms-and-ota-updates.3792244/ (XDA mirror thread listing the same filename)

### Wayback Machine snapshots

The URLs above were submitted to Save Page Now on 2026-10-17 (the timestamps are UTC). Where a new save failed, the most recent existing capture is listed instead.

| # | Result | Snapshot |
|---|---|---|
| 1 | Save failed (HTTP 520; the 1.68 GB file is probably too large for Save Page Now). No capture of this URL exists. | – |
| 2 | Save failed (HTTP 520). No capture of this URL exists. | – |
| 3 | Save failed (HTTP 523; the origin no longer responds). **The full OTA zip was archived in 2020 under this URL** and can be downloaded from the archive. | https://web.archive.org/web/20200608030412/https://oxygenos.oneplus.net/OnePlus6Oxygen_22_OTA_034_all_1909112343_31f86cec5f8d4c7b.zip |
| 4 | Saved | https://web.archive.org/web/20261016202608/https://android.googlesource.com/platform/external/avb/+/refs/heads/main/test/data/testkey_rsa4096.pem |
| 5 | Saved | https://web.archive.org/web/20261016202720/https://android.googlesource.com/platform/external/avb/+/refs/heads/main/test/data/testkey_rsa2048.pem |
| 6 | Saved | https://web.archive.org/web/20261016202826/https://www.getdroidtips.com/download-oxygenos-9-0-9-9-0-17-update-for-oneplus-6-and-6t/ |
| 7 | Save failed twice (HTTP 520). The latest existing capture is used instead. | https://web.archive.org/web/20250717155317/https://xdaforums.com/t/oneplus-6-rom-ota-oxygen-os-mirrors-for-official-oxygen-os-roms-and-ota-updates.3792244/ |

If OnePlus's S3 bucket goes away, use the 2020 Wayback capture (#3) as the official source. Rerun `otacompare.py` with that `web.archive.org/web/20200608030412id_/…` URL; the `id_` suffix returns the original bytes. This was tested on 2026-10-17: the archived copy is the same size (1,681,259,811 bytes), supports range requests, and all 24 partitions match. Alternatively, download the zip and compare its `payload.bin` hashes against the table in Check 1.

## Project files from this verification

- `verification/avbcheck.py`: AVB signature and hashtree verifier
- `verification/otacompare.py`: compares local images against the official OTA manifest (takes a URL or a local zip)
- `verification/otasigcheck.sh`: verifies an OTA zip's whole-file signature against a certificate
- `OnePlus6Oxygen_22_OTA_034_all_1909112343_31f86cec5f8d4c7b.zip` (project root): the official OTA
- `verification/official-ota-otacert.x509.pem`: OnePlus OTA certificate from the official zip
- `verification/official-ota-metadata.txt`: the official OTA's `META-INF/com/android/metadata`
- `flash-linux.sh` (project root): the Linux flash script that was used
