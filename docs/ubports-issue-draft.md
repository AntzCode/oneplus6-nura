# Draft issue for UBports. Post at: https://gitlab.com/ubports/porting/community-ports/android9/oneplus-6/oneplus-enchilada-fajita/-/issues/new

**Title:** OnePlus 6 (enchilada): 24.04-1.x install fails, rootfs + device tarball don't fit in system partition ("No space left on device")

---

### Summary

On a OnePlus 6 (A6003), installing **24.04-1.x/stable** with the UBports Installer appears to succeed ("All done!"). After that, the phone hangs forever on the unlocked-bootloader warning screen. The recovery log shows the device tarball fails to unpack because the `system` partition is full. 20.04 fits.

### Environment

- Device: OnePlus 6, model A6003, 256 GB. Firmware: official OxygenOS 9.0.9 (full OTA via Local upgrade, all partitions incl. abl/xbl/tz on the active slot b)
- UBports Installer 0.11.2 (Linux AppImage), device selected manually (`sdm845` not detected, see #15)
- Channel: `24.04-1.x/arm64/android9plus/stable`, version 6 (tag 24.04-1.5); options: Bootstrap ✅, Wipe ✅
- Bootstrap boot.img from the installer config: kernel `4.9.112-g82c44811a`, built 2021-07-18 (`system-image-upgrader` with `USE_SYSTEM_PARTITION=1`)

### What happens

`/cache/ubuntu_updater.log` (read over adb in the bootstrap recovery afterwards):

```
/dev/block/bootdevice/by-name/system_b: 11/183264 files (0.0% non-contiguous), 28970/732160 blocks
Formating: data
Applying update: rootfs-4ff3474efa2c7a2ff94548539691247d43682fa996f8dfc9355894232e838691.tar.xz
mv: bad 'data/*': No such file or directory
Applying update: device-f7015fd4b1f17a55d6a3144569575a6124784a0a0c073b620eaffbaefca29a9f.tar.xz
tar: write error: No space left on device
```

`/cache/recovery/ubuntu_command.applying` is left behind, and the boot and keyring updates never run. `system_b` afterwards:

```
Filesystem       Size  Used Avail Use% Mounted on
/dev/block/sda14 2.6G  2.6G   16M 100% /tmp/sys
```

(`/var/lib/lxc/android/android-rootfs.img` is truncated at 336,805,888 bytes.)

### Sizes

- OnePlus 6 `system_a`/`system_b`: 2,998,927,360 bytes (2.79 GiB). Usable as ext4 after mkfs: about 2.6 GiB.
- Uncompressed sizes, read from the xz indexes on system-image.ubports.com:

| Channel | rootfs | device | Total |
|---|---|---|---|
| 24.04-1.x stable (v6) | 2.24 GiB | 0.54 GiB | **2.78 GiB**, doesn't fit |
| 20.04 stable (OTA-12) | 1.90 GiB | 0.54 GiB | 2.44 GiB, fits |

The 6T may have a larger system partition. If so, that would explain why this only affects the OnePlus 6, but I haven't checked.

### Steps to reproduce

1. OnePlus 6 on OxygenOS 9.0.9, bootloader unlocked
2. UBports Installer → OnePlus 6/6T → Ubuntu Touch → `24.04-1.x/stable`, Wipe + Bootstrap
3. The installer reports success. The phone never gets past the bootloader warning screen.
4. Boot the bootstrap recovery from the fastboot menu and read `/cache/ubuntu_updater.log`

### Expected

Either 24.04 fits on the OnePlus 6, or the installer stops with an error (the upgrader currently fails silently).

### Possible fixes (suggestions)

- Install the rootfs to `/data/rootfs.img` (`USE_SYSTEM_PARTITION=0`) on enchilada, or otherwise use part of userdata
- Reduce filesystem overhead or the image size so it fits in about 2.6 GiB
- Have `system-image-upgrader` abort visibly when an `update` step fails
- Until fixed, mark 24.04 as not installable on the OnePlus 6 (as opposed to the 6T) in the installer config / devices page
