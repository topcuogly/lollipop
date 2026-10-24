#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Build and sign a release announcement; never uploads/publishes automatically."""
from pathlib import Path
import argparse,datetime as dt,json,os,subprocess,sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'profile/airootfs/usr/lib/lollipop'))
import updates
p=argparse.ArgumentParser()
p.add_argument('--date',required=True,help='YYYY-MM-DD; quarterly dates are Jan/Apr/Jul/Oct 15')
p.add_argument('--sequence',type=int,required=True)
p.add_argument('--release',required=True)
p.add_argument('--kind',choices=['quarterly','emergency'],default='quarterly')
p.add_argument('--snapshot',help='Emergency full snapshot YYYY/MM/DD')
p.add_argument('--reason',default='Scheduled quarterly full update')
p.add_argument('--native-repo',default='',help='Published signed lollipop.db and packages, HTTPS URL')
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();day=dt.date.fromisoformat(a.date)
snap=a.snapshot or updates.previous_month(day).strftime('%Y/%m/%d')
m={'schema':1,'sequence':a.sequence,'release':a.release,'kind':a.kind,'date':a.date,'snapshot':snap,'reason':a.reason}
if a.native_repo:m['native_repo']=a.native_repo
# A future announcement may be prepared, but installed clients reject applying it before its release day.
updates.validate(m,{'sequence':0,'snapshot':'2026/10/22'},today=max(day,dt.date.today()))
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_text(json.dumps(m,indent=2)+'\n')
fpr=(root/'state/signing-fingerprint').read_text().strip()
env=dict(os.environ,GNUPGHOME=str(root/'state/signing'))
subprocess.run(['gpg','--batch','--yes','--pinentry-mode','loopback','--passphrase','','--local-user',fpr,'--detach-sign','--output',str(a.output)+'.sig',str(a.output)],check=True,env=env)
print('Signed locally:',a.output,'; publish only after independent VM validation.')
