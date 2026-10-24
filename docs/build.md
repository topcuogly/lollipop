# Build an Alpha 0.3 ISO

The repository now contains the package recipes, profile staging, pinned mkarchiso script, and build orchestration. The imported flow has passed source and component checks, but a complete ISO build from this repository and subsequent boot/install tests have not yet been performed.

## Builder

Use a dedicated disposable Arch Linux x86_64 VM with working networking, sudo, sufficient disk space, and a normal build user. Do not use the development host as the builder. `prepare-builder.sh` replaces `/etc/pacman.conf` with the pinned 2026-10-22 configuration and performs `pacman -Syyuu`, which may downgrade the builder to that snapshot.

Copy or clone this repository into the VM, then run from its root:

```sh
bash scripts/build-full.sh --disposable-builder
```

The explicit flag is required by all host-mutating entry points. The normal user runs makepkg and manages signing state; sudo is used for builder preparation and ISO creation. Review `build.env` and `profile/pacman.conf` together before deliberately changing the snapshot.

## Sequence

1. Initialize Arch package trust and install the snapshot toolchain and build dependencies, including Python/Pillow, schema validation, Qt/KDE tools, and ISO tooling.
2. Fetch the pinned Calamares commit, validate its archive, and run source/configuration/regression tests.
3. Verify the two snapshot repository database hashes and 102 direct official package version/file/checksum records against `package-direct.lock.json`.
4. Initialize or reuse the local release signing key under ignored `state/signing/`, exporting only public verification material.
5. Build Calamares, `lollipop-system`, `lollipop-decoration`, PhotoCraft, and Upscayl as a normal user. Verify sources through their preparation scripts/makepkg checksums. Sign the exact package outputs and create a signed local repository.
6. Stage the live profile, removing package-owned files and injecting the public release keyring. Attach the build-only local repository and isolated package cache.
7. Run the vendored mkarchiso script. Its hash and upstream commit are checked before use. The profile's customization hook installs default Flatpaks and their runtimes; failure stops the build.
8. Write ISO checksums, builder package inventory, input clock/commits, build log, and public signing key to `out/`.

## Outputs and state

The expected ISO is `out/lollipop-alpha-0.3-x86_64.iso`; verify the actual output alongside `out/SHA256SUMS`. The default ISO work directory is `/var/tmp/lollipop-build-alpha03`; `BUILD_WORK` can select a different fresh path. Build state and source downloads live under ignored `state/`.

Keep `state/signing/` private and backed up if you intend to use its public key for future releases. The local development key is created without a passphrase and expires after two years. It is not a published production signing service. Neither private signing state nor the local repository is copied into the ISO profile. Only the public keyring is injected.

Existing `state/repo`, `state/profile`, or ISO work directories cause the relevant steps to stop rather than reuse stale packages/profile data. Preserve needed keys and outputs, then archive old build state and choose a fresh work directory before rebuilding. Do not rerun the complete flow blindly over an interrupted build.

The original profile Pacman configurations remain snapshot-based. The `file://` repository URL and isolated `CacheDir` are added only to the staging profile's build configuration; they are not placed in the installed target's `pacman.conf`.

## Validation without an ISO build

With Python, Pillow, PyYAML, jsonschema, GnuPG, Git, and Bash available:

```sh
python3 scripts/prepare-calamares.py
bash scripts/validate.sh
python3 scripts/check-packages.py
```

The first and last commands may download source/repository metadata. Tests use temporary files, mock update transactions, and temporary signature-test keys; they do not install or recover a system. The optional Node layout contract test runs when Node is available. The destructive sudo policy test is separate and only runs inside its guarded disposable container.

## Acceptance still required

A successful build must still be booted in UEFI and BIOS VMs, checked for one-click installer launch, installed onto disposable disks, and rebooted. Validate Btrfs, ext4 and optional encryption separately. Verify the installed target has no live passwordless sudo rule, and confirm default applications, wallpaper selection and clipboard integration. Update/recovery testing remains separate. No byte-for-byte ISO reproducibility is claimed because the Flatpak payload is not fully pinned.

`scripts/run-qemu.sh ISO [bios|uefi] [kvm|tcg]` provides an optional live boot helper. It does not attach an installation target disk; configure a disposable disk separately for installer testing.
