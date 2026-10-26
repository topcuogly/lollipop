# SPDX-License-Identifier: GPL-3.0-only
from pathlib import Path
import hashlib,json,ast
root=Path(__file__).resolve().parents[1]
lock=json.loads((root/'external-packages.lock.json').read_text())
assert hashlib.sha256((root/'vendor/archiso/mkarchiso').read_bytes()).hexdigest()==lock['archiso']['sha256']
assert (root/'profile/packages.x86_64').read_bytes()==(root/'packages/native.txt').read_bytes()
assert (root/'profile/airootfs/usr/share/lollipop/flatpak-apps.txt').read_bytes()==(root/'packages/flatpak.txt').read_bytes()
assert lock['archiso']['commit'] in (root/'build.conf').read_text()
assert lock['calamares']['commit'] in (root/'build.conf').read_text()
for name in ['calamares','lollipop-system','lollipop-decoration','photocraft-bin','upscayl-bin']:
 assert (root/'packaging'/name/'PKGBUILD').is_file()
for folder in ['scripts','tests','profile/airootfs/usr/lib']:
 for p in (root/folder).rglob('*.py'):
  if '__pycache__' not in p.parts:ast.parse(p.read_text())
assert not (root/'profile/airootfs/etc/lollipop/release-keyring.gpg').exists()
assert not list((root/'profile').rglob('private-keys-v1.d'))
print('PASS: pinned Archiso hash, canonical package lists, build commits, recipes and no injected signing state')
