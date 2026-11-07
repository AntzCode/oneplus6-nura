# OnePlus 6: OxygenOS 11.1.2.2 firmware refresh and Nura (Phosh) install

A record of where each file came from, how it was checked, how it was installed, and why. It continues `README.md` (the 9.0.9 downgrade) and `verification-report.md` (proof that the 9.0.9 images are authentic).

> Status (2026-10-17): Both slots now run the full official OxygenOS 11.1.2.2 firmware, installed by OnePlus's own updater. SMS and mobile data worked in Android 11, but VoLTE calls didn't. Nura has been reflashed on slot a, and **SMS and mobile data now work on Nura**.
>
> Update (2026-10-18): **VoLTE calls work on Nura**, in and out, using the modem's `Netherlands-VoLTE-Vodafone` carrier profile (see "VoLTE working" at the end). Mute works with a helper service; speakerphone doesn't work yet (needs kernel work).

## Why this was necessary

1. **Ubuntu Touch 24.04 doesn't fit on the OnePlus 6.** The rootfs plus device tarball is 2.78 GiB, but `system` has only about 2.6 GiB usable. The installer's recovery failed with `tar: write error: No space left on device` and the phone hung at the bootloader warning. Draft bug report: `ubports-issue-draft.md`.
2. **Ubuntu Touch 20.04 worked, including SMS, but the owner didn't like it.** He moved on to the long-term plan: postmarketOS, renamed **Nura** on 2026-09-27.
3. **On Nura, the modem can't register on the network.** The SIM (Mighty Mobile, on One NZ, PLMN 530-01) is read correctly. The modem finds One's 4G cell but gets only "limited" service (`registration in network failed: Network timeout`), so SMS (`QMI protocol error (53): 'NetworkNotReady'`) and mobile data fail. Restarting `81voltd` and toggling the modem didn't help.
4. **Likely cause: mismatched modem firmware state.** Nura runs its own modem firmware, `MPSS.AT.4.0.c2.15-00007-SDM845_GEN_PACK-1.358880.1.399256.2` (built May 2021, i.e. the OxygenOS 11 generation). The modem's saved settings (EFS) were last written by the OxygenOS 9.0.9 firmware. The Nura wiki recommends having the **latest OxygenOS (11.1.2.2) on both slots** before installing, and notes a case where crashdumps went away after a firmware update and a reflash. It's not proven to be the cause yet.

## Sources

### Nura v26.06 with Phosh 29.1 (installed 2026-10-17)

- **Image server:** `https://images.nura.eco/bpo/v26.06/oneplus-enchilada/phosh/20261009-0726/` (formerly `images.postmarketos.org`, which now redirects there)
- **Saved in:** `nura-phosh-v26.06/`

| File | SHA-256 |
|---|---|
| `20261009-0726-postmarketOS-v26.06-phosh-29.1-oneplus-enchilada-boot.img.xz` | `1a16dfea2ba70e59905ebba5627e4f3c2f8617d96a81353a80124f2e9cca2b3a` |
| `20261009-0726-postmarketOS-v26.06-phosh-29.1-oneplus-enchilada.img.xz` | `7761e2f33a14b5ddd2676774a96b4116b66d595a77e5bf0abf7ce96ee58ccfa2` |

- **Verification:** both the `.sha256` and `.sha512` files published next to the images matched, and `xz -t` passed. The images aren't separately signed, so trust rests on HTTPS from the project's own server.
- **Contents:** the boot image is an Android boot image, header v0/1, page size 4096. The rootfs is an Android sparse image of 840,960 × 4096-byte blocks (3.2 GiB).

### Install instructions

- **Device page:** Nura wiki, "OnePlus 6 (oneplus-enchilada)": `https://wiki.nura.eco/wiki/OnePlus_6_(oneplus-enchilada)`.
  - The page is behind bot protection. The raw text was read via `https://wiki.nura.eco/index.php?title=OnePlus_6_(oneplus-enchilada)&action=raw`.
  - Key points: erase `dtbo` before flashing; "it's recommended that you upgrade your device to the latest release of OxygenOS on both slots" (9.0.8 if GPS and VoLTE are wanted); CrashDump mode is a known, not fully understood issue.
