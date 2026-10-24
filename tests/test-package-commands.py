# SPDX-License-Identifier: GPL-3.0-only
from pathlib import Path
import tempfile,os,subprocess,json,unittest
root=Path(__file__).resolve().parents[1];bins=root/'profile/airootfs/usr/local/bin'
class Commands(unittest.TestCase):
 def test_install_preserves_argument_boundaries(self):
  with tempfile.TemporaryDirectory() as name:
   p=Path(name);mock=p/'sudo';mock.write_text('#!/usr/bin/env python3\nimport os,sys,json\nopen(os.environ["TEST_LOG"],"w").write(json.dumps(sys.argv[1:]))\n');mock.chmod(0o755)
   log=p/'log';env=dict(os.environ,PATH=name+':'+os.environ['PATH'],TEST_LOG=str(log))
   subprocess.run(['bash',str(bins/'loli-install'),'--needed','example argument'],env=env,check=True)
   self.assertEqual(json.loads(log.read_text()),['pacman','-S','--needed','example argument'])
 def test_unconfigured_update_never_applies_or_runs_pacman(self):
  with tempfile.TemporaryDirectory() as name:
   p=Path(name);config=p/'channel.json';config.write_text('{"manifest_url":""}')
   wrapper=p/'loli-update';wrapper.write_text((bins/'loli-update').read_text().replace('/etc/lollipop/update-channel.json',str(config)))
   mock=p/'sudo';mock.write_text('#!/usr/bin/env python3\nimport os,sys,json\nopen(os.environ["TEST_LOG"],"w").write(json.dumps(sys.argv[1:]))\n');mock.chmod(0o755)
   log=p/'log';env=dict(os.environ,PATH=name+':'+os.environ['PATH'],TEST_LOG=str(log))
   subprocess.run(['bash',str(wrapper)],env=env,check=True)
   self.assertEqual(json.loads(log.read_text()),['/usr/local/sbin/lollipop-update','check'])
if __name__=='__main__':unittest.main()
