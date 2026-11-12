# MONODESK OS 1.0.0 — Post-Release Final Validation & Source Reconciliation Report

**Date:** 2026-11-12  
**Repository:** `albykl123/monodesk-os` (`D:\anti\monodesk-os`)  
**Published Release Under Review:** `v1.0.0` (`https://github.com/albykl123/monodesk-os/releases/tag/v1.0.0`)  
**Remediation Candidate Built Locally:** `v1.0.1-rc1` (`D:\anti\monodesk-os\releases\monodesk-os-1.0.1-rc1-universal-amd64.iso`)  

> **Preservation Notice:** The published GitHub `v1.0.0` release and local `monodesk-os-1.0.0-universal-amd64.iso` binaries were **never modified or replaced**. All defect fixes were isolated to `v1.0.1-rc1`.

---

## 1. Release Integrity & Asset Audit (`v1.0.0`)

### Verified Checksums & Asset Inventory
- **Local `v1.0.0` ISO SHA-256 (verified identical across all 4 Disk D paths):**
  - `9779da035e735351cbb4932fab4679ef98661d3d9dd0d8a10c5d25f6198e5371` (`419,575,808` bytes / `400.14 MiB`)
  - Paths:
    - `D:\monodesk-os-1.0.0-universal-amd64.iso`
    - `D:\anti\monodesk-os\releases\monodesk-os-1.0.0-universal-amd64.iso`
    - `D:\anti\src\monodesk-os-1.0.0-universal-amd64.iso`
    - `D:\anti\monodesk-os\src\monodesk-os-1.0.0-universal-amd64.iso`
- **GitHub `v1.0.0` Downloaded Asset Verification (`gh release download v1.0.0`):**
  - Downloaded `monodesk-os-1.0.0-universal-amd64.iso` SHA-256: `9779DA035E735351CBB4932FAB4679EF98661D3D9DD0D8A10C5D25F6198E5371` (**exact match**)
  - Downloaded `monodesk-os-1.0.0-universal-amd64.iso.sha256` SHA-256: `2C3B4CA78FD9FD470824DB8F955F4B56DD0900A296AB0691D59AA412DB4B88FC`
- **GitHub Release Asset Completeness Gap:**
  - Attached on GitHub `v1.0.0`: `monodesk-os-1.0.0-universal-amd64.iso`, `monodesk-os-1.0.0-universal-amd64.iso.sha256`.
  - Present locally in `releases/` but **not attached** to GitHub `v1.0.0`: `SHA256SUMS.txt`, `BUILD-MANIFEST.json`, `BUILD-MANIFEST.txt`, `PACKAGE-MANIFEST.txt`, `RELEASE-NOTES.md`.

---

## 2. Source Reconciliation vs Tag `v1.0.0` (`af12f8b`)

