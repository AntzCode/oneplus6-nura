# Daily-driver setup: Nura + Phosh on the OnePlus 6

These are the changes made after installing Nura (see `nura-install-report.md`) to make the phone usable day to day. They are written so they can be repeated on a rebuilt phone or another installation.

Tested on Nura v26.06 with phosh 0.55.0, phoc 0.55.1, stevia 0.55.0 and GTK 4.22.4.

## Setup script

`setup-oneplus6.sh` applies everything below that can be scripted, on a freshly flashed phone. Run it from the PC, from this folder:

```sh
./setup-oneplus6.sh                  # or: ./setup-oneplus6.sh --journal-sync user@172.16.42.1
```

Before running: flash Nura, finish the phone's first setup and stay logged in to Phosh, enable SSH and copy your key (see "Access"). It asks for the sudo password once, and is safe to run again.

What it does:
- **Packages** added to the stock image (stock list: `/etc/apk/world` in the `nura-phosh-v26.06` image): `gtk4-layer-shell wtype` (og-home-panel), `keepassxc gnome-system-monitor htop gnome-sound-recorder`. Not included: `postmarketos-ui-plasma-mobile` and the hands-free test's `py3-qt6 py3-dbus py3-vobject py3-psutil`, which were installed on the first phone but aren't wanted.
- **System:** the haptics udev rule, `volte-mcfg` and `privacy-switch` services, and with `--journal-sync` the journal sync.
- **User:** the `call-mic-mute` service, the settings below, and the mobile data APN (`Mighty`, APN `vodafone`; see `nura-install-report.md`).
- **og-home-panel:** runs its `tools/deploy.sh` (repo at `~/Projects/GitHub/AntzCode/og-home-panel`, or set `PANEL_REPO`), which also installs its autostart.

