# Tor Browser verification material

- `tor-browser-developers.gpg`: public Tor Browser Developers verification keyring.
- `tor-browser.tar.xz.asc`: upstream detached signature for the archive pinned in `external-packages.lock.json`.
- Upstream download origin: https://dist.torproject.org/torbrowser/15.0.26/
- Pinned primary fingerprint: `EF6E286DDA85EA2A4BA7DE684E2C6E8793298290`.

These are public verification materials, not private signing keys. `scripts/prepare-tor.py` requires the pinned archive SHA-256 and an upstream signature matching the pinned fingerprint. The browser archive is downloaded into ignored `state/`, not committed. These files preserve the Alpha 0.3 build inputs; this is not a claim that the pinned browser is the latest release.

Tor Browser and its components retain upstream licenses. See the license notices shipped inside the official archive; Lollipop's GPL license does not replace them.

## Archiso

The unchanged pinned mkarchiso entry point, its upstream GPL license, and provenance are under [archiso/](archiso/README.md).
