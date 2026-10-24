# lollipop-decoration

A separate KWin window decoration derived from KDE Breeze 6.8.1. Existing desktop defaults select the plugin ID `org.kde.lollipop`.

## Changes from Breeze

- Change `Frame_FrameRadius` from `2.5` to `4.5` (approximately 9 logical pixels where Breeze applies its usual scaling).
- Build the decoration plugin as `org.kde.lollipop.so`, leaving the official Breeze plugin intact.
- Set its plugin name to `Lollipop Rounded` and ID to `org.kde.lollipop`.

The preparation step requires exact upstream replacement matches and fails if the expected source changes. It preserves upstream description, author, copyright, and license metadata. Only the renamed decoration plugin is packaged; shared libraries and configuration UI remain provided by matching Breeze.

## Build

On an Arch builder configured for Lollipop's 2026-10-22 snapshot:

```sh
cd packaging/lollipop-decoration
makepkg --syncdeps
```

Run as a normal user. The recipe downloads the versioned upstream archive and verifies its SHA-256 before extraction. Generated archives, build directories, and binary packages are ignored by Git. `LOLLIPOP_JOBS` can override the default four build jobs.

The package requires `breeze=6.8.1` and KDecoration. This is a pinned Alpha 0.3 component, not a decoration intended to track arbitrary future Plasma versions. Rebase and test it when changing the desktop snapshot.

## Scope and licensing

KWin applies this decoration to windows using server-side decoration. Applications drawing their own frames may retain their own corner shape. Runtime appearance must be tested in a Plasma session; compiling the plugin alone does not prove its appearance or behavior.

The Lollipop package recipe is GPL-3.0-only. The Breeze-derived plugin retains upstream GPL-2.0-or-later terms and notices. The repository license does not replace those upstream terms.
