# SPDX-License-Identifier: GPL-3.0-only
"""Signed, whole-repository releases. No unattended package transaction."""
import hashlib
import calendar, datetime as dt, fcntl, json, os, re, shutil, subprocess, tempfile, urllib.request
from pathlib import Path
BASE = Path('/var/lib/lollipop-update')
CURRENT = Path('/etc/lollipop/release.json')
TRUST = Path('/etc/lollipop/release-keyring.gpg')
SNAPSHOTS = Path('/.snapshots/lollipop')
PACMAN_CONF = Path('/etc/pacman.conf')
LIVE_MARKER = Path('/run/archiso/bootmnt')

def run(*args, **kw):
    return subprocess.run(list(args), check=True, text=True, **kw)

def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.'+path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(data, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try: os.fsync(directory)
        finally: os.close(directory)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)

def previous_month(day):
    y, m = (day.year-1, 12) if day.month == 1 else (day.year, day.month-1)
    return dt.date(y, m, min(day.day, calendar.monthrange(y, m)[1]))

def validate(m, current, today=None):
    today = today or dt.date.today()
    required = {'schema', 'sequence', 'release', 'kind', 'date', 'snapshot', 'reason'}
    if not required <= set(m) or set(m)-required-{'native_repo'} or m['schema'] != 1:
        raise ValueError('Unsupported release manifest fields/schema')
    if type(m['sequence']) is not int or m['sequence'] <= current['sequence']:
        raise ValueError('Replay/older release rejected')
    if not re.fullmatch(r'[A-Za-z0-9._-]{1,80}', m['release']):
        raise ValueError('Invalid release name')
    date = dt.date.fromisoformat(m['date'])
    snapshot = dt.datetime.strptime(m['snapshot'], '%Y/%m/%d').date()
    if date > today or snapshot > date:
        raise ValueError('Future release/snapshot rejected')
    if snapshot < dt.datetime.strptime(current['snapshot'], '%Y/%m/%d').date():
        raise ValueError('Snapshot regression rejected')
    if m['kind'] == 'quarterly':
        if date.day != 15 or date.month not in (1, 4, 7, 10) or snapshot != previous_month(date):
            raise ValueError('Quarterly schedule must be day 15, snapshot one calendar month earlier')
    elif m['kind'] != 'emergency' or not isinstance(m['reason'], str) or not m['reason'].strip():
        raise ValueError('Emergency releases need an explicit reason')
    native = m.get('native_repo','')
    if native and not re.fullmatch(r'https://[A-Za-z0-9./:_~-]+',native):
        raise ValueError('Native repository must be a plain HTTPS URL without configuration syntax')
    return m

def verified(manifest, signature):
    if not TRUST.is_file():
        raise RuntimeError('No trusted release signing key installed')
    run('gpgv', '--keyring', str(TRUST), str(signature), str(manifest))
    return validate(json.loads(Path(manifest).read_text()), json.loads(CURRENT.read_text()))

def fetch():
    conf = json.loads(Path('/etc/lollipop/update-channel.json').read_text())
    url = conf.get('manifest_url', '')
    if not url:
        print('Lollipop: release channel is local/manual; no published server configured.')
        return
    if not url.startswith('https://'):
        raise ValueError('Only HTTPS release channels are accepted')
    BASE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=BASE) as name:
        folder = Path(name)
        for suffix in ('', '.sig'):
            with urllib.request.urlopen(url+suffix, timeout=45) as response:
                # Release manifests/signatures are intentionally small.
                data = response.read(131073)
                if len(data) > 131072:
                    raise ValueError('Release response too large')
                (folder/('release.json'+suffix)).write_bytes(data)
        release = verified(folder/'release.json', folder/'release.json.sig')
        for suffix in ('', '.sig'):
            shutil.copyfile(folder/('release.json'+suffix), BASE/('available.json'+suffix))
        print('Available Lollipop release:', release['release'])

