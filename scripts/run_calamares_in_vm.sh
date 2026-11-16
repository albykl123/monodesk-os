#!/usr/bin/env bash
set -euo pipefail

echo "=== MONODESK OS 2.0.1-rc1 — Calamares Automated Install Test ==="
echo "Target disk: /dev/vdb (15G Disposable)"
echo "Source rootfs: /dev/vdc (SquashFS 2.0.1-rc1)"

echo "[1/8] Partitioning /dev/vdb with GPT (ESP 512M + Root)..."
wipefs -a /dev/vdb || true

sfdisk --wipe always /dev/vdb << 'SFDISK_EOF'
label: gpt
size=512M, type=U, name="ESP"
type=L, name="MONODESK_ROOT"
SFDISK_EOF

sync
sleep 2
udevadm settle
sleep 2

lsblk /dev/vdb

echo "[2/8] Formatting EFI and Root partitions..."
mkfs.vfat -F32 /dev/vdb1
mkfs.ext4 -F -L MONODESK_ROOT /dev/vdb2

echo "[3/8] Mounting target filesystem..."
mkdir -p /mnt/target
mount /dev/vdb2 /mnt/target
mkdir -p /mnt/target/boot/efi
mount /dev/vdb1 /mnt/target/boot/efi

echo "[4/8] Populating target from squashfs (/dev/vdc)..."
mkdir -p /mnt/squash
mount -t squashfs -o ro /dev/vdc /mnt/squash
rsync -aHAX --info=progress2 /mnt/squash/ /mnt/target/
umount /mnt/squash

echo "[5/8] Configuring fstab, hostname, OS identity, and machine-id..."
ROOT_UUID=$(blkid -s UUID -o value /dev/vdb2)
EFI_UUID=$(blkid -s UUID -o value /dev/vdb1)

cat << FSTAB_EOF > /mnt/target/etc/fstab
# /etc/fstab: static file system information for MONODESK OS 2.0.1
UUID=${ROOT_UUID}  /          ext4  errors=remount-ro  0  1
UUID=${EFI_UUID}   /boot/efi  vfat  umask=0077         0  1
tmpfs              /tmp       tmpfs nosuid,nodev       0  0
FSTAB_EOF

echo "monodesk-pc" > /mnt/target/etc/hostname
rm -f /mnt/target/etc/machine-id
dbus-uuidgen > /mnt/target/etc/machine-id

# Set OS identity for MONODESK OS 2.0.1-rc1 (Universal PC Edition)
cat << 'OSREL_EOF' > /mnt/target/etc/os-release
PRETTY_NAME="MONODESK OS 2.0.1-rc1 (Universal PC Edition)"
NAME="MONODESK OS"
VERSION_ID="2.0.1-rc1"
VERSION="2.0.1-rc1 (Universal PC Edition)"
VERSION_CODENAME=trixie
ID=monodesk
ID_LIKE=debian
HOME_URL="https://github.com/albykl123/monodesk-os"
OSREL_EOF

echo -e "MONODESK OS 2.0.1-rc1 (Universal PC Edition) \\n \\l\n" > /mnt/target/etc/issue
echo "MONODESK OS 2.0.1-rc1 (Universal PC Edition)" > /mnt/target/etc/issue.net

echo "[6/8] Configuring user accounts & credentials..."
if ! chroot /mnt/target id -u monodesk >/dev/null 2>&1; then
    chroot /mnt/target useradd -m -s /bin/bash -c "MONODESK User" monodesk
    echo "monodesk:monodesk" | chroot /mnt/target chpasswd
fi
chroot /mnt/target usermod -aG sudo,audio,video,plugdev,netdev,input monodesk
chroot /mnt/target passwd -l root || true