- **Device package:** pmaports, `device/community/device-oneplus-enchilada/deviceinfo`, branch `v26.06`, on `gitlab.postmarketos.org`.

### OxygenOS 11.1.2.2 (official OnePlus full OTA)

- **URL** (linked from the Nura wiki): `https://otafsg1.h2os.com/patch/amazone2/GLO/OnePlus6Oxygen/OnePlus6Oxygen_22.J.62_GLO_0620_2111252336/OnePlus6Oxygen_22.J.62_OTA_0620_all_2111252336_14afec75dd6fa.zip`
- **Server headers (2026-10-17):** `content-length: 2107631950`, `last-modified: Fri, 26 Nov 2021 08:16:04 GMT`, `etag: "8630970d253fd4222966ac962aa6f302-402"` (an S3 multipart ETag, not a whole-file MD5)
- **Saved in:** `oxygenos-11.1.2.2/`
- **File hashes:**
  - MD5 `ddd0d5f6a4a25d44e1ba958a16a13298`
  - SHA-256 `728d3bf37b12204024fb3db51489fad66a72b6e44071f727c1f79019945d71ef`
  - 2,107,631,950 bytes, matching `content-length`
- **Whole-file signature: VALID.** Signed by `C=CN, ST=Guangdong, L=Shenzhen, O=OnePlus, OU=SW, CN=OnePlus`. The OTA certificate's SHA-256 is `46:81:AD:50:CA:FC:58:0E:DF:E0:27:BD:3F:E5:93:25:4E:72:CD:2D:EF:1B:35:1F:EA:30:6C:CF:62:20:CF:07`, identical to the 9.0.9 OTA's certificate.
- **Metadata:**
  - `post-build=OnePlus/OnePlus6/OnePlus6:11/RKQ1.201217.002/2111252325:user/release-keys`
  - `post-security-patch-level=2021-11-01`, `ota-type=AB`, `wipe=0`
- **Partitions:** all **26 of 26 MATCH** the SHA-256s in the signed `payload.bin` manifest (`ALL OFFICIAL PARTITIONS MATCH`). The extracted images are in `oxygenos-11.1.2.2/images/`.

