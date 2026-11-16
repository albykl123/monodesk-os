#!/bin/bash
set -e

echo "=== MONODESK OS 2.0 — Calamares Automated Install Test ==="
echo "Target disk: /dev/vdb (15G)"
echo "Source rootfs: /root/monodesk-os/build/live-build/binary/live/filesystem.squashfs"

# 1. Partition /dev/vdb with sfdisk
echo "[1/8] Partitioning /dev/vdb with GPT (ESP 512M + Root)..."
sfdisk --wipe always /dev/vdb << 'EOF'
label: gpt
size=512M, type=U, name="ESP"
type=L, name="MONODESK_ROOT"
EOF

sync
sleep 2

# 2. Format
echo "[2/8] Formatting EFI and Root partitions..."
mkfs.vfat -F32 /dev/vdb1
mkfs.ext4 -F -L MONODESK_ROOT /dev/vdb2

# 3. Mount target
echo "[3/8] Mounting target..."
mkdir -p /mnt/target
mount /dev/vdb2 /mnt/target
mkdir -p /mnt/target/boot/efi
mount /dev/vdb1 /mnt/target/boot/efi

# 4. Unpack squashfs (simulate Calamares unpackfs)
echo "[4/8] Unpacking filesystem.squashfs onto /mnt/target..."
unsquashfs -f -d /mnt/target /root/monodesk-os/build/live-build/binary/live/filesystem.squashfs

# 5. Configure fstab and machine-id
echo "[5/8] Configuring fstab, hostname, and machine-id..."
ROOT_UUID=$(blkid -s UUID -o value /dev/vdb2)
EFI_UUID=$(blkid -s UUID -o value /dev/vdb1)

cat << EOF > /mnt/target/etc/fstab
# /etc/fstab: static file system information for MONODESK OS
UUID=${ROOT_UUID}  /          ext4  errors=remount-ro  0  1
UUID=${EFI_UUID}   /boot/efi  vfat  umask=0077         0  1
tmpfs              /tmp       tmpfs nosuid,nodev       0  0
EOF

echo "monodesk-pc" > /mnt/target/etc/hostname
rm -f /mnt/target/etc/machine-id
dbus-uuidgen > /mnt/target/etc/machine-id

# 6. Create user monodesk if not exists and lock root
echo "[6/8] Configuring installed user accounts..."
if ! chroot /mnt/target id -u monodesk >/dev/null 2>&1; then
    chroot /mnt/target useradd -m -s /bin/bash -c "MONODESK User" monodesk
    echo "monodesk:monodesk" | chroot /mnt/target chpasswd
fi
chroot /mnt/target usermod -aG sudo,audio,video,plugdev,netdev,input monodesk
chroot /mnt/target passwd -l root || true

# 7. Execute Calamares post-install cleanup
echo "[7/8] Executing Calamares post-install cleanup..."
rm -rf /mnt/target/etc/systemd/system/getty@tty1.service.d /mnt/target/etc/systemd/system/serial-getty@ttyS0.service.d
rm -f /mnt/target/etc/systemd/system/*/autologin.conf
rm -f /mnt/target/etc/sudoers.d/99-monodesk-live /mnt/target/etc/sudoers.d/live
rm -f /mnt/target/etc/lightdm/lightdm.conf.d/01-monodesk-autologin.conf /mnt/target/etc/lightdm/lightdm.conf.d/*live*
rm -rf /mnt/target/etc/live/config.conf.d
rm -f /mnt/target/home/monodesk/Desktop/calamares.desktop || true
mkdir -p /mnt/target/etc/lightdm/lightdm.conf.d

cat << 'EOF' > /mnt/target/etc/lightdm/lightdm.conf.d/01-monodesk-greeter.conf
[Seat:*]
greeter-session=lightdm-gtk-greeter
user-session=monodesk-session
allow-guest=false
EOF

# 8. Install GRUB EFI bootloader
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

# Unmount cleanly
echo "Unmounting target filesystems..."
umount /mnt/target/run
umount /mnt/target/sys
umount /mnt/target/proc
umount /mnt/target/dev/pts
umount /mnt/target/dev
umount /mnt/target/boot/efi
umount /mnt/target

echo "=== CALAMARES INSTALLATION TEST COMPLETED SUCCESSFULLY ==="
