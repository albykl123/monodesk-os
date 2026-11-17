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
    echo "MONODESK OS: Loading live filesystem and hardware drivers..."
    MODDIR="/usr/lib/modules/6.1.0-54-amd64/kernel"
    insmod "${MODDIR}/drivers/block/loop.ko" 2>/dev/null || modprobe -q loop 2>/dev/null || true
    insmod "${MODDIR}/fs/overlayfs/overlay.ko" 2>/dev/null || modprobe -q overlay 2>/dev/null || true
    insmod "${MODDIR}/fs/squashfs/squashfs.ko" 2>/dev/null || modprobe -q squashfs 2>/dev/null || true
    insmod "${MODDIR}/fs/nls/nls_cp437.ko" 2>/dev/null || modprobe -q nls_cp437 2>/dev/null || true
    insmod "${MODDIR}/fs/nls/nls_ascii.ko" 2>/dev/null || modprobe -q nls_ascii 2>/dev/null || true
    insmod "${MODDIR}/fs/nls/nls_iso8859-1.ko" 2>/dev/null || modprobe -q nls_iso8859-1 2>/dev/null || true
    insmod "${MODDIR}/fs/nls/nls_utf8.ko" 2>/dev/null || modprobe -q nls_utf8 2>/dev/null || true
    insmod "${MODDIR}/fs/fat/fat.ko" 2>/dev/null || modprobe -q fat 2>/dev/null || true
    insmod "${MODDIR}/fs/fat/vfat.ko" 2>/dev/null || modprobe -q vfat 2>/dev/null || true
    insmod "${MODDIR}/fs/exfat/exfat.ko" 2>/dev/null || modprobe -q exfat 2>/dev/null || true

    modprobe -q cdrom 2>/dev/null || true
    modprobe -q isofs 2>/dev/null || true
    modprobe -q sr_mod 2>/dev/null || true
    modprobe -q sd_mod 2>/dev/null || true
    modprobe -q ahci 2>/dev/null || true
    modprobe -q ata_piix 2>/dev/null || true
    modprobe -q nvme 2>/dev/null || true
    modprobe -q usb_storage 2>/dev/null || true
    modprobe -q uas 2>/dev/null || true
    modprobe -q virtio_blk 2>/dev/null || true
    modprobe -q ext4 2>/dev/null || true

    mkdir -p /run/live/medium /run/live/rootfs /run/live/overlay /run/live/findiso_dev

    # Check cmdline for findiso parameter
    findiso=""
    for cmd_arg in $(cat /proc/cmdline); do
        case "$cmd_arg" in
            findiso=*)
                findiso="${cmd_arg#findiso=}"
                ;;
        esac
    done

    echo "MONODESK OS: Locating boot medium (findiso='${findiso}')..."
    found_dev=""
    rootfs_img=""
    rootfs_fs=""

    for try in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
        for dev in /dev/sr* /dev/sd* /dev/nvme* /dev/vd* /dev/hd* /dev/mmcblk*; do
            [ -b "$dev" ] || continue

            # 1. If findiso parameter is present, mount and look for ISO file
            if [ -n "$findiso" ]; then
                for fstype in iso9660 vfat ext4 exfat; do
                    if mount -t "$fstype" -o ro "$dev" /run/live/findiso_dev 2>/dev/null; then
                        iso_target="/run/live/findiso_dev/${findiso#/}"
                        if [ -f "$iso_target" ]; then
                            echo "MONODESK OS: Found findiso target on ${dev} (${fstype}): ${iso_target}"
                            [ -b /dev/loop1 ] || mknod /dev/loop1 b 7 1
                            if losetup /dev/loop1 "$iso_target" 2>/dev/null; then
                                if mount -t iso9660 -o ro /dev/loop1 /run/live/medium 2>/dev/null; then
                                    if [ -f /run/live/medium/live/filesystem.squashfs ]; then
                                        found_dev="$dev"
                                        rootfs_img="/run/live/medium/live/filesystem.squashfs"
                                        rootfs_fs="squashfs"
                                        echo "MONODESK OS: Mounted findiso loopback on ${dev}"
                                        break 3
                                    elif [ -f /run/live/medium/live/filesystem.ext4 ]; then
                                        found_dev="$dev"
                                        rootfs_img="/run/live/medium/live/filesystem.ext4"
                                        rootfs_fs="ext4"
                                        echo "MONODESK OS: Mounted findiso loopback on ${dev}"
                                        break 3
                                    fi
                                    umount /run/live/medium 2>/dev/null || true
                                fi
                                losetup -d /dev/loop1 2>/dev/null || true
                            fi
                        fi
                        umount /run/live/findiso_dev 2>/dev/null || true
                    fi
                done
            fi

            # 2. Direct filesystem check (e.g. CD/DVD iso9660, extracted FAT32 partition, ext4)
            for fstype in iso9660 vfat ext4 exfat; do
                if mount -t "$fstype" -o ro "$dev" /run/live/medium 2>/dev/null; then
                    if [ -f /run/live/medium/live/filesystem.squashfs ]; then
                        found_dev="$dev"
                        rootfs_img="/run/live/medium/live/filesystem.squashfs"
                        rootfs_fs="squashfs"
                        echo "MONODESK OS: Boot medium found on ${found_dev} (${fstype}, squashfs)"
                        break 3
                    elif [ -f /run/live/medium/live/filesystem.ext4 ]; then
                        found_dev="$dev"
                        rootfs_img="/run/live/medium/live/filesystem.ext4"
                        rootfs_fs="ext4"
                        echo "MONODESK OS: Boot medium found on ${found_dev} (${fstype}, ext4)"
                        break 3
                    fi
                    umount /run/live/medium 2>/dev/null || true
                fi
            done

            # 3. Auto ISO search fallback if findiso wasn't set but an ISO exists on partition
            for fstype in vfat ext4 exfat iso9660; do
                if mount -t "$fstype" -o ro "$dev" /run/live/findiso_dev 2>/dev/null; then
                    for iso_cand in /run/live/findiso_dev/*.iso /run/live/findiso_dev/boot/*.iso /run/live/findiso_dev/iso/*.iso; do
                        [ -f "$iso_cand" ] || continue
                        [ -b /dev/loop1 ] || mknod /dev/loop1 b 7 1
                        if losetup /dev/loop1 "$iso_cand" 2>/dev/null; then
                            if mount -t iso9660 -o ro /dev/loop1 /run/live/medium 2>/dev/null; then
                                if [ -f /run/live/medium/live/filesystem.squashfs ]; then
                                    found_dev="$dev"
                                    rootfs_img="/run/live/medium/live/filesystem.squashfs"
                                    rootfs_fs="squashfs"
                                    echo "MONODESK OS: Auto-detected ISO medium: ${iso_cand} on ${dev}"
                                    break 4
                                fi
                                umount /run/live/medium 2>/dev/null || true
                            fi
                            losetup -d /dev/loop1 2>/dev/null || true
                        fi
                    done
                    umount /run/live/findiso_dev 2>/dev/null || true
                fi
            done
        done
        sleep 1
    done

    if [ -z "$found_dev" ]; then
        echo "MONODESK OS ERROR: Live boot medium (/live/filesystem.squashfs) not found!"
        echo "Available block devices:"
        ls -l /dev/sd* /dev/sr* /dev/nvme* /dev/vd* 2>/dev/null || true
        exec /bin/sh < /dev/console > /dev/console 2>&1
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
            cp -af /run/live/medium/monodesk/rootfs_overlay/. "${rootmnt}/" 2>/dev/null || true
            chmod +x "${rootmnt}/usr/bin/monodesk-"* 2>/dev/null || true
        fi
    else
        mount -t overlay -o lowerdir=/run/live/rootfs,upperdir=/run/live/overlay/rw,workdir=/run/live/overlay/work overlay "${rootmnt}"
    fi

    echo "MONODESK OS: Root filesystem mounted cleanly at ${rootmnt}."
}
'''

cpio_path = r'D:\anti\overlay.cpio'
with open(cpio_path, 'wb') as f:
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
        'usr/lib/modules/6.1.0-54-amd64/kernel/fs/fat',
        'usr/lib/modules/6.1.0-54-amd64/kernel/fs/exfat',
        'usr/lib/modules/6.1.0-54-amd64/kernel/fs/nls',
    ]
    for d in dirs:
        write_cpio_entry(f, d, b'', mode=0o040755, nlink=2)
    
    write_cpio_entry(f, 'scripts/live', live_script, mode=0o100755, nlink=1)
    
    modules = [
        (r'D:\anti\initrd_modules\loop.ko', 'usr/lib/modules/6.1.0-54-amd64/kernel/drivers/block/loop.ko'),
        (r'D:\anti\initrd_modules\overlay.ko', 'usr/lib/modules/6.1.0-54-amd64/kernel/fs/overlayfs/overlay.ko'),
        (r'D:\anti\initrd_modules\squashfs.ko', 'usr/lib/modules/6.1.0-54-amd64/kernel/fs/squashfs/squashfs.ko'),
        (r'D:\anti\initrd_modules\nls_cp437.ko', 'usr/lib/modules/6.1.0-54-amd64/kernel/fs/nls/nls_cp437.ko'),
        (r'D:\anti\initrd_modules\nls_ascii.ko', 'usr/lib/modules/6.1.0-54-amd64/kernel/fs/nls/nls_ascii.ko'),
        (r'D:\anti\initrd_modules\nls_iso8859-1.ko', 'usr/lib/modules/6.1.0-54-amd64/kernel/fs/nls/nls_iso8859-1.ko'),
        (r'D:\anti\initrd_modules\nls_utf8.ko', 'usr/lib/modules/6.1.0-54-amd64/kernel/fs/nls/nls_utf8.ko'),
        (r'D:\anti\initrd_modules\fat.ko', 'usr/lib/modules/6.1.0-54-amd64/kernel/fs/fat/fat.ko'),
        (r'D:\anti\initrd_modules\vfat.ko', 'usr/lib/modules/6.1.0-54-amd64/kernel/fs/fat/vfat.ko'),
        (r'D:\anti\initrd_modules\exfat.ko', 'usr/lib/modules/6.1.0-54-amd64/kernel/fs/exfat/exfat.ko'),
    ]
    for src_path, entry_name in modules:
        with open(src_path, 'rb') as mod_f:
            mod_data = mod_f.read()
        write_cpio_entry(f, entry_name, mod_data, mode=0o100644, nlink=1)
    
    write_cpio_trailer(f)

print('Successfully created aligned overlay.cpio! Size:', os.path.getsize(cpio_path))

output_targets = [
    r'D:\anti\iso_staging_v201\live\initrd.img',
    r'D:\anti\iso_staging\live\initrd.img'
]

with open(cpio_path, 'rb') as cpio, open(r'D:\anti\initrd_base.img', 'rb') as base:
    cpio_bytes = cpio.read()
    base_bytes = base.read()

for out_initrd in output_targets:
    target_path = pathlib.Path(out_initrd)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_initrd, 'wb') as out:
        out.write(cpio_bytes)
        out.write(base_bytes)
    print(f'Successfully updated {out_initrd}! Size: {os.path.getsize(out_initrd)}')
