import libcalamares
import os, subprocess

def run():
    target = libcalamares.globalstorage.value("rootMountPoint")
    try:
        subprocess.run(["chroot", target, "mkinitcpio", "-p", "linux-lts"], check=True)
        image = target + "/boot/initramfs-linux-lts.img"
        if not os.path.isfile(image) or os.path.getsize(image) < 1000000:
            raise RuntimeError("LTS initramfs missing or implausibly small")
        listing = subprocess.run(["chroot", target, "lsinitcpio", "/boot/initramfs-linux-lts.img"], check=True, capture_output=True, text=True).stdout
        if not any(line.strip().removeprefix("./") == "init" for line in listing.splitlines()):
            raise RuntimeError("LTS initramfs does not contain /init")
        subprocess.run(["chroot", target, "grub-mkconfig", "-o", "/boot/grub/grub.cfg"], check=True)
        with open(target + "/boot/grub/grub.cfg") as stream:
            config = stream.read()
        if not any(line.strip().startswith("initrd") and "initramfs-linux-lts.img" in line for line in config.splitlines()):
            raise RuntimeError("GRUB configuration has no LTS initrd entry")
    except Exception as error:
        return ("Lollipop boot verification failed", str(error))
    return None
