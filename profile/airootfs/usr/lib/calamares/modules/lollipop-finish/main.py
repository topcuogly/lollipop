import libcalamares
from libcalamares.utils import target_env_call

def run():
    import json
    from pathlib import Path
    root = Path(libcalamares.globalstorage.value("rootMountPoint"))
    boot = libcalamares.globalstorage.value("bootLoader") or {}
    (root / "etc/lollipop/boot.json").write_text(json.dumps({
        "firmware": libcalamares.globalstorage.value("firmwareType"),
        "disk": boot.get("installPath", "")
    }) + "\n")
    code = target_env_call(["/usr/local/sbin/lollipop-target", "finish"])
    if code != 0:
        return ("Lollipop target setup failed", "Stage finish, exit code " + str(code))
    return None
