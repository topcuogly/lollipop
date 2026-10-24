# Desktop defaults

The imported profile files preserve the Alpha 0.3 identity and desktop behavior. This step does not include the full installer, update implementation, or a complete ISO build profile.

## Source layout

- `profile/airootfs/etc/skel/.config/`: KDE, KWin, Konsole, shortcuts, and per-user Fastfetch configuration.
- `profile/airootfs/usr/share/`: Plasma theme, color scheme, Konsole profile, Lollipop layout, Bash prompt, and OS identity template.
- `profile/airootfs/usr/local/bin/`: session initialization and user defaults, including Applications, Trashfiles, Projects, and the Dolphin Projects bookmark after Home.
- `profile/airootfs/usr/local/sbin/lollipop-branding`: restores Lollipop identity inside the target system; do not run this script on the host.
- `packaging/lollipop-system/desktop-assets.json`: maps existing repository artwork into installed paths.

The Plasma autostart entry runs first-session initialization. It changes the panel layout only until the per-user initialization marker exists. It is intended for fresh Lollipop homes, not importing settings into an existing desktop.

## Prepare an isolated desktop tree

With Python 3 and Pillow installed, from the repository root:

```sh
python3 scripts/prepare-desktop.py --output /tmp/lollipop-desktop-preview
```

The output directory must not exist. This command only stages files; it does not change the running desktop or build an ISO. It copies profile files, copies logos and ASCII from `assets/`, and creates KDE wallpaper packages with metadata and thumbnails for all eight repository wallpapers. Original artwork is stored only in `assets/`; generated copies belong outside Git.

The old Alpha 0.3 wallpaper entry `Lollipop-Hypnotic-original` has no exact image match in the current assets and is not recreated. The default Sugarline wallpaper remains mapped to `neon-orb-over-violet-waves.png`; the two additional repository wallpapers receive their own KDE entries.

`make-system-payload.py` now stages these generated files before assembling the package. The remaining package inputs and browser verification step are now imported, so the package can be built separately; see the [package instructions](../packaging/lollipop-system/README.md).

## Runtime limitations

The panel transparency and battery percentage settings are preserved, including the known visual issues. Window decoration configuration references `org.kde.lollipop`; its [separate package](../packaging/lollipop-decoration/README.md) is now imported and has passed a container build. The installer desktop entry and Calamares branding are now imported. `prepare-desktop.py` stages the Calamares logo from the main asset alongside the wallpaper packages. The live-session setup and boot profile are now imported; full ISO orchestration and boot testing remain required. These dependencies must be supplied before testing a complete image.

Automated checks cover user-home initialization and the layout script's requested settings. They do not prove the rendered Plasma appearance. Verify the assembled desktop in a fresh VM session before publishing an ISO.