| Partition | Size (bytes) | SHA-256 |
|---|---:|---|
| abl | 2,183,168 | `cff7cbf5fc9cb4e146eb2a4f41ad27c55d3583c38fd4843e9d3b5dfb55afbe34` |
| aop | 184,320 | `f6311ac6411ea0b87ddda4a56c511e20e16200d2b61b2c719214244d78b12629` |
| bluetooth | 765,952 | `a01be531d8f9bcab42beda4c84032492bedbb3c9896902111311420e14fe5721` |
| boot | 67,108,864 | `b2399e505d3471c259ae7dfef03aa212bce2ccd2b2fc2b8a1bc2f45186ccb7a6` |
| cmnlib | 380,928 | `fc7266810fbe02a408083daa567daee6461886a6a8d1d37273b378abee425920` |
| cmnlib64 | 499,712 | `0cb7e040376299e8771f1645ff79ce858de5ca98b156844afd3e2ebc33753725` |
| devcfg | 40,960 | `139e0d80b34f3f8bc7d4a42f5b16c4db521012fed299d11b760511d8adbf4b6e` |
| dsp | 33,554,432 | `ed96e09f54bbb2c363bd9e6c04f22f20259750f1ba245fc9a739ea70dd666019` |
| dtbo | 8,388,608 | `886bd4fa8673df0c877d728eec1701c90d88c2ff92f70c4d309d6d0e100c0c67` |
| fw_4j1ed | 352,256 | `b89c91add1dd791338eaadb3b95d2ed99404920636007836229826486f8302c5` |
| fw_4u1ea | 352,256 | `eb18786518fd75a6797704bb523d40b76ec995458bfd9e3dfa3746812dce5352` |
| hyp | 397,312 | `eaf681c1c5effb51cfa498480750f7c31ed635f37eabb26f4de587786c83e2a8` |
| india | 321,073,152 | `8952831ae02a80f417a7f0107c0787a43f55ca63be4a2f9c6a295fef5364cfea` |
| keymaster | 233,472 | `7e61215dc947ae87350634403bf4d318027369b26f843a6f43b555857af114fb` |
| LOGO | 8,011,776 | `b729cb42a89799383021ba689e4cab91ebd44600f2fef95ac92baf89cb07f9a9` |
| modem | 119,820,288 | `ae9de0b5fedfb0ce721a4d2a7881fcf7ac02b3c445d8599c9977d290b5748398` |
| oem_stanvbk | 974,848 | `041b16186425189628083976675292cff04b1c71da654fc545bdded9504d19a8` |
| qupfw | 65,536 | `92edf512bc75b87782e147c8b40b7bdbb7422c9686845667f975d43230eca96e` |
| reserve | 968,146,944 | `0c09d915b30066140c0693f960b555b68c0402ea4cd9020e8b2997424135bb38` |
| storsec | 24,576 | `6d170aef7470fd1e3e991d53f48271732ac0888dbbeceb0f4bd91f064795fda1` |
| system | 2,998,927,360 | `032566055ab24b0d9ee0749c479ea5781567e9d98982654fbb9296b075ddfb4e` |
| tz | 2,056,192 | `2d133bdafc70122ff18c12766c855c8f8490c825bf91e1da95c6535d1d16baca` |
| vbmeta | 8,192 | `217c58a6df09e01d9c3c5f28482fc915a2cbd01c554759cbab42e3fbf0be8a04` |
| vendor | 1,073,741,824 | `f479660d77246cf058c8ff6ae91c65f4f132d3590d1b40840a91acb9e23fbcc7` |
| xbl | 3,289,088 | `b0bd42808a3a9a94d9fd41a396b09877aa499b31421ac7acf444f49b847810e0` |
| xbl_config | 98,304 | `b089b9dee5bb1b73ebbae11e6c25f148609892e72325840c5154495962f7b84f` |

To recheck:
```
verification/otasigcheck.sh oxygenos-11.1.2.2/OnePlus6Oxygen_22.J.62_OTA_0620_all_2111252336_14afec75dd6fa.zip verification/official-ota-otacert.x509.pem
python3 -I verification/otacompare.py oxygenos-11.1.2.2/OnePlus6Oxygen_22.J.62_OTA_0620_all_2111252336_14afec75dd6fa.zip oxygenos-11.1.2.2/images
```

## Verification method

The same approach as `verification-report.md`, using only Python's standard library and OpenSSL. No new packages were installed.

1. **Whole-file signature:** `verification/otasigcheck.sh` checks the OTA zip's signapk PKCS#7 signature against OnePlus's OTA certificate. The 9.0.9 certificate is kept as `verification/official-ota-otacert.x509.pem`, and the 11.1.2.2 zip is expected to be signed by the same key.
2. **Extraction:** `verification/payloadextract.py`, new for this step, unpacks `payload.bin` into partition images. It handles REPLACE, REPLACE_BZ, REPLACE_XZ, ZERO and DISCARD, and checks each data blob's SHA-256 against the manifest.
   - **Self-test:** extracted the already-verified 9.0.9 OTA, then compared the result with `otacompare.py`: **ALL OFFICIAL PARTITIONS MATCH** (24 of 24).
3. **Per-partition check:** `verification/otacompare.py` compares every extracted image with the SHA-256 in the signed manifest.

## Installation method

### Nura (first attempt, 2026-10-17)

Phone in fastboot, slot b active:

