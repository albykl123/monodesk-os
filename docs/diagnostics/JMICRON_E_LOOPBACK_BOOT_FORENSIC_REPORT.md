# MONODESK OS 2.0 — JMICRON DRIVE E: BOOT FORENSIC AUDIT REPORT
**Document Reference:** `FORENSIC-AUDIT-2026-11-16-E-BOOT-PANIC`  
**Target Hardware:** Lenovo IdeaPad Slim 5 (16IAH8 / Core i5-12450H / Intel Iris Xe / NVMe SSD + JMicron 1TB USB HDD)  
**Target Volume:** JMicron External USB HDD — Disk 1, Partition 2 (`E:\`, FAT32, `NEW VOLUME` / `MONODESK_OS`, ~31.23 GB)  
**Investigation Mode:** Strictly Read-Only Host Forensic Inspection & Emulated Reproduction  

---

## EXECUTIVE SUMMARY

A forensic examination of the physical JMicron external drive (Disk 1), partition `E:`, and the MONODESK OS 2.0.1-rc1 live system artifacts was conducted to diagnose the reported boot failure:
```
Kernel panic - not syncing: Attempted to kill init! exitcode=0x00000200
```

### Key Diagnostic Findings:
1. **Drive E: Contents & Method of Deployment:**
   - There is **no `.iso` file** on partition `E:`. Instead, the file hierarchy of `monodesk-os-2.0.1-rc1-universal-amd64.iso` was extracted directly to the root of the FAT32 filesystem (evidenced by the presence of `[BOOT]\1-Boot-NoEmul.img`, `2-Boot-NoEmul.img`, `.disk/`, `EFI/`, `boot/`, and `live/`).
   - Candidate ISO images exist on partition `D:` (`D:\anti\monodesk-os\releases\monodesk-os-2.0.1-rc1-universal-amd64.iso`, SHA-256 `e4dff2a2a...`).
2. **GRUB Bootloader Execution:**
   - GRUB is loaded by UEFI firmware from `E:\EFI\BOOT\BOOTX64.EFI`.
   - `E:\EFI\BOOT\grub.cfg` chains to `E:\boot\grub\grub.cfg`.
   - **GRUB does NOT use loopback.** It executes a direct search:
     ```grub
     search --no-floppy --file --set=root /.disk/info
     linux /live/vmlinuz boot=live components monodesk.profile=standard apparmor=1 security=apparmor console=tty0 console=ttyS0,115200n8
     initrd /live/initrd.img
     ```
   - GRUB successfully loads `vmlinuz` and `initrd.img` into RAM and transfers control to the Linux kernel.
3. **Primary Root Cause — The Initramfs Medium Locator Defect:**
   - The custom initramfs script (`scripts/live` injected via early uncompressed CPIO by `prepare-initrd-win.py`) contains a **hardcoded device scan**:
     ```bash
     for dev in /dev/sr0 /dev/sr1 /dev/sda /dev/sda1 /dev/sdb /dev/sdb1 /dev/vda /dev/vdb /dev/hda /dev/hdc; do
         mount -t iso9660 -o ro "$dev" /run/live/medium
     ```
   - **Partition E: is Partition 2 on Disk 1 (`/dev/sda2` or `/dev/sdb2`).**
     - `/dev/sda2` and `/dev/sdb2` are **completely omitted** from the candidate device list!
     - The script **only attempts `mount -t iso9660`**. Because partition `E:` is formatted as **FAT32 (`vfat`)**, `mount -t iso9660` fails with `EINVAL`.
     - **Missing Kernel Modules:** `initrd.img` contains `loop.ko`, `overlay.ko`, and `squashfs.ko`, but **lacks `fat.ko`, `vfat.ko`, `nls_cp437.ko`, and `nls_utf8.ko`**. Even if the mount command attempted `-t vfat`, the kernel would reject it due to missing filesystem drivers in the initramfs.
4. **The Kernel Panic Mechanism (`exitcode=0x00000200`):**
   - Because no live medium is mounted, `mountroot()` prints `Live boot medium not found!`, attempts to spawn `/bin/sh`, and returns `1`.
   - In `/init`, `validate_init()` fails because `${rootmnt}` is unmounted.
   - `/init` calls `panic()`. Since `console=tty0` has no active controlling terminal, the fallback shell exits.
   - `/init` reaches the end of the script and terminates with exit code 2.
   - In Linux kernel wait status representation, exit code 2 is shifted left by 8 bits: `0x02 << 8 = 0x0200`.
   - The Linux kernel panics when PID 1 exits: `Attempted to kill init! exitcode=0x00000200`.

---

## 1. STORAGE ARCHITECTURE & PARTITION LAYOUT

Inspection via Windows Storage Management (`Get-Disk`, `Get-Partition`, `Get-Volume`):

| Disk Number | Friendly Name | Bus Type | Partition Style | Total Capacity |
| :--- | :--- | :--- | :--- | :--- |
| **Disk 0** | WDC PC SN530 NVMe SSD | NVMe | GPT | 512 GB (Internal OS / Windows 11) |
| **Disk 1** | JMicron Tech External HDD | USB | GPT | 1,000,204,886,016 bytes (~1.0 TB) |

### Disk 1 Partition Breakdown:
- **Partition 1 (`D:\`, NTFS, "hdd"):**
  - Size: 966,647,611,392 bytes (~900 GB).
  - Linux Device Equivalent: `/dev/sda1` (or `/dev/sdb1` if external drives enumerate second).
  - Content: Development workspace (`D:\anti\monodesk-os`), release archives, personal data.
- **Partition 2 (`E:\`, FAT32, "NEW VOLUME" / "MONODESK_OS"):**
  - Size: 33,554,432,000 bytes (~31.23 GB).
  - Filesystem: FAT32.
  - Linux Device Equivalent: `/dev/sda2` (or `/dev/sdb2`).
  - Active Boot Flag / EFI System Directory: Present (`\EFI\BOOT\BOOTX64.EFI`).

---

## 2. FILE FORENSICS ON DRIVE E:

A recursive file enumeration of `E:\` revealed that no standalone `.iso` file exists on this volume. Rather, the entire candidate release ISO was unpacked onto the FAT32 volume:

```
E:\
├── [BOOT]\
│   ├── 1-Boot-NoEmul.img      (2,048 bytes - El Torito floppy/catalog boot record)
│   └── 2-Boot-NoEmul.img      (961,695,744 bytes - El Torito EFI system partition image)
├── .disk\
│   ├── info                   (62 bytes: "MONODESK OS 2.0.1-rc1 Universal PC Edition - amd64 (20261116)")
│   └── mini-info              (23 bytes)
├── boot\
│   └── grub\
│       ├── cdboot.img         (161,990 bytes)
│       ├── efi.img            (130,023,424 bytes)
│       └── grub.cfg           (2,411 bytes - Primary GRUB Configuration)
├── EFI\
│   ├── BOOT\
│   │   ├── BOOTX64.EFI        (1,048,504 bytes - GRUB Shim / EFI Loader)
│   │   ├── grub.cfg           (109 bytes - Staging loader)
│   │   ├── grubx64.efi        (4,183,488 bytes - GRUB 2.12 core)
│   │   └── mmx64.efi          (877,992 bytes - MOK manager)
│   └── debian\
├── live\
│   ├── filesystem.packages   (24,032 bytes)
│   ├── filesystem.squashfs   (779,599,872 bytes - Rootfs container)
│   ├── initrd.img            (30,797,578 bytes - Composite CPIO initramfs)
│   └── vmlinuz               (8,234,944 bytes - Linux 6.1.0-54-amd64 kernel)
└── monodesk\
    ├── docs\
    └── rootfs_overlay\
```

The presence of the `[BOOT]` folder proves that the ISO was extracted using an archive extractor (such as 7-Zip), which exposes El Torito metadata as regular files and folders.

---

## 3. GRUB CONFIGURATION ANALYSIS

### 3.1 EFI Loader (`E:\EFI\BOOT\grub.cfg`)
```grub
search --no-floppy --file --set=root /.disk/info
set prefix=($root)/boot/grub
configfile $prefix/grub.cfg
```
*Assessment:* Clean and functional. Correctly locates partition `E:` by searching for `/.disk/info` and sources `E:\boot\grub\grub.cfg`.

### 3.2 Main Menu (`E:\boot\grub\grub.cfg`)
```grub
set default="0"
set timeout=5

insmod part_gpt
insmod part_msdos
insmod fat
insmod iso9660
insmod ext2
insmod all_video
insmod efi_gop
insmod efi_uga

menuentry "MONODESK OS 2.0.1-rc1.1-rc1 (Universal PC - Standard Profile)" --class monodesk --class gnu-linux --class gnu --class os {
    search --no-floppy --file --set=root /.disk/info
    echo "Loading MONODESK OS 2.0.1-rc1.1-rc1 Kernel (AMD64 Linux LTS)..."
    linux /live/vmlinuz boot=live components monodesk.profile=standard apparmor=1 security=apparmor console=tty0 console=ttyS0,115200n8
    echo "Loading Hardware Detection & Initial Ramdisk..."
    initrd /live/initrd.img
}
```

### 3.3 Loopback vs. Direct Boot Evaluation
- **Is Loopback Used?** No. GRUB treats `E:` as a standard native filesystem. It does not invoke `loopback loop (hdX,gptY)/filename.iso`.
- **Command-Line Parameters:**
  - `boot=live`: Tells `/init` to execute `/scripts/live`.
  - `components`: Instructs live scripts to run user configuration hooks.
  - `monodesk.profile=standard`: Sets custom shell mode.
  - **Omissions:** Missing `findiso=`, `live-media=`, `live-media-path=`, and `root=`.

---

## 4. INITRAMFS ARCHITECTURE & DEFECT TRACE

### 4.1 Structure of `initrd.img` (30,797,578 bytes)
Binary dissection of `E:\live\initrd.img` reveals a dual-stage archive:
1. **Offset `0x00000000` to `0x00091000` (593,920 bytes):**
   - Uncompressed ASCII CPIO archive (`070701`).
   - Injected by `scripts/prepare-initrd-win.py`.
   - Contains `scripts/live` (3,879 bytes) and 3 kernel modules:
     - `usr/lib/modules/6.1.0-54-amd64/kernel/drivers/block/loop.ko`
     - `usr/lib/modules/6.1.0-54-amd64/kernel/fs/overlayfs/overlay.ko`
     - `usr/lib/modules/6.1.0-54-amd64/kernel/fs/squashfs/squashfs.ko`
2. **Offset `0x00091000` to EOF (30,203,658 bytes):**
   - Zstandard (`zstd`) compressed stream containing Debian `initramfs-tools` base (`initrd_base.img`).
   - Contains standard `init`, `scripts/functions`, `scripts/local`, `scripts/nfs`.
   - **Crucially: Contains NO `fat.ko`, `vfat.ko`, `nls_cp437.ko`, or `nls_utf8.ko`!**

### 4.2 The Live Mount Script (`scripts/live` -> `mountroot()`)
```bash
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
                ...
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
    ...
```

---

## 5. ROOT CAUSE & KERNEL PANIC BREAKDOWN

| Step | Execution Stage | What Actually Occurs on Hardware |
| :--- | :--- | :--- |
| **1** | BIOS / UEFI Boot | Laptop UEFI loads `E:\EFI\BOOT\BOOTX64.EFI`. |
| **2** | GRUB Execution | GRUB loads `linux /live/vmlinuz` and `initrd /live/initrd.img` into RAM. |
| **3** | Kernel Hand-off | Kernel mounts rootfs (tmpfs), decompresses CPIO, executes `/init` (PID 1). |
| **4** | Parameter Parsing | `/init` sets `BOOT=live`, loads `. /scripts/live`. |
| **5** | Device Probing | `mountroot()` scans `/dev/sr0..`, `/dev/sda`, `/dev/sda1`, `/dev/sdb`, `/dev/sdb1`. |
| **6** | Device Mismatch | Partition `E:` is **Partition 2 (`/dev/sda2`)**. It is never evaluated. |
| **7** | Filesystem Mismatch | Even if `/dev/sda2` were evaluated, the script only attempts `mount -t iso9660`. Partition `E:` is FAT32. |
| **8** | Module Absence | Even if `mount -t vfat` were attempted, `initrd.img` lacks `vfat.ko` and `fat.ko`. |
| **9** | Mount Failure | `found_dev` remains empty after 12 retries. |
| **10** | Error Fallback | Script outputs error message, attempts `/bin/sh`, and executes `return 1`. |
| **11** | Init Termination | `/init` verifies `/root/sbin/init`. Since `/root` is empty, it invokes `panic()`. |
| **12** | Shell Disconnect | With `console=tty0`, the interactive fallback shell cannot allocate a controlling terminal and exits. |
| **13** | PID 1 Termination | `/init` exits with status `2`. |
| **14** | **Kernel Panic** | Linux kernel catches PID 1 termination: `0x02 << 8 = 0x0200` -> **`Kernel panic: Attempted to kill init! exitcode=0x00000200`**. |

---

## 6. COMPARISON: DEBIAN LIVE-BOOT VS. MONODESK CUSTOM SCRIPT

| Capability | Official Debian `live-boot` | MONODESK `prepare-initrd-win.py` |
| :--- | :--- | :--- |
| **Storage Discovery** | Uses `blkid` to enumerate all block devices dynamically | Hardcoded array of 10 fixed device names |
| **Partition Support** | Probes all partitions (`/dev/sd*`, `/dev/nvme*`, `/dev/mmcblk*`) | Checks only partition 1 (`sda1`, `sdb1`); ignores partition 2 (`sda2`) |
| **Filesystems** | Detects and mounts `iso9660`, `vfat`, `ext4`, `ntfs`, `f2fs` | Strictly forces `mount -t iso9660` |
| **FAT32 Modules** | Includes `fat.ko`, `vfat.ko`, `nls_cp437.ko`, `nls_utf8.ko` in initramfs | Completely absent from initramfs |
| **ISO Loopback** | Supported via `findiso=/path/to.iso` (`9990-findiso.sh`) | Completely unsupported |
| **Error Handling** | Interactive rescue shell with retry timeouts | Terminal `return 1` causing PID 1 exit and kernel panic |

---

## 7. REMEDIATION PLAN & SAFEST CORRECTION

To achieve seamless, universal bootability without modifying or erasing any partition on the 1TB JMicron drive (`D:` NTFS remains 100% untouched and safe):

### Step 1: Extract Missing Kernel Modules from `filesystem.squashfs`
Extract the following kernel modules from `usr/lib/modules/6.1.0-54-amd64/` inside `filesystem.squashfs`:
- `kernel/fs/fat/fat.ko`
- `kernel/fs/fat/vfat.ko`
- `kernel/fs/nls/nls_cp437.ko`
- `kernel/fs/nls/nls_ascii.ko`
- `kernel/fs/nls/nls_utf8.ko`
- `kernel/fs/nls/nls_iso8859-1.ko`

### Step 2: Update `prepare-initrd-win.py`
1. **Bundle FAT modules:** Add the extracted FAT and NLS modules into the early CPIO archive alongside `loop.ko`, `overlay.ko`, and `squashfs.ko`.
2. **Universal Device Iteration in `scripts/live`:**
   Replace the hardcoded device list with dynamic block device discovery:
   ```bash
   # Dynamically detect all block devices and partitions
   all_devs=$(ls /dev/sr* /dev/sd* /dev/nvme*n*p* /dev/vd* /dev/hd* 2>/dev/null)
   ```
3. **Multi-Filesystem Probing:**
   Try mounting candidate partitions with auto-detection or sequential filesystem types:
   ```bash
   for fstype in iso9660 vfat ext4; do
       if mount -t "$fstype" -o ro "$dev" /run/live/medium 2>/dev/null; then
           if [ -f /run/live/medium/live/filesystem.squashfs ]; then
               found_dev="$dev"
               break 2
           fi
           umount /run/live/medium 2>/dev/null || true
       fi
   done
   ```
4. **ISO-Scan Support (Optional / Future-proof):**
   If `findiso=*` is present in `/proc/cmdline`, check if `/run/live/medium/$findiso` exists, attach via `losetup`, and mount the inner `filesystem.squashfs`.

### Step 3: Rebuild and Deploy Fixed `initrd.img` to `E:\live\initrd.img`
- Generate the new composite `initrd.img` (~31.5 MB).
- Verify in QEMU with a FAT32 test disk.
- Copy the verified `initrd.img` to `E:\live\initrd.img`.
- Update release candidate ISO and publish `v2.0.1-rc2`.

---
*Report certified by Lead Distribution Integrator & QA Architect.*
