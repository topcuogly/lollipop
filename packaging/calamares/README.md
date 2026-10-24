# Calamares

Pinned Calamares 3.4.2, built with Qt 6. The upstream git commit and archive SHA-256 are recorded in `external-packages.lock.json`.

## Build on the Arch snapshot builder

From the repository root as a normal user:

```sh
python3 scripts/prepare-calamares.py
cd state/calamares
makepkg --syncdeps
```

The preparation script fetches the exact upstream commit into a temporary Git repository and creates a `git archive` with the expected prefix. It checks the archive digest before copying the package recipe and patch into `state/calamares`. A cached archive is also checksum-checked. No source archive, private key, or binary package is committed.

The patch clarifies the installation-failure message. The package installs upstream modules and application QML data but does not install upstream example configuration (`INSTALL_CONFIG=OFF`). Lollipop's profile supplies its own configuration, custom jobs, branding, and launcher; see [installer integration](../../docs/installer.md).

Calamares retains its upstream GPL-3.0-or-later license. The original Lollipop recipe and integration code use GPL-3.0-only. The pinned source archive includes upstream notices.
