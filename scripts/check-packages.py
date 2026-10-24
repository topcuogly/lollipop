#!/usr/bin/env python3
"""Verify snapshot DB bytes and compare direct package locks; no packages are installed."""
from pathlib import Path
import argparse, hashlib, io, json, tarfile, urllib.request
root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--db-dir', type=Path, help='Use already downloaded core.db and extra.db')
args = parser.parse_args()
expected = {
 'core': '6d358cdc978130c021b12fe690f6f2a5ec28c0b06732eaa2e010b912aca534f9',
 'extra': 'efd7c70287a0c7c9a71c0820438b9d35304960842c667979fcedd3bbafd0a720',
}
index = {}
for repo, digest in expected.items():
 if args.db_dir:
  raw = (args.db_dir / (repo + '.db')).read_bytes()
 else:
  url = f'https://archive.archlinux.org/repos/2026/10/22/{repo}/os/x86_64/{repo}.db'
  with urllib.request.urlopen(url, timeout=120) as response:
   raw = response.read()
 if hashlib.sha256(raw).hexdigest() != digest:
  raise SystemExit(f'Snapshot DB checksum mismatch: {repo}')
 with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
  for member in archive:
   if not member.name.endswith('/desc'):
    continue
   lines = archive.extractfile(member).read().decode().splitlines()
   data = {line.strip('%'): lines[i+1] for i, line in enumerate(lines[:-1])
           if line.startswith('%') and lines[i+1]}
   index[data['NAME']] = {'version': data['VERSION'], 'filename': data['FILENAME'],
                          'sha256': data['SHA256SUM'], 'repo': repo}
packages = [n for n in (root / 'profile/packages.x86_64').read_text().split() if n not in {'calamares','lollipop-system','photocraft-bin','upscayl-bin','lollipop-decoration'}]
actual = {package: index[package] for package in packages}
locked = json.loads((root / 'package-direct.lock.json').read_text())
if actual != locked:
 raise SystemExit('Direct package lock mismatch')
print(f'PASS: {len(packages)} direct package versions/files/SHA256 values match pinned snapshot databases')
