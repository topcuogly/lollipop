# SPDX-License-Identifier: GPL-3.0-only
import sys,tempfile,json,unittest,subprocess
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'profile/airootfs/usr/lib/lollipop'))
import updates
class Transaction(unittest.TestCase):
 def exercise(self,fail=False,third=False):
  with tempfile.TemporaryDirectory() as name:
   p=Path(name);base=p/'state';snaps=p/'snapshots';snaps.mkdir();current=p/'release.json';current.write_text('{"sequence":0,"snapshot":"2026/10/22"}')
   pacman=p/'pacman.conf';pacman.write_text('old repository')
   release={'sequence':1,'release':'test','snapshot':'2026/10/23'}
   if third:
    (snaps/'transactions.json').write_text(json.dumps([{'pre':1,'post':2,'status':'complete'},{'pre':3,'post':4,'status':'complete'}]))
    for number in range(1,5):(snaps/str(number)).mkdir()
   events=[]
   def checkpoint(kind,*args):events.append(kind);return 5 if kind=='pre' else 6
   def run(*args,**kw):
    events.append(args)
    if fail and args[0]=='pacman':raise subprocess.CalledProcessError(1,args)
   with patch.multiple(updates,BASE=base,SNAPSHOTS=snaps,CURRENT=current,PACMAN_CONF=pacman,LIVE_MARKER=p/'not-live'),patch.object(updates.os,'geteuid',return_value=0),patch.object(updates.os.path,'ismount',return_value=True),patch.object(updates.shutil,'disk_usage',return_value=SimpleNamespace(free=10*1024**3)),patch.object(updates.subprocess,'check_output',return_value='btrfs\n'),patch.object(updates,'verified',return_value=release),patch.object(updates,'checkpoint',side_effect=checkpoint),patch.object(updates,'refresh_grub'),patch.object(updates,'run',side_effect=run):
    if fail:
     with self.assertRaises(subprocess.CalledProcessError):updates.apply('manifest','sig')
     self.assertEqual(json.loads((snaps/'transactions.json').read_text())[-1]['status'],'failed-recovery-required')
     self.assertEqual(json.loads(current.read_text())['sequence'],0)
     self.assertIn('2026/10/23',pacman.read_text())
     with self.assertRaises(RuntimeError):updates.apply('manifest','sig')
    else:
     updates.apply('manifest','sig')
     history=json.loads((snaps/'transactions.json').read_text())
     self.assertEqual(history[-1]['post'],6);self.assertEqual(history[-1]['status'],'complete')
     self.assertEqual(json.loads(current.read_text())['sequence'],1)
     if third:
      self.assertEqual(len(history),2);self.assertFalse((snaps/'1').exists());self.assertFalse((snaps/'2').exists());self.assertTrue((snaps/'3').exists())
   self.assertEqual(events[0],'pre')
   self.assertTrue(any(isinstance(x,tuple) and x[0]=='pacman' for x in events))
 def test_success(self):self.exercise()
 def test_failure_requires_recovery(self):self.exercise(fail=True)
 def test_two_owned_pairs(self):self.exercise(third=True)
unittest.main()
