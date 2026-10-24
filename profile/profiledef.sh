#!/usr/bin/env bash
iso_name="lollipop"
iso_label="LOLLIPOP_A03"
iso_publisher="Lollipop prototype"
iso_application="Lollipop Alpha 0.3 Plasma Wayland Live"
iso_version="alpha-0.3"
install_dir="lollipop"
buildmodes=('iso')
bootmodes=('bios.syslinux' 'uefi.systemd-boot')
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'xz' '-Xbcj' 'x86' '-b' '1M' '-Xdict-size' '1M' '-processors' '1')
file_permissions=(
 ["/usr/local/bin/lollipop-user-defaults"]="0:0:755"
 ["/usr/local/bin/lollipop-installer-preflight"]="0:0:755"
 ["/usr/local/sbin/lollipop-snapshot-setup"]="0:0:755"
 ["/usr/local/sbin/lollipop-update"]="0:0:755"
 ["/usr/local/sbin/lollipop-recover"]="0:0:755"
 ["/root/customize_airootfs.sh"]="0:0:755"

 ["/usr/local/sbin/lollipop-branding"]="0:0:755"
 ["/usr/local/sbin/lollipop-target"]="0:0:755"
 ["/usr/local/bin/install-lollipop"]="0:0:755"
 ["/etc/sudoers.d/20-lollipop-admin"]="0:0:440"
 ["/etc/skel/Desktop/install-lollipop.desktop"]="0:0:755"
 ["/etc/shadow"]="0:0:400"
 ["/etc/sudoers.d/90-lollipop-live"]="0:0:440"
 ["/usr/local/bin/lollipop-live-setup"]="0:0:755"
 ["/usr/local/bin/lollipop-flathub"]="0:0:755"
 ["/usr/local/bin/lollipop-install-flatpaks"]="0:0:755"
 ["/usr/local/bin/lollipop-session"]="0:0:755"
)
