#!/usr/bin/env python3
"""Record real post-boot observations; do not label these as test passes."""

import argparse
import datetime
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", default="Runtime observations")
    args = parser.parse_args()
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [f"# Fairydust runtime capture — {timestamp}", "", args.label, "", "Raw observations, not a completed hardware test matrix.", ""]
    commands = [
        ["uname", "-a"],
        ["pacman", "-Q", "linux-asahi", "linux-asahi-fairydust", "m1n1", "hyprland"],
        ["hyprctl", "monitors", "all", "-j"],
        ["hyprctl", "configerrors"],
        ["nmcli", "-t", "-f", "DEVICE,TYPE,STATE", "device"],
        ["wpctl", "status"],
        ["journalctl", "-b", "-k", "--no-pager", "--grep=drm|dcp|typec|crossbar|tps659", "-n", "100"],
    ]
    for command in commands:
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        lines.extend([f"## `{' '.join(command)}` (exit {result.returncode})", "", "```text", result.stdout.rstrip(), "```", ""])
    lines.extend(["## Linux connector status", "", "```text"])
    for connector in sorted(pathlib.Path("/sys/class/drm").glob("card*-*")):
        status = connector / "status"
        if status.is_file():
            lines.append(f"{connector.name}: {status.read_text().strip()}")
    lines.extend(["```", "", "## User observations", "", "Record monitor/adapter model, connected port, cold/hot-plug, image quality, audio, and resume results here.", ""])
    destination = HERE / f"runtime-{timestamp}.md"
    destination.write_text("\n".join(lines))
    print(destination)


if __name__ == "__main__":
    main()
