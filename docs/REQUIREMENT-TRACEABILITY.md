# MONODESK OS 1.0 — Requirement Traceability Matrix (RTM)

| Req ID | Requirement Description | Source Implementation | Test / Verification Method | Status |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-01** | Original brand identity, monochrome dot-matrix aesthetic | `branding/`, `branding/assets/monodesk-logo.svg`, `branding/wallpapers/` | Visual asset check, license compliance | **VERIFIED** |
| **REQ-02** | Universal x86-64 CPU support (Intel & AMD) | `build/live-build/config/package-lists/core.list.chroot` | Microcode verification, kernel package check | **VERIFIED** |
| **REQ-03** | Graphics stack (Intel, AMD, NVIDIA Nouveau default + proprietary script) | `system/drivers/graphics.conf`, `applications/monodesk-nvidia-installer` | Mesa driver check, driver script test | **VERIFIED** |
| **REQ-04** | Base OS: Debian 12 (Bookworm) stable, systemd, APT | `build/live-build/auto/config` | Repository pinning & GPG verification | **VERIFIED** |
| **REQ-05** | Desktop Shell: Desktop-first, bottom taskbar, dot-matrix clock | `desktop/shell/`, `desktop/taskbar/xfce4-panel.xml` | XFCE panel config validation | **VERIFIED** |
| **REQ-06** | Desktop Widgets: Lightweight CPU, RAM, disk, battery | `desktop/widgets/monodesk_widget.py` | Unit tests (`test_applications.py`) | **VERIFIED** |
| **REQ-07** | Application Launcher: Search, categories, keyboard nav | `desktop/launcher/`, XFCE Whisker menu config | Desktop entry validation | **VERIFIED** |
| **REQ-08** | Control Centre: Wi-Fi, Ethernet, Bluetooth, Audio, Brightness, Power | `applications/control-centre/monodesk_control_centre.py` | Unit tests (`test_applications.py`) | **VERIFIED** |
| **REQ-09** | Appearance System: Dark, Light, auto-switch, dot-matrix themes | `desktop/appearance/`, `applications/settings/monodesk_appearance.py` | Theme switch validation test | **VERIFIED** |
| **REQ-10** | System Applications: Welcome onboarding | `applications/welcome/monodesk_welcome.py` | GTK app launch unit test | **VERIFIED** |
| **REQ-11** | System Applications: Hardware Diagnostic Report with redaction | `applications/hardware-report/monodesk_hardware_report.py` | Hardware scanner test & redaction check | **VERIFIED** |
| **REQ-12** | System Applications: System Monitor (CPU, RAM, processes) | `applications/system-monitor/monodesk_system_monitor.py` | Process sampling test | **VERIFIED** |
| **REQ-13** | System Applications: Update Manager & Software Manager | `applications/update-manager/monodesk_update_manager.py`, `applications/software-manager/` | APT wrapper verification test | **VERIFIED** |
| **REQ-14** | Performance Profiles: MONODESK Lite (4GB) vs. Standard (8GB+) | `system/power/monodesk-profile-ctl`, `system/configuration/zram.conf` | Profile toggling CLI test | **VERIFIED** |
| **REQ-15** | Security & Privacy: UFW firewall, AppArmor, no telemetry, least privilege | `system/security/ufw.rules`, `system/security/privacy.conf` | Security audit check | **VERIFIED** |
| **REQ-16** | Graphical Installer: Calamares, EFI + BIOS, partitioning, LUKS | `build/live-build/config/includes.chroot/etc/calamares/` | Calamares configuration validation | **VERIFIED** |
| **REQ-17** | ISO Build System: Debian live-build, hybrid UEFI/BIOS, xorriso | `scripts/build-iso.sh`, `build/live-build/auto/config` | Build script syntax & pipeline check | **VERIFIED** |
| **REQ-18** | Automated Quality Assurance: Unit tests, lint, VM boot script | `tests/unit/`, `scripts/check-source.sh`, `scripts/test-iso.sh` | Pytest and syntax linter suite | **VERIFIED** |
| **REQ-19** | Documentation: Installation, Hardware Matrix, Security, Licenses, Audit | `docs/` (complete markdown suite) | Markdown documentation validation | **VERIFIED** |
| **REQ-20** | Universal PC Release artifacts: Manifests, Checksums, Release Notes | `scripts/generate-manifest.sh`, `docs/RELEASE-NOTES.md` | Manifest script and checksum harness | **VERIFIED** |
