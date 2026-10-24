#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Stage profile text and existing artwork without changing the source tree."""
from pathlib import Path
import argparse
import json
import shutil
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

def prepare(output):
    output = Path(output).resolve()
    if output.exists():
        raise SystemExit(f'Refusing to overwrite existing output: {output}')
    # Validate sources before creating the staging directory.
    manifest = json.loads((ROOT / 'packaging/lollipop-system/desktop-assets.json').read_text())
    def asset(name):
        path = (ROOT / name).resolve()
        if not path.is_relative_to((ROOT / 'assets').resolve()) or not path.is_file():
            raise ValueError(f'Invalid asset: {name}')
        return path
    def target(name):
        path = output / name
        if not path.resolve().is_relative_to(output):
            raise ValueError(f'Invalid destination: {name}')
        return path
    for dest, source in manifest['files'].items():
        asset(source); target(dest)
    for wallpaper in manifest['wallpapers']:
        asset(wallpaper['source'])
        ident = wallpaper['id']
        if not ident or Path(ident).name != ident or ident in ('.', '..'):
            raise ValueError(f'Invalid wallpaper ID: {ident}')
    shutil.copytree(ROOT / 'profile/airootfs', output, symlinks=True)
    for dest, source in manifest['files'].items():
        path = target(dest); path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(asset(source), path)
    # Calamares branding uses the same main logo; no second artwork copy is tracked.
    branding = output / 'usr/share/calamares/branding/lollipop'
    if branding.is_dir():
        shutil.copyfile(asset('assets/logos/lollipop-icon.png'), branding / 'logo.png')
    for wallpaper in manifest['wallpapers']:
        directory = output / 'usr/share/wallpapers' / wallpaper['id']
        images = directory / 'contents/images'; images.mkdir(parents=True, exist_ok=True)
        with Image.open(asset(wallpaper['source'])) as image:
            shutil.copyfile(asset(wallpaper['source']), images / f'{image.width}x{image.height}.png')
            preview = image.convert('RGB')
            preview.thumbnail((400, 225), Image.Resampling.LANCZOS)
            preview.save(directory / 'contents/screenshot.png')
        metadata = {'KPlugin': {'Id': wallpaper['id'], 'Name': wallpaper['name'],
                    'License': 'LicenseRef-UserProvided', 'Authors': [{'Name': 'Lollipop artwork'}]},
                    'KPackageStructure': 'Wallpaper/Images'}
        (directory / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New staging directory; must not exist')
    args = parser.parse_args()
    print(prepare(args.output))