```
fastboot erase dtbo
fastboot flash boot     20261009-0726-postmarketOS-v26.06-phosh-29.1-oneplus-enchilada-boot.img
fastboot flash userdata 20261009-0726-postmarketOS-v26.06-phosh-29.1-oneplus-enchilada.img
fastboot reboot
```

- **Result:** all writes OKAY. The first boot landed in **Qualcomm CrashDump Mode** (USB ID `05c6:900e`). Holding Power for 10–15 seconds restarted it, and the second boot reached Phosh. The default PIN is `147147`.
- **Debug access:** USB networking puts the phone at `172.16.42.1` and the PC at `172.16.42.2`. SSH was enabled with `sudo systemctl enable --now sshd`, and a key was added with `ssh-copy-id`.

### OxygenOS 11.1.2.2 firmware refresh

**Attempt 1: fastboot only (failed).**
- `./flash-oos11.sh` (same procedure as `flash-linux.sh`, reading from `oxygenos-11.1.2.2/images`) flashed the non-critical partitions to both slots from slot a. Every write was OKAY.
- Booting into recovery then crashed into CrashDump Mode: `Attempted to kill init! exitcode=0x0000000b`. Init died with SIGSEGV.
- **Why:**
  - The OTA also contains `reserve` (968 MB) and `india` (321 MB). These aren't fastboot partitions: `fastboot getvar partition-size:reserve` returns "Variable Not found". Only OnePlus's updater knows where they go.
  - Slot a's critical partitions were also an older OxygenOS 11 build.
  - Conclusion: Android 11 can't be installed completely with fastboot alone. `flash-oos11.sh` is kept for reference only; don't use it.

**Attempt 2: official updater (worked).**
1. Reflashed 9.0.9 to slot a with `./flash-linux.sh` (the verified procedure), formatted data in recovery, and booted 9.0.9.
2. Copied the zip over USB with `adb push`. The on-phone SHA-256 matched (`728d3bf3…71ef`).
3. Ran **Settings → System → System updates → cogwheel → Local upgrade** with the zip. The updater installed the full 11.1.2.2 to slot b (`ONEPLUS A6000_22_211125`).
4. Ran Local upgrade a **second** time with the same zip, which filled slot a. Both slots now have the full 11.1.2.2, including the critical partitions, written by OnePlus's own updater.
5. **Test in Android 11 with the Mighty SIM:**
   - Registered on LTE ("Mighty").
   - **SMS: works.**
   - **Mobile data: works.**
   - **VoLTE: no.** A test call didn't ring. With One NZ's 3G switched off, calls need VoLTE, and stock OxygenOS apparently has no VoLTE configuration for Mighty (an MVNO on One NZ).

### Nura reflash (2026-10-17)

From Android with `adb reboot bootloader`. Then, on slot a, the same commands as the first attempt:

```
fastboot erase dtbo
fastboot flash boot     20261009-0726-postmarketOS-v26.06-phosh-29.1-oneplus-enchilada-boot.img
fastboot flash userdata 20261009-0726-postmarketOS-v26.06-phosh-29.1-oneplus-enchilada.img
fastboot reboot
```

All writes were OKAY.

**Modem result on Nura: fixed.**
- **Registration:** the modem registered on One NZ's LTE straight away (`registration: home`, `packet service state: attached`). Before the firmware refresh it never got past "searching". The Nura modem firmware is unchanged (`MPSS.AT.4.0.c2.15-00007…`), so the difference is the official 11.1.2.2 install on both slots.
- **SMS:** works, sending and receiving, in the Chats app.
- **Mobile data:**
  - First, a NetworkManager profile "Mighty" was made with APN `internet`. The network rejected it (`[3gpp] unknown-apn`), and the modem then throttled retries (`pdn-ipv4-call-throttled`).
  - The correct APN came from Android 11's own list, `/system/etc/apns-conf.xml` inside the verified `system.img`, read with `debugfs -R "dump /system/etc/apns-conf.xml …"`. For network 530-01 it lists `VFNZ Internet`, `apn="vodafone"`, `type="default,supl"`, and `VFNZ Gateway`, `apn="live.vodafone.com"`, for MMS. There's no separate Mighty entry.
  - Commands, run over SSH as the normal user:
    ```
    nmcli c add type gsm ifname "*" con-name Mighty gsm.apn internet connection.autoconnect yes
    nmcli c modify Mighty gsm.apn vodafone
    mmcli -m any --disable && mmcli -m any --enable    # clears the throttling
    ```
  - **Result:** connected. A ping to 1.1.1.1 over mobile data took 34–42 ms. IPv6 isn't offered (`pdn-ipv6-call-disallowed`); IPv4 works.
  - **Note:** activating a connection over SSH is refused ("Not authorized to control networking"). Only the person logged in on the phone can do that, but creating and modifying profiles works.
