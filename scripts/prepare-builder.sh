#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
[[ ${1:-} == --disposable-builder && $EUID == 0 && -e /etc/arch-release && $(uname -m) == x86_64 ]] || { echo 'Use only the disposable Arch builder VM.' >&2; exit 1; }
pacman-key --init
pacman-key --populate archlinux
# This VM is dedicated to this release. Its toolchain must use the same snapshot.
install -m 644 "$ROOT/profile/pacman.conf" /etc/pacman.conf
pacman -Syyuu --noconfirm kdecoration kcmutils kiconthemes kcolorscheme breeze base-devel archiso arch-install-scripts dosfstools e2fsprogs grub libarchive libisoburn mtools openssl squashfs-tools syslinux cmake extra-cmake-modules ninja qt6-tools qt6-translations qt6-declarative qt6-svg libglvnd polkit-qt6 kpmcore libpwquality yaml-cpp python python-pillow python-yaml python-jsonschema flatpak git gnupg snapper btrfs-progs fastfetch gtk3 nss libxss libxtst alsa-lib at-spi2-core mesa libxkbcommon vulkan-icd-loader
