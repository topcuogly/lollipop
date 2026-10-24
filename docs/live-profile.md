# Archiso live profile

The profile now contains Alpha 0.3's BIOS Syslinux and UEFI systemd-boot entries, live account setup, SDDM autologin, locale, networking, guest clipboard services, temporary Pacman keyring, and build-time Flatpak provisioning.

The live image uses systemd-boot on UEFI; GRUB is installed on the target system by Calamares. Ventoy's own boot selection is outside this profile. Both live menus identify Alpha 0.3 and load the LTS kernel and matching initramfs.

## Package sources

`profile/packages.x86_64` links to the canonical `packages/native.txt`. `profile/pacman.conf` selects the 2026-10-22 Arch snapshot for building; the target's repository configuration is in `profile/airootfs/etc/pacman.conf`. The build clock and pinned tool commits are recorded in `build.env`.

Local packages must be built and supplied through a signed repository before mkarchiso runs. The pinned Archiso entry point and complete ISO orchestration are now imported; see [build instructions](build.md). The profile alone is not the full build command.

## Live session and permissions

The live setup service creates `live` with an empty password and wheel membership before SDDM. `90-lollipop-live` enables passwordless live-session sudo after the installed wheel policy. The root account is locked; the tracked shadow file contains no password hash. These settings are for the ephemeral Live ISO only.

`profiledef.sh` records root ownership and exact permissions for shadow, sudo policies, scripts, and the desktop installer launcher. Git preserves executable bits and symlinks but not all these modes; mkarchiso must apply the profile permission rules. Installer cleanup removes live-specific rules and services from the target.

NetworkManager, SDDM, QEMU guest agent, and Spice guest integration use profile service links. Spice clipboard synchronization also requires the host VM's Spice agent channel. The imported channel condition prevents starting the daemon without that device.

## Build-time Flatpak payload

`root/customize_airootfs.sh` restores branding, registers Flathub, installs the selected applications and required runtimes, and refreshes AppStream. It records installed refs and creates `full-payload-ready` only after success. The hook requires working network access and fails visibly instead of shipping a partially provisioned desktop.

The separate Flathub refresh service/timer and manual Flatpak helper are also included. The refresh units are not enabled through profile links in this import. Flathub refs are recorded at build time; the entire Flatpak payload is not reproducibly pinned.

## Assemble a staging profile

After preparing `lollipop-system`, use a builder-generated **public** release keyring:

```sh
python3 scripts/prepare-live-profile.py \
  --output state/profile \
  --package-files state/system-payload-files.json \
  --release-key state/release-keyring.gpg
```

The output directory must not exist. The script stages generated artwork and Calamares branding, materializes the package list, removes package-owned files using the payload inventory, and injects the public keyring. This prevents the profile from overlaying the same persistent files installed by `lollipop-system`.

The key argument is copied as supplied: maintainers must provide the intended public release keyring, never a private key. No signing key generation or publication happens in this script. The ISO orchestrator attaches the signed local package repository, configures an isolated cache, and calls the pinned mkarchiso version.

## Checks

```sh
python3 tests/test-live-profile.py
python3 tests/test-installer-regressions.py
```

Tests cover staging boundaries, service links, kernel paths, permission declarations, branding, and exclusion of package-owned files. They do not boot the ISO. A full build, UEFI/BIOS VM boot, one-click installer launch, installation, and reboot remain required after orchestration is imported.
