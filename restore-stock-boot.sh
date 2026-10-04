#!/usr/bin/env bash
# Restore the shared pre-experiment boot image/config, keeping both packages.
set -euo pipefail

[[ $EUID == 0 ]] || { printf 'Run with sudo from a working Linux boot.\n' >&2; exit 1; }
backup=/var/lib/asahi-fairydust/backups/pre-fairydust-20261001
[[ -s $backup/boot.bin && -s $backup/grub.cfg && -s $backup/archives.sha256 ]]
findmnt --mountpoint /boot >/dev/null
sha256sum --check "$backup/archives.sha256"

# Do not overwrite boot files in place: an interruption would leave them partial.
cp "$backup/boot.bin" /boot/m1n1/boot.bin.restore
cmp "$backup/boot.bin" /boot/m1n1/boot.bin.restore
mv -f /boot/m1n1/boot.bin.restore /boot/m1n1/boot.bin
if [[ -f $backup/update-m1n1.conf.absent ]]; then
  rm -f /etc/default/update-m1n1
else
  cp -a "$backup/update-m1n1.conf" /etc/default/update-m1n1
fi
rm -f /etc/default/grub.d/90-fairydust-default.cfg
cp "$backup/grub.cfg" /boot/grub/grub.cfg.restore
grub-script-check /boot/grub/grub.cfg.restore
mv -f /boot/grub/grub.cfg.restore /boot/grub/grub.cfg
sync
printf 'Restored stock m1n1 image, DTB-selection config, and original GRUB menu.\n'
printf 'Both kernel packages are still installed. Reboot when ready.\n'
