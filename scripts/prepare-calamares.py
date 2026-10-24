#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Prepare a verified pinned git archive and Calamares package recipe."""
from pathlib import Path
import hashlib,json,shutil,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
lock=json.loads((root/'external-packages.lock.json').read_text())['calamares']
output=root/'state/calamares';output.mkdir(parents=True,exist_ok=True)
archive=output/f"calamares-{lock['version']}.tar"
if not archive.exists() or hashlib.sha256(archive.read_bytes()).hexdigest()!=lock['sha256']:
    with tempfile.TemporaryDirectory(prefix='calamares-source-',dir=root/'state') as name:
        git=Path(name)/'source'
        subprocess.run(['git','init','--quiet',str(git)],check=True)
        subprocess.run(['git','-C',str(git),'fetch','--depth=1',lock['source'],lock['commit']],check=True)
        actual=subprocess.check_output(['git','-C',str(git),'rev-parse','FETCH_HEAD'],text=True).strip()
        if actual!=lock['commit']:raise SystemExit('Unexpected Calamares commit')
        temporary=Path(name)/'source.tar'
        subprocess.run(['git','-C',str(git),'archive','--format=tar',f"--prefix=calamares-{lock['version']}/",'--output',str(temporary),actual],check=True)
        if hashlib.sha256(temporary.read_bytes()).hexdigest()!=lock['sha256']:
            raise SystemExit('Calamares source archive checksum mismatch')
        temporary.replace(archive)
for name in ['PKGBUILD','clear-failure-message.patch']:
    shutil.copyfile(root/'packaging/calamares'/name,output/name)
print('PASS: Calamares source SHA256; build inputs:',output)
