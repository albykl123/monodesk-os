# MONODESK OS 1.0.1 — Final Release Validation Report

**Product:** MONODESK OS 1.0.1 (Universal PC Edition)  
**Tag / Source Commit:** `v1.0.1` / `e0efd886af79b8f8c7db62f8adf1e14b177efb05`  
**Final ISO:** `releases/monodesk-os-1.0.1-universal-amd64.iso`  
**ISO Size:** `766,408,704` bytes (`730.90 MiB` / `0.714 GiB`)  
**ISO SHA-256:** `3b8ad75a7f3d011d591d30b42efbb48d7edb53a316a642d7ea8465105c219776`  
**Rootfs SquashFS SHA-256:** `a418a38466180c864b77243f236447255a474a76b51eae89d4c6ee226f84c949` (`583,917,568` bytes, `761` Debian Bookworm packages)  
**Validation Date:** 2026-11-12

---

## 1. Executive Summary

Both release blockers remaining after `v1.0.1-rc1` have been resolved in source (`e0efd886af79b8f8c7db62f8adf1e14b177efb05`), packaged into `monodesk-os-1.0.1-universal-amd64.iso`, and verified across all 17 QEMU / Xorg / Calamares / post-install / pytest test gates. Previously published `v1.0.0` (`9779da03...`) and local candidate `v1.0.1-rc1` (`eb5dbb19...`) remain preserved intact.

**Physical Hardware Certification Status:** Physical testing on **Lenovo IdeaPad Slim 5** and **Lenovo B590** has **NOT** been performed in this environment and remains **PENDING / UNVERIFIED**.

---

## 2. Blocker Resolutions Implemented & Verified in `1.0.1`

1. **MONODESK Shell & Qt 6 / QML Stack Fixed:**
   - Added `python3-pyqt6.qtquick` (`6.4.2-1`), `python3-pyqt6.qtqml` (`6.4.2-1`), `qml6-module-qtquick{,-window,-controls,-layouts,-templates}`, and `qml6-module-qtqml-models` to `build/live-build/config/package-lists/02-desktop.list.chroot` and the live SquashFS rootfs.
   - Created `themes/qmldir` and `qmldir` descriptors in `desktop/{dock,launcher,quick-search,control-centre,notifications,widgets}/qml/`.
   - Corrected relative `MonodeskTheme` import paths (`../../../themes` -> `../../themes`) across all 6 QML subcomponents, fixed `WidgetsContainer.qml` layout alignment, separated `NotificationCenter` top margin from telemetry cards in `MainShell.qml`, added `MonodeskIconProvider` (`image://icon/...`) with 2-arg PyQt6 signature + single-instance `fcntl` lock + `fallback_to_xfce` launching `xfce4-panel` & `xfdesktop`, and repaired `xfce4-session.xml` (`FailsafeSessionName=Failsafe`, `Count=2`).
2. **Installed-System Security & Live Credential Cleanup Fixed:**
   - Added Debian `user-setup` (`1.95`) to `01-core.list.chroot` and fixed `stage-overlay-win.py` (`write_lf`) to emit strict Unix LF endings for `/etc/live/config.conf.d/10-monodesk.conf`, allowing live sessions to run non-root as `monodesk` without root autologin drop-ins.
   - Added Calamares `shellprocess@cleanup` (`shellprocess-cleanup.conf`) cleanly stripping `/etc/systemd/system/getty@tty1.service.d`, `/etc/systemd/system/serial-getty@ttyS0.service.d`, `*/autologin.conf`, `/etc/sudoers.d/99-monodesk-live`, `/etc/sudoers.d/live`, live LightDM autologin configs, and `/etc/live/config.conf.d`, locking `root` (`passwd -l root`), and enforcing LightDM GTK greeter without autologin.

---

## 3. Complete Verification Results (All 17 Gates on Final `1.0.1` ISO)