Settings it applies (all found by comparing the phone's `dconf dump /` with the image, which has no user settings):
- `org.gnome.desktop.interface clock-format '24h'`: with Phosh's 12-hour default, "PM" pushed the status icons under the notch (the gsettings default reads `'24h'`, but Phosh used 12-hour until it was set explicitly).
- `org.gnome.desktop.interface toolkit-accessibility true`: og-home-panel's Back button reads apps through AT-SPI.
- `org.gnome.desktop.session idle-delay 180`: screen off after 3 minutes.
- Scale to fit for System Monitor and KeePassXC (section 3).

Left as they are (defaults, or chosen in the phone's settings): rotation lock, location, Phosh's quick settings and notification wake-up.

By hand afterwards: Wi-Fi, and Firefox's add-on and settings (section 4).

## Access

- USB networking: phone `172.16.42.1`, PC `172.16.42.2`.
- SSH user: `user` (default image user). Enable SSH on the phone with `sudo systemctl enable --now sshd`, then `ssh-copy-id user@172.16.42.1`.
- `sudo` needs the password. Run it from the PC with `ssh -t user@172.16.42.1 sudo …`.
- `gsettings` over SSH needs the session bus: `export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/10000/bus` (10000 is the uid of `user`).

## Problems found in daily use

1. There is no system back button.
2. The on-screen keyboard has no Ctrl or Alt keys.
3. Apps that are too big for the screen can't be zoomed out, moved or resized.
4. The battery drains about twice as fast as on the Galaxy A31 (Android) while watching YouTube in Firefox.

## What the stock install has

- The on-screen keyboard is **Stevia** (`phosh-osk-stevia`), not Squeekboard. Squeekboard is in the repo but isn't installed.
- Stevia already has a Terminal layout with Ctrl, Alt and other shortcuts. Its shortcut row comes from the `mobi.phosh.osk.Terminal shortcuts` setting. Default: `['<ctrl>', '<alt>', 'Left', 'Up', 'Down', 'Right', '<ctrl>r', 'Home', 'End', '<ctrl>w', '<alt>b', '<alt>f', '<ctrl>v', '<ctrl>c', '<ctrl><shift>v', '<ctrl><shift>c', 'Menu']`.
- Stevia can be shown and hidden over D-Bus: `sm.puri.OSK0` → `/sm/puri/OSK0` → `SetVisible(b)`, plus a `Visible` property.
- Phosh shortcut for the app view: `org.gnome.shell.keybindings toggle-application-view` = `<Super>a`. `toggle-overview` has no shortcut by default.
- Phosh has no setting to hide its bottom home bar.
- Phoc defaults: `sm.puri.phoc scale-to-fit false`, `auto-maximize true`.

## Haptics fix (vibration not working)

Symptom: no vibration at all, even with the feedback profile on quiet or full.

Cause: a race at login. feedbackd (D-Bus activated, unit `dbus-:1.1-org.sigxcpu.Feedback@0.service`) opens the haptics device `/dev/input/event4` (`spmi_haptics`) before logind applies the `uaccess` ACL. It logs `Failed to init vibra device: Unable to open '/dev/input/event4': Permission denied` and never retries. The device itself is `root:input 0660`, and `user` isn't in `input`.

Fix (2026-10-18): give the device to the `feedbackd` group, which `user` is already in. Nura has no `/etc/udev/rules.d/`, so create it:

```sh
sudo mkdir -p /etc/udev/rules.d
echo 'SUBSYSTEM=="input", KERNEL=="event*", ATTRS{name}=="spmi_haptics", GROUP="feedbackd", MODE="0660"' \
  | sudo tee /etc/udev/rules.d/73-spmi-haptics-group.rules
sudo udevadm trigger -s input
```

Check: `ls -l /dev/input/event4` should show group `feedbackd`. To fix it immediately without a reboot, restart feedbackd with `systemctl --user stop 'dbus-:1.1-org.sigxcpu.Feedback@0.service'`. D-Bus starts it again on the next request.

Status: vibration confirmed working after the restart. Not yet tested across a reboot.

The panel's touch tick uses the `button-pressed` event (7 ms at 0.2 strength). feedbackd plays it only in the quiet and full profiles, not in silent, and apps can't override that.

## VoLTE carrier profile at boot

VoLTE on One NZ (Mighty) needs the modem's `Netherlands-VoLTE-Vodafone` carrier profile (background in `nura-install-report.md`, "VoLTE working"). The modem selects `Oversea-Commercial_DS` again at every boot, which has no IMS, so calls fail. A boot service switches it back.

Files are in `volte/`:
- `volte-mcfg`: waits until the modem has registered (up to 5 min), checks the active profile with `qmicli`, and activates the Netherlands one if needed. Retries the profile list, because it sometimes hangs.
- `volte-mcfg.service`: a oneshot system unit, run after ModemManager.
- `ims-status.py`: shows the IMS registration status (read-only, no root needed).

Install (2026-10-18):

```sh
scp volte/volte-mcfg volte/volte-mcfg.service user@172.16.42.1:/home/user/
ssh -t user@172.16.42.1 'sudo install -m 755 /home/user/volte-mcfg /usr/local/bin/volte-mcfg && sudo install -m 644 /home/user/volte-mcfg.service /etc/systemd/system/volte-mcfg.service && sudo systemctl daemon-reload && sudo systemctl enable volte-mcfg.service'
```

Check after a boot: `journalctl -b -u volte-mcfg` should show `active profile: Oversea-Commercial_DS` and then `Successfully requested config activation`, about 25 s after boot. `python3 ims-status.py` should show `ims_registration_status: 2`. Data drops for about 2 s while the profile switches.

Status: tested across one reboot; IMS registered afterwards. Speaker and mute don't work during calls yet (a gap in the call sound config, not VoLTE).

**Fix (2026-10-24): `timeout -k`.** At one boot the first `qmicli --pdc-list-configs` hung, and the service stayed in "activating" for 6 h with the wrong profile: SMS worked, but calls didn't (no IMS voice, `ims_voice_service_enabled: False`). `timeout 30` didn't help, because qmicli catches SIGTERM to release its QMI client and hung in that cleanup, and BusyBox's `timeout` sends only SIGTERM. The script now uses `timeout -k 5 …`, which follows up with SIGKILL (checked on the phone). Reinstall it with the commands above. To recover a hung run without rebooting: `sudo systemctl kill -s KILL volte-mcfg && sudo systemctl restart volte-mcfg`.

**Mobile data with no traffic (2026-10-24).** The same day, mobile data connected (APN `vodafone`, an address assigned), but the modem passed nothing back: `rmnet_ipa0` received 0 packets, even from the carrier's DNS. Toggling mobile data didn't help; a reboot fixed it. Cause unknown.

**IMS lost while running (2026-10-25).** After a day's uptime, calls stopped working: outgoing calls stayed on "Calling…" for 30 s, and incoming calls went to voicemail. SMS and data still worked. The modem was registered on LTE with the right profile, but `ims_registration_status: 0`. Calls had worked after boot. IMS dropped some time after 13:20, probably at a network detach (one at 19:54, with data then stalling as `OutOfCall`, and an `implicitly-detached` reject at 10:14 during the failed call). ModemManager doesn't log IMS, so the exact time is unknown. `mmcli -m any -d` / `-e` didn't bring IMS back; a reboot did. Privacy mode wasn't involved: it only touches mic gains and camera permissions.

## VoLTE watchdog

`volte/volte-watchdog` (system unit `volte-watchdog.service`, root) checks IMS every 60 s through `ims-status`, which is `volte/ims-status.py` installed as `/usr/local/bin/ims-status`. After 3 checks in a row without IMS voice, with the modem on the network and no call going on, it tries these fixes in order, 90 s apart:
1. Re-activate `Netherlands-VoLTE-Vodafone` (a SIM refresh).
2. Restart the modem's processor (remoteproc `4080000.remoteproc`: stop, then start), then run `volte-mcfg`.
3. Show a critical notification asking for a reboot, then try again after 30 min.

Neither fix has been tried yet on a modem that really lost IMS. The snapshots will show which one works.

Logs: `journalctl -u volte-watchdog`, one line per event. On IMS lost, on every failed round of fixes and when IMS comes back, it writes a snapshot to `/var/log/volte-watchdog/` (it keeps the last 100), with a timestamp and the event in the file name. A snapshot holds ModemManager's state, the IMS status, the active profile, the last 2 h of the ModemManager log and the modem's kernel messages. The IMEI, phone number and SIM IDs are left out. `volte-watchdog --check` prints the same without fixing anything.

Installed by `setup-oneplus6.sh`. To install only the watchdog:

```sh
scp volte/volte-watchdog volte/volte-watchdog.service volte/ims-status.py user@172.16.42.1:/home/user/
ssh -t user@172.16.42.1 'sudo install -m 755 /home/user/ims-status.py /usr/local/bin/ims-status && sudo install -m 755 /home/user/volte-watchdog /usr/local/bin/volte-watchdog && sudo install -m 644 /home/user/volte-watchdog.service /etc/systemd/system/volte-watchdog.service && sudo systemctl daemon-reload && sudo systemctl enable --now volte-watchdog.service'
```

## Call audio: mute fix, and what doesn't work yet

**Mute fix (2026-10-18).** The Calls app's mute button did nothing: `callaudiod` mutes the PulseAudio source, but call audio goes from the mic to the modem inside the DSP and never passes through PulseAudio. The fix is a user service that mirrors that mute onto `DEC7 Volume`, the bottom mic's digital gain in the codec (0 = silent, 75 = the UCM boot value). Files are in `call-audio/`. No root needed:

```sh
scp call-audio/call-mic-mute user@172.16.42.1:/home/user/.local/bin/
ssh user@172.16.42.1 'mkdir -p ~/.config/systemd/user'
scp call-audio/call-mic-mute.service user@172.16.42.1:/home/user/.config/systemd/user/
ssh user@172.16.42.1 'export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/10000/bus; systemctl --user daemon-reload && systemctl --user enable --now call-mic-mute.service'
```

Check: `journalctl --user -u call-mic-mute` logs `DEC7 Volume 75 -> 0` on mute and `0 -> 75` on unmute. Tested on a real call: the other side hears nothing while muted.

**Known issues:**
- **Don't tap speaker during a call.** There's no speakerphone. The audio stays in the earpiece but goes very quiet and stays quiet after speaker is turned off; the next call is normal again. See `nura-install-report.md`, "Call audio prototype", for why speakerphone needs kernel work.
- **Earpiece distortion at normal volume.** PulseAudio maps the call volume onto `RX0 Digital Volume`, whose range goes up to +40 dB (84 = 0 dB). At 55% it was 109 (+25 dB), which clips. Workaround: keep the in-call volume low, or set it directly during a call with `amixer -c0 cset name='RX0 Digital Volume' 84`.
- Restarting PulseAudio over SSH: Phosh autospawns it. A `pulseaudio --start` from an SSH shell dies with the session; the session respawns it on the next client.

## Privacy mode on the alert slider (2026-10-19)

The alert slider (input device "Alert slider", `ABS_SND_PROFILE`: top 0, middle 1, bottom 2) still sets the sound profile through feedbackd's `fbd-alert-slider` user service (top silent, middle vibrate, bottom ring). The top position is now also **privacy mode**: cameras and microphones off.

| Position | Sound | Cameras and mics |
|---|---|---|
| Top | Silent | Off |
| Middle | Vibrate | On |
| Bottom | Ring | On |

A root system service does it. Files are in `privacy-switch/`:
- `privacy-switch`:
  - **Cameras:** makes the camera device files root-only (every video4linux and media device except the video codec's, `qcom-venus`), then restarts the session's WirePlumber, so it can't open them again and no app sees a camera. Leaving privacy mode restores `root:video 0660` and restarts WirePlumber again.
  - **Don't unbind the camera driver (`qcom-camss`).** The first version did. WirePlumber holds the cameras open all the time; after the unbind it showed only the dead devices (Snapshot hung for ~3 min, then "no camera" even after binding again), and restarting it left the process stuck in the kernel, unkillable until a reboot.
  - **Mics:** sets every mic's digital gain in the codec (`DEC0`–`DEC8 Volume`) to 0. That silences calls too, since call audio never passes through a capture device (see "Call audio"). It watches `amixer events` and sets back to 0 any gain changed during privacy mode (UCM, `call-mic-mute`).
  - **Leaving the top position:** restores the saved gains (`/run/privacy-switch/gains.json`; UCM's boot values if there are none).
  - **State file:** while privacy mode is on, the service creates `/run/privacy-switch/on` (folder `0755`, readable by everyone), as a hook for a future indicator. Wanted: an icon next to the Bluetooth icon in Phosh's top bar, but Phosh has no hook for status icons, so it's on hold. An indicator in og-home-panel's bar was tried and taken out again (2026-10-19), undecided how it should affect that bar.
  - **At start:** applies the slider's current position, and re-checks every 2 s. At login, logind gives the session access to the cameras again (seen in a boot with the slider at the top, ~45 s after boot); the re-check locks them again and restarts WirePlumber.
- `privacy-switch.service`: a system unit, started at boot.

Install:

```sh
scp privacy-switch/privacy-switch privacy-switch/privacy-switch.service user@172.16.42.1:/home/user/
ssh -t user@172.16.42.1 'sudo install -m 755 /home/user/privacy-switch /usr/local/bin/privacy-switch && sudo install -m 644 /home/user/privacy-switch.service /etc/systemd/system/privacy-switch.service && rm /home/user/privacy-switch /home/user/privacy-switch.service && sudo systemctl daemon-reload && sudo systemctl enable --now privacy-switch.service'
```

Check: `journalctl -b -u privacy-switch` logs `privacy mode on|off`, `cameras on|off` and each gain change.

Status: the slider and mic part works (gains 75/84 -> 0 and back; a gain set during privacy mode is reset within a second). Camera part tested 2026-10-19: at the top, Snapshot shows no camera (no hang); back down, it works again. While Snapshot was open in privacy mode, something set `DEC7` back to 75 twice, and the service reset it within a second. A boot with the slider at the top works: privacy mode is on from the start (with the login gap above, now at most 2 s).

Known limits:
- Leaving privacy mode during a muted call unmutes the call mic (the gains are restored).
- A camera app that's open when privacy mode starts loses its camera when WirePlumber restarts; untested whether apps cope.

## Camera (2026-10-22)

Sensors (all on `qcom-camss`, used through libcamera's `simple` pipeline with its software ISP):

| Camera | Sensor | Device tree node | PipeWire node |
|---|---|---|---|
| Front | imx371 | `cci@ac4a000/i2c-bus@0/camera@10` | `libcamera_input._base_soc_0_cci_ac4a000_i2c-bus_0_camera_10` |
| Back, main | imx519 (autofocus motor `lc898217xc`) | `cci@ac4a000/i2c-bus@0/camera@1a` | `…_i2c-bus_0_camera_1a` |
| Back, second | imx376k | `cci@ac4a000/i2c-bus@1/camera@10` | `…_i2c-bus_1_camera_10` |

- Each camera streams on its own at 1920x1080, ~30 fps (tested through PipeWire with GStreamer).
- **Only one at a time.** Opening a second camera while one streams fails: `Failed to setup link 'msm_csiphy2'[1] -> 'msm_csid0'[0]: Resource busy`. Closing both recovers.
- **Snapshot** (stock) opens the new camera before closing the old, so switching to a back camera stays black, and Snapshot then refuses every switch ("Could not set camera, where are taking a picture") until it's quit.
- **Plasma Camera** (`plasma-camera`, tried 2026-10-22, not kept: same picture quality and lag as Snapshot) stops the viewfinder first, and its switch button cycles front → main back → second back without errors, and all three show a picture. Its viewfinder runs at the full sensor size (4648x3496 front and main, 2584x1940 second) and is a bit laggy. It has a video resolution setting (Auto, 540p–2160p); untested whether it also lowers the viewfinder's size.
- Picture quality is limited by the software ISP for every app: no sensor helpers (`Failed to create camera sensor helper`), no libcamera tuning file for the imx519 (`uncalibrated.yaml`), and no autofocus.
- Not usable: Megapixels 2.x (no `oneplus,enchilada` config in libmegapixels) and Millipixels (Librem 5 only).

## Bluetooth hands-free app (tested 2026-10-18, not in use)

Installed for the test: `sudo apk add py3-qt6 py3-dbus py3-vobject py3-psutil`. The reviewed copy of handsfree-linux v1.2.6 is in `~/handsfree-linux` on the phone (no `.git`), with its config in `~/.config/handsfree/config.toml` (changed: `show_main_window_on_start = true`, `country_code = "64"`) and the imported contacts in its local database. Launch for testing:

```sh
systemd-run --user --unit=handsfree --working-directory=/home/user/handsfree-linux -E WAYLAND_DISPLAY=wayland-0 -E QT_QPA_PLATFORM=wayland -E QT_SCALE_FACTOR=0.8 /usr/bin/python3 main.py
```

It doesn't carry call audio on this phone (see `nura-install-report.md`, "Bluetooth hands-free test"). Don't leave it connected to the A31: the A31 then sends its calls to the OnePlus 6, where there's no audio. The A31 is still paired; remove the pairing or keep Bluetooth off on the OnePlus 6.

## Journal sync (catching CrashDump boots)

The phone sometimes boots into Qualcomm CrashDump Mode (see `nura-install-report.md`, "CrashDump boots"). The reset comes from firmware, so the kernel leaves no panic record, and journald's default sync interval (5 min) loses the last seconds of the failed boot.

Fix (2026-10-18): write the journal to disk every second.

```sh
sudo mkdir -p /etc/systemd/journald.conf.d
printf "[Journal]\nSyncIntervalSec=1s\n" | sudo tee /etc/systemd/journald.conf.d/sync.conf
```

It takes effect after a reboot, or after `sudo systemctl restart systemd-journald`. After a failed boot, read it with `journalctl --list-boots` and `journalctl -b -1`. Remove the file once the CrashDump issue is understood, since it means more writes to flash.

## 4. Battery: YouTube in Firefox (2026-10-18)

Measured over SSH while charging over USB, as the phone's own draw: USB power in minus power into the battery, averaged over 30 s. Firefox 140.12.0esr, same video each time.

| Playback | Power | Decoder (RDD Process), % of one core |
|---|---|---|
| Idle, Firefox on Google's search page | 1.56 W | — |
| VP9 1080p, software WebRender | 2.53 W | 63% |
| VP9 1080p, hardware WebRender | 2.59 W | 72% |
| H.264 1080p | 2.40 W | 67% |
| H.264 1080p, hardware decoding forced on | 2.59 W | 64% |
| **H.264 720p** | **2.09 W** | **32%** |
| H.264 480p | 2.01 W | 20% |
| H.264 480p, Venus hardware decoder (forced) | 1.71 W | 0%, but the video area was black (sound only) |

Findings:
- **Video is decoded on the CPU.** VP9 has no hardware decoder in Firefox (`FEATURE_FAILURE_VIDEO_DECODING_MISSING`). For H.264, Firefox normally doesn't use the Venus decoder (`qcom-venus-decoder`; it is `/dev/video12` or `/dev/video13`, and the number can change between boots). With `media.hardware-video-decoding.force-enabled = true`, Firefox's V4L2 path did use Venus once, after a switch to 480p: decoder CPU dropped to 0% and power to 1.71 W, but the video area stayed black (sound only) until the page was reloaded, which went back to software decoding. So the hardware decoding works, but its frames don't reach the screen. FFmpeg 8.1 has the V4L2 decoders (`h264_v4l2m2m`, `vp9_v4l2m2m`, …).
- **Hardware WebRender** (`gfx.webrender.all = true`) works (Compositing: `WebRender`), but saved nothing measurable for video. The GPU stays at its minimum 257 MHz either way, and the Adreno 630 has plenty of headroom.
- **Resolution matters most, down to 720p.** YouTube picks 1080p even though the inline player is only about 1080×453 device pixels. 720p halves the video's cost (about +1.0 W → +0.5 W). 480p saves only another 0.08 W, because the page and Firefox's main process cost the same at any resolution.
- At 720p, YouTube's page scripts (about 48% of a core) and Firefox's main process (about 44%) each use more CPU than the decoder.

Current Firefox setup (profile `zlfv7j67.default-release`):
- Add-on **enhanced-h264ify**, with VP9 and AV1 blocked, so YouTube serves H.264 (`avc1`).
- `gfx.webrender.all = true`, and `gfx.webrender.software = false`. No measured benefit; keep only if Firefox stays stable, otherwise reset both.
- `media.hardware-video-decoding.force-enabled`: **reset it** (back to false). Forced on, it caused black video.
- Watch at 720p. 480p barely saves more.

mpv 0.41 + yt-dlp 2026.08.19 (with deno), same video at 720p H.264, mpv window full screen. Installed with `sudo apk add mpv yt-dlp`:

| mpv options | Power | mpv CPU | GPU |
|---|---|---|---|
| `--hwdec=v4l2m2m-copy` (Venus, frames copied back to RAM) | 2.47 W | 66% | 456 MHz |
| `--profile=fast --hwdec=v4l2m2m-copy` | 2.06 W | 69% | 257 MHz |
| `--profile=fast --hwdec=v4l2m2m`: "Unsupported hwdec", so software decoding | 2.06 W | 78% | 257 MHz |

- Venus decoding works in mpv (`Using hardware decoding (v4l2m2m-copy)`, `/dev/video12` open), but it saves nothing measurable: copying frames back costs about what decoding them in software does. Zero-copy `v4l2m2m` isn't available with Alpine's FFmpeg.
- mpv's default rendering (gpu-next, high-quality scaling) costs about 0.4 W extra; always use `--profile=fast` on this phone.
- **Conclusion:** for battery, mpv is no better than Firefox at 720p with H.264 (2.06 W vs 2.09 W). Not worth pursuing for power. mpv and yt-dlp were uninstalled again the same day (`sudo apk del mpv yt-dlp`). Format selection that works for videos with dubbed audio tracks: `--ytdl-format="bestvideo[height<=720][vcodec^=avc1]+bestaudio[ext=m4a][format_note*=original]"`.

## 3. Scale to fit (apps too big for the screen)

Phoc can shrink a window that is bigger than the screen so that all of it shows.

```sh
gsettings set sm.puri.phoc scale-to-fit true    # all apps
gsettings set sm.puri.phoc scale-to-fit false   # undo
```

It can also be turned on for single apps in **Phosh Mobile Settings → Compositor**.

Rejected options:
- Lowering the global display scale: everything gets too small.
- `auto-maximize false` (floating windows): impractical to move windows by touch.

Per app (relocatable schema; the path ends in the app id, e.g. from the `.desktop` name):

```sh
gsettings set sm.puri.phoc.application:/sm/puri/phoc/application/<app-id>/ scale-to-fit true
```

og-home-panel does this for the app you're in: long-press ⋯, then **Fit *app* to the screen** (tap it again, as *Stop fitting…*, to remove the setting).

**Don't enable it globally.** Turned on for all apps on 2026-10-18, it broke Firefox (confirmed: Firefox went back to normal the moment the setting was turned off): Firefox switched from the mobile UI (mobile-config-firefox) to the desktop UI, and taps no longer landed (videos wouldn't open). The global setting was turned off again the same day. Use it only per app, for apps that are actually too big.

## 2. Ctrl and Alt on the keyboard

Decision: stay with Stevia rather than switch to Squeekboard.

Status: still to do. Get Ctrl and Alt into the normal layout, not only the Terminal layout.

## 1. Navigation panel: og-home-panel

Since 2026-10-18 the panel is its own project: **og-home-panel**, at `github.com/AntzCode/og-home-panel` (public), cloned to `~/Projects/GitHub/AntzCode/og-home-panel`. App ID: `com.antzcode.og_home_panel`. It started here as `navpanel/`. The repo's README covers its behavior. This section keeps the history and the OnePlus 6-specific notes.

A layer-shell panel of our own that sits **above** the Phosh home bar. Replacing the bar instead would mean patching and rebuilding phosh after every update. That can come later.

Buttons:

| Button | Tap | Long press |
|---|---|---|
| Back | Android-style back (see below) | Escape (closes dialogs) |
| Apps | Phosh overview (keyboard kept closed) | Running-apps switcher |
| Keyboard | Show or hide Stevia | |
| More (⋯) | Show or hide the quick-actions row: undo, redo, cut, copy, paste, select word, select all | Panel menu: fit the app to the screen, About |

How it works:
- Python 3 + GTK 4 + gtk4-layer-shell. It anchors to the bottom edge and reserves `BAR_HEIGHT` px. The quick-actions row overlaps the app instead of resizing it.
- It's on the **overlay** layer. On the top layer, Phosh's opened overview and Stevia were drawn over it, because surfaces on the same layer stack in the order they were raised. Phoc reserves the overlay layer's exclusive zone first, so the others now sit above the panel.
- The lock screen is on the overlay layer too, so the panel hides itself while logind's `LockedHint` is set on the session (Phosh sets it on lock). Phosh's `org.gnome.ScreenSaver` "active" follows screen blanking instead: it goes false when the screen wakes on the lock screen, so it can't be used.
- Autostart (since 2026-10-18): `og-home-panel/tools/deploy.sh` installs `~/.config/autostart/com.antzcode.og_home_panel.desktop` with an absolute `Exec=/home/user/.local/bin/og-home-panel`. systemd's autostart generator looks up `Exec=` without `~/.local/bin` and silently skips the entry otherwise. gnome-session launches it itself, in a scope named `app-gnome-com.antzcode.og_home_panel-<pid>.scope`. `dev-restart.sh` stops that scope too, because a second launch only re-activates the running copy.
- Keyboard mode is `NONE`, so the panel never takes focus and the keys go to the app.
- Keys are sent with `wtype`, which uses the Wayland virtual-keyboard protocol.
- gtk4-layer-shell must load before libwayland, so Python is started with `LD_PRELOAD=/usr/lib/libgtk4-layer-shell.so.0`.
- **Android-style back.** Wayland has no API that says whether an app has back history, so the panel uses the accessibility tree (AT-SPI, `Atspi` from py3-gobject3) instead:
  1. Find the focused window: the one whose state is `ACTIVE`.
  2. If it belongs to `phosh`, the overview is open, so close it (Super+A).
  3. If it's a dialog, alert or file chooser, send Escape.
  4. Otherwise search the window for a push or toggle button whose name starts with "Back" or "Go back". The search skips web page, terminal and text subtrees for speed. If the button is enabled and visible, press it through its AT-SPI action.
  5. If there's no usable Back button, open the Phosh overview (Super+A). The app keeps running in the background, as on Android.
  - Speed: pressing Firefox's Back button through AT-SPI added about 0.8 s, because Firefox handles accessibility actions slowly. For apps in `BACK_KEY_APPS` (just Firefox for now), the panel uses AT-SPI only to check that Back is available, then sends Alt+Left. Other apps still get the AT-SPI press, and its time is logged as `back: action …s`.
  - Every button gives a haptic tick on touch down through feedbackd (`Lfb`, event `button-pressed`), so a tap is felt even before its action finishes.
  - It runs in a helper process (`og-home-panel --atspi-helper`, started by the panel), so the panel doesn't freeze. libatspi can't share a process with GTK's main loop: its lazily opened connections always attach to the default main context. Threads gave a segfault, then lost events and `g_source_unref` warnings. The helper also hides the panel while Phosh's quick-settings drawer is open, by watching the drawer's drag handle over AT-SPI. In Firefox it takes about 0.18 s. Before skipping page content it took 0.64 s.
  - Probing Firefox through AT-SPI switches on its accessibility support until it restarts. That alone hasn't caused problems.
- Note: in a terminal, Ctrl+C is interrupt, not copy.

Packages: `sudo apk add gtk4-layer-shell wtype`. python3, py3-gobject3 and libadwaita are already in the image.

Deploy from the repo: `tools/deploy.sh`. It copies `og-home-panel` and `dev-restart.sh` to `~/.local/bin/` on the phone and (re)starts the panel as the transient systemd user unit `og-home-panel`. Logs: `journalctl --user -u og-home-panel`. Stop it with `systemctl --user stop og-home-panel`.

The script preloads gtk4-layer-shell itself (it re-executes with `LD_PRELOAD` set), so no wrapper is needed.


Pitfalls found while testing:
- The preload library is `/usr/lib/libgtk4-layer-shell.so.0`. A wrong `LD_PRELOAD` path is silently ignored, and the log then shows "Failed to initialize layer surface".
- A process started with `nohup … &` from SSH gets killed when the SSH session ends (systemd cleans up the session scope). Use `systemd-run --user` instead.
- `pkill -f <script>` run through `ssh host '…'` also matches the remote shell's own command line and kills it.

Status: in daily use since 2026-10-19; see the repo's README for current behavior. It restarts itself after a crash.

## MMS and duplicate SMS (2026-11-08)

Symptom: Chatty showed a constant "Chatty cannot process 40 MMSes… MMSC is not configured" notification, and some SMS arrived several times (first noticed 2026-10-26 12:36).

Cause of the notification: mmsd-tng (`~/.mms/modemmanager/mms`) was on placeholder values (`http://mms.invalid`, `apn.invalid`), so 40 incoming MMS notifications queued unprocessed. The duplicate-SMS cause is not confirmed; the network may be re-sending unacknowledged MMS notifications.

Fix (one NZ / Vodafone NZ, 530-01). Stop `mmsd-tng` first, because it rewrites the file:
- `CarrierMMSC=http://pxt.vodafone.net.nz/pxtsend`
- `MMS_APN=live.vodafone.com` (the MMS APN in Android 11's list for 530-01)
- `CarrierMMSProxy=10.202.2.60:8080`
- Move the stale queue files (everything except `mms`) out of `~/.mms/modemmanager/`, then `systemctl --user start mmsd-tng`.

The MMSC and proxy values are unverified until a real MMS is received. Queued notifications pointed at `pxt.one.nz`, which may be the current host. A backup of the old queue is at `~/mms-backup-20261108-081416` on the phone.