- **Git Tag `v1.0.0`:** Annotated tag `ae5c52b8c18b75b91ed51718b11dc1df5a79aaeb` pointing to commit `af12f8bed5a590e63b3dfb7003934b51a43b4470`.
- **Actual `v1.0.0` ISO Build Source vs `af12f8b`:**
  1. `af12f8b` reflects the earlier `Disk F` / `filesystem.ext4` (`3,268,114,432` byte) build scripts and manifests (`78c7b9cd...`).
  2. The published single-file `v1.0.0` ISO (`419,575,808` bytes) was built after `af12f8b` using `mksquashfs -comp xz -b 1M` on `D:\anti\iso_staging` via preserved host scripts:
     - `D:\anti\prepare_live_initrd.py` (SHA-256 prefix `822f152ef455`) — added `/run/live/medium/live/filesystem.squashfs` lookup with `ext4` fallback.
     - `D:\anti\build_monodesk_universal_iso.py` (SHA-256 prefix `55523b2ad763`) — updated staging path to `D:\anti\iso_staging`, skipped `filesystem.ext4`, enforced `< 2 GiB`.
     - `D:\anti\stage_monodesk_overlay.py` (SHA-256 prefix `d8bb2ad3a380`) & `D:\anti\patch_efi_img.py` (SHA-256 prefix `9bc0edda49e3`) remain preserved in `D:\anti\`.
  3. Three staged docs inside `D:\anti\iso_staging\monodesk\docs` (`BUILD-STATUS.md` `46a3f8371c70`, `RELEASE-STATUS.md` `3975a6fd6bc9`, `TEST-STATUS.md` `c4b4f197f2f2`) predated edits committed at `af12f8b` (`5b373aeb4489`, `794e34fa9121`, `8a837bbc2b58`); the remaining 21 docs matched identically.
  4. `BUILD-MANIFEST.json` and `BUILD-MANIFEST.txt` have now been updated to record exact `source_commit`, `source_tag_object`, actual build host (`Windows-11-10.0.26300-SP0`, `Python 3.14.7`, `PyCdlib 1.16.0`, QEMU Debian 12 `mksquashfs`), empirical `v1.0.0` test results, and `v1.0.1-rc1`.

---

## 3. Defects Found on `v1.0.0` & Remediation in `v1.0.1-rc1`

1. **Legacy BIOS Boot Broken (`v1.0.0` FAILED):**
   - *Symptom:* QEMU SeaBIOS halted at `Booting from DVD/CD... / no boot info _` (`D:\anti\bios_screen.png`).
   - *Root Cause:* `v1.0.0` registered a raw 2048-byte `cdboot.img` without embedded GRUB `i386-pc` `core.img` and with `boot_info_table=False`.
   - *Fix in `v1.0.1-rc1`:* Built `cdboot_eltorito.img` (`159,675` bytes = `cdboot.img` + `grub-mkimage -O i386-pc biosdisk iso9660 ...`) and updated `scripts/build-iso-win.py` to auto-set `boot_info_table=True` when BIOS image size > 2048 bytes.
2. **Calamares Installer & GUI Desktop Missing (`v1.0.0` FAILED):**
   - *Symptom:* `which calamares`, `xorg`, `startx`, `xfce4-session`, `xfwm4`, `lightdm`, `xfconf-query`, `powerprofilesctl`, `zramswap`, `PyQt6`, and `gi` were all missing inside the `v1.0.0` live VM (286 CLI packages inherited from base `0.img`).
   - *Fix in `v1.0.1-rc1`:* Installed Calamares (`3.2.61-1+b1`), `calamares-settings-debian`, `fdisk` (`sfdisk`), `gdisk`, `udisks2`, `upower`, `parted`, `dosfstools`, `e2fsprogs`, `btrfs-progs`, `cryptsetup`, `grub-efi-amd64`, `grub-pc-bin`, `os-prober`, `xorg`, `xfce4-*`, `lightdm`, `lightdm-gtk-greeter`, `python3-pyqt6`, `python3-gi`, `gir1.2-gtk-3.0`, `zram-tools`, `power-profiles-daemon`, `network-manager`, `console-setup`, `keyboard-configuration` into `v1.0.1-rc1` rootfs (`D:\anti\iso_staging_v101\live\filesystem.squashfs`, `504,745,984` bytes). Note: during RC1 testing, Calamares initially reported `"There are no partitions to install on"` despite `/dev/vda` existing because `sfdisk` (`fdisk`) and `udisks2` were omitted; adding them resolved KPMCore `pmsfdiskbackendplugin` detection immediately.
3. **`monodesk-shell` Crash Without QML Bindings (`v1.0.0` FAILED):**
   - *Symptom:* `monodesk-shell` raised `NameError: name 'QObject' is not defined` at line 51 when PyQt6/PySide6 were absent.
   - *Fix in `desktop/shell/monodesk_shell.py` & `v1.0.1-rc1`:* Added fallback `QObject`/`pyqtSignal`/`pyqtSlot`/`pyqtProperty`/`QTimer`/`QUrl` definitions when `runtime is None`; confirmed `import monodesk_shell` completes cleanly without exception.
4. **`monodesk-profile.service` Disabled on Boot (`v1.0.0` & initial `rc1` FAILED):**
   - *Symptom:* `systemctl status monodesk-profile` showed `disabled; inactive (dead)`. Initially in `rc1`, copying `multi-user.target.wants/monodesk-profile.service` as a regular file inside `rootfs_overlay` over iso9660 shadowed the squashfs symlink.
   - *Fix in `scripts/stage-overlay-win.py` & `v1.0.1-rc1`:* Removed the regular-file `.wants` copy in overlay and created symlink `multi-user.target.wants/monodesk-profile.service -> /etc/systemd/system/monodesk-profile.service` inside squashfs.

---

## 4. Strict Validation Ledger

### A. VERIFIED RESULTS (Directly Observed After Final Edits)
- **Checksums & Repository Integrity:**
  - `monodesk-os-1.0.0-universal-amd64.iso` (`9779da03...`) matches identically across GitHub download and all 4 Disk D paths; `v1.0.0` release remains live and untouched.
  - `monodesk-os-1.0.1-rc1-universal-amd64.iso` SHA-256: `eb5dbb19c4cf83efe30f5196bf563e8eaeb8d344e373e1f7cef98be4fe103b37` (`687,063,040` bytes).
  - `pytest -v` in `D:\anti\monodesk-os`: **32 passed in 1.65s**.
- **`v1.0.0` Live QEMU UEFI Verification:**
  - Booted GRUB -> Linux `6.1.0-54-amd64` -> `squashfs` + `overlayfs` -> `graphical.target`; `monodesk-hw-detect --report` passed; `monodesk-profile-ctl recommend`/`set` updated `/etc/monodesk/profile.conf` (`LITE` at 4096 MB, `STANDARD` at 8192 MB).
  - **Verified Failures on `v1.0.0`:** Legacy BIOS failed (`no boot info`); Calamares, Xorg, XFCE4, LightDM, `monodesk-shell`, `zramswap`, and `powerprofilesctl` were non-functional/absent.
- **`v1.0.1-rc1` Legacy BIOS Live Verification (`task-396`):**
  - QEMU SeaBIOS (`-boot d`, no OVMF) booted `BOOT_MODE=LEGACY_BIOS` via `cdboot_eltorito.img`, mounted `squashfs` + `overlayfs`, started `monodesk-profile.service` (`enabled`, `active (exited)`, `PROFILE=lite`), `lightdm.service` (`enabled`, `active (running)` with `Xorg :0`), and `udisks2.service` (`active (running)`), and passed `GTK3_GI_OK`.
- **`v1.0.1-rc1` Calamares Installation & Installed Disk Boot (`task-377`, `task-384`, `task-391`):**
  - Calamares `3.2.61` automated GUI install onto disposable `25 GiB` `test-disposable-install.qcow2` created GPT partition table (`/dev/vda1` 512 MiB FAT32 `/boot/efi`, `/dev/vda2` ext4 `/`), unpacked `filesystem.squashfs`, wrote `/etc/fstab` & `/boot/efi/EFI/MONODESK_OS`, created user `monodesk` (`uid=1000`), hostname `monodesk-vm`, and expanded qcow2 to `2.05 GiB`.
  - Direct QEMU UEFI boot **with NO ISO attached** booted from `/dev/vda2` (`MONODESK OS 1.0`, `lightdm` + `Xorg :0` active, `zramswap` active, `monodesk-profile.service` `enabled` & `active (exited)`).
- **`v1.0.1-rc1` Standard & Lite Profile Operation in Installed System (`task-391`):**
  - At `4096 MB` RAM: `monodesk-profile.service` auto-selected `PROFILE=lite`, `powerprofilesctl`=`power-saver`, `zram0`=`1.9G`.
  - `monodesk-profile-ctl set standard` switched `/etc/monodesk/profile.conf` -> `PROFILE=standard`, `zram0` -> `977.2M`, `powerprofilesctl` -> `balanced`; `set lite` restored `PROFILE=lite`, `zram0` -> `1.9G`, `power-saver`.
  - At `8192 MB` RAM: `monodesk-profile.service` auto-selected `PROFILE=standard`, `powerprofilesctl`=`balanced`.

### B. UNVERIFIED CLAIMS
- **Physical Hardware Certification (Lenovo IdeaPad Slim 5 & Lenovo B590):** Not tested on physical bare-metal hardware; Intel Iris Xe / AX201, Intel HD 4000 / AR9485, Wi-Fi, Bluetooth, PipeWire sound hardware, battery transitions, and touchpad gestures on physical units are **unverified**.
- **Calamares LUKS2 Full-Disk Encryption & Dual-Boot:** Verified only the automated GPT + ext4 `Erase disk` flow in QEMU UEFI; LUKS2 passphrase unlock and dual-boot alongside Windows were not exercised.
- **Installed System Legacy BIOS Boot:** Legacy BIOS boot was verified on the `v1.0.1-rc1` Live ISO (`BOOT_MODE=LEGACY_BIOS`), while the Calamares installed-disk test ran in UEFI mode.
- **Interactive Desktop Rendering of All 23 GTK3 Apps & `monodesk-shell` QML Window:** Individual app windows and QML compositor rendering on screen were not end-to-end GUI clicked inside Xorg beyond `GTK3_GI_OK` and `Calamares` GUI installation.

### C. REMAINING LIMITATIONS
1. **Published `v1.0.0` Functional Scope:** Because `v1.0.0` is preserved unmodified, the public `v1.0.0` ISO remains a CLI-only live UEFI preview image lacking BIOS boot, Calamares, and GUI packages until `v1.0.1` is promoted after release review.
2. **Missing `python3-pyqt6.qtquick` in `v1.0.1-rc1`:** `python3-pyqt6` alone does not include `PyQt6.QtQml` on Debian Bookworm (`ModuleNotFoundError: No module named 'PyQt6.QtQml'`). `monodesk-shell` falls back without crashing while XFCE4/LightDM provides the desktop session; `python3-pyqt6.qtquick` should be added before promoting `v1.0.1` final.
3. **Root Autologin Getty Drop-ins Persisted to Target Disk:** `/etc/systemd/system/getty@tty1.service.d/autologin.conf` and `serial-getty@ttyS0.service.d/autologin.conf` inside `filesystem.squashfs` are copied onto installed targets by Calamares `unpackfs`, causing automatic root login on `tty1`/`ttyS0` post-install. These should be stripped during Calamares install (`shellprocess` / `live-config`) before `v1.0.1` final.
4. **Host WSL2 Corruption (`WSL_E_DISK_CORRUPTED`):** Windows host WSL2 failed during builds; Linux squashfs/grub image construction ran reliably via an ephemeral QEMU Debian 12 builder VM instead.