- **VoLTE:** not yet tested on Nura. It didn't work on stock Android 11 either.

### CrashDump boots (2026-10-18)

After the SIM was reinserted, two boots in a row showed the Nura logo for a few seconds and then went into Qualcomm CrashDump Mode. Holding Power for 10–15 s restarted it, and the third boot reached Phosh. The modem then registered normally (`registration: home`).

What the logs showed:
- **Both failed boots stopped at about 18.5 s**, in early userspace, just before the modem services start (rmtfs, pd-mapper, the IMS data service, q6voice; on the good boot they start at 18.7–18.8 s). The journal was synced every 5 min at the time, so the last moments weren't saved.
- **No kernel panic record.** pstore was empty after the crashes, so the reset came from firmware below Linux.
- **Warnings that are also on good boots, so they're not the cause:** `clk_core_disable` traces, `a630_sqe.fw` load error -40, the SPMI/`wcn3990-pmu` EPERM errors, the camss dependency cycles.
- **An older pstore record (12:31, from a deliberate reboot)** shows the modem hanging at shutdown (`qcom-q6v5-mss: timeout waiting for ssctl service`) and Wi-Fi firmware timing out (`ath10k … -110`). Much of the record was corrupted (`ECC: … 129 unrecoverable blocks`), so pstore isn't reliable after a hard reset. Whether that hung shutdown is linked to the CrashDump boots isn't known.
- The failed boots had `androidboot.startupmode=pon1` (one also had `androidboot.mode=charger`), and the good boot had `pwrkey`. USB being plugged in at boot was suspected, but it then booted fine both plugged in and unplugged, so that was ruled out. `pon1` is probably just the restart after the crash.

Status: intermittent and not reproducible on demand. It has followed flashing and a SIM insertion. This matches the "known, not fully understood" CrashDump issue on the Nura wiki. To catch the next one, the journal now syncs every second (`daily-driver-setup.md`, "Journal sync"). If it happens again, note what changed just before (SIM, reboot vs power-off, charging) and read `journalctl -b -1`.

### VoLTE: carrier profiles in the modem firmware (2026-10-18)

Qualcomm modems choose an MCFG carrier profile (`mcfg_sw.mbn`) to configure IMS/VoLTE. The profiles were listed from the FAT image `oxygenos-11.1.2.2/images/modem.img` with `mdir -/ -b -i modem.img ::/image/modem_pr/mcfg/configs`:
- **OOS 11.1.2.2:** 53 profiles. **OOS 9.0.9:** 44 profiles. **Neither has a profile for New Zealand or Australia.** That probably explains why VoLTE failed on stock Android 11: the modem falls back to a generic profile without IMS.
- Candidates to try, since One NZ was Vodafone NZ until 2023: `eu/vodafone/volte/uk`, then `eu/vodafone/volte/netherla`, `spain`, `italy`, and the OnePlus lab profiles `oem/lab/volte_te` and `volte_pt`. `common/row/commerci` is the generic fallback, probably without VoLTE.
- Before switching profiles on the phone (`qmicli -d qrtr://0 --pdc-…`), back up the modem EFS partitions `modemst1`, `modemst2`, `fsg` and `fsc`. Done 2026-10-18, see "Modem EFS backup" below.
- Also check with Mighty/One NZ that VoLTE is provisioned on the account and allowed on a OnePlus 6.

