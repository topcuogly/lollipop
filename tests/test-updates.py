# SPDX-License-Identifier: GPL-3.0-only
from pathlib import Path
import sys,datetime as dt,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'profile/airootfs/usr/lib/lollipop'))
import updates
class Policy(unittest.TestCase):
 def manifest(self):return {'schema':1,'sequence':1,'release':'2027.01','kind':'quarterly','date':'2027-01-15','snapshot':'2026/12/15','reason':'Scheduled'}
 def validate(self,m):return updates.validate(m,{'sequence':0,'snapshot':'2026/10/22'},dt.date(2027,1,15))
 def test_calendar(self):self.assertEqual(updates.previous_month(dt.date(2027,1,15)),dt.date(2026,12,15))
 def test_accept(self):self.validate(self.manifest())
 def test_replay(self):
  m=self.manifest();m['sequence']=0
  with self.assertRaises(ValueError):self.validate(m)
 def test_wrong_month(self):
  m=self.manifest();m['snapshot']='2026/12/14'
  with self.assertRaises(ValueError):self.validate(m)
 def test_future(self):
  with self.assertRaises(ValueError):updates.validate(self.manifest(),{'sequence':0,'snapshot':'2026/10/22'},dt.date(2026,10,23))
 def test_emergency(self):
  m=self.manifest();m.update(kind='emergency',date='2026-10-23',snapshot='2026/10/22',reason='Critical coordinated fix');self.validate(m)
 def test_empty_emergency_reason(self):
  m=self.manifest();m.update(kind='emergency',reason='')
  with self.assertRaises(ValueError):self.validate(m)
 def test_unknown_key(self):
  m=self.manifest();m['shell']='bad'
  with self.assertRaises(ValueError):self.validate(m)
unittest.main()