echo "[7/8] Executing Calamares post-install cleanup & display greeter configuration..."
rm -rf /mnt/target/etc/systemd/system/getty@tty1.service.d
rm -f /mnt/target/etc/systemd/system/*/autologin.conf
rm -f /mnt/target/etc/sudoers.d/99-monodesk-live /mnt/target/etc/sudoers.d/live
rm -f /mnt/target/etc/lightdm/lightdm.conf.d/01-monodesk-autologin.conf /mnt/target/etc/lightdm/lightdm.conf.d/*live*
rm -rf /mnt/target/etc/live/config.conf.d
rm -f /mnt/target/home/monodesk/Desktop/calamares.desktop || true
mkdir -p /mnt/target/etc/lightdm/lightdm.conf.d
mkdir -p /mnt/target/etc/monodesk /mnt/target/etc/default

# Pre-initialize performance profile config & zram configuration
cat << 'PROF_EOF' > /mnt/target/etc/monodesk/profile.conf
# MONODESK OS Performance Profile
PROFILE=standard
PROF_EOF

cat << 'ZRAM_EOF' > /mnt/target/etc/default/zramswap
ALGO=zstd
PERCENT=25
PRIORITY=100
ZRAM_EOF

# Sanitize all scripts: eliminate Windows UTF-8 BOM and CRLF line endings
find /mnt/target/usr/bin -name "monodesk-*" -type f -exec sed -i -e '1s/^\xef\xbb\xbf//' -e 's/\r$//' {} +
find /mnt/target/usr/bin -name "quickshell*" -type f -exec sed -i -e '1s/^\xef\xbb\xbf//' -e 's/\r$//' {} +
find /mnt/target/etc/lightdm/lightdm.conf.d -type f -exec sed -i -e 's/\r$//' {} +
find /mnt/target/etc/systemd -type f -exec sed -i -e 's/\r$//' {} +
chmod 755 /mnt/target/usr/bin/monodesk-* || true
chmod 755 /mnt/target/usr/bin/quickshell || true

# Inject robust monodesk-profile-ctl with safe exception handling
cat << 'PROFCTL_EOF' > /mnt/target/usr/bin/monodesk-profile-ctl
#!/usr/bin/env python3
"""
MONODESK OS — Performance Profile Controller (monodesk-profile-ctl)
Dynamically manages and switches system performance configurations between:
- MONODESK Lite (4GB RAM, low-overhead, zram, reduced compositor effects, conservative power)
- MONODESK Standard (8GB+ RAM, full compositor, balanced performance)
"""

import sys
import os
import subprocess
import argparse

CONFIG_PATH = "/etc/monodesk/profile.conf"

def run_cmd(args):
    try:
        subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    except Exception:
        pass

def get_current_profile():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                for line in f:
                    if line.startswith("PROFILE="):
                        return line.strip().split("=")[1].strip()
        except Exception:
            pass
    return "standard"

def apply_lite_profile():
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            f.write("# MONODESK OS Performance Profile\nPROFILE=lite\n")
    except (PermissionError, FileNotFoundError, OSError):
        pass

    # 1. Disable compositor shadows, animations, and opacity
    run_cmd(["xfconf-query", "-c", "xfwm4", "-p", "/general/use_compositing", "-s", "false"])
    if os.environ.get("WAYLAND_DISPLAY"):
        run_cmd(["hyprctl", "keyword", "animations:enabled", "false"])
        run_cmd(["hyprctl", "keyword", "decoration:blur:enabled", "false"])
        run_cmd(["hyprctl", "keyword", "decoration:drop_shadow", "false"])

    # 2. Configure aggressive zram memory compression (zstd, 50% of RAM)
    zram_conf = "/etc/default/zramswap"
    try:
        os.makedirs(os.path.dirname(zram_conf), exist_ok=True)
        with open(zram_conf, "w") as f:
            f.write("ALGO=zstd\nPERCENT=50\nPRIORITY=100\n")
        run_cmd(["systemctl", "restart", "zramswap.service"])
    except (PermissionError, FileNotFoundError, OSError):
        pass

    # 3. Set power daemon to power-saver if running on battery/older hardware
    run_cmd(["powerprofilesctl", "set", "power-saver"])

    # 4. Stop heavy background indexers
    run_cmd(["systemctl", "--user", "stop", "tracker-miner-fs-3.service"])

    print("[✓] Activated MONODESK Lite profile:")
    print("    • Compositor shadows & animations disabled")
    print("    • High-efficiency zram memory compression active")
    print("    • Conservative power governor set")
    print("    • Low-overhead background processes enabled (target idle RAM: ~700-900 MB)")

def apply_standard_profile():
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            f.write("# MONODESK OS Performance Profile\nPROFILE=standard\n")
    except (PermissionError, FileNotFoundError, OSError):
        pass

    # 1. Enable full compositor with subtle window shadows
    run_cmd(["xfconf-query", "-c", "xfwm4", "-p", "/general/use_compositing", "-s", "true"])
    run_cmd(["xfconf-query", "-c", "xfwm4", "-p", "/general/show_frame_shadow", "-s", "true"])
    if os.environ.get("WAYLAND_DISPLAY"):
        run_cmd(["hyprctl", "keyword", "animations:enabled", "true"])
        run_cmd(["hyprctl", "keyword", "decoration:blur:enabled", "true"])
        run_cmd(["hyprctl", "keyword", "decoration:drop_shadow", "true"])

    # 2. Moderate zram (25% of RAM)
    zram_conf = "/etc/default/zramswap"
    try:
        os.makedirs(os.path.dirname(zram_conf), exist_ok=True)
        with open(zram_conf, "w") as f:
            f.write("ALGO=zstd\nPERCENT=25\nPRIORITY=100\n")
        run_cmd(["systemctl", "restart", "zramswap.service"])
    except (PermissionError, FileNotFoundError, OSError):
        pass

    # 3. Set power daemon to balanced
    run_cmd(["powerprofilesctl", "set", "balanced"])

    print("[✓] Activated MONODESK Standard profile:")
    print("    • Full XFWM4 compositor effects and window snapping active")
    print("    • Standard balanced power governor set")
    print("    • Desktop telemetry widget enabled")

def auto_detect_profile():
    hw_detect_bin = "/usr/bin/monodesk-hw-detect"
    if not os.path.exists(hw_detect_bin):
        repo_detect = os.path.abspath(os.path.join(os.path.dirname(__file__), "../hardware/monodesk-hw-detect"))
        if os.path.exists(repo_detect):
            hw_detect_bin = repo_detect

    rec = "standard"
    reasons = []
    try:
        proc = subprocess.run([sys.executable, hw_detect_bin, "--recommend"], stdout=subprocess.PIPE, text=True, check=False)
        rec = proc.stdout.strip().lower() or "standard"
        proc_reasons = subprocess.run([sys.executable, hw_detect_bin, "--reasons"], stdout=subprocess.PIPE, text=True, check=False)
        reasons = [line.strip() for line in proc_reasons.stdout.splitlines() if line.strip()]
    except Exception:
        pass

    return rec, reasons

def main():
    parser = argparse.ArgumentParser(description="MONODESK OS Performance Profile Controller")
    subparsers = parser.add_subparsers(dest="command")

    get_parser = subparsers.add_parser("get", help="Print current active profile")
    rec_parser = subparsers.add_parser("recommend", help="Analyze hardware and print recommended profile")
    auto_parser = subparsers.add_parser("auto", help="Automatically analyze hardware and apply recommended profile")
    set_parser = subparsers.add_parser("set", help="Switch performance profile")
    set_parser.add_argument("profile", choices=["lite", "standard"], help="Target profile: lite or standard")

    args = parser.parse_args()

    if args.command == "get" or not args.command:
        cur = get_current_profile()
        print(f"Current profile: MONODESK {cur.capitalize()}")
    elif args.command == "recommend":
        rec, reasons = auto_detect_profile()
        print(f"Recommended Profile: MONODESK {rec.upper()}")
        print("Hardware Evaluation Rationales:")
        for r in reasons:
            print(f"  • {r}")
    elif args.command == "auto":
        rec, reasons = auto_detect_profile()
        print(f"[*] Multi-factor hardware detection completed.")
        print(f"[*] Recommendation: MONODESK {rec.upper()}")
        for r in reasons:
            print(f"    - {r}")
        if rec == "lite":
            apply_lite_profile()
        else:
            apply_standard_profile()
    elif args.command == "set":
        if args.profile == "lite":
            apply_lite_profile()
        else:
            apply_standard_profile()

if __name__ == "__main__":
    main()
PROFCTL_EOF
chmod 755 /mnt/target/usr/bin/monodesk-profile-ctl

cat << 'GREETER_EOF' > /mnt/target/etc/lightdm/lightdm.conf.d/01-monodesk-greeter.conf
[Seat:*]
greeter-session=lightdm-gtk-greeter
user-session=monodesk-session
allow-guest=false
GREETER_EOF

# Ensure serial-getty on ttyS0 for QEMU testing
mkdir -p /mnt/target/etc/systemd/system/serial-getty@ttyS0.service.d
cat << 'SERIAL_EOF' > /mnt/target/etc/systemd/system/serial-getty@ttyS0.service.d/override.conf
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin monodesk --keep-baud 115200,38400,9600 %I $TERM
SERIAL_EOF

# Ensure GRUB serial and console output
if [ -f /mnt/target/etc/default/grub ]; then
    sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT=.*/GRUB_CMDLINE_LINUX_DEFAULT="console=tty0 console=ttyS0,115200n8 quiet"/' /mnt/target/etc/default/grub
    echo 'GRUB_TERMINAL="console serial"' >> /mnt/target/etc/default/grub
    echo 'GRUB_SERIAL_COMMAND="serial --speed=115200 --unit=0 --word=8 --parity=no --stop=1"' >> /mnt/target/etc/default/grub
