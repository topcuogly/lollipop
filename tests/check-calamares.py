from pathlib import Path
import tarfile,yaml,jsonschema
p=Path(__file__).resolve().parents[1]
config=p/'profile/airootfs/etc/calamares'
errors=[]
with tarfile.open(p/'state/calamares/calamares-3.4.2.tar') as t:
 for file in (config/'modules').glob('*.conf'):
  name=file.stem;schema=f'calamares-3.4.2/src/modules/{name}/{name}.schema.yaml'
  try:source=t.extractfile(schema)
  except KeyError:continue
  data=yaml.safe_load(file.read_text());rules=yaml.safe_load(source.read())
  errors.extend(str(file.name)+': '+e.message for e in jsonschema.Draft7Validator(rules).iter_errors(data))
assert not errors, '\n'.join(errors)
s=yaml.safe_load((config/'settings.conf').read_text())
execs=next(x['exec'] for x in s['sequence'] if 'exec' in x)
assert execs.index('lollipop-clean')<execs.index('users')<execs.index('initcpiocfg')<execs.index('initcpio')<execs.index('bootloader')
part=yaml.safe_load((config/'modules/partition.conf').read_text())
assert part['luksGeneration']=='luks2' and part['defaultFileSystemType']=='btrfs'
assert part['partitionLayout'][0]['noEncrypt'] and part['partitionLayout'][0]['mountPoint']=='/boot'
mount=yaml.safe_load((config/'modules/mount.conf').read_text())
assert not any('compress' in opt for entry in mount['mountOptions'] for opt in entry.get('options',[]))
print('PASS: pinned Calamares module schemas, job ordering, Btrfs/LUKS2/boot layout and no filesystem compression')
