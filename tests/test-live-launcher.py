# SPDX-License-Identifier: GPL-3.0-only
"""Check pre-SDDM launcher setup without creating accounts or changing the host."""
from pathlib import Path
import json,os,subprocess,tempfile,unittest
root=Path(__file__).resolve().parents[1]
class LauncherSetup(unittest.TestCase):
 def exercise(self,desktop):
  with tempfile.TemporaryDirectory() as name:
   base=Path(name);log=base/'calls';bin=base/'bin';bin.mkdir()
   stub='''#!/usr/bin/env python3
import sys,os,json
from pathlib import Path
cmd=Path(sys.argv[0]).name
with open(os.environ['TEST_CALLS'],'a') as f:f.write(json.dumps([cmd]+sys.argv[1:])+'\\n')
if cmd=='runuser' and sys.argv[-2:]==['xdg-user-dir','DESKTOP']:print(os.environ['TEST_DESKTOP'])
'''
   for cmd in ['id','useradd','passwd','locale-gen','runuser','install']:
    p=bin/cmd;p.write_text(stub);p.chmod(0o755)
   subprocess.run(['bash',str(root/'profile/airootfs/usr/local/bin/lollipop-live-setup')],check=True,env=dict(os.environ,PATH=str(bin)+':'+os.environ['PATH'],TEST_CALLS=str(log),TEST_DESKTOP=desktop))
   return [json.loads(line) for line in log.read_text().splitlines()]
 def test_prepares_localized_desktop_before_login(self):
  calls=self.exercise('/home/live/Masaüstü')
  self.assertIn(['runuser','-u','live','--','xdg-user-dirs-update'],calls)
  self.assertIn(['install','-o','live','-g','live','-m','755','/usr/share/applications/install-lollipop.desktop','/home/live/Masaüstü/install-lollipop.desktop'],calls)
 def test_disabled_xdg_desktop_is_reenabled(self):
  calls=self.exercise('/home/live')
  self.assertIn(['runuser','-u','live','--','xdg-user-dirs-update','--set','DESKTOP','/home/live/Desktop'],calls)
  self.assertIn(['install','-o','live','-g','live','-m','755','/usr/share/applications/install-lollipop.desktop','/home/live/Desktop/install-lollipop.desktop'],calls)
if __name__=='__main__':unittest.main()
