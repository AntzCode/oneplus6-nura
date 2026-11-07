#!/usr/bin/env bash
# Flash OxygenOS 9.0.9 (OnePlus 6) to BOTH slots from Linux, then wipe data.
# Based on mauronofrio's flash-all-partitions-fastboot.bat.
# Deliberately skips persist.img (device-unique calibration) and the
# "critical" partitions (abl, xbl, xbl_config, tz, hyp, keymaster,
# cmnlib, cmnlib64, devcfg) that the original writes via TWRP + dd.
set -euo pipefail

cd "$(dirname "$0")/9.0.9-OnePlus6Oxygen_22_OTA_034_all_1909112343_dd26-FASTBOOT/images"

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
