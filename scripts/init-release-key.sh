#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
[[ $EUID != 0 ]] || { echo 'Run as the normal builder user.' >&2; exit 1; }
export GNUPGHOME="$ROOT/state/signing"
mkdir -p "$GNUPGHOME"
chmod 700 "$GNUPGHOME"
if ! gpg --batch --list-secret-keys 2>/dev/null | grep -q '^sec'; then
 gpg --batch --pinentry-mode loopback --passphrase '' --quick-generate-key 'Lollipop Local Release Signing' ed25519 sign 2y
fi
fingerprint=$(gpg --batch --with-colons --list-keys | awk -F: '$1=="fpr" {print $10;exit}')
printf '%s\n' "$fingerprint" > "$ROOT/state/signing-fingerprint"
gpg --batch --armor --export "$fingerprint" > "$ROOT/state/release-public.asc"
gpg --batch --export "$fingerprint" > "$ROOT/state/release-keyring.gpg"
echo "Local signing fingerprint: $fingerprint"
echo 'Keep state/signing private and backed up; it is excluded from the source archive and ISO.'
