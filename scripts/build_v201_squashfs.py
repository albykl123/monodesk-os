#!/usr/bin/env python3
"""
MONODESK OS 2.0.1-rc1 — SquashFS and Artifact Generator
Builds the upgraded rootfs inside the Debian Builder VM and extracts
filesystem.squashfs, cdboot.img, and PACKAGE-MANIFEST.txt.
"""
import os
import sys
import time
import shutil
import pathlib
import subprocess

QEMU = r"C:\Program Files\qemu\qemu-system-x86_64.exe"
SSH_KEY = r"C:\anti\builder_key"
BUILDER_QCOW2 = r"C:\anti\debian-builder.qcow2"
BASE_ROOTFS = r"D:\anti\v101_rootfs.ext4"
OVERLAY_TAR = r"D:\anti\v201_overlay.tar"
STAGING_V200 = r"D:\anti\iso_staging_v200"
STAGING_V201 = r"D:\anti\iso_staging_v201"
OUTPUT_DIR = r"D:\anti\monodesk-os\releases"

SSH_BASE = [
    "ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=NUL",
    "-o", "ConnectTimeout=5", "-i", SSH_KEY, "-p", "2222", "root@127.0.0.1"
]

SCP_BASE = [
    "scp", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=NUL",
    "-o", "ConnectTimeout=10", "-i", SSH_KEY, "-P", "2222"
]

def prepare_staging_directory():
    print(f"[*] Preparing staging directory at {STAGING_V201}...")
    staging_path = pathlib.Path(STAGING_V201)
    if not staging_path.exists():
        print(f"[*] Cloning {STAGING_V200} -> {STAGING_V201}...")
        shutil.copytree(STAGING_V200, STAGING_V201, dirs_exist_ok=True)
    
    # Remove any old squashfs in staging
    old_squashfs = staging_path / "live" / "filesystem.squashfs"
    if old_squashfs.exists():
        old_squashfs.unlink()
        print("[*] Removed prior squashfs from staging.")

    # Update .disk info
    disk_info = staging_path / ".disk" / "info"
    disk_info.parent.mkdir(parents=True, exist_ok=True)
    disk_info.write_text("MONODESK OS 2.0.1-rc1 (Universal PC Edition) - Release amd64\n", encoding="utf-8")
    
    disk_mini = staging_path / ".disk" / "mini-info"
    disk_mini.write_text("MONODESK OS 2.0.1-rc1\n", encoding="utf-8")

    # Update grub.cfg titles
    grub_cfg = staging_path / "boot" / "grub" / "grub.cfg"
    if grub_cfg.exists():
        content = grub_cfg.read_text(encoding="utf-8")
        content = content.replace("MONODESK OS 2.0", "MONODESK OS 2.0.1-rc1")
        grub_cfg.write_text(content, encoding="utf-8")

    efi_grub_cfg = staging_path / "EFI" / "BOOT" / "grub.cfg"
    if efi_grub_cfg.exists():
        content = efi_grub_cfg.read_text(encoding="utf-8")
        content = content.replace("MONODESK OS 2.0", "MONODESK OS 2.0.1-rc1")
        efi_grub_cfg.write_text(content, encoding="utf-8")

    print("[✓] Staging directory initialized with v2.0.1-rc1 metadata.")

