import os
import struct
import pathlib

_ino_counter = 1

def write_cpio_entry(out, path, data, mode=0o100644, nlink=1, uid=0, gid=0, mtime=0):
    global _ino_counter
    ino = _ino_counter
    _ino_counter += 1

    filename = path.encode('utf-8') + b'\x00'
    filesize = len(data)
    
    header = b'070701'  # magic
    header += f'{ino:08x}'.encode()  # ino
    header += f'{mode:08x}'.encode()  # mode
    header += f'{uid:08x}'.encode()  # uid
    header += f'{gid:08x}'.encode()  # gid
    header += f'{nlink:08x}'.encode()  # nlink
    header += f'{mtime:08x}'.encode()  # mtime
    header += f'{filesize:08x}'.encode()  # filesize
    header += f'{0:08x}'.encode()  # devmajor
    header += f'{0:08x}'.encode()  # devminor
    header += f'{0:08x}'.encode()  # rdevmajor
    header += f'{0:08x}'.encode()  # rdevminor
    header += f'{len(filename):08x}'.encode()  # namesize
    header += f'{0:08x}'.encode()  # check
    
    out.write(header)
    out.write(filename)
    pad1 = (4 - ((len(header) + len(filename)) % 4)) % 4
    out.write(b'\x00' * pad1)
    
    if filesize > 0:
        out.write(data)
        pad2 = (4 - (filesize % 4)) % 4
        out.write(b'\x00' * pad2)

def write_cpio_trailer(out):
    write_cpio_entry(out, 'TRAILER!!!', b'', mode=0, nlink=1)
    # Pad entire cpio to 4096 bytes so subsequent compressed cpio aligns cleanly
    cur = out.tell()
    pad = (4096 - (cur % 4096)) % 4096
    out.write(b'\x00' * pad)

live_script = b'''mount_top() {
    :
}

mount_premount() {
    :
}

mount_bottom() {
    :
}

mountroot() {
    echo "MONODESK OS: Loading live filesystem drivers..."
    insmod /usr/lib/modules/6.1.0-54-amd64/kernel/drivers/block/loop.ko 2>/dev/null || modprobe -q loop 2>/dev/null || true
    insmod /usr/lib/modules/6.1.0-54-amd64/kernel/fs/overlayfs/overlay.ko 2>/dev/null || modprobe -q overlay 2>/dev/null || true
    insmod /usr/lib/modules/6.1.0-54-amd64/kernel/fs/squashfs/squashfs.ko 2>/dev/null || modprobe -q squashfs 2>/dev/null || true
    modprobe -q cdrom 2>/dev/null || true
    modprobe -q isofs 2>/dev/null || true
    modprobe -q sr_mod 2>/dev/null || true
    modprobe -q sd_mod 2>/dev/null || true
    modprobe -q ahci 2>/dev/null || true
    modprobe -q ata_piix 2>/dev/null || true
    modprobe -q ext4 2>/dev/null || true

    mkdir -p /run/live/medium /run/live/rootfs /run/live/overlay

    echo "MONODESK OS: Locating boot medium..."
    found_dev=""
    rootfs_img=""
    rootfs_fs=""
    for try in 1 2 3 4 5 6 7 8 9 10 11 12; do
        for dev in /dev/sr0 /dev/sr1 /dev/sda /dev/sda1 /dev/sdb /dev/sdb1 /dev/vda /dev/vdb /dev/hda /dev/hdc; do
            [ -b "$dev" ] || continue
            if mount -t iso9660 -o ro "$dev" /run/live/medium 2>/dev/null; then
                if [ -f /run/live/medium/live/filesystem.squashfs ]; then
                    found_dev="$dev"
                    rootfs_img="/run/live/medium/live/filesystem.squashfs"
                    rootfs_fs="squashfs"
                    echo "MONODESK OS: Boot medium found on ${found_dev} (squashfs)"
                    break 2
                elif [ -f /run/live/medium/live/filesystem.ext4 ]; then
                    found_dev="$dev"
                    rootfs_img="/run/live/medium/live/filesystem.ext4"
                    rootfs_fs="ext4"
                    echo "MONODESK OS: Boot medium found on ${found_dev} (ext4)"
                    break 2
                fi
                umount /run/live/medium 2>/dev/null || true
            fi
        done
        sleep 1
    done

    if [ -z "$found_dev" ]; then
        echo "MONODESK OS ERROR: Live boot medium (/live/filesystem.squashfs) not found!"
        /bin/sh
        return 1
    fi

    [ -b /dev/loop0 ] || mknod /dev/loop0 b 7 0
    echo "MONODESK OS: Attaching loopback root filesystem (${rootfs_fs})..."
    losetup /dev/loop0 "${rootfs_img}"
    mount -t "${rootfs_fs}" -o ro /dev/loop0 /run/live/rootfs

    echo "MONODESK OS: Creating writable overlay in RAM..."
    mount -t tmpfs -o mode=0755,size=75% tmpfs /run/live/overlay
    mkdir -p /run/live/overlay/rw /run/live/overlay/work

    if [ -d /run/live/medium/monodesk/rootfs_overlay ]; then
        if mount -t overlay -o lowerdir=/run/live/medium/monodesk/rootfs_overlay:/run/live/rootfs,upperdir=/run/live/overlay/rw,workdir=/run/live/overlay/work overlay "${rootmnt}" 2>/dev/null; then
            echo "MONODESK OS: Layered MONODESK overlay mounted via overlayfs."
        else
            echo "MONODESK OS: Mounting base rootfs and injecting MONODESK overlay..."
            mount -t overlay -o lowerdir=/run/live/rootfs,upperdir=/run/live/overlay/rw,workdir=/run/live/overlay/work overlay "${rootmnt}"
            mkdir -p "${rootmnt}/mnt_iso"
            if mount -t iso9660 -o ro "$found_dev" "${rootmnt}/mnt_iso" 2>/dev/null; then
                chroot "${rootmnt}" /usr/bin/cp -af /mnt_iso/monodesk/rootfs_overlay/. / 2>/dev/null || true
                chroot "${rootmnt}" /usr/bin/chmod +x /usr/bin/monodesk-* 2>/dev/null || true
                umount "${rootmnt}/mnt_iso" 2>/dev/null || true
            fi
        fi
    else
        mount -t overlay -o lowerdir=/run/live/rootfs,upperdir=/run/live/overlay/rw,workdir=/run/live/overlay/work overlay "${rootmnt}"
    fi

    echo "MONODESK OS: Root filesystem mounted cleanly at ${rootmnt}."
}
'''

