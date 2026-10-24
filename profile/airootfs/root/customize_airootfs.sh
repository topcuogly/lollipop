#!/usr/bin/env bash
set -euo pipefail
# Supported by the vendored Archiso commit; source is removed by mkarchiso after execution.
/usr/local/sbin/lollipop-branding
# Offline install payload: fail the build rather than silently ship an incomplete desktop.
flatpak --system remote-add --if-not-exists flathub /usr/share/lollipop/flathub.flatpakrepo
mapfile -t apps < /usr/share/lollipop/flatpak-apps.txt
flatpak --system install --noninteractive -y flathub "${apps[@]}"
flatpak --system update --appstream flathub
flatpak --system list --columns=ref,origin,active > /usr/share/lollipop/flatpak-installed.lock
# This marker can only appear in a build with the complete default Flatpak payload.
touch /usr/share/lollipop/full-payload-ready