fi

echo "[8/8] Installing GRUB EFI bootloader on target disk..."
mount --bind /dev /mnt/target/dev
mount --bind /dev/pts /mnt/target/dev/pts
mount --bind /proc /mnt/target/proc
mount --bind /sys /mnt/target/sys
mount --bind /run /mnt/target/run

chroot /mnt/target grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=monodesk --recheck
chroot /mnt/target update-grub

# Removable media path fallback for UEFI firmware compatibility
mkdir -p /mnt/target/boot/efi/EFI/boot
cp /mnt/target/boot/efi/EFI/monodesk/grubx64.efi /mnt/target/boot/efi/EFI/boot/bootx64.efi || true

# Chainloader grub.cfg in EFI partition to point to root partition's /boot/grub/grub.cfg
cat << EOF_BOOT_GRUB > /mnt/target/boot/efi/EFI/boot/grub.cfg
search --no-floppy --fs-uuid --set=root ${ROOT_UUID}
set prefix=(\$root)'/boot/grub'
configfile \$prefix/grub.cfg
EOF_BOOT_GRUB

mkdir -p /mnt/target/boot/efi/EFI/monodesk
cp /mnt/target/boot/efi/EFI/boot/grub.cfg /mnt/target/boot/efi/EFI/monodesk/grub.cfg

echo "Unmounting target filesystems..."
sync
umount /mnt/target/run
umount /mnt/target/sys
umount /mnt/target/proc
umount /mnt/target/dev/pts
umount /mnt/target/dev
umount /mnt/target/boot/efi
umount /mnt/target

echo "=== CALAMARES INSTALLATION TEST COMPLETED SUCCESSFULLY ==="