| # | Test Gate | Method & Scope | Observed Result | Status |
|---|---|---|---|---|
| 1 | **UEFI Live Boot** | QEMU `q35` + OVMF (`4096 MB`, WHPX) booting `monodesk-os-1.0.1-universal-amd64.iso` | `BOOT_MODE: UEFI`, `/dev/loop0` squashfs + `overlayfs` mounted, `ROOT_AUTOLOGIN_IN_OVERLAY: False`, user `monodesk` (`uid=1000`) | **PASSED** |
| 2 | **Legacy BIOS Live Boot** | QEMU `q35` + SeaBIOS (`4096 MB`, WHPX) booting `monodesk-os-1.0.1-universal-amd64.iso` | `BOOT_MODE: LEGACY_BIOS`, squashfs + overlayfs mounted, 5 services (`lightdm udisks2 monodesk-profile zramswap NetworkManager`) active, `BIOS_QT6_QML_QUICK_OK` | **PASSED** |
| 3 | **MONODESK Shell Launch & Rendering** | Running `Xorg :0` + `xfwm4` in live UEFI VM (`1280x800`), inspected real framebuffer `D:\anti\shell_xorg.png` | `PyQt6.QtQml` & `QtQuick` `6.4.2`, `XWIN_SHELL: 14680078`, `[MONODESK Shell] QML root window loaded successfully.`, zero QML warnings; dark glass clock, telemetry, notification cards & dock rendered | **PASSED** |
| 4 | **XFCE Fallback** | Executed `monodesk_shell.main()` on `DISPLAY=:0` with `sys.modules['PyQt6']=None` & `sys.modules['PySide6']=None` | Printed fallback banner cleanly, returned `rc=0`, started `xfce4-panel` (`PID 1300`) and `xfdesktop` without crashing | **PASSED** |
| 5 | **Hardware Detection** | Executed `monodesk-hw-detect --report` in live UEFI VM | Reported processor (`QEMU Virtual CPU version 2.5+`), firmware (`Boot Mode: UEFI`), and adaptive recommendation (`MONODESK LITE` at 4 GiB) | **PASSED** |
| 6 | **Standard Profile (8 GiB)** | Installed system direct UEFI boot (`-m 8192`) + `monodesk-profile-ctl set standard` | `INITIAL_PROFILE_8G: Current profile: MONODESK Standard`, `/dev/zram0` `2031308` KiB | **PASSED** |
| 7 | **Lite Profile (4 GiB)** | Installed system direct UEFI reboot (`-m 4096`) + `monodesk-profile-ctl auto` & `set lite` | Recommended & activated `MONODESK Lite`, `/dev/zram0` `2001312` KiB (at `3908 MB` RAM) | **PASSED** |
| 8 | **ZRAM Behaviour** | Dynamic toggle between `standard` and `lite` at `8192 MB` RAM (`cat /proc/swaps`) | `/dev/zram0` dynamically resized between `2031308` KiB (Standard, 25%) and `4062616` KiB (Lite, 50%) with `zramswap` `active` | **PASSED** |
| 9 | **Calamares Installer UI** | Live Xvfb `:99` + `xfwm4` automated click-through of Welcome -> Location -> Keyboard -> Partition -> Users -> Summary -> Install (`cal_confirm.png`, `cal_final.png`) | Reached `All done.` screen (`13:59:01 Completion: succeeded`), zero job failures | **PASSED** |
| 10 | **Disposable-Disk Installation** | `25 GiB` `D:\anti\test-disposable-101.qcow2` partitioned by Calamares | Created GPT `vda1` (`FAT32`, `/boot/efi`), `vda2` (`ext4`), `MONODESK_OS` UEFI boot entry (`\EFI\MONODESK_OS\shimx64.efi`), ran `shellprocess@cleanup` & `bootloader` (`grub-install` exit 0) | **PASSED** |
| 11 | **Installed-System Boot** | Two independent QEMU OVMF UEFI boots of `test-disposable-101.qcow2` with NO ISO attached | Direct boot to `monodesk-vm login:` at both `8192 MB` and `4096 MB` RAM; `lightdm`, `NetworkManager`, `ufw`, `monodesk-profile`, `zramswap` all `active` | **PASSED** |
| 12 | **Non-Root User Login** | Serial console & installed OS verification as `monodesk` (`MonodeskTest2026!`) | `uid=1000(monodesk)`, `sudo -n true` failed (`rc=1`, passwordless live sudo removed), `echo ... \| sudo -S id` succeeded (`uid=0`), LightDM GTK greeter active (no autologin) | **PASSED** |
| 13 | **Root Autologin Disabled** | Inspected installed filesystem drop-ins, LightDM configs, sudoers & shadow status | `/etc/systemd/system/getty@tty1.service.d`, `serial-getty@ttyS0.service.d`, `/etc/sudoers.d/99-monodesk-live`, `/etc/sudoers.d/live`, `01-monodesk-autologin.conf`, `/etc/live/config.conf.d` all absent (`True`); `GREETER_CONFS: CLEAN_NO_ACTIVE_AUTOLOGIN`; `passwd -S root` -> `L` (`locked`); `root_autologged=False` | **PASSED** |
| 14 | **Network Services** | `systemctl is-active` & `nmcli dev status` in live + installed boots | `NetworkManager` and `ufw` `active` in both live & installed OS (see Limitations re `enp0s2` unmanaged status) | **PASSED (with note)** |
| 15 | **Application Launch** | Live `Xorg :0` + installed `Xvfb :98` GUI launch checks | Live: `monodesk-welcome`, `monodesk-recovery`, `monodesk-hardware-report` created visible X11 windows (`XWIN_APPS`); Installed: `monodesk-shell` (`QML root window loaded successfully`) & `monodesk-welcome` alive | **PASSED** |
| 16 | **Recovery Mode** | Inspected `/run/live/medium/boot/grub/grub.cfg` + launched `monodesk-recovery` | Verified `MONODESK OS 1.0 (Safe Graphics / Hardware Recovery Mode)` stanza & GTK 3 `monodesk-recovery` window launch | **PASSED** |
| 17 | **Automated Host Test Suite** | `python -m pytest -v D:\anti\monodesk-os\tests` | **35 passed in `2.90s`** (all 32 existing tests untouched + 3 new tests in `tests/unit/test_desktop_shell.py`) | **PASSED** |

