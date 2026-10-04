# Local agent-assisted experiment. See README.md for provenance and results.
# Packaging follows asahi-alarm/PKGBUILDs linux-asahi, but retains stock Linux.
_rcver=7.1.13
_asahirel=3
_fairydust_commits=12
pkgrel=1
pkgbase=linux-asahi-fairydust
pkgname=("$pkgbase")
pkgver="${_rcver}.asahi${_asahirel}.fairydust${_fairydust_commits}"
pkgdesc='Asahi kernel with experimental native USB-C display output (local build)'
arch=('aarch64')
url='https://github.com/AsahiLinux/linux/tree/fairydust'
license=('GPL2')
depends=(coreutils kmod initramfs 'm1n1>=1.6.1')
makedepends=(base-devel bc dtc libelf pahole cpio perl rustup rust-bindgen tar xz xmlto python)
optdepends=('linux-firmware: firmware for additional devices')
options=('!strip' '!debug' '!lto')

_commit_id="asahi-${_rcver}-${_asahirel}"
_srcname="linux-${_commit_id}"
source=(
  "https://github.com/AsahiLinux/linux/archive/${_commit_id}.tar.gz"
  config
  fairydust.patch
)
# The archive hash is from the matching official Asahi ALARM package recipe.
# The config and patch hashes are recorded in source-provenance.json.
sha256sums=(
  '874ef68d04ac8c831b90bb01a387cfabb58fceb60842c49a0d0e58bcd6c146ad'
  'ae1d4ce855bd435b62c8fb213cbcf2d4eefd47b62274792c4a6bf299848b3876'
  '7af72b4e4a359c61af45973e6d330906097162e6629d08efeebb27e5b981418b'
)

export RUSTUP_TOOLCHAIN=1.93.1
export KBUILD_BUILD_HOST=local-asahi
export KBUILD_BUILD_USER=linux-asahi-fairydust
export KBUILD_BUILD_TIMESTAMP='2026-09-12 09:57:34 UTC'
export KBUILD_BUILD_VERSION=1

prepare() {
  cd "$_srcname"
  # Fail instead of silently building an unpatched or fuzzy-patched tree.
  patch --dry-run --fuzz=0 -Np1 < ../fairydust.patch
  patch --fuzz=0 -Np1 < ../fairydust.patch

  printf '%s\n' "-${_asahirel}-${pkgrel}-fairydust" > localversion.10-pkgrel
  mkdir -p build/base
  cp ../config build/base/.config
  # Keep the baseline GPU and 16K-page settings and available Alt Mode helpers.
  scripts/config --file build/base/.config --module TYPEC_DP_ALTMODE
  scripts/config --file build/base/.config --module TYPEC_NVIDIA_ALTMODE
  scripts/config --file build/base/.config --module TYPEC_TBT_ALTMODE
  make olddefconfig prepare O="$PWD/build/base" -j "${FAIRYDUST_JOBS:-2}"
  make -s kernelrelease O="$PWD/build/base" > build/base/version
  printf 'Prepared %s (%s)\n' "$pkgbase" "$(<build/base/version)"
}

build() {
  cd "$_srcname"
  make all O="$PWD/build/base" -j "${FAIRYDUST_JOBS:-2}"
}

package() {
  cd "$_srcname"
  local output="$PWD/build/base"
  local kernver="$(<"$output/version")"
  local modulesdir="$pkgdir/usr/lib/modules/$kernver"

  install -Dm644 "$output/arch/arm64/boot/Image" "$modulesdir/vmlinuz"
  printf '%s\n' "$pkgbase" | install -Dm644 /dev/stdin "$modulesdir/pkgbase"
  make O="$output" INSTALL_MOD_PATH="$pkgdir/usr" INSTALL_MOD_STRIP=1 modules_install
  install -Dt "$modulesdir/dtbs" "$output"/arch/arm64/boot/dts/apple/*.dtb
  # Build trees are large; no external DKMS modules are required for this test.
  rm -f "$modulesdir/source" "$modulesdir/build"
}
