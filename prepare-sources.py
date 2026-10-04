#!/usr/bin/env python3
"""Export a pinned upstream delta and the installed kernel config for makepkg."""

import gzip
import hashlib
import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE / "upstream-linux"
STABLE = "94fb23346d522edf53722357c426a3e58030beea"
FAIRYDUST = "ce9f2eba72c061a50b2d790450e90af3439d8c24"
ANCESTOR = "ed2201483aa4e94868164306412cd821633cedf6"


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(REPO), *args])


def main() -> None:
    assert git("rev-parse", "HEAD").decode().strip() == STABLE
    assert git("merge-base", STABLE, FAIRYDUST).decode().strip() == ANCESTOR
    patch = git("diff", "--binary", ANCESTOR, FAIRYDUST)
    names = git("diff", "--name-only", ANCESTOR, FAIRYDUST).decode().splitlines()
    # Protect against accidentally including unrelated base-kernel regressions.
    assert all(
        name.startswith("arch/arm64/boot/dts/apple/")
        or name in (
            "drivers/usb/typec/tipd/core.c",
            "drivers/usb/typec/tipd/tps6598x.h",
        )
        for name in names
    ), names
    config = gzip.decompress(pathlib.Path("/proc/config.gz").read_bytes())
    (HERE / "fairydust.patch").write_bytes(patch)
    (HERE / "config").write_bytes(config)
    provenance = {
        "stable": STABLE,
        "fairydust": FAIRYDUST,
        "ancestor": ANCESTOR,
        "commits": git("log", "--reverse", "--format=%H %s", f"{ANCESTOR}..{FAIRYDUST}")
        .decode()
        .splitlines(),
        "files": names,
        "config_sha256": hashlib.sha256(config).hexdigest(),
        "patch_sha256": hashlib.sha256(patch).hexdigest(),
        "running_kernel": subprocess.check_output(["uname", "-r"], text=True).strip(),
    }
    (HERE / "source-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps(provenance, indent=2))


if __name__ == "__main__":
    main()
