#!/usr/bin/env bash
# Destructive to the disposable container's sudoers only; never run on a host/builder.
set -euo pipefail
[[ $EUID == 0 && -f /run/.containerenv && ${LOLLIPOP_ISOLATED_SUDO_TEST:-} == 1 ]] || { echo 'Disposable Podman test container only.' >&2; exit 1; }
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
id live &>/dev/null || useradd -m -G wheel live
usermod -aG wheel live
passwd -d live >/dev/null
install -m 440 "$ROOT/profile/airootfs/etc/sudoers.d/20-lollipop-admin" /etc/sudoers.d/20-lollipop-admin
printf 'live ALL=(ALL:ALL) NOPASSWD: ALL\n' > /etc/sudoers.d/10-live
chmod 440 /etc/sudoers.d/10-live
if runuser -u live -- sudo -n /usr/bin/true; then
 echo 'FAIL: old conflicting policy unexpectedly permitted noninteractive sudo'; exit 1
fi
echo 'PASS: reproduced password-required with old 10-live before 20-lollipop-admin'
rm /etc/sudoers.d/10-live
install -m 440 "$ROOT/profile/airootfs/etc/sudoers.d/90-lollipop-live" /etc/sudoers.d/90-lollipop-live
visudo -c
runuser -u live -- sudo -n /usr/bin/true
echo 'PASS: corrected Live policy permits noninteractive installer elevation'
rm /etc/sudoers.d/90-lollipop-live
runuser -u live -- sudo -k
if runuser -u live -- sudo -n /usr/bin/true; then
 echo 'FAIL: noninteractive access remained after removing Live policy'; exit 1
fi
echo 'PASS: removing Live-only policy restores password requirement for wheel'