### Modem EFS backup (2026-10-18)

Taken on Nura, with SMS and mobile data working on One NZ, before any carrier profile changes. The images are in `efs-backup-2026-10-18/`, with checksums in `SHA256SUMS`. They're tied to this phone (they hold the IMEI and RF calibration), so keep them private.

```
ssh -t user@172.16.42.1 'mkdir -p /home/user/efs-backup && for p in modemst1 modemst2 fsg fsc; do sudo dd if=/dev/disk/by-partlabel/$p of=/home/user/efs-backup/$p.img bs=4096; done && sudo chown user: /home/user/efs-backup/* && sha256sum /home/user/efs-backup/*'
scp 'user@172.16.42.1:/home/user/efs-backup/*' efs-backup-2026-10-18/
```

Use the full path: BusyBox ash doesn't expand `~` after `of=`.

| Partition | Size | sha256 | Content |
|---|---|---|---|
| modemst1 | 2 MiB | `1d9fbf64113036166350f00594e5633ef9356a737c214ac84dac3dc0129c6360` | data |
| modemst2 | 2 MiB | `1a884b7a8cfbf794bb28a2779053cdb3b6f0f0f9092b276167ab7926e6ce1d93` | data |
| fsg | 2 MiB | `5647f05ec18958947d32874eeb788fa396a05d0bab7c1b71f112ceb7e9b31eee` | **all zeros** |
| fsc | 128 KiB | `fa43239bcee7b97ca62f007cc68487560a39e19f74f3dde7486db3f98df8e471` | all zeros |

The checksums on the PC match the phone's. **`fsg` is empty:** it's meant to hold the factory "golden" copy of the EFS, which the modem restores from if `modemst1`/`modemst2` get corrupted. This phone has no such copy, so this backup is the only way back.

To restore, from fastboot: `fastboot flash modemst1 modemst1.img` and `fastboot flash modemst2 modemst2.img`. Leave `fsg` and `fsc` alone. (Not tested yet. Writing them back with `dd` from Nura works too, but only with the modem stopped.)

### VoLTE working (2026-10-18)

The same SIM makes VoLTE calls in a Samsung Galaxy A31, so the account was never the problem.

**Profiles on the modem.** `qmicli -d qrtr://0 --pdc-list-configs=software` (works as the normal user) lists 25 profiles already loaded. The modem's own choice for the One NZ SIM is `Oversea-Commercial_DS`, with no IMS. Vodafone UK isn't loaded, and `--pdc-load-config` crashed `qmicli` 1.39 (a development release) with a segfault before it sent anything. `Netherlands-VoLTE-Vodafone` (ID `F4:09:0D:E2:C8:DA:9B:63:52:26:BE:7D:BB:80:5D:3D:DD:BA:92:B1`) is already loaded, and its size matches `eu/vodafone/volte/netherla/mcfg_sw.mbn` in the OOS 11 image exactly.

**Activating it:**

```
qmicli -d qrtr://0 --pdc-activate-config=software,F4:09:0D:E2:C8:DA:9B:63:52:26:BE:7D:BB:80:5D:3D:DD:BA:92:B1
```

The modem applies it with a SIM refresh, without restarting (`mmgdsi-card-event`). It re-registers on One NZ in about 2 s, mobile data reconnects with the existing `vodafone` APN, and IMS registers about 7 s later.

**Result:** IMS registered over LTE, voice over IMS available. Outgoing and incoming calls ring and connect, with audio both ways through the earpiece.

**The modem goes back to `Oversea-Commercial_DS` at every boot.** A call made in that state stays on "Calling…" for about 30 s and then ends, because there's no VoLTE and no 3G to fall back to. A boot service fixes it: see `daily-driver-setup.md`, "VoLTE carrier profile at boot". To undo, activate `Oversea-Commercial_DS` (ID `B0:A4:EC:0E:42:AA:ED:D7:E7:1E:2A:E7:AF:EF:5A:42:0E:83:70:80`) and disable the service.

