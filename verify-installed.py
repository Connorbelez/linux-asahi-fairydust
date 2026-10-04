#!/usr/bin/env python3
"""Validate boot artifacts after installation, without changing the system."""

import hashlib
import pathlib
import subprocess

RELEASE = "7.1.13-3-1-fairydust-ARCH"
PKGBASE = "linux-asahi-fairydust"
BACKUP = pathlib.Path("/var/lib/asahi-fairydust/backups/pre-fairydust-20261001")


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def require(condition: bool, description: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {description}")
    print(f"OK: {description}")


def main() -> None:
    print(f"Validating installed artifacts for {RELEASE}; hardware is not yet tested.")
    require(run("pacman", "-Q", "linux-asahi") == "linux-asahi 7.1.13.asahi3-2", "stock package retained")
    require(
        run("pacman", "-Q", PKGBASE) == f"{PKGBASE} 7.1.13.asahi3.fairydust12-1",
        "expected experimental package installed",
    )
    modules = pathlib.Path("/usr/lib/modules") / RELEASE
    image = pathlib.Path(f"/boot/vmlinuz-{PKGBASE}")
    require(image.read_bytes() == (modules / "vmlinuz").read_bytes(), "boot kernel matches packaged image")
    require((modules / "pkgbase").read_text().strip() == PKGBASE, "distinct mkinitcpio package base")
    for name in ("appledrm", "tps6598x", "hid_apple", "btrfs"):
        vermagic = run("modinfo", "-k", RELEASE, "-F", "vermagic", name)
        require(vermagic.startswith(RELEASE + " "), f"{name} module release matches")

    contents = run("lsinitcpio", f"/boot/initramfs-{PKGBASE}.img").splitlines()
    for suffix in ("hooks/asahi", "hooks/encrypt"):
        require(any(line.endswith(suffix) for line in contents), f"initramfs includes {suffix}")
    for module in ("btrfs", "hid_apple"):
        filename = pathlib.Path(run("modinfo", "-k", RELEASE, "-F", "filename", module)).name
        require(any(pathlib.PurePosixPath(line).name == filename for line in contents), f"initramfs includes {filename}")

    dtb = modules / "dtbs/apple/t8103-j293.dtb"
    # ALARM's package layout is flat; support the nested layout only for diagnosis.
    if not dtb.exists():
        dtb = modules / "dtbs/t8103-j293.dtb"
    require(dtb.is_file(), "J293 device tree installed")
    dcpext = run("fdtget", str(dtb), "/aliases", "dcpext")
    require(run("fdtget", str(dtb), dcpext, "status") == "okay", "external display controller enabled")
    require(run("fdtget", str(dtb), dcpext, "apple,connector-type") == "DP", "external connector is DisplayPort")
    require(run("fdtget", "-t", "i", str(dtb), dcpext, "apple,dptx-phy") == "1", "front-left USB-C PHY selected")
    require(bool(run("fdtget", str(dtb), "/aliases", "sio")), "SIO alias present for display audio")
    require(dtb.read_bytes() in pathlib.Path("/boot/m1n1/boot.bin").read_bytes(), "m1n1 embeds the exact patched J293 DTB")

    grub = pathlib.Path("/boot/grub/grub.cfg").read_text()
    for path in (
        "/vmlinuz-linux-asahi",
        "/initramfs-linux-asahi.img",
        f"/vmlinuz-{PKGBASE}",
        f"/initramfs-{PKGBASE}.img",
    ):
        require(path in grub, f"GRUB references {path}")
    run("grub-script-check", "/boot/grub/grub.cfg")
    print("OK: GRUB configuration syntax")

    for line in (BACKUP / "baseline.sha256").read_text().splitlines():
        digest, path = line.split(maxsplit=1)
        path = path.lstrip("*")
        if path in ("/boot/vmlinuz-linux-asahi", "/boot/initramfs-linux-asahi.img"):
            require(hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest() == digest, f"baseline unchanged: {path}")
    print("Boot-artifact checks passed. A reboot and real monitor testing are still required.")


if __name__ == "__main__":
    main()
