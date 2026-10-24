#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
from pathlib import Path
import hashlib,json,urllib.request,subprocess,os
root=Path(__file__).resolve().parents[1]
lock=json.loads((root/'external-packages.lock.json').read_text())['tor-browser']
output=root/'state/tor-browser.tar.xz';output.parent.mkdir(exist_ok=True)
if not output.exists() or hashlib.sha256(output.read_bytes()).hexdigest()!=lock['sha256']:
    temporary=output.with_suffix('.partial')
    with urllib.request.urlopen(lock['url'], timeout=180) as response, temporary.open('wb') as stream:
        while block:=response.read(1024*1024): stream.write(block)
    if hashlib.sha256(temporary.read_bytes()).hexdigest()!=lock['sha256']:
        raise SystemExit('Tor Browser archive checksum mismatch')
    temporary.replace(output)
result=subprocess.run(['gpgv','--status-fd','1','--keyring',str(root/'vendor/tor-browser-developers.gpg'),str(root/'vendor/tor-browser.tar.xz.asc'),str(output)],check=True,text=True,stdout=subprocess.PIPE)
valid=[line.split() for line in result.stdout.splitlines() if line.startswith('[GNUPG:] VALIDSIG ')]
if not any(lock['signing_fingerprint'] in (fields[2],fields[-1]) for fields in valid):
    raise SystemExit('Tor Browser signature does not match the pinned signing fingerprint')
print('PASS: pinned Tor Browser archive checksum and Tor Project signature')
