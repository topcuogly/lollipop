#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
[[ ${1:-} == --disposable-builder && $EUID != 0 ]] || { echo 'Run as the normal user: bash scripts/build-full.sh --disposable-builder (dedicated Arch VM only).' >&2; exit 1; }
sudo bash "$ROOT/scripts/prepare-builder.sh" --disposable-builder
python3 "$ROOT/scripts/prepare-calamares.py"
bash "$ROOT/scripts/validate.sh"
python3 "$ROOT/scripts/check-packages.py"
bash "$ROOT/scripts/init-release-key.sh"
bash "$ROOT/scripts/build-packages.sh"
sudo bash "$ROOT/scripts/build.sh" --disposable-builder
