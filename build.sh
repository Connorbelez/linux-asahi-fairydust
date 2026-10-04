#!/usr/bin/env bash
set -euo pipefail

project_dir=$(dirname -- "$(realpath -- "${BASH_SOURCE[0]}")")
cd "$project_dir"
exec > >(tee -a "$project_dir/build.log") 2>&1

trap 'status=$?; printf "%s\n" "$status" > "$project_dir/build.exit-status"; printf "Build finished: status=%s, time=%s\n" "$status" "$(date --iso-8601=seconds)"' EXIT

printf 'Build started: %s\n' "$(date --iso-8601=seconds)"
[[ $(uname -m) == aarch64 ]]
[[ $EUID != 0 ]]
export RUSTUP_TOOLCHAIN=1.93.1
export FAIRYDUST_JOBS="${FAIRYDUST_JOBS:-2}"
rustc --version
bindgen --version
# prepare() was already run and inspected. This also permits incremental retries
# without reapplying the patch or discarding hours of completed compilation.
makepkg --noextract --noconfirm --log
package=$(makepkg --packagelist)
[[ -f $package ]]
sha256sum "$(basename -- "$package")" > package.sha256
