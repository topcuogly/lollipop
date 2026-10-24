#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
source "$ROOT/build.env"
export SOURCE_DATE_EPOCH TZ=UTC LC_ALL=C GNUPGHOME="$ROOT/state/signing"
[[ $EUID != 0 ]] || { echo 'Run package builds as the normal builder user.' >&2; exit 1; }
[[ -f "$ROOT/state/signing-fingerprint" ]] || { echo 'Initialize release signing first.' >&2; exit 1; }
[[ ! -e "$ROOT/state/repo" ]] || { echo 'Archive the previous state/repo before rebuilding; stale packages must not enter the ISO.' >&2; exit 1; }
python3 "$ROOT/scripts/prepare-calamares.py"
python3 "$ROOT/scripts/make-system-payload.py"
for name in lollipop-decoration photocraft-bin upscayl-bin; do
 mkdir -p "$ROOT/state/$name"
 cp "$ROOT/packaging/$name/PKGBUILD" "$ROOT/state/$name/"
done
packages=()
for name in calamares lollipop-system lollipop-decoration photocraft-bin upscayl-bin; do
 directory="$ROOT/state/$name"
 (cd "$directory"; makepkg --noconfirm --cleanbuild --force)
 mapfile -t built < <(cd "$directory"; makepkg --packagelist)
 [[ ${#built[@]} == 1 && -f "${built[0]}" ]] || { echo "Unexpected package output: $name" >&2; exit 1; }
 packages+=("${built[0]}")
done
mkdir "$ROOT/state/repo"
fingerprint=$(cat "$ROOT/state/signing-fingerprint")
for package in "${packages[@]}"; do
 gpg --batch --yes --pinentry-mode loopback --passphrase '' --local-user "$fingerprint" --detach-sign "$package"
 cp "$package" "$package.sig" "$ROOT/state/repo/"
done
repo-add --sign --key "$fingerprint" "$ROOT/state/repo/lollipop.db.tar.gz" "$ROOT/state/repo/"*.pkg.tar.zst