def main():
    prepare_staging_directory()

    qemu_cmd = [
        QEMU, "-accel", "whpx", "-m", "4096", "-smp", "4",
        "-drive", f"file={BUILDER_QCOW2},format=qcow2,if=virtio,snapshot=on",
        "-drive", f"file={BASE_ROOTFS},format=raw,if=virtio,readonly=on",
        "-netdev", "user,id=net0,hostfwd=tcp:127.0.0.1:2222-:22",
        "-device", "virtio-net-pci,netdev=net0",
        "-display", "none"
    ]

    print("[*] Launching Debian Builder VM with 4GB RAM, 4 vCPUs...")
    proc = subprocess.Popen(qemu_cmd)

    try:
        # Wait for SSH
        print("[*] Waiting for VM SSH to become responsive...")
        ready = False
        for i in range(40):
            time.sleep(2)
            res = subprocess.run(SSH_BASE + ["echo VM_READY"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if "VM_READY" in res.stdout:
                ready = True
                print(f"[✓] Builder VM is online! ({i*2+2}s)")
                break

        if not ready:
            print("[-] Timeout waiting for Builder VM.")
            sys.exit(1)

        # Upload overlay tar
        print(f"[*] Uploading {OVERLAY_TAR} to builder VM...")
        upload_res = subprocess.run(SCP_BASE + [OVERLAY_TAR, "root@127.0.0.1:/tmp/v201_overlay.tar"], capture_output=True, text=True)
        if upload_res.returncode != 0:
            print(f"[-] Upload failed: {upload_res.stderr}")
            sys.exit(1)
        print("[✓] Overlay tar successfully uploaded.")

        build_script = r"""#!/usr/bin/env bash
set -euo pipefail

echo "=== STEP 1: Copy base Debian 13 rootfs to builder workspace ==="
mkdir -p /mnt/base /var/rootfs201
mount -o ro /dev/vdb /mnt/base
rsync -a --delete /mnt/base/ /var/rootfs201/
umount /mnt/base
df -h /var/rootfs201

echo "=== STEP 2: Configure chroot environment ==="
mount --bind /dev /var/rootfs201/dev
mount --bind /dev/pts /var/rootfs201/dev/pts
mount -t proc proc /var/rootfs201/proc
mount -t sysfs sysfs /var/rootfs201/sys
mount -t tmpfs tmpfs /var/rootfs201/run
echo "nameserver 8.8.8.8" > /var/rootfs201/etc/resolv.conf

cat <<'POLICY' > /var/rootfs201/usr/sbin/policy-rc.d
#!/bin/sh
exit 101
POLICY
chmod +x /var/rootfs201/usr/sbin/policy-rc.d

echo "=== STEP 3: Install all required applications, desktop packages & Wayland tools ==="
DEBIAN_FRONTEND=noninteractive chroot /var/rootfs201 apt-get update
DEBIAN_FRONTEND=noninteractive chroot /var/rootfs201 apt-get install -y --no-install-recommends \
    thunar thunar-archive-plugin thunar-volman \
    firefox-esr mousepad galculator ristretto file-roller \
    xfce4-screenshooter qpdfview \
    pipewire pipewire-pulse pipewire-alsa wireplumber pavucontrol \
    cups cups-client system-config-printer \
    bluez bluez-tools \
    brightnessctl xdg-user-dirs flatpak \
    apparmor apparmor-utils nftables ufw \
    feh xdotool wmctrl \
    seatd fuzzel swaybg swaylock swayidle mesa-va-drivers mesa-vulkan-drivers

echo "=== STEP 4: Inject MONODESK OS 2.0.1 overlay ==="
tar --no-same-owner -xf /tmp/v201_overlay.tar -C /var/rootfs201/

echo "=== STEP 5: Configure systemd services & permissions ==="
chroot /var/rootfs201 systemctl enable monodesk-profile.service || true
chroot /var/rootfs201 systemctl enable lightdm.service || true
chroot /var/rootfs201 systemctl enable NetworkManager.service || true
chroot /var/rootfs201 systemctl enable zramswap.service || true
chroot /var/rootfs201 systemctl enable cups.service || true
chroot /var/rootfs201 systemctl enable apparmor.service || true
chroot /var/rootfs201 systemctl enable ufw.service || true

chmod 755 /var/rootfs201/usr/bin/monodesk-* || true
chmod 755 /var/rootfs201/usr/bin/quickshell || true
chmod 755 /var/rootfs201/usr/bin/monodesk-session || true
chmod 644 /var/rootfs201/usr/share/xsessions/*.desktop || true
chmod 644 /var/rootfs201/usr/share/wayland-sessions/*.desktop || true
chmod 644 /var/rootfs201/usr/share/applications/*.desktop || true
chmod 644 /var/rootfs201/etc/lightdm/lightdm.conf.d/*.conf || true
chmod 644 /var/rootfs201/etc/NetworkManager/conf.d/*.conf || true
chmod 440 /var/rootfs201/etc/sudoers || true
chmod 750 /var/rootfs201/etc/sudoers.d || true

echo "=== STEP 6: Capture package manifest ==="
chroot /var/rootfs201 dpkg-query -W -f='${Package}\t${Version}\n' > /tmp/PACKAGE-MANIFEST.txt
echo "Total installed packages: $(wc -l < /tmp/PACKAGE-MANIFEST.txt)"

echo "=== STEP 7: Build GRUB Legacy BIOS El Torito boot image ==="
if grub-mkimage -O i386-pc -p /boot/grub -o /tmp/core.img \
    biosdisk iso9660 part_msdos part_gpt fat ext2 search search_fs_file normal configfile linux echo terminal gfxterm all_video; then
    cat /usr/lib/grub/i386-pc/cdboot.img /tmp/core.img > /tmp/cdboot_eltorito.img
    ls -lh /tmp/cdboot_eltorito.img
else
    echo "grub-mkimage skipped or failed, using existing cdboot.img"
    touch /tmp/cdboot_eltorito.img
fi

echo "=== STEP 8: Clean up chroot & compress filesystem.squashfs ==="
rm -f /var/rootfs201/usr/sbin/policy-rc.d
chroot /var/rootfs201 apt-get clean
rm -rf /var/rootfs201/var/lib/apt/lists/* /var/rootfs201/tmp/* /var/rootfs201/var/tmp/* /var/rootfs201/run/*
umount /var/rootfs201/run 2>/dev/null || true
umount /var/rootfs201/sys 2>/dev/null || true
umount /var/rootfs201/proc 2>/dev/null || true
umount /var/rootfs201/dev/pts 2>/dev/null || true
umount /var/rootfs201/dev 2>/dev/null || true

mksquashfs /var/rootfs201 /tmp/filesystem.squashfs -comp zstd -Xcompression-level 9 -b 262144 -noappend -no-progress -e lost+found
ls -lh /tmp/filesystem.squashfs
sha256sum /tmp/filesystem.squashfs
echo "BUILD_PIPELINE_COMPLETE"
"""

        print("[*] Creating remote build script in VM...")
        script_upload = subprocess.run(SSH_BASE + ["cat > /tmp/run_build.sh << 'EOF'\n" + build_script + "\nEOF\nchmod +x /tmp/run_build.sh"], capture_output=True, text=True)
        if script_upload.returncode != 0:
            print(f"[-] Failed to write build script: {script_upload.stderr}")
            sys.exit(1)

        print("[*] Executing build pipeline inside Debian Builder VM (this may take 3-6 minutes)...")
        exec_proc = subprocess.Popen(SSH_BASE + ["/tmp/run_build.sh"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in iter(exec_proc.stdout.readline, ""):
            print(line, end="", flush=True)
        exec_proc.wait()

        if exec_proc.returncode != 0:
            print(f"[-] Build pipeline failed with code {exec_proc.returncode}")
            sys.exit(1)

        # Download artifacts
        print(f"[*] Downloading filesystem.squashfs to {STAGING_V201}\\live\\filesystem.squashfs...")
        dest_squashfs = pathlib.Path(STAGING_V201) / "live" / "filesystem.squashfs"
        dest_squashfs.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(SCP_BASE + ["root@127.0.0.1:/tmp/filesystem.squashfs", str(dest_squashfs)], check=True)

        dest_cdboot = pathlib.Path(STAGING_V201) / "boot" / "grub" / "cdboot.img"
        res = subprocess.run(SSH_BASE + ["[ -s /tmp/cdboot_eltorito.img ]"])
        if res.returncode == 0:
            print(f"[*] Downloading cdboot_eltorito.img to {dest_cdboot}...")
            subprocess.run(SCP_BASE + ["root@127.0.0.1:/tmp/cdboot_eltorito.img", str(dest_cdboot)], check=True)
        else:
            print(f"[*] Preserving verified cdboot.img in {dest_cdboot}...")

        print(f"[*] Downloading PACKAGE-MANIFEST.txt to {OUTPUT_DIR}\\PACKAGE-MANIFEST-2.0.1-rc1.txt...")
        dest_manifest = pathlib.Path(OUTPUT_DIR) / "PACKAGE-MANIFEST-2.0.1-rc1.txt"
        dest_manifest.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(SCP_BASE + ["root@127.0.0.1:/tmp/PACKAGE-MANIFEST.txt", str(dest_manifest)], check=True)

        # Also copy manifest into staging /live/filesystem.packages
        dest_pkg = pathlib.Path(STAGING_V201) / "live" / "filesystem.packages"
        shutil.copy2(dest_manifest, dest_pkg)

        # Shut down builder VM
        print("[*] Shutting down builder VM...")
        # Restore real poweroff if needed
        subprocess.run(SSH_BASE + ["/usr/sbin/poweroff.real -f || /sbin/poweroff -f || poweroff -f"])
        proc.wait(timeout=30)
        print("[✓] Build and artifact extraction completed successfully!")

    except Exception as e:
        print(f"[-] An exception occurred during the build: {e}")
        try:
            proc.kill()
        except Exception:
            pass
        sys.exit(1)
    finally:
        try:
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=5)
        except Exception:
            pass

if __name__ == "__main__":
    main()
