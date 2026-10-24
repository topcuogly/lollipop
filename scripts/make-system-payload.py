#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
from pathlib import Path
import tarfile,json,hashlib,os
root=Path(__file__).resolve().parents[1];fs=root/'profile/airootfs'
includes=['usr/local/bin/lollipop-user-defaults','usr/local/bin/loli-install','usr/local/bin/loli-remove','usr/local/bin/loli-search','usr/local/bin/loli-which','usr/local/bin/loli-listall','usr/local/bin/loli-clean','usr/local/bin/loli-update','usr/share/applications/lollipop-tor-browser.desktop','etc/skel/.local','usr/local/bin/lollipop-tor-browser','usr/share/konsole','usr/share/icons/hicolor/512x512/apps/lollipop-launcher.png','etc/systemd/system/lollipop-libvirt-network.service','etc/systemd/system/multi-user.target.wants/libvirtd.service','etc/systemd/system/multi-user.target.wants/lollipop-libvirt-network.service','usr/share/lollipop','usr/share/pixmaps/lollipop.png','usr/share/icons/hicolor/512x512/apps/lollipop.png','etc/sddm.conf.d/20-lollipop-theme.conf','usr/share/wallpapers','usr/share/color-schemes','usr/share/plasma/desktoptheme','usr/lib/lollipop','usr/local/bin/lollipop-session','usr/local/bin/lollipop-install-flatpaks','usr/local/sbin/lollipop-branding','usr/local/sbin/lollipop-update','usr/local/sbin/lollipop-recover','usr/local/sbin/lollipop-snapshot-setup','etc/skel/.config','etc/fastfetch','etc/lollipop','etc/systemd/zram-generator.conf','etc/sudoers.d/20-lollipop-admin','etc/pacman.d/hooks/zz-lollipop-branding.hook','etc/systemd/system/lollipop-update-check.service','etc/systemd/system/lollipop-update-check.timer','etc/systemd/system/systemd-coredumpd.service']
files=set()
for item in includes:
 p=fs/item
 if p.is_dir():files.update(x for x in p.rglob('*') if (x.is_file() or x.is_symlink()) and '__pycache__' not in x.parts and x.suffix != '.pyc')
 else:files.add(p)
torfile=root/'state/tor-browser.tar.xz'
assert torfile.is_file(), 'Run scripts/prepare-tor.py first'
output=root/'state/lollipop-system';output.mkdir(parents=True,exist_ok=True)
with tarfile.open(output/'lollipop-system.tar','w') as archive:
 for file in sorted(files):
  info=archive.gettarinfo(file,arcname='payload/'+str(file.relative_to(fs)))
  info.uid=info.gid=0;info.uname=info.gname='';info.mtime=int(os.environ.get('SOURCE_DATE_EPOCH','1792627200'))
  if info.isfile():
   with file.open('rb') as stream:archive.addfile(info,stream)
  else:archive.addfile(info)
 with torfile.open('rb') as stream:
  info=archive.gettarinfo(torfile,arcname='payload/usr/share/lollipop/tor-browser.tar.xz')
  info.uid=info.gid=0;info.uname=info.gname='';info.mtime=int(os.environ.get('SOURCE_DATE_EPOCH','1792627200'));archive.addfile(info,stream)
digest=hashlib.sha256((output/'lollipop-system.tar').read_bytes()).hexdigest()
(output/'PKGBUILD').write_text((root/'packaging/lollipop-system/PKGBUILD').read_text().replace('SOURCE_DIGEST',digest))
(root/'state/system-payload-files.json').write_text(json.dumps([str(f.relative_to(fs)) for f in sorted(files)],indent=2)+'\n')
print('Lollipop system payload SHA256:',digest)