**Checking IMS status.** `qmicli`'s IMS commands return `InvalidOperation` unless the client is first bound to SIM slot 0. On QRTR, a client ID doesn't survive between separate `qmicli` runs, so binding and querying have to happen in one process. `volte/ims-status.py` does that through the libqmi Python bindings (read-only): `python3 ims-status.py`. Values: `ims_registration_status` 0 = not registered, 1 = registering, 2 = registered; technology 1 = `wwan` (LTE); service status 0 = unavailable, 2 = available.

**Known issues during calls:**
- **Speaker doesn't work.** The call config (`/usr/share/alsa/ucm2/OnePlus/enchilada/VoiceCall.conf`, package `alsa-ucm-conf-sdm845-2-r0`) only defines Earpiece and Mic. The speaker is mentioned in its header comment, but there's no Speaker device, so `callaudiod` has nothing to switch to ("no available output found!").
- **Mute doesn't work.** Call audio goes from the mic to the modem inside the DSP (`VoiceMMode1 Capture Mixer SLIMBUS_0_TX`), never through PulseAudio. `callaudiod` mutes the PulseAudio source, which the call doesn't use. Fixed since; see "Call audio prototype" below.
- The `pw-loopback: not found` errors from `call_audio_idle_suspend_workaround` are harmless. The image uses PulseAudio for audio (`postmarketos-base-ui-audio-backend-pulseaudio`).
- SMS over IMS shows as unavailable. SMS still works the usual way.
- Not tested yet: emergency calls (111), Wi-Fi calling (disabled in the profile), MMS.

### Call audio prototype: speaker and mute (2026-10-18)

Tested with `pulseaudio` 17.0, `callaudiod` 0.1.99, `alsa-ucm-conf-sdm845-2-r0` and `q6voiced` (voice PCM `hw:0,6`, VoiceMMode1). Prototyped without root: a copy of the UCM tree in `~/ucm2-proto`, with PulseAudio run against it via `ALSA_CONFIG_UCM2` (autospawn turned off in `~/.config/pulse/client.conf` while testing). All of that has since been removed; the stock setup is back.

**Mute: fixed** with the `call-mic-mute` user service (see `daily-driver-setup.md`). Setting `DEC7 Volume` to 0 during a call silenced the uplink; 75 restored it. The DSP has no voice mute control, and `ADC4` (the UCM `CaptureMixerElem`) has volume only, no switch, so PulseAudio can only mute in software.

**Speakerphone: not possible with config changes alone.** Findings:
- The stock `VoiceCall.conf` only defines Earpiece and Mic. A Speaker device was added (`call-audio/VoiceCall.conf.speaker-prototype`): `QUAT_MI2S_RX Voice Mixer VoiceMMode1`, `QUAT_MI2S_RX Audio Mixer MultiMedia1` and `Amp DSP Switch`, with the earpiece's voice route moved into the Earpiece device.
- **PulseAudio 17 makes one sink per UCM device**, so Earpiece and Speaker became separate profiles, "Voice Call (Earpiece, Mic)" and "Voice Call (Mic, Speaker)". `callaudiod` only switches between ports of one sink ("Card lacks speaker and/or earpiece port"), so its speaker button can't select the other profile. With `ConflictingDevice` it splits the same way.
- PulseAudio probes profiles with only the verb set. A PCM whose route is enabled only in a device has no backend during the probe and fails to open (`Invalid argument`), so the profile disappears. Routes needed to open the PCM must be in the verb.
- **Mid-call route changes kill the downlink**, in both directions (earpiece → speaker and back). The DSP's voice RX port is fixed when the call's voice stream starts.
- **Voice to the speaker is silent even when routed there from the start of the call.** With the speaker profile preferred, the call started with `QUAT_MI2S_RX Voice Mixer VoiceMMode1` on, `SLIMBUS_0_RX Voice Mixer VoiceMMode1` off, and the max98927 was set up at call start; the uplink worked, but nothing came out. A 600 Hz tone through `MultiMedia3 → QUAT_MI2S_RX` (`speaker-test -D hw:0,2`) during the call was heard, so the amp and the I2S link work. Audio through `MultiMedia1 → QUAT_MI2S_RX` (with MultiMedia1 also routed to `SLIMBUS_0_RX`) was silent too.
- Conclusion: speakerphone needs q6voice/AFE work in the kernel (voice to `QUATERNARY_MI2S_RX`), plus `callaudiod` support for switching profiles, or PulseAudio-side handling. Worth reporting to the sdm845-mainline / postmarketOS OnePlus 6 maintainers with these findings.