cpio_path = r'D:\anti\overlay.cpio'
with open(cpio_path, 'wb') as f:
    # Create all required parent directories
    dirs = [
        'scripts',
        'usr',
        'usr/lib',
        'usr/lib/modules',
        'usr/lib/modules/6.1.0-54-amd64',
        'usr/lib/modules/6.1.0-54-amd64/kernel',
        'usr/lib/modules/6.1.0-54-amd64/kernel/drivers',
        'usr/lib/modules/6.1.0-54-amd64/kernel/drivers/block',
        'usr/lib/modules/6.1.0-54-amd64/kernel/fs',
        'usr/lib/modules/6.1.0-54-amd64/kernel/fs/overlayfs',
        'usr/lib/modules/6.1.0-54-amd64/kernel/fs/squashfs',
    ]
    for d in dirs:
        write_cpio_entry(f, d, b'', mode=0o040755, nlink=2)
    
    # Live script
    write_cpio_entry(f, 'scripts/live', live_script, mode=0o100755, nlink=1)
    
    # Kernel modules
    modules = [
        (r'D:\anti\initrd_modules\loop.ko', 'usr/lib/modules/6.1.0-54-amd64/kernel/drivers/block/loop.ko'),
        (r'D:\anti\initrd_modules\overlay.ko', 'usr/lib/modules/6.1.0-54-amd64/kernel/fs/overlayfs/overlay.ko'),
        (r'D:\anti\initrd_modules\squashfs.ko', 'usr/lib/modules/6.1.0-54-amd64/kernel/fs/squashfs/squashfs.ko'),
    ]
    for src_path, entry_name in modules:
        with open(src_path, 'rb') as mod_f:
            mod_data = mod_f.read()
        write_cpio_entry(f, entry_name, mod_data, mode=0o100644, nlink=1)
    
    write_cpio_trailer(f)

print('Successfully created aligned overlay.cpio! Size:', os.path.getsize(cpio_path))

# Prepend early uncompressed CPIO BEFORE the zstd compressed Debian base initrd!
out_initrd = r'D:\anti\iso_staging\live\initrd.img'
with open(cpio_path, 'rb') as cpio, open(r'D:\anti\initrd_base.img', 'rb') as base, open(out_initrd, 'wb') as out:
    out.write(cpio.read())
    out.write(base.read())

print('Successfully updated initrd.img (early_cpio + zstd_initrd)! Size:', os.path.getsize(out_initrd))
