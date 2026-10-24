# SPDX-License-Identifier: GPL-3.0-only
from pathlib import Path
import os,subprocess,tempfile,unittest
root=Path(__file__).resolve().parents[1]
class Guards(unittest.TestCase):
 def test_mutating_entrypoints_require_builder_flag(self):
  with tempfile.TemporaryDirectory() as name:
   path=Path(name);log=path/'called'
   for cmd in ['sudo','pacman','pacman-key','makepkg']:
    mock=path/cmd;mock.write_text('#!/bin/sh\ntouch "$GUARD_LOG"\nexit 99\n');mock.chmod(0o755)
   for script in ['build-full.sh','build.sh','prepare-builder.sh']:
    with self.subTest(script=script):
     result=subprocess.run(['bash',str(root/'scripts'/script)],env=dict(os.environ,PATH=name+':'+os.environ['PATH'],GUARD_LOG=str(log)),capture_output=True,text=True)
     self.assertNotEqual(result.returncode,0)
     self.assertFalse(log.exists())
 def test_release_key_directory_is_ignored(self):
  # Check the actual ignore rules without depending on this source tree being a Git checkout.
  with tempfile.TemporaryDirectory() as name:
   p=Path(name);subprocess.run(['git','init','-q',name],check=True)
   (p/'.gitignore').write_bytes((root/'.gitignore').read_bytes())
   files=['state/signing/private-keys-v1.d/test.key','state/release-keyring.gpg','out/lollipop.iso']
   for file in files:
    result=subprocess.run(['git','-C',name,'check-ignore','-q',file])
    self.assertEqual(result.returncode,0,file)
if __name__=='__main__':unittest.main()