**Speaker button with the stock config:** `callaudiod` logs "no available output found!" and the audio stays in the earpiece, but it goes very quiet and stays quiet after speaker is turned off. Cause not found.

**Earpiece gain:** PulseAudio maps the call sink volume onto `RX0 Digital Volume` (0–124, 84 = 0 dB, so up to +40 dB). At 55% it was 109 (+25 dB) and the earpiece distorted. 84 sounded clean. A UCM fix would limit the range PulseAudio uses.

### Bluetooth hands-free test: OnePlus 6 as a headset for the A31 (2026-10-18)

Goal: keep the Galaxy A31 as the phone and hotspot, and use the OnePlus 6 as its Bluetooth hands-free device, so call audio arrives on Linux and can be recorded. **Result: doesn't work on this hardware.**

- **Stack check:** BlueZ 5.86; kernel SCO sockets present; WCN3990 (`hci_uart_qca`, NVM `qca/OnePlus/enchilada/crnv21.bin`). `btmgmt info` doesn't list `wide-band-speech`, so only CVSD 8 kHz is available. PulseAudio 17's Bluetooth backend only registers gateway roles (`HFPAGProfile`, `HSPAGProfile`, `HSPHSProfile`); being the hands-free unit needs oFono or the app's own profile. PipeWire has no Bluetooth plugin installed.
- **App:** [handsfree-linux](https://github.com/PavelTarlev1/handsfree-linux) v1.2.6 (commit `8e6026c`, MIT), reviewed before running. It registers the HFP HF role with BlueZ itself, bridges the SCO socket through `pacat` (works with PulseAudio), and pulls contacts over PBAP. Its pairing agent (auto-accept) is dead code. It runs a silent GitHub update check on a timer, and runs `git pull` only when you click Update (the copy on the phone has no `.git`, so that can't happen). Its `CallRecorder` (stereo WAV) exists but isn't wired in. The main window is a fixed 520×580 and frameless. Its default config writes `show_main_window_on_start = false` (tray only, which Phosh doesn't have) and `country_code = "359"` (Bulgaria): four test dials went to +359 numbers before this was noticed.
- **What worked:** pairing, the HFP service-level connection, dialing from the app, and contact sync (491 contacts).
- **What failed:** during two calls the SCO link opened (CVSD), but `hciconfig hci0` showed **RX `sco:0`** against TX `sco:20220`. The chip never passed the A31's call audio to Linux. On SDM845 the WCN3990's SCO audio is normally wired to the audio DSP over SLIMbus, and mainline exposes no Bluetooth audio route there (no `SLIMBUS_7` controls). The recipient's phone also didn't ring.
- **Side effect:** while connected, the A31 routes its calls to the OnePlus 6, where there's no audio. The app was stopped and the A31 disconnected; they're still paired.
- **Remaining options:** a patched `crnv21.bin` with SCO over HCI (it's loaded from disk at each boot, so easy to undo, but the setting isn't known); a USB Bluetooth adapter on the USB-C port (USB adapters send SCO to the host); Samsung's built-in call recorder on the A31; or waiting for q6voice upstream work.
