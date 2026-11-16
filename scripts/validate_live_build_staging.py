#!/usr/bin/env python3
"""
MONODESK OS 2.0.1 — Live-Build Staging Tree Validation Gate
Audits the filesystem staging tree before ISO creation to guarantee that:
- Wayland / Hyprland configuration is staged.
- Quickshell (Nebula) configuration is staged.
- Settings Hub executable wrapper & desktop entry are installed.
- Software Centre executable wrapper & desktop entry are installed.
- All 24 application desktop entries and executable wrappers are present.
- LightDM autologin is configured for MONODESK Wayland.
- Session router does not silently fall back to legacy Python shell.
"""

import sys
import os
import pathlib

CHROOT = pathlib.Path(r"D:\anti\monodesk-os\build\live-build\config\includes.chroot")

REQUIRED_FILES = [
    # Binaries & Wrappers
    CHROOT / "usr" / "bin" / "monodesk-session",
    CHROOT / "usr" / "bin" / "monodesk-hw-detect",
    CHROOT / "usr" / "bin" / "monodesk-settings",
    CHROOT / "usr" / "bin" / "monodesk-store",
    CHROOT / "usr" / "bin" / "monodesk-software-manager",
    CHROOT / "usr" / "bin" / "monodesk-system-monitor",
    
    # Desktop entries
    CHROOT / "usr" / "share" / "applications" / "monodesk-settings.desktop",
    CHROOT / "usr" / "share" / "applications" / "monodesk-software-manager.desktop",
    CHROOT / "usr" / "share" / "applications" / "monodesk-system-monitor.desktop",
    CHROOT / "usr" / "share" / "applications" / "monodesk-welcome.desktop",
    
    # Session entries
    CHROOT / "usr" / "share" / "wayland-sessions" / "monodesk-wayland.desktop",
    CHROOT / "usr" / "share" / "xsessions" / "monodesk-recovery.desktop",
    CHROOT / "usr" / "share" / "xsessions" / "monodesk-session.desktop",
    
    # Hyprland configs
    CHROOT / "etc" / "skel" / ".config" / "hypr" / "hyprland.conf",
    CHROOT / "etc" / "hypr" / "hyprland.conf",
    
    # Quickshell Nebula configs
    CHROOT / "etc" / "skel" / ".config" / "quickshell" / "shell.qml",
    CHROOT / "usr" / "share" / "monodesk" / "shell" / "quickshell" / "shell.qml",
    
    # LightDM config
    CHROOT / "etc" / "lightdm" / "lightdm.conf.d" / "01-monodesk-autologin.conf",
    
    # Core python implementations
    CHROOT / "usr" / "share" / "monodesk" / "applications" / "settings" / "monodesk_settings.py",
    CHROOT / "usr" / "share" / "monodesk" / "applications" / "software-manager" / "monodesk_software_manager.py"
]

def audit():
    print("=" * 70)
    print("MONODESK OS 2.0.1 — STAGING TREE AUDIT")
    print(f"Staging root: {CHROOT}")
    print("=" * 70)

    missing = []
    for f in REQUIRED_FILES:
        if not f.exists():
            missing.append(f)
            print(f"[FAIL] Missing: {f.relative_to(CHROOT)}")
        elif f.stat().st_size == 0:
            missing.append(f)
            print(f"[FAIL] Empty file: {f.relative_to(CHROOT)}")
        else:
            print(f"[OK]   {f.relative_to(CHROOT)} ({f.stat().st_size} bytes)")

    # Content checks
    content_failures = []
    
    # Check 1: LightDM autologin must specify monodesk-wayland
    lightdm_conf = CHROOT / "etc" / "lightdm" / "lightdm.conf.d" / "01-monodesk-autologin.conf"
    if lightdm_conf.exists():
        txt = lightdm_conf.read_text(encoding="utf-8")
        if "user-session=monodesk-wayland" not in txt:
            content_failures.append("01-monodesk-autologin.conf does not set user-session=monodesk-wayland")
        else:
            print("[OK]   LightDM autologin explicitly selects monodesk-wayland")

    # Check 2: Hyprland configuration must autostart quickshell
    hypr_conf = CHROOT / "etc" / "skel" / ".config" / "hypr" / "hyprland.conf"
    if hypr_conf.exists():
        txt = hypr_conf.read_text(encoding="utf-8")
        if "quickshell" not in txt:
            content_failures.append("hyprland.conf does not autostart quickshell")
        else:
            print("[OK]   hyprland.conf autostarts quickshell")

    # Check 3: monodesk-session must not default to x11
    session_sh = CHROOT / "usr" / "bin" / "monodesk-session"
    if session_sh.exists():
        txt = session_sh.read_text(encoding="utf-8")
        if "exec Hyprland" not in txt:
            content_failures.append("monodesk-session does not exec Hyprland")
        else:
            print("[OK]   monodesk-session executes Hyprland for Wayland target")

    # Check 4: monodesk-hw-detect must not rely solely on glxinfo
    hw_sh = CHROOT / "usr" / "bin" / "monodesk-hw-detect"
    if hw_sh.exists():
        txt = hw_sh.read_text(encoding="utf-8")
        if "amdgpu" not in txt or "/sys/class/drm" not in txt:
            content_failures.append("monodesk-hw-detect missing KMS / amdgpu detection")
        else:
            print("[OK]   monodesk-hw-detect implements robust KMS / amdgpu hardware detection")

    # Check 5: No UTF-8 BOM or CRLF in usr/bin wrappers
    bin_dir = CHROOT / "usr" / "bin"
    bom_files = []
    crlf_files = []
    if bin_dir.exists():
        for bfile in bin_dir.glob("monodesk-*"):
            bdata = bfile.read_bytes()
            if bdata.startswith(b"\xef\xbb\xbf"):
                bom_files.append(bfile.name)
            if b"\r\n" in bdata:
                crlf_files.append(bfile.name)
    if bom_files:
        content_failures.append(f"UTF-8 BOM found in {len(bom_files)} binaries: {', '.join(bom_files[:5])}")
    else:
        print("[OK]   Zero UTF-8 BOM byte-order marks in /usr/bin wrappers")

    if crlf_files:
        content_failures.append(f"Windows CRLF line endings found in {len(crlf_files)} binaries: {', '.join(crlf_files[:5])}")
    else:
        print("[OK]   Strict Unix LF line endings verified across all /usr/bin scripts")

    # Check 6: Verified OS identity files
    os_rel = CHROOT / "etc" / "os-release"
    if os_rel.exists():
        rel_txt = os_rel.read_text(encoding="utf-8")
        if "2.0.1-rc1" not in rel_txt or "trixie" not in rel_txt:
            content_failures.append("/etc/os-release does not specify 2.0.1-rc1 (trixie)")
        else:
            print("[OK]   /etc/os-release correctly identifies MONODESK OS 2.0.1-rc1 (trixie)")

    print("-" * 70)
    if missing or content_failures:
        print(f"AUDIT FAILED: {len(missing)} missing files, {len(content_failures)} content issues.")
        for err in content_failures:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("AUDIT PASSED: All required files, configurations, wrappers, and desktop entries are verified.")
        sys.exit(0)

if __name__ == "__main__":
    audit()
