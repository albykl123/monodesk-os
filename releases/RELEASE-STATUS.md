# MONODESK OS — Release Status & Validation Summary

**Published Release:** `v1.0.0` (`monodesk-os-1.0.0-universal-amd64.iso`, preserved intact on GitHub Releases and Disk D)  
**Validation Candidate:** `v1.0.1-rc1` (`monodesk-os-1.0.1-rc1-universal-amd64.iso`, local defect-fix candidate)  
**Base Distribution:** Debian GNU/Linux 12 (Bookworm) AMD64 (`6.1.0-54-amd64`)  
**Source Tag / Commit:** `v1.0.0` (`ae5c52b8c18b75b91ed51718b11dc1df5a79aaeb` -> `af12f8bed5a590e63b3dfb7003934b51a43b4470`)  
**Validation Date:** 2026-11-12  

---

## Release Gate Comparison (`v1.0.0` Published vs `v1.0.1-rc1` Candidate)

| Check / Gate | `v1.0.0` (Published, Preserved) | `v1.0.1-rc1` (Local Candidate) | Evidence / Notes |
| :--- | :--- | :--- | :--- |
| **Single Unsplit ISO < 2 GiB** | **PASSED** (`419,575,808` B / `400.14 MiB`) | **PASSED** (`687,063,040` B / `655.23 MiB`) | Verified across Disk D paths (`v1.0.0`) & `releases/` |
| **GitHub Download SHA-256 Match** | **PASSED** (`9779da03...`) | N/A (local RC1 only) | Downloaded `gh release download` matched local ISO |
| **GitHub Release Asset Completeness** | **PARTIAL** (2 of 7 local assets) | N/A | Only `.iso` and `.iso.sha256` on GitHub `v1.0.0` |
| **QEMU UEFI Live Boot (`q35` + OVMF)** | **PASSED** | **PASSED** | Live `squashfs` + `overlayfs` booted cleanly |
| **Legacy BIOS Boot (QEMU SeaBIOS)** | **FAILED** (`no boot info`) | **PASSED** (`BOOT_MODE=LEGACY_BIOS`) | Fixed via 159,675 B `cdboot_eltorito.img` + `boot_info_table=True` |
| **Calamares Installer Execution** | **FAILED** (`calamares` missing) | **PASSED** (`25 GiB` qcow2 GPT + EFI + ext4) | Verified end-to-end GUI install onto `test-disposable-install.qcow2` |
| **Installed System Boot (No ISO)** | **FAILED** (not installable) | **PASSED** (UEFI boot from `/dev/vda2`) | `/etc/fstab`, user `monodesk`, `lightdm`, `monodesk-profile` verified |
| **GUI Stack (Xorg/XFCE4/LightDM)** | **FAILED** (CLI base only) | **PASSED** (`lightdm` + `Xorg :0` active) | `GTK3_GI_OK` verified; `PyQt6.QtQml` still absent (graceful fallback) |
| **Standard & Lite Profile Switching** | **PARTIAL** (CTL + `profile.conf` only) | **PASSED** (4 GB->Lite / 8 GB->Standard) | Verified `zram0` (`1.9G` <-> `977.2M`) and `powerprofilesctl` |
| **Host Python Unit Test Suite** | **PASSED** (32 tests) | **PASSED** (32 tests in `1.65s`) | `pytest -v` on `D:\anti\monodesk-os\tests` |
| **Physical Lenovo Slim 5 & B590** | **UNVERIFIED** | **UNVERIFIED** | Pending manual physical hardware testing |

See [FINAL-VALIDATION-REPORT.md](FINAL-VALIDATION-REPORT.md) for the complete breakdown of Verified Results, Unverified Claims, Source Reconciliation against `af12f8b`, Failures & Fixes, and Remaining Limitations.