---

## 4. Unverified Claims & Remaining Limitations

### Unverified (Pending Manual Physical Testing)
- **Physical Lenovo IdeaPad Slim 5:** Real-hardware UEFI boot, Wi-Fi/Bluetooth/audio/touchpad/display scaling, thermal/battery telemetry, and NVMe installation are **not yet tested** on physical hardware.
- **Physical Lenovo B590:** Real-hardware Legacy BIOS/UEFI boot, 4 GB Lite profile responsiveness, Broadcom/Realtek NICs, and SATA HDD performance are **not yet tested** on physical hardware.

### Remaining Technical Limitations Observed
1. **`NetworkManager` Wired Interface Unmanaged Status:** Both live and installed VMs show `NetworkManager` `active` and `lo:connected`, while `enp0s2` reports `ethernet:unmanaged` in `nmcli dev status` due to Debian Bookworm's default `/usr/lib/NetworkManager/conf.d/10-globally-managed-devices.conf` rule (`unmanaged-devices=*,except:type:wifi,...`). Wi-Fi interfaces remain managed by default; ethernet interfaces require an explicit `/etc/NetworkManager/conf.d/` `[keyfile] unmanaged-devices=none` override or manual `ifupdown`/`systemd-networkd` configuration when networking on wired-only hosts.
2. **Calamares Live Desktop Icon Helper:** Live `.xsession-errors` logged `add-calamares-desktop-icon: xdg-user-dir: not found` because `xdg-user-dirs` is not preinstalled in the minimal squashfs; Calamares itself launches and completes installation cleanly when invoked directly or from the application launcher/terminal.
3. **AppArmor Service in Live QEMU Kernel:** `systemctl is-active apparmor` reported `inactive` during the QEMU live VM run because `apparmor=1 security=apparmor` is not enabled by default on the live kernel command line.
4. **Virtual Display Driver Scope:** Xorg rendering and screenshots were validated under QEMU virtual display/Xvfb (`1280x800`); hardware-specific Intel i915, AMD amdgpu, and NVIDIA DKMS modesetting require physical machine validation.
5. **QEMU SquashFS Re-mastering Host:** Because WSL2 (`WSL_E_DISK_CORRUPTED`) was unavailable on the Windows build host, `v1.0.1` squashfs construction ran cleanly inside an ephemeral Debian 12 QEMU builder VM (`zstd` compression level 9) rather than native Linux `live-build`.

---

## 5. Preserved Release Inventory

| Version | Tag | Artifact Filename | Size (Bytes) | SHA-256 | Status |
|---|---|---|---|---|---|
| `1.0.0` | `v1.0.0` | `monodesk-os-1.0.0-universal-amd64.iso` | `419,575,808` | `9779da035e735351cbb4932fab4679ef98661d3d9dd0d8a10c5d25f6198e5371` | Preserved on GitHub & Disk D |
| `1.0.1-rc1` | — | `monodesk-os-1.0.1-rc1-universal-amd64.iso` | `687,063,040` | `eb5dbb19c4cf83efe30f5196bf563e8eaeb8d344e373e1f7cef98be4fe103b37` | Preserved locally in `releases/` |
| **`1.0.1`** | **`v1.0.1`** | **`monodesk-os-1.0.1-universal-amd64.iso`** | **`766,408,704`** | **`3b8ad75a7f3d011d591d30b42efbb48d7edb53a316a642d7ea8465105c219776`** | **Current Production Release** |
