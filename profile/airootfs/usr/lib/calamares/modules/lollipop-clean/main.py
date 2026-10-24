import libcalamares
from libcalamares.utils import target_env_call

def run():
    from pathlib import Path
    root = Path(libcalamares.globalstorage.value("rootMountPoint"))
    (root / "run/lollipop-installer-target").write_text("Calamares Lollipop target\n")
    code = target_env_call(["/usr/local/sbin/lollipop-target", "clean"])
    if code != 0:
        return ("Lollipop target setup failed", "Stage clean, exit code " + str(code))
    return None
