"""Regressions for failures observed on real hardware in Alpha 0.1."""
from pathlib import Path
import json,subprocess,re,unittest,tempfile,types,sys,runpy
from unittest.mock import patch
root=Path(__file__).resolve().parents[1];fs=root/'profile/airootfs'
class InstallerRegressionTests(unittest.TestCase):
 def test_live_sudo_rule_after_installed_admin_rule(self):
  rules=sorted(p.name for p in (fs/'etc/sudoers.d').iterdir())
  self.assertGreater(rules.index('90-lollipop-live'),rules.index('20-lollipop-admin'))
  self.assertIn('NOPASSWD: ALL',(fs/'etc/sudoers.d/90-lollipop-live').read_text())
  self.assertIn('/etc/sudoers.d/90-lollipop-live',(fs/'usr/local/sbin/lollipop-target').read_text())
 def test_actual_generated_preset_is_recognized_by_shell(self):
  helper=(fs/'usr/local/sbin/lollipop-target').read_text()
  line=next(x.strip() for x in helper.splitlines() if x.strip().startswith('printf "ALL_config='))
  line=line.split(' > ')[0]
  preset=subprocess.check_output(['bash','-c',line],text=True)
  result=subprocess.check_output(['bash','-c',preset+'\nprintf "%s" "${PRESETS[@]}"'],text=True)
  self.assertEqual(result,'default')
 def test_no_app_data_override_and_preflight_before_launcher(self):
  s=(fs/'usr/local/bin/install-lollipop').read_text()
  self.assertNotIn('/run/archiso/bootmnt',s);self.assertNotIn(' -c ',s);self.assertLess(s.index('lollipop-installer-preflight'),s.index('if sudo'))
 def test_both_live_sources_are_supported(self):
  s=(fs/'usr/local/bin/lollipop-installer-preflight').read_text()
  self.assertIn('/run/archiso/copytoram/airootfs.sfs',s)
  self.assertIn('/run/archiso/bootmnt/lollipop/x86_64/airootfs.sfs',s)
  self.assertIn('unsquashfs -s',s)
 def test_final_verifier_rejects_missing_and_omitted_initrd(self):
  with tempfile.TemporaryDirectory() as directory:
   base=Path(directory);(base/'boot/grub').mkdir(parents=True)
   fake=types.SimpleNamespace(globalstorage=types.SimpleNamespace(value=lambda _:directory))
   with patch.dict(sys.modules,{'libcalamares':fake}):
    run=runpy.run_path(str(fs/'usr/lib/calamares/modules/lollipop-verify/main.py'))['run']
    with patch('subprocess.run', return_value=types.SimpleNamespace(stdout='init\nusr/bin/busybox\n')):
     self.assertIn('initramfs missing',run()[1])
     (base/'boot/initramfs-linux-lts.img').write_bytes(b'\0'*1000001)
     (base/'boot/grub/grub.cfg').write_text('linux /vmlinuz-linux-lts\n')
     self.assertIn('no LTS initrd',run()[1])
     (base/'boot/grub/grub.cfg').write_text('linux /vmlinuz-linux-lts\n initrd /initramfs-linux-lts.img\n')
     self.assertIsNone(run())
 def test_wallpapers_have_matching_resolution_names(self):
  manifest=json.loads((root/'packaging/lollipop-system/desktop-assets.json').read_text())
  self.assertEqual(len(manifest['wallpapers']),8)
  self.assertTrue(all((root/x['source']).is_file() for x in manifest['wallpapers']))
 def test_terminal_and_new_apps(self):
  s=(fs/'usr/share/konsole/Lollipop.colorscheme').read_text()
  self.assertIn('Opacity=0.85',s);self.assertIn('Blur=true',s)
  names=set((root/'packages/native.txt').read_text().split())
  self.assertTrue({'zed','opencode','virt-manager','qemu-desktop','qbittorrent','torbrowser-launcher','rust','python-pip','base-devel','btop','arch-install-scripts'}<=names)
if __name__=='__main__':unittest.main()
