#!/usr/bin/env bash
set -euo pipefail

[[ $EUID == 0 ]] || { printf 'Run with pkexec or sudo.\n' >&2; exit 1; }
[[ $(uname -r) == 7.1.13-3-2-ARCH ]] || { printf 'Unexpected baseline kernel.\n' >&2; exit 1; }
[[ $(tr -d '\0' </sys/firmware/devicetree/base/model) == 'Apple MacBook Pro (13-inch, M1, 2020)' ]]
findmnt --mountpoint /boot >/dev/null

backup=/var/lib/asahi-fairydust/backups/pre-fairydust-20261001
[[ ! -e $backup ]] || { printf 'Backup already exists; refusing to overwrite %s\n' "$backup" >&2; exit 1; }
install -d -m 700 "$backup"
tar -C / -cpf "$backup/boot.tar" boot
tar -C / -cpf "$backup/config.tar" etc/default/grub etc/mkinitcpio.conf etc/mkinitcpio.conf.d etc/mkinitcpio.d
if [[ -e /etc/default/update-m1n1 ]]; then
  cp -a /etc/default/update-m1n1 "$backup/update-m1n1.conf"
else
  touch "$backup/update-m1n1.conf.absent"
fi
cp -a /boot/m1n1/boot.bin "$backup/boot.bin"
cp -a /boot/grub/grub.cfg "$backup/grub.cfg"
pacman -Q > "$backup/packages.txt"
sha256sum /boot/m1n1/boot.bin /boot/grub/grub.cfg /boot/vmlinuz-linux-asahi /boot/initramfs-linux-asahi.img > "$backup/baseline.sha256"
sha256sum "$backup/boot.tar" "$backup/config.tar" "$backup/boot.bin" "$backup/grub.cfg" > "$backup/archives.sha256"
sha256sum --check "$backup/archives.sha256"
printf 'Verified baseline backup: %s\n' "$backup"
