#!/bin/sh
# !! NEW ZEALAND / One NZ (Mighty Mobile) SPECIFIC !!
# Parts of this script are written for one SIM on one network, One NZ
# (MCC/MNC 530-01) in New Zealand, and will give wrong settings elsewhere:
#   - the mobile data APN ("vodafone", connection "Mighty"), set below
#   - the VoLTE modem profile (Netherlands-VoLTE-Vodafone), installed via
#     volte/volte-mcfg and volte/volte-watchdog
#   - the MMS settings (documented in docs/daily-driver-setup.md)
# The panel, keyboard, scaling, privacy switch and call-audio parts are
# generic to the OnePlus 6. If you are on another carrier, review or remove
# the carrier-specific steps before running.
#
# Configure a OnePlus 6 running a fresh Nura (postmarketOS) + Phosh install
# as a daily driver: everything in docs/daily-driver-setup.md that can be
# scripted. Run it from the PC, from this folder's copy.
#
# Before running:
#   1. Flash Nura (nura-install-report.md), and finish the first setup on
#      the phone. Stay logged in to Phosh: the user settings need the
#      running session.
#   2. Enable SSH on the phone (sudo systemctl enable --now sshd) and copy
#      your key (ssh-copy-id user@172.16.42.1).
#
# Usage: ./setup-oneplus6.sh [--journal-sync] [user@host]
#   --journal-sync  also write the journal to disk every second (for
#                   catching CrashDump boots; meant to be temporary)
#
# Safe to run again: every step checks or overwrites rather than adds.
# It asks for the phone's sudo password once.
set -e

journal_sync=0
if [ "$1" = "--journal-sync" ]; then
    journal_sync=1
    shift
fi
host=${1:-user@172.16.42.1}
here=$(cd "$(dirname "$0")" && pwd)
panel_repo=${PANEL_REPO:-$HOME/Projects/GitHub/AntzCode/og-home-panel}
stage=.oneplus6-setup  # On the phone, in the user's home

# Added to the stock image's package list (/etc/apk/world in
# nura-phosh-v26.06): og-home-panel's dependencies, then apps.
packages="gtk4-layer-shell wtype keepassxc gnome-system-monitor htop
gnome-sound-recorder"

step() {
    printf '\n== %s\n' "$*"
}

step "Checking the phone"
ssh -o ConnectTimeout=10 "$host" 'test -S /run/user/$(id -u)/bus' || {
    echo "No session bus on the phone: log in to Phosh first." >&2
    exit 1
}
[ -x "$panel_repo/tools/deploy.sh" ] || {
    echo "og-home-panel not found at $panel_repo (set PANEL_REPO)." >&2
    exit 1
}

step "Copying files"
ssh "$host" "rm -rf $stage && mkdir -p $stage"
scp -q "$here/volte/volte-mcfg" "$here/volte/volte-mcfg.service" \
    "$here/volte/volte-watchdog" "$here/volte/volte-watchdog.service" \
    "$here/volte/ims-status.py" \
    "$here/privacy-switch/privacy-switch" \
    "$here/privacy-switch/privacy-switch.service" \
    "$here/call-audio/call-mic-mute" "$here/call-audio/call-mic-mute.service" \
    "$host:$stage/"

step "System setup (sudo)"
# Copied as a file and run from there: fed to sudo on stdin, its password
# prompt would read the script's lines.
ssh "$host" "cat > $stage/root.sh" <<'ROOT'
set -e
stage=$1
journal_sync=$2
shift 2

echo "- packages: $*"
apk add "$@"

echo "- haptics: give the vibration motor to the feedbackd group"
mkdir -p /etc/udev/rules.d
echo 'SUBSYSTEM=="input", KERNEL=="event*", ATTRS{name}=="spmi_haptics", GROUP="feedbackd", MODE="0660"' \
    > /etc/udev/rules.d/73-spmi-haptics-group.rules
udevadm trigger -s input

echo "- VoLTE carrier profile at boot"
install -m 755 $stage/volte-mcfg /usr/local/bin/volte-mcfg
install -m 644 $stage/volte-mcfg.service /etc/systemd/system/

echo "- VoLTE watchdog"
install -m 755 $stage/ims-status.py /usr/local/bin/ims-status
install -m 755 $stage/volte-watchdog /usr/local/bin/volte-watchdog
install -m 644 $stage/volte-watchdog.service /etc/systemd/system/

echo "- privacy mode on the alert slider"
install -m 755 $stage/privacy-switch /usr/local/bin/privacy-switch
install -m 644 $stage/privacy-switch.service /etc/systemd/system/

systemctl daemon-reload
systemctl enable volte-mcfg.service
systemctl enable volte-watchdog.service
systemctl restart volte-watchdog.service
systemctl enable privacy-switch.service
systemctl restart privacy-switch.service

if [ "$journal_sync" = 1 ]; then
    echo "- journal: sync every second"
    mkdir -p /etc/systemd/journald.conf.d
    printf '[Journal]\nSyncIntervalSec=1s\n' \
        > /etc/systemd/journald.conf.d/sync.conf
fi
ROOT
ssh -t "$host" "sudo sh $stage/root.sh \$HOME/$stage $journal_sync" $packages

step "User setup"
ssh "$host" sh -s <<'USER'
set -e
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
stage=$HOME/.oneplus6-setup

echo "- call mute fix"
mkdir -p ~/.local/bin ~/.config/systemd/user
install -m 755 $stage/call-mic-mute ~/.local/bin/
install -m 644 $stage/call-mic-mute.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable call-mic-mute.service
systemctl --user restart call-mic-mute.service

echo "- settings"
gsettings set org.gnome.desktop.interface clock-format 24h
# og-home-panel's Back button reads apps through accessibility.
gsettings set org.gnome.desktop.interface toolkit-accessibility true
gsettings set org.gnome.desktop.session idle-delay 180
# Scale to fit, only for apps too big for the screen. Never globally: it
# breaks Firefox.
for app in org-gnome-systemmonitor org-keepassxc-keepassxc; do
    gsettings set sm.puri.phoc.application:/sm/puri/phoc/application/$app/ \
        scale-to-fit true
done

# NZ-specific: One NZ / Mighty Mobile APN. Change or remove for other carriers.
echo "- mobile data APN (One NZ / Mighty)"
if nmcli -t -f NAME connection show | grep -qx Mighty; then
    nmcli connection modify Mighty gsm.apn vodafone
else
    nmcli connection add type gsm ifname '*' con-name Mighty \
        gsm.apn vodafone connection.autoconnect yes
fi

rm -rf "$stage"
USER

step "og-home-panel"
"$panel_repo/tools/deploy.sh" "$host"

cat <<'DONE'

== Done. Still to do by hand (see docs/daily-driver-setup.md):
- Wi-Fi: connect in Settings.
- Firefox: add-on enhanced-h264ify (VP9 and AV1 blocked), and
  gfx.webrender.all = true in about:config (section 4).
- MMS: set CarrierMMSC, MMS_APN and CarrierMMSProxy in
  ~/.mms/modemmanager/mms (see docs/daily-driver-setup.md, MMS section).
- Reboot, then check: journalctl -b -u volte-mcfg, -u volte-watchdog,
  -u privacy-switch.
DONE
