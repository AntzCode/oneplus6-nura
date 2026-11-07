# oneplus6-nura

Setup notes, scripts and fixes for running Nura (postmarketOS) with Phosh as a daily driver on the OnePlus 6 (enchilada).

It covers the OxygenOS downgrade and flashing, installing Nura with Phosh, and the fixes needed to make the phone usable every day: modem and APN, MMS, VoLTE, a back/home panel, keyboard Ctrl/Alt and app scaling. Everything is written to be repeatable on a rebuild or another device.

> **New Zealand specific.** This project was built on one OnePlus 6 with a Mighty Mobile SIM on the One NZ network (530-01). The carrier-dependent parts — the data APN, the VoLTE modem profile and its watchdog, and the MMS settings — are specific to that SIM and **will not work as-is on other carriers or in other countries**. Everything else (flashing, panel, keyboard, scaling, privacy switch, call audio) is generic to the OnePlus 6. Review the carrier settings before running anything.

## Contents

| Path | What it is |
| --- | --- |
| `docs/nura-install-report.md` | Full record of the install, including what failed and why |
| `docs/daily-driver-setup.md` | Post-install setup: panel, keyboard, scaling, VoLTE, MMS |
| `docs/verification-report.md` | Verifying the OxygenOS images before flashing |
| `docs/ubports-issue-draft.md` | Why Ubuntu Touch 24.04 doesn't fit on the OnePlus 6 |
| `flash-linux.sh`, `flash-oos11.sh` | Flash OxygenOS 9.0.9 / 11 on both slots, skipping `persist` and the critical partitions |
| `setup-oneplus6.sh` | Applies the daily-driver setup over SSH. Contains **One NZ specific** steps (APN, VoLTE) |
| `volte/` | **One NZ specific.** VoLTE profile selection and IMS watchdog |
| `privacy-switch/`, `call-audio/` | Generic helper services installed on the phone by the setup script |
| `verification/` | Scripts used to check the OTA images |
| `reports/` | Upstream issue reports |

The home/back panel lives in its own repo, [og-home-panel](https://github.com/AntzCode/og-home-panel).

## Source images

Nothing here is redistributed. These are the images used, and where they came from (hashes and verification details are in `docs/`):

| Image | Source |
| --- | --- |
| Nura v26.06 Phosh 29.1, `oneplus-enchilada` | <https://images.nura.eco/bpo/v26.06/oneplus-enchilada/phosh/20261009-0726/> (SHA-256 in `docs/nura-install-report.md`) |
| OxygenOS 11.1.2.2 (official full OTA), flashed on both slots | `https://otafsg1.h2os.com/patch/amazone2/GLO/OnePlus6Oxygen/OnePlus6Oxygen_22.J.62_GLO_0620_2111252336/OnePlus6Oxygen_22.J.62_OTA_0620_all_2111252336_14afec75dd6fa.zip`, linked from the Nura wiki |
| OxygenOS 9.0.9, official OTA (reference for verification) | <https://s3.amazonaws.com/oxygenos.oneplus.net/OnePlus6Oxygen_22_OTA_034_all_1909112343_31f86cec5f8d4c7b.zip>, with Wayback Machine copies listed in `docs/verification-report.md` |
| OxygenOS 9.0.9 fastboot repack (the images `flash-linux.sh` flashes) | Community repack by XDA user mauronofrio. See the [XDA OTA mirrors thread](https://xdaforums.com/t/oneplus-6-rom-ota-oxygen-os-mirrors-for-official-oxygen-os-roms-and-ota-updates.3792244/) |
| Nura install instructions | <https://wiki.nura.eco/wiki/OnePlus_6_(oneplus-enchilada)> |

Check any download against the hashes in `docs/` before flashing.

## Usage

Read `docs/nura-install-report.md` first. The flash scripts expect the firmware to be downloaded next to them (it isn't in this repo). Flashing can brick a phone: back up first, and check the images before you flash.

```sh
./setup-oneplus6.sh [--journal-sync] [user@host]
```

## Not included

Firmware, `persist.img` and the EFS backup are device-unique or too large and are deliberately left out. Back up your own `persist` and EFS before flashing anything.

## License

GPL-3.0-or-later. See `LICENSE`.
