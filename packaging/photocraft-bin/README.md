# photocraft-bin

Repackages the pinned upstream PhotoCraft 0.14.0 x86_64 Arch package. The recipe verifies SHA-256 and copies only `usr/`, preserving upstream executables, desktop entry, icons, documentation, and license notices. It does not execute the upstream application or import upstream package-manager metadata.

On the Arch snapshot builder, run as a normal user:

```sh
cd packaging/photocraft-bin
makepkg --syncdeps
```

The upstream archive is downloaded by makepkg. Generated downloads, package files, `src/`, and `pkg/` are ignored by Git. The URL and checksum are also recorded in `external-packages.lock.json`.

The original Lollipop recipe is GPL-3.0-only. The upstream application retains its declared MIT/Apache-2.0 terms and bundled component notices; font licenses shipped under `usr/share/doc/photocraft/` are preserved. Lollipop does not relicense upstream binaries.

Validation covers checksum verification, package creation and resulting executable, desktop-entry, and license-file contents. A graphical launch and dependency installation still require a disposable desktop VM test.
