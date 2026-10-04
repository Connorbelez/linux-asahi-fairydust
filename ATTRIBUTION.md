# Attribution and licenses

This project packages existing Asahi Linux Fairydust work. It does not claim authorship of the native USB-C display driver.

- Kernel and Fairydust delta: [AsahiLinux/linux](https://github.com/AsahiLinux/linux). Exact commits and authors remain in `source-provenance.json` and the upstream Git history. The kernel and `fairydust.patch` use GPL-2.0; see `LICENSES/GPL-2.0` and each original file's SPDX identifier. A complete kernel source archive is pinned in `PKGBUILD`.
- Recipe structure and tested config: [asahi-alarm/PKGBUILDs](https://github.com/asahi-alarm/PKGBUILDs/tree/356454b/linux-asahi). These retain their upstream terms. The top-level MIT license covers this repository's original helper code and documentation, not imported kernel material or inherited packaging.
- Packaging, recovery helpers, and validation: Connor Beleznay, with AI assistance. New contributions must disclose AI assistance and preserve upstream notices.

This is an unofficial community experiment. Asahi Linux and Omarchy do not endorse or support this package.
