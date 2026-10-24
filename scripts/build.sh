#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
source "$ROOT/build.env"
export SOURCE_DATE_EPOCH TZ=UTC LC_ALL=C
[[ ${1:-} == --disposable-builder && $EUID == 0 && -e /etc/arch-release && $(uname -m) == x86_64 ]] || { echo 'Use --disposable-builder on the dedicated Arch x86_64 builder VM.' >&2; exit 1; }
work=${BUILD_WORK:-/var/tmp/lollipop-build-alpha03}
stage="$ROOT/state/profile"
[[ ! -e "$work" && ! -e "$stage" ]] || { echo 'Use fresh work and state/profile paths; archive old state before retrying.' >&2; exit 1; }
[[ -f "$ROOT/state/repo/lollipop.db.tar.gz.sig" && -f "$ROOT/state/release-keyring.gpg" ]] || { echo 'Build signed local packages first.' >&2; exit 1; }
python3 "$ROOT/tests/check-build-inputs.py"
pacman-key --add "$ROOT/state/release-public.asc"
pacman-key --lsign-key "$(cat "$ROOT/state/signing-fingerprint")"
python3 "$ROOT/scripts/prepare-live-profile.py" --output "$stage" --package-files "$ROOT/state/system-payload-files.json" --release-key "$ROOT/state/release-keyring.gpg"
mkdir -p "$ROOT/out" "$ROOT/state/pacman-cache"
python3 - "$stage/pacman.conf" "$ROOT/state/repo" "$ROOT/state/pacman-cache" <<'PYCONFIG'
from pathlib import Path
import sys
conf,repo,cache=map(Path,sys.argv[1:])
if any('\n' in str(p) or '\r' in str(p) for p in (repo,cache)):raise SystemExit('Invalid builder path')
text=conf.read_text().replace('[options]','[options]\nCacheDir = '+str(cache),1)
text+='\n[lollipop]\nSigLevel = Required DatabaseOptional\nServer = '+repo.resolve().as_uri()+'\n'
conf.write_text(text)
PYCONFIG
bash "$ROOT/vendor/archiso/mkarchiso" -v -w "$work" -o "$ROOT/out" "$stage" 2>&1 | tee "$ROOT/out/build.log"
(cd "$ROOT/out"; sha256sum ./*.iso > SHA256SUMS)
pacman -Q > "$ROOT/out/builder-packages.txt"
cp "$ROOT/build.env" "$ROOT/out/build-inputs.env"
cp "$ROOT/state/release-public.asc" "$ROOT/out/release-public.asc"
