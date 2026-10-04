# Pinned Fairydust kernel experiment

[![CI](https://github.com/Connorbelez/linux-asahi-fairydust/actions/workflows/ci.yml/badge.svg)](https://github.com/Connorbelez/linux-asahi-fairydust/actions/workflows/ci.yml)

This independently named package combines Asahi `asahi-7.1.13-3` with the 12 Fairydust commits at `ce9f2eba72c061a50b2d790450e90af3439d8c24`. It installs beside stock `linux-asahi`, with release `7.1.13-3-1-fairydust-ARCH`. The delta is generated from the shared ancestor, retaining the two newer stable fixes missing from the experimental branch: Broadcom Wi-Fi authentication and newer-Mac audio device-tree corrections.

The package was built and booted on a MacBook Pro 13-inch M1/J293 with Omarchy, using Rust 1.93.1 and two build jobs. Native USB-C-to-HDMI video worked at 2560×1440 / 60 Hz on a KTC H27T27 through the left-front USB-C port. The kernel build took about 38 minutes with 2.5 GiB peak build memory. Reconnect, HDMI audio, suspend/resume, and a separate stock-kernel boot were not established by that first video result.

## Source provenance

| Source | Commit |
| --- | --- |
| Stable base | `94fb23346d522edf53722357c426a3e58030beea` |
| Fairydust snapshot | `ce9f2eba72c061a50b2d790450e90af3439d8c24` |
| Shared ancestor | `ed2201483aa4e94868164306412cd821633cedf6` |

`source-provenance.json` lists the original upstream commits and changed files. `fairydust.patch` is upstream work, not a new display-driver implementation by this fork. The included kernel config is the exact tested 16 KiB-page/Rust/Asahi-GPU baseline. The package recipe follows the existing `linux-asahi` packaging structure.

Keep the patch byte-identical to its checksum. Its unified-diff context includes single-space blank lines and Linux tab indentation; a file-scoped Git attribute prevents those required data prefixes from being misclassified as whitespace errors when the patch itself is added to Git.

## Build

Run from this directory as an unprivileged aarch64 user:

```sh
sudo pacman -S --needed base-devel bc dtc kmod libelf pahole cpio perl rustup rust-bindgen tar xz xmlto python
rustup toolchain install 1.93.1 --profile minimal --component rust-src --component rustfmt
export RUSTUP_TOOLCHAIN=1.93.1
export FAIRYDUST_JOBS=2
makepkg --verifysource
makepkg --nobuild --log
bash build.sh
```

The source archive, config, and patch have fixed SHA-256 checksums. Preparation dry-runs the patch with zero fuzz before applying it. `build.sh` reuses the prepared tree for incremental retries and records `build.exit-status` and a freshly generated `package.sha256` manifest. Neither the build nor the package itself reboots the machine.

The committed sources are sufficient for building. `prepare-sources.py` is retained as provenance tooling for regenerating the exact delta from an `upstream-linux` checkout at the pinned stable revision plus the pinned Fairydust history; regenerating `config` from a different running kernel requires updating the recipe's checksum deliberately.

## Installation and recovery helpers

The shell/Python helpers preserve the locally tested installation workflow. They are baseline-guarded for J293 and stock `linux-asahi 7.1.13.asahi3-2`; they are not a general updater for newer versions or other hardware. Review them and the existing boot configuration before running privileged operations.

1. `sudo bash backup-boot.sh` preserves the ESP and relevant configuration under `/var/lib/asahi-fairydust/backups/pre-fairydust-20261001` and refuses to overwrite that baseline.
2. `sudo bash install-kernel.sh` checks the successful build/manifest and baseline hashes, suppresses automatic m1n1 rewriting during the package transaction, builds/validates the experimental initramfs, embeds matching DTBs, and keeps stock as GRUB's unattended default. The published helper derives menu IDs from the filesystem UUID instead of embedding the original machine's UUID. It rolls back boot selection if verification fails.
3. `sudo python verify-installed.py` checks kernel/module identity, firmware/encryption/HID support, the J293 DTB, its presence in m1n1, GRUB syntax, and unchanged stock boot images.
4. Select `linux-asahi-fairydust` explicitly in GRUB for testing, with the monitor on the left-front USB-C port and the lid initially open.
5. `python capture-runtime.py --label 'First Fairydust boot'` captures local observations. Generated observations are not committed by this fork.
6. `sudo bash restore-stock-boot.sh` restores the original shared m1n1 image, DTB selection, and GRUB menu while retaining both package installations.

## Footguns learned locally

- A stable-tip-to-Fairydust-tip diff would remove unrelated stable fixes. Apply only the ancestor-to-experimental delta onto stable.
- GRUB kernel choice is not a fully independent device-tree fallback: m1n1 embeds shared DTBs before GRUB starts. Back up the original `boot.bin`; retain an emergency copy on the ESP.
- The package DTB hook automatically calls `update-m1n1`. Control DTB selection before installation and validate the final image instead of relying on hook exit status alone.
- The ESP had only about 308 MiB free before installation. A second full fallback initramfs is unnecessary when stock is retained.
- Omarchy mkinitcpio drop-ins can replace `HOOKS`; verify `asahi` and encryption support in the generated initramfs.
- `hid_apple` is a module name, but its file is `hid-apple.ko`. The verifier now obtains actual filenames from `modinfo`.
- Rust's minimal profile does not include `rustfmt`; bindgen reported non-fatal formatter errors until it was installed.
- A kernel file built later will not match the original machine's package hash. The published installer uses the current build's manifest rather than the historical binary hash.
- A fixed DTB pin must be updated/restored before removing or replacing the experimental module directory.
- Graphical authentication did not initially work in the agent session; visible-terminal `sudo` succeeded. No privilege policy or passwordless rule was added.

This is an agent-assisted personal-fork experiment. Asahi's policy prohibits LLM-generated material contributions to its project; this branch does not constitute an upstream submission or an official supported package.


## Maintenance and verification

This is a standalone packaging project extracted from the published PKGBUILDs experiment. Run `bash scripts/verify.sh` for source integrity and manifest behavior. CI does not compile or boot the kernel. See [attribution](ATTRIBUTION.md), [maintenance](MAINTAINERS.md), [roadmap](ROADMAP.md), and [promotion plan](PROMOTION.md). No stable release or signed binary package is provided.

## Maintenance backlog

The [GitHub Project](https://github.com/users/Connorbelez/projects/15) tracks the roadmap issues and release qualification. See [maintenance](MAINTAINERS.md) for ownership and review expectations.
