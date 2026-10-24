# SPDX-License-Identifier: GPL-3.0-only
from pathlib import Path
import importlib.util,json,tempfile,unittest,subprocess
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('prepare_live',root/'scripts/prepare-live-profile.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class LiveProfile(unittest.TestCase):
 def test_stage_removes_packaged_files_and_keeps_live_setup(self):
  with tempfile.TemporaryDirectory() as name:
   base=Path(name);manifest=base/'files.json';owned=['usr/local/bin/lollipop-session','etc/skel/.config/kdeglobals','usr/share/lollipop/logo-ascii.txt']
   manifest.write_text(json.dumps(owned));key=base/'test-public.gpg';key.write_bytes(b'test fixture only')
   out=module.prepare(base/'profile',manifest,key);fs=out/'airootfs'
   self.assertFalse(any((fs/p).exists() for p in owned))
   self.assertTrue((fs/'usr/local/bin/lollipop-live-setup').is_file())
   self.assertEqual((fs/'etc/systemd/system/display-manager.service').readlink(),Path('/usr/lib/systemd/system/sddm.service'))
   self.assertEqual((fs/'etc/lollipop/release-keyring.gpg').read_bytes(),key.read_bytes())
   self.assertEqual((out/'packages.x86_64').read_bytes(),(root/'packages/native.txt').read_bytes())
   self.assertTrue((fs/'usr/share/calamares/branding/lollipop/logo.png').is_file())
 def test_rejects_manifest_escape_before_creating_output(self):
  with tempfile.TemporaryDirectory() as name:
   base=Path(name);m=base/'files.json';m.write_text('["../outside"]')
   with self.assertRaises(ValueError):module.prepare(base/'out',m,base/'no-key')
   self.assertFalse((base/'out').exists())
 def test_boot_identity_and_permissions(self):
  for name in ['syslinux/syslinux-linux.cfg','efiboot/loader/entries/01-lollipop.conf']:
   text=(root/'profile'/name).read_text()
   self.assertIn('Lollipop Alpha 0.3',text);self.assertIn('vmlinuz-linux-lts',text);self.assertIn('initramfs-linux-lts.img',text)
  text=(root/'profile/profiledef.sh').read_text()
  self.assertIn('["/etc/sudoers.d/90-lollipop-live"]="0:0:440"',text)
  self.assertIn('["/etc/shadow"]="0:0:400"',text)
  self.assertEqual((root/'profile/packages.x86_64').resolve(),(root/'packages/native.txt').resolve())
if __name__=='__main__':unittest.main()
