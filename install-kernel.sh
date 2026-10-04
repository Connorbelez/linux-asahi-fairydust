#!/usr/bin/env bash
# Install only the completed, inspected local package. Never reboot automatically.
set -Eeuo pipefail

[[ $EUID == 0 ]] || { printf 'Run this script with sudo in a visible terminal.\n' >&2; exit 1; }
project_dir=$(dirname -- "$(realpath -- "${BASH_SOURCE[0]}")")
backup=/var/lib/asahi-fairydust/backups/pre-fairydust-20261001
release=7.1.13-3-1-fairydust-ARCH
pkgbase=linux-asahi-fairydust
package="$project_dir/$pkgbase-7.1.13.asahi3.fairydust12-1-aarch64.pkg.tar.xz"
root_uuid=$(grub-probe --target=fs_uuid /)
[[ $root_uuid =~ ^[0-9a-fA-F-]+$ ]]
stock_id="gnulinux-linux-asahi-advanced-$root_uuid"
experiment_id="gnulinux-linux-asahi-fairydust-advanced-$root_uuid"

[[ $(<"$project_dir/build.exit-status") == 0 ]]
(cd "$project_dir" && sha256sum --check package.sha256)
[[ $(pacman -Qp "$package") == "$pkgbase 7.1.13.asahi3.fairydust12-1" ]]
[[ $(pacman -Q linux-asahi) == 'linux-asahi 7.1.13.asahi3-2' ]]
findmnt --mountpoint /boot >/dev/null
sha256sum --check "$backup/archives.sha256"
sha256sum --check "$backup/baseline.sha256"
[[ -f $backup/update-m1n1.conf.absent && ! -e /etc/default/update-m1n1 ]]
[[ ! -e /etc/default/grub.d/90-fairydust-default.cfg ]]

mapfile -t space < <(df --output=avail -B1 /boot)
available=${space[1]//[[:space:]]/}
(( available > 200 * 1024 * 1024 )) || { printf 'Less than 200 MiB free on the ESP.\n' >&2; exit 1; }

rollback_on_error() {
  local status=$?
  trap - ERR
  printf 'Installation failed (%s); restoring original boot selection.\n' "$status" >&2
  if [[ -s $backup/boot.bin ]]; then
    cp "$backup/boot.bin" /boot/m1n1/boot.bin.restore
    mv -f /boot/m1n1/boot.bin.restore /boot/m1n1/boot.bin
  fi
  if [[ -s $backup/grub.cfg ]]; then
    cp "$backup/grub.cfg" /boot/grub/grub.cfg.restore
    mv -f /boot/grub/grub.cfg.restore /boot/grub/grub.cfg
  fi
  rm -f /etc/default/update-m1n1 /etc/default/grub.d/90-fairydust-default.cfg
  sync
  printf 'The experimental package may be installed, but stock boot files were restored.\n' >&2
  exit "$status"
}
trap rollback_on_error ERR

# A recovery copy on the ESP remains reachable without decrypting Linux root.
cp "$backup/boot.bin" /boot/m1n1/boot.bin.pre-fairydust-20261001
cmp "$backup/boot.bin" /boot/m1n1/boot.bin.pre-fairydust-20261001

# Suppress automatic boot-image rewriting until the installed artifacts pass checks.
printf 'M1N1_UPDATE_DISABLED=1\n' | install -Dm644 /dev/stdin /etc/default/update-m1n1
pacman -U --noconfirm "$package"

# Explicit generation: a failed post-transaction hook must not masquerade as success.
mkinitcpio -p "$pkgbase"
[[ -s /boot/vmlinuz-$pkgbase && -s /boot/initramfs-$pkgbase.img ]]
cmp "/usr/lib/modules/$release/vmlinuz" "/boot/vmlinuz-$pkgbase"
dtb="/usr/lib/modules/$release/dtbs/t8103-j293.dtb"
[[ $(fdtget "$dtb" /soc/dcp@271c00000 status) == okay ]]
[[ $(fdtget "$dtb" /aliases sio) == /soc/sio@236400000 ]]

install -m644 "$project_dir/update-m1n1-fairydust.conf" /etc/default/update-m1n1
update-m1n1
printf '# Keep the stock kernel as the unattended default.\nGRUB_DEFAULT=%q\n' \
  "gnulinux-advanced-$root_uuid>$stock_id" \
  | install -Dm644 /dev/stdin /etc/default/grub.d/90-fairydust-default.cfg
grub-mkconfig -o /boot/grub/grub.cfg
grub-script-check /boot/grub/grub.cfg
rg --fixed-strings "$stock_id" /boot/grub/grub.cfg
rg --fixed-strings "$experiment_id" /boot/grub/grub.cfg
python "$project_dir/verify-installed.py"
sync
trap - ERR
printf 'Installation and boot-artifact verification passed. Stock remains the default.\n'
printf 'When ready, reboot and choose Advanced options → Linux linux-asahi-fairydust.\n'
