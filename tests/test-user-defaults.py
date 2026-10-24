from pathlib import Path
import tempfile,subprocess,os,unittest,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
script=root/'profile/airootfs/usr/local/bin/lollipop-user-defaults'
class Places(unittest.TestCase):
 def test_idempotent_preserves_custom_bookmark_and_home_order(self):
  with tempfile.TemporaryDirectory() as name:
   h=Path(name);(h/'.bashrc').write_text('# existing user setting\n');p=h/'.local/share/user-places.xbel';p.parent.mkdir(parents=True)
   p.write_text(f'<xbel version="1.0"><bookmark href="{h.as_uri()}"><title>Home</title></bookmark><bookmark href="file:///custom"><title>Keep me</title></bookmark></xbel>')
   env=dict(os.environ,HOME=name,USER='test')
   for _ in range(2):subprocess.run(['python3',str(script)],env=env,check=True)
   b=ET.parse(p).getroot().findall('bookmark')
   self.assertEqual([x.findtext('title') for x in b],['Home','Projects','Keep me'])
   self.assertTrue((h/'.bashrc').read_text().startswith('# existing user setting'))
   self.assertEqual((h/'.bashrc').read_text().count('[ -r /usr/share/lollipop/bashrc ]'),1)
   self.assertTrue(all((h/x).is_dir() for x in ['Applications','Trashfiles','Projects']))
 def test_fresh_home_has_standard_places(self):
  with tempfile.TemporaryDirectory() as name:
   subprocess.run(['python3',str(script)],env=dict(os.environ,HOME=name,USER='test'),check=True)
   b=ET.parse(Path(name)/'.local/share/user-places.xbel').getroot().findall('bookmark')
   self.assertEqual([x.findtext('title') for x in b][:2],['Home','Projects'])
   self.assertIn('Trash',[x.findtext('title') for x in b])
if __name__=='__main__':unittest.main()
