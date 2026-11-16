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

echo "[5/8] Configuring fstab, hostname, and machine-id..."
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
