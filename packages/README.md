# Package inventory

These lists document the direct package selections in the Alpha 0.3 build source. Dependencies are resolved separately; these are not a complete installed-package inventory or version lockfiles.

- `native.txt`: Pacman package names from the Archiso profile, including locally built packages.
- `flatpak.txt`: application IDs installed from Flathub during the ISO build. Required runtimes are installed as dependencies.

The locally built native packages are `calamares`, `lollipop-system`, `lollipop-decoration`, `photocraft-bin`, and `upscayl-bin`. They require the build project's signed local repository and cannot be installed from the official Arch repositories alone.

Tor Browser also has a verified upstream browser archive bundled by the build process; the `torbrowser-launcher` package name alone does not describe that payload.

This repository currently records the inventory. It does not yet contain the full build system, local package recipes, version locks, or bundled browser preparation scripts. These files alone are insufficient to reproduce an ISO.
