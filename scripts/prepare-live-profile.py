#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Stage an Archiso profile without duplicating package-owned files."""
from pathlib import Path
import argparse,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1]

def prepare(output,package_files,release_key):
    output=Path(output).resolve()
    if output.exists():raise ValueError('Output must be a new directory')
    names=json.loads(Path(package_files).read_text())
    if not isinstance(names,list) or not all(isinstance(n,str) for n in names):raise ValueError('Invalid payload file manifest')
    for name in names:
        p=Path(name)
        if p.is_absolute() or '..' in p.parts:raise ValueError('Unsafe payload path: '+name)
    key=Path(release_key).resolve()
    if not key.is_file():raise ValueError('A builder-generated public release keyring is required')
    output.mkdir(parents=True)
    for p in (ROOT/'profile').iterdir():
        if p.name in ('airootfs','packages.x86_64'):continue
        if p.is_dir():shutil.copytree(p,output/p.name,symlinks=True)
        else:shutil.copyfile(p,output/p.name)
    shutil.copyfile(ROOT/'packages/native.txt',output/'packages.x86_64')
    subprocess.run(['python3',str(ROOT/'scripts/prepare-desktop.py'),'--output',str(output/'airootfs')],check=True)
    fs=output/'airootfs'
    for name in names:
        p=fs/name
        if p.is_file() or p.is_symlink():p.unlink()
    dest=fs/'etc/lollipop/release-keyring.gpg';dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(key,dest)
    # mkarchiso's path-specific rules apply live credentials and executable permissions.
    # The signed local repo and isolated cache are attached later by ISO orchestration.
    return output

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--package-files',required=True,type=Path)
    p.add_argument('--release-key',required=True,type=Path,help='Public keyring, never a private key')
    a=p.parse_args();print(prepare(a.output,a.package_files,a.release_key))
