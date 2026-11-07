#!/usr/bin/env bash
# DO NOT USE: the result crashes (init SIGSEGV). Use Local upgrade instead; see nura-install-report.md.
# Flash OxygenOS 11.1.2.2 (OnePlus 6) non-critical partitions to BOTH slots, then wipe data.
# Images were extracted from the official OTA with verification/payloadextract.py
# and checked with verification/otacompare.py (see nura-install-report.md).
# Same procedure as flash-linux.sh (the verified 9.0.9 downgrade).
# Deliberately skips persist.img (device-unique calibration) and the
# "critical" partitions (abl, xbl, xbl_config, tz, hyp, keymaster,
# cmnlib, cmnlib64, devcfg), plus reserve and india (written by the updater).
set -euo pipefail

cd "$(dirname "$0")/oxygenos-11.1.2.2/images"

echo "Checking device..."
fastboot devices | grep -q fastboot || { echo "No device in fastboot mode."; exit 1; }
product=$(fastboot getvar product 2>&1 | awk '/^product:/ {print $2}')
[[ "$product" == "sdm845" ]] || { echo "Unexpected product '$product', aborting."; exit 1; }
unlocked=$(fastboot getvar unlocked 2>&1 | awk '/^unlocked:/ {print $2}')
[[ "$unlocked" == "yes" ]] || { echo "Bootloader is locked, aborting."; exit 1; }

# Each slot has its own bootloader (abl). On this phone, abl_b refuses to flash aop
# ("Flashing is not allowed for Critical Partitions"), while abl_a allows it.
slot=$(fastboot getvar current-slot 2>&1 | awk '/^current-slot:/ {print $2}')
if [[ "$slot" != "a" ]]; then
    echo "Active slot is '$slot'. Run: fastboot --set-active=a && fastboot reboot bootloader"
    echo "then run this script again."
    exit 1
fi

read -rp "This ERASES ALL DATA on the phone. Type YES to continue: " answer
[[ "$answer" == "YES" ]] || { echo "Cancelled."; exit 1; }

slotted=(aop bluetooth boot dsp dtbo fw_4j1ed fw_4u1ea modem qupfw storsec system vbmeta vendor LOGO)
# Critical partitions are left to the official updater: after first boot, do a Local
# upgrade with the same zip (twice) so both slots get the full 11.1.2.2.

for part in "${slotted[@]}"; do
    for slot in a b; do
        echo ">>> ${part}_${slot}"
        fastboot flash "${part}_${slot}" "${part}.img"
    done
done

echo ">>> oem_stanvbk"
fastboot flash oem_stanvbk oem_stanvbk.img

# Erase only: "fastboot -w" also formats ext4 on the host, which fails with
# Debian's fastboot/mke2fs. Android formats the erased partition on first boot.
echo ">>> Erasing userdata"
fastboot erase userdata

fastboot --set-active=a
echo "Done. Rebooting. The phone should land in OnePlus recovery: choose"
echo "Wipe data and cache -> Erase everything, then Reboot (see README.md)."
fastboot reboot