def checkpoint(kind, release, pre=None):
    args = ['snapper','-c','root','create','--type',kind,'--print-number','--description','Lollipop '+release,
            '--userdata','lollipop=yes']
    if pre is not None:
        args += ['--pre-number', str(pre)]
    number = int(subprocess.check_output(args, text=True).strip())
    location = SNAPSHOTS/str(number)
    location.mkdir(parents=True, exist_ok=False)
    # Boot and ESP are outside the root snapshot: checkpoint them separately.
    run('tar','--one-file-system','-cpf',str(location/'boot.tar'),'-C','/boot','.')
    if Path('/sys/firmware/efi').exists():
        if not os.path.ismount('/boot/efi'):
            raise RuntimeError('EFI system partition is not mounted')
        run('tar','--one-file-system','-cpf',str(location/'efi.tar'),'-C','/boot/efi','.')
    def uuid(mount):
        return subprocess.check_output(['findmnt','-n','-o','UUID',mount],text=True).strip()
    metadata={'root_uuid':uuid('/'),'boot_uuid':uuid('/boot'),'efi_uuid':uuid('/boot/efi') if Path('/sys/firmware/efi').exists() else None,
              'sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in location.glob('*.tar')}}
    write_json(location/'checkpoint.json', metadata)
    run('sync','-f',str(location))
    return number

def refresh_grub():
    boot = json.loads(Path('/etc/lollipop/boot.json').read_text())
    if boot['firmware'] == 'efi':
        run('grub-install','--target=x86_64-efi','--efi-directory=/boot/efi','--bootloader-id=Lollipop','--recheck')
    else:
        disk = boot.get('disk','')
        if not re.fullmatch(r'/dev/[A-Za-z0-9_/-]+',disk):
            raise ValueError('No valid installed BIOS boot disk configured')
        run('grub-install','--target=i386-pc','--recheck',disk)
    run('grub-mkconfig','-o','/boot/grub/grub.cfg')

def apply(manifest, signature, allow_no_snapshot=False):
    if os.geteuid() != 0:
        raise PermissionError('Run apply with sudo')
    if LIVE_MARKER.exists():
        raise RuntimeError('Updates apply to the installed system, not the Live ISO')
    BASE.mkdir(parents=True, exist_ok=True)
    with (BASE/'transaction.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        release = verified(manifest, signature)
        if not os.path.ismount('/boot'):
            raise RuntimeError('Expected a separately mounted /boot; refusing unprotected boot update')
        if Path('/sys/firmware/efi').exists() and not os.path.ismount('/boot/efi'):
            raise RuntimeError('ESP must be mounted')
        if shutil.disk_usage('/').free < 5*1024**3 or shutil.disk_usage('/boot').free < 200*1024**2:
            raise RuntimeError('Insufficient free space for update/checkpoints')
        fs = subprocess.check_output(['findmnt','-n','-o','FSTYPE','/'],text=True).strip()
        if fs != 'btrfs' and not allow_no_snapshot:
            raise RuntimeError('ext4 has no Snapper recovery; explicitly pass --allow-no-snapshot')
        if fs == 'btrfs' and not os.path.ismount('/.snapshots'):
            raise RuntimeError('Missing separate @snapshots mount')
        journal = (SNAPSHOTS/'transactions.json') if fs=='btrfs' else BASE/'transactions.json'
        existing = json.loads(journal.read_text()) if journal.exists() else []
        if any(x.get('status') != 'complete' for x in existing):
            raise RuntimeError('An interrupted/failed update needs offline recovery before another update')
        # Use a single coherent official snapshot; pacman validates every package signature.
        server = 'https://archive.archlinux.org/repos/'+release['snapshot']+'/$repo/os/$arch'
        conf = '[options]\nArchitecture = auto\nSigLevel = Required DatabaseOptional\nLocalFileSigLevel = Required\n[core]\nServer = '+server+'\n[extra]\nServer = '+server+'\n'
        if release.get('native_repo'):
            conf += '\n[lollipop]\nSigLevel = Required\nServer = '+release['native_repo']+'\n'
        # pacman -w still changes sync databases, so snapshot happens before that too.
        pre = checkpoint('pre', release['release']) if fs == 'btrfs' else None
        record = {'release':release['release'],'pre':pre,'post':None,'status':'started'}
        journal = (SNAPSHOTS/'transactions.json') if pre else BASE/'transactions.json'
        history = json.loads(journal.read_text()) if journal.exists() else []
        history.append(record)
        write_json(journal, history)
        try:
            PACMAN_CONF.write_text(conf)
            run('pacman','--config','/etc/pacman.conf','-Syyuu','--noconfirm')
            run('lollipop-branding')
            run('mkinitcpio','-P')
            refresh_grub()
            write_json(CURRENT, release)
            record['post'] = checkpoint('post', release['release'], pre) if pre else None
            record['status'] = 'complete'
            # Keep exactly the last two complete *owned* update pairs; never delete an incomplete/failed pair.
            complete = [x for x in history if x['status']=='complete']
            for obsolete in complete[:-2]:
                for number in [obsolete['post'], obsolete['pre']]:
                    if number:
                        try:
                            run('snapper','-c','root','delete',str(number))
                            shutil.rmtree(SNAPSHOTS/str(number))
                        except (subprocess.CalledProcessError, OSError) as error:
                            print('Checkpoint cleanup needs attention:', error)
                            break
                else:
                    history.remove(obsolete)
        except Exception:
            # A failed pacman transaction cannot safely be undone live. Preserve evidence and pre checkpoint.
            record['status'] = 'failed-recovery-required'
            # Preserve the signed target snapshot config: reverting repo metadata after a partial transaction would mix package generations.
            raise
        finally:
            write_json(journal, history)
        print('Lollipop update complete. Reboot to use the new kernel.')
