# lollipop-system

Alpha 0.3 package recipe for Lollipop identity, desktop defaults, user setup, and update/recovery helpers. Imported from the existing Alpha 0.3 build tree without changing package behavior.

## Contents

The payload selection is defined in [`scripts/make-system-payload.py`](../../scripts/make-system-payload.py). It includes desktop configuration, themes, wallpapers, icons, Fastfetch configuration, user defaults, package command wrappers, update/recovery tools, system services, and installed-system administration policy.

The live-only passwordless sudo policy is not included in this package. The package contains `20-lollipop-admin`, which requires authentication for the wheel group.

## Preparation and build flow

This is a staged import, not yet a standalone buildable package. Required inputs have not all been imported into this repository:

- The remaining service, application, update/recovery, and policy files under `profile/airootfs/`. Desktop and identity files are already imported; see [desktop defaults](../../docs/desktop-defaults.md).
- `state/tor-browser.tar.xz`, downloaded and verified by the original build's `prepare-tor.py` using its version lock and upstream signature.
- The original build orchestration and signing configuration.

In the complete build tree, the payload script creates `state/lollipop-system/lollipop-system.tar` and a generated `PKGBUILD` with the archive's SHA-256 digest. `makepkg` runs in that generated directory as a normal user. The package is then signed and added to the local package repository by the build pipeline.

Do not run `makepkg` directly in this directory: `SOURCE_DIGEST` is a template placeholder, and the source archive is generated separately. Do not replace the checksum with `SKIP`.

The preparation script also records selected profile paths in `state/system-payload-files.json`. The ISO builder uses this list to avoid installing the same files both through the profile and through the package.

## Import boundaries

Generated archives, binary packages, browser downloads, signing keys, and local build state are not included here. The remaining profile files and browser preparation scripts will be imported in subsequent steps. Desktop artwork is generated from `assets/` by `scripts/prepare-desktop.py` (requires Python and Pillow). Original Lollipop code and this recipe are licensed under GPL-3.0-only. The package license array also retains the existing payload license entries for incorporated material. See [licensing scope](../../LICENSES.md); supplied artwork and upstream components are not relicensed by this change.
