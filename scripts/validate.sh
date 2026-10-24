#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
for file in "$ROOT"/scripts/*.sh "$ROOT/profile/profiledef.sh" "$ROOT/profile/airootfs/usr/local/bin/"* "$ROOT/profile/airootfs/usr/local/sbin/"* "$ROOT/profile/airootfs/root/customize_airootfs.sh"; do
 if head -n 1 "$file" | grep -q bash; then bash -n "$file"; fi
done
python3 "$ROOT/tests/check-build-inputs.py"
[[ -f "$ROOT/state/calamares/calamares-3.4.2.tar" ]] || { echo 'Run python3 scripts/prepare-calamares.py before validation.' >&2; exit 1; }
python3 "$ROOT/tests/check-calamares.py"
for test in updates transactions signatures installer-regressions user-defaults package-commands live-profile live-launcher build-orchestration; do
 python3 "$ROOT/tests/test-$test.py"
done
# The layout contract test is optional on minimal builders; it is not a visual test.
if command -v node >/dev/null; then node "$ROOT/tests/check-layout.mjs"; fi
