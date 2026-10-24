#!/usr/bin/env bash
set -euo pipefail
[[ $# -ge 1 ]] || { echo "Usage: $0 ISO [bios|uefi] [kvm|tcg]" >&2; exit 2; }
iso=$(realpath "$1"); firmware=${2:-bios}; accel=${3:-kvm}
[[ -f "$iso" ]] || exit 1
case "$accel" in
 kvm) [[ -r /dev/kvm && -w /dev/kvm ]] || { echo '/dev/kvm inaccessible; use tcg or fix host permissions.' >&2; exit 1; }; cpu=host ;;
 tcg) cpu=max ;;
 *) exit 2 ;;
esac
args=(-machine "q35,accel=$accel" -cpu "$cpu" -m 4096 -smp 4
 -device virtio-vga -display gtk -nic user,model=virtio-net-pci
 -device qemu-xhci -device usb-tablet -device intel-hda -device hda-duplex
 -cdrom "$iso" -boot d)
case "$firmware" in
 bios) ;;
 uefi)
  code=${OVMF_CODE:-/usr/share/edk2/ovmf/OVMF_CODE.fd}
  vars=${OVMF_VARS:-/usr/share/edk2/ovmf/OVMF_VARS.fd}
  [[ -r "$code" && -r "$vars" ]] || { echo 'Set OVMF_CODE and OVMF_VARS to matching non-Secure-Boot firmware files.' >&2; exit 1; }
  temp=$(mktemp -d); trap 'rm -rf -- "$temp"' EXIT
  cp "$vars" "$temp/vars.fd"
  args+=(-drive "if=pflash,format=raw,readonly=on,file=$code" -drive "if=pflash,format=raw,file=$temp/vars.fd") ;;
 *) exit 2 ;;
esac
qemu-system-x86_64 "${args[@]}"
