# lollipop-system

Alpha 0.3 identity, desktop defaults, user setup, package commands, and signed update/recovery helpers. The package includes the official pinned x86_64 Tor Browser archive, so its architecture is `x86_64`.

## Build on Arch Linux

Run as a normal user from the repository root. Install `base-devel`, Python, Pillow (`python-pillow`), GnuPG, and Git first. Build/runtime dependencies must be available in your configured repositories.

```sh
python3 scripts/prepare-tor.py
python3 scripts/make-system-payload.py
cd state/lollipop-system
makepkg --syncdeps
```

The second step rechecks the browser hash and signature even if it is cached. The payload generator stages desktop assets, selects the profile files, creates `lollipop-system.tar`, and writes a generated `PKGBUILD` with the archive SHA-256. Never replace that checksum with `SKIP` or run the template directly.

The resulting package is unsigned unless your local makepkg configuration requests signing. Signing and repository publication are separate maintainer tasks; no private signing key is stored here. The package may be built independently of the remaining ISO tooling. Installing it alters system policy and desktop defaults: validate installation in a disposable Arch VM, not on the development host.

## Contents and boundaries

`make-system-payload.py` defines the selected profile files and records them in `state/system-payload-files.json` for later ISO integration. Artwork is sourced from `assets/`; KDE wallpaper metadata and previews are generated with Pillow.

The package includes Tor/Flatpak launchers, a default libvirt network service and enablement links, Zram configuration, and the wheel administration policy. It also preserves the Alpha 0.3 `systemd-coredumpd.service` mask. The live passwordless sudo rule and `/etc/skel/.bashrc` are deliberately excluded. The packaged wheel rule is installed with mode `0440`.

Plasma, Konsole and Qt tools are declared dependencies. The configured custom window decoration is a separate package still to be imported. The installed updater also needs the installer's boot metadata, a trusted release key and a configured release channel before real updates can be used. Building this package does not supply a complete ISO or a deployed update service.

The browser lock, detached upstream signature, and public verification keyring are tracked; the downloaded browser and generated packages are ignored build state. See [vendor provenance](../../vendor/README.md), [desktop defaults](../../docs/desktop-defaults.md), and [updates](../../docs/updates.md).

Original Lollipop code is GPL-3.0-only. Incorporated material retains its existing terms; see [licensing scope](../../LICENSES.md). The mixed package license array does not relicense supplied artwork or upstream components.

## Validation

The package was produced in an isolated Arch container with dependency checking disabled (`makepkg --nodeps`) to verify packaging without installing the desktop stack. Source checksum, resulting inventory, executable modes, sudo policy mode, systemd symlinks, and exclusion of live-only sudo rules were checked. Dependency installation and full desktop runtime behavior still require an Arch VM test.
