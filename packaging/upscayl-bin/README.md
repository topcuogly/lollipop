# upscayl-bin

Repackages the pinned official Upscayl 2.15.0 x86_64 Debian archive as an Arch package. The recipe verifies SHA-512, extracts its data archive, preserves `opt/` and `usr/`, and provides `/usr/bin/upscayl` pointing to `/opt/Upscayl/upscayl`. Debian maintainer scripts are not executed.

On the Arch snapshot builder, run as a normal user:

```sh
cd packaging/upscayl-bin
makepkg --syncdeps
```

The upstream archive is downloaded by makepkg. Generated downloads, package files, `src/`, and `pkg/` are ignored by Git. The URL and checksum are also recorded in `external-packages.lock.json`.

The packaged Electron `chrome-sandbox` helper retains the Alpha 0.3 recipe's root-owned setuid mode `4755`. Package creation is tested in an isolated container, without installing or running the application on the development host.

The original Lollipop recipe is GPL-3.0-only. Upscayl retains upstream AGPL-3.0-only terms and its bundled Electron/component license notices. Lollipop does not relicense upstream binaries.

Validation covers checksum verification, package creation, executable/sandbox permissions, launcher symlink, desktop entry, and bundled license notices. Graphical launch and GPU/Vulkan functionality still require a desktop VM or hardware test.
