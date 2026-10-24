# Architecture

This document describes the Alpha 0.3 build source and its current limitations.

## Base and desktop

Lollipop is an experimental x86_64 distribution based on Arch Linux. Alpha 0.3 uses the Arch Linux Archive snapshot dated 2026-10-22, Linux LTS 6.18.57-2-lts, and KDE Plasma 6.8.1 with KWin on Wayland. SDDM provides the login screen; Bash and Konsole are the default shell and terminal.

Lollipop branding and desktop defaults are delivered through the locally built `lollipop-system` package. A separate `lollipop-decoration` package supplies the customized window decoration. Artwork source files are stored under `assets/` in this repository.

## Software delivery

Pacman handles native packages. Most direct selections come from Arch repositories; Calamares and the Lollipop-specific packages are built into a signed local repository. Flatpak applications are installed system-wide from Flathub during ISO creation so their default payload is available offline.

See the [package inventory](../packages/README.md). The lists describe direct selections, not all dependencies. Flatpak refs are recorded by the build, but the full Flatpak payload is not pinned here; byte-for-byte reproducibility is not claimed.

## Live system and installation

Archiso creates the live image. Calamares installs the system and configures GRUB for the installed system. The installer locates and validates the live SquashFS image, including the copy-to-RAM case, before extracting it.

The default root filesystem is Btrfs, with ext4 available as an alternative. The layout includes a separate ext4 `/boot` and an EFI system partition mounted at `/boot/efi`. Btrfs uses separate subvolumes for root, home, snapshots, cache, and logs. LUKS2 encryption is optional. Zram supplies compressed swap.

Installation finalization regenerates the initramfs and GRUB configuration and checks that an initramfs entry exists. Passwordless elevation is restricted to the live session's policy; that policy is removed from the installed target.

## Updates and recovery

The build includes a controlled update client that verifies signed release manifests before applying a selected repository snapshot. `loli-update` invokes this client. A public update service has not been deployed.

The Btrfs update path includes pre/post snapshots and backups of `/boot` and the EFI system partition. Ext4 requires explicitly proceeding without snapshot protection. Recovery still needs broader validation; automatic rollback is not guaranteed.

## Validation status

Installation and subsequent boot have succeeded in user testing. Panel transparency, battery percentage layout, and launching the installer from the desktop have required further fixes and runtime verification. Alpha 0.3 remains experimental.

The `lollipop-system` recipe, payload preparation, identity files, and desktop defaults have been imported. Artwork staging uses the existing `assets/` directory. Package command wrappers, the update/recovery implementation, and update check units have also been imported. The remaining lollipop-system service/application payload and browser verification inputs are now imported, enabling standalone package preparation. The custom decoration package has also been imported and compiled. Calamares packaging, installer configuration, and installer regression tests have now also been imported. The Archiso boot profile, live services, and profile staging script have also been imported. Pinned Archiso tooling, full ISO build orchestration, and remaining external package recipes are still to be imported. This document records the existing design; it does not make this checkout a complete ISO build tree.
