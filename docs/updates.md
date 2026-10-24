# Package commands, updates, and recovery

This is a staged import of the Alpha 0.3 implementation. No update server is configured, no release is published, and no signing key is included by this import.

## Package commands

| Command | Action |
|---|---|
| `loli-install` | `sudo pacman -S` |
| `loli-remove` | `sudo pacman -Rns` |
| `loli-search` | `pacman -Ss` |
| `loli-which` | `pacman -Qo` |
| `loli-listall` | `pacman -Q` |
| `loli-clean` | `sudo pacman -Sc` |
| `loli-update` | Check and apply a verified Lollipop release |

These are executable wrappers, not shell aliases. They preserve argument boundaries. Read-only queries do not request administrator privileges. `loli-update` does not bypass the controlled updater with a raw system upgrade.

## Release policy

The update client checks a detached GPG signature against `/etc/lollipop/release-keyring.gpg`. It rejects replayed release sequence numbers, snapshot regressions, future releases, unsupported manifest fields, and invalid release schedules.

Scheduled releases use January, April, July, or October 15 and a repository snapshot one calendar month earlier. Emergency releases require an explicit reason. This is policy implemented in code, not a commitment that releases have been published on that schedule.

`update-channel.json` deliberately contains an empty `manifest_url`. Until a real channel is configured, checking prints a local/manual-channel message. The systemd timer only checks for announcements; it does not automatically install packages. Timer activation belongs to the installation integration, which has not yet been imported.

## Applying a release

On a fully configured installed system, the explicit local workflow is:

```sh
loli-update /path/to/release.json /path/to/release.json.sig
```

The client requires administrator privileges, a trusted public key, release state, mounted boot partitions, sufficient space, and installed-system boot metadata in `/etc/lollipop/boot.json`. That boot metadata must be produced by installer integration; do not copy a builder machine's configuration into it.

For Btrfs, the client requires a separate `/.snapshots` mount and a configured Snapper root configuration. It creates pre/post snapshots and separate boot/EFI archives, recording UUIDs and checksums. It retains the latest two complete owned update pairs. Failed or interrupted journal entries block another update pending recovery.

Ext4 requires the explicit `--allow-no-snapshot` argument and does not receive Btrfs snapshot protection. An update changes the configured Arch repository snapshot and performs a full Pacman transaction, regenerates the initramfs, refreshes GRUB, and records the release. A signed `native_repo` is needed when updating locally maintained packages through a published native repository.

## Signing and publishing

`scripts/make-release.py` prepares a manifest and signs it locally using the build's `state/signing` directory and `state/signing-fingerprint`. Local key initialization and full build orchestration are available in `scripts/init-release-key.sh` and `scripts/build-full.sh`; see [build instructions](build.md). The script does not publish anything. Private keys and generated release artifacts belong outside tracked source files.

## Recovery and validation limits

`lollipop-recover` is an offline Btrfs recovery tool intended for the Live ISO. It requires explicit device and snapshot confirmation, validates checkpoint ownership, device UUIDs, and archive checksums, and replaces the target root and boot contents. It must not be run on the development host. A complete recovery runbook and destructive VM recovery testing are still required before treating this as a supported recovery mechanism.

The imported tests exercise manifest policy, real detached signatures and tampering, mocked update transactions, and package wrapper arguments. They do not validate actual Pacman upgrades, disk recovery, power loss, or bootability after rollback. Automatic rollback is not guaranteed.

## Development checks

From the repository root, run these as a normal user with Python 3 and GnuPG installed:

```sh
python3 tests/test-updates.py
python3 tests/test-transactions.py
python3 tests/test-signatures.py
python3 tests/test-package-commands.py
```

The signature test generates a temporary test-only key. Transaction tests mock system-changing operations. No installed-system update or recovery is performed by these tests.
