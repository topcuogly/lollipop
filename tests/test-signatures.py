# SPDX-License-Identifier: GPL-3.0-only
from pathlib import Path
import tempfile,subprocess,sys,json,datetime as dt,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'profile/airootfs/usr/lib/lollipop'))
import updates
class Signatures(unittest.TestCase):
 def test_valid_and_modified_manifest(self):
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder);home=p/'signing';home.mkdir(mode=0o700)
   subprocess.run(['gpg','--homedir',str(home),'--batch','--pinentry-mode','loopback','--passphrase','','--quick-generate-key','Lollipop test only','ed25519','sign','1d'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   key=p/'public.gpg'
   with key.open('wb') as f:subprocess.run(['gpg','--homedir',str(home),'--export'],check=True,stdout=f,stderr=subprocess.DEVNULL)
   current=p/'current.json';current.write_text(json.dumps({'sequence':0,'snapshot':'2026/10/22'}))
   manifest=p/'release.json';manifest.write_text(json.dumps({'schema':1,'sequence':1,'release':'test','date':dt.date.today().isoformat(),'snapshot':'2026/10/22','kind':'emergency','reason':'Test'}))
   subprocess.run(['gpg','--homedir',str(home),'--batch','--pinentry-mode','loopback','--passphrase','','--detach-sign',str(manifest)],check=True,stderr=subprocess.DEVNULL)
   updates.TRUST=key;updates.CURRENT=current
   self.assertEqual(updates.verified(manifest,str(manifest)+'.sig')['sequence'],1)
   manifest.write_text(manifest.read_text()+' ')
   with self.assertRaises(subprocess.CalledProcessError):updates.verified(manifest,str(manifest)+'.sig')
unittest.main()
