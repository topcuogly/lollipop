# Installer integration

This import preserves Alpha 0.3's Calamares configuration and fixes from earlier hardware testing. It does not yet provide the full bootable Archiso profile or an end-to-end validated ISO build.

## Files

- `packaging/calamares/`: upstream package recipe and failure-message patch.
- `scripts/prepare-calamares.py`: pinned upstream source preparation.
- `profile/airootfs/etc/calamares/`: installer settings and module configuration.
- `profile/airootfs/usr/lib/calamares/modules/`: Lollipop clean, finish, and boot-verification jobs.
- `profile/airootfs/usr/share/calamares/branding/lollipop/`: branding text and slideshow. Its logo is generated from the existing main logo by `prepare-desktop.py`.
- `profile/airootfs/usr/local/bin/install-lollipop`: graphical launcher with a per-user log and error dialog.
- `profile/airootfs/usr/local/bin/lollipop-installer-preflight`: root preflight that selects and validates the live SquashFS source.
- `profile/airootfs/usr/local/sbin/lollipop-target`: installer-target finalization helper; do not run on the host.

These installer-only files are profile content, not additions to the installed `lollipop-system` package. The `Install Lollipop` desktop entry is included both in the application menu and the skeleton Desktop directory. Existing user initialization also copies it to the XDG desktop directory in the live session.

## Preserved fixes

The launcher invokes Calamares without `-c /etc/calamares`, avoiding the application-data override that caused missing QML errors. Preflight accepts both copy-to-RAM and boot-media SquashFS paths, runs `unsquashfs -s`, and writes the detected path to `unpackfs.conf` before launch.

`90-lollipop-live` sorts after the installed wheel policy, enabling noninteractive sudo for the live user. The target clean job removes it before installation is finalized. Archiso integration must set this rule to root ownership and mode `0440`; Git does not encode that permission. The rule must never be activated on the development host.

Target cleanup removes live-specific components, restores the LTS kernel, and generates the uppercase `PRESETS` variable expected by mkinitcpio. Final verification regenerates initramfs and GRUB configuration, checks for `/init` inside the image, and rejects a missing LTS initrd entry before unmounting the target.

The finish job records firmware/boot-disk metadata used by the updater, restores distribution identity, initializes package trust, locks the root password, and initializes snapshot configuration. The full build must inject its trusted **public** release key; private keys do not belong in the profile.

## Validation

After preparing the upstream source, the configuration checker needs Python, PyYAML, and jsonschema:

```sh
python3 tests/check-calamares.py
python3 tests/test-installer-regressions.py
```

`test-live-sudo-policy.sh` deliberately changes sudoers and is guarded to run only as root in a disposable Podman container with `LOLLIPOP_ISOLATED_SUDO_TEST=1`. Never run it on the host.

Schema checks, mocked boot-finalization failure checks, and isolated sudo tests do not replace a fresh VM installation, reboot, encrypted-layout test, or graphical launcher test. These remain required after the complete ISO profile is imported. Panel transparency and other desktop appearance issues are outside this import.
