import os
import shutil
import pathlib

repo = pathlib.Path(r'F:\anti\monodesk-os')
overlay = pathlib.Path(r'F:\anti\iso_staging\monodesk\rootfs_overlay')

if overlay.exists():
    shutil.rmtree(overlay)

dirs = [
    overlay / 'usr/bin',
    overlay / 'usr/share/applications',
    overlay / 'usr/share/backgrounds/monodesk',
    overlay / 'usr/share/icons/hicolor/scalable/apps',
    overlay / 'usr/share/themes/Monodesk-Dark/gtk-3.0',
    overlay / 'usr/share/themes/Monodesk-Light/gtk-3.0',
    overlay / 'usr/share/themes/Monodesk-Dark/xfwm4',
    overlay / 'usr/share/monodesk/shell',
    overlay / 'usr/share/monodesk/themes',
    overlay / 'etc/monodesk',
    overlay / 'etc/systemd/user',
    overlay / 'etc/systemd/system',
    overlay / 'etc/calamares',
]
for d in dirs:
    d.mkdir(parents=True, exist_ok=True)

# Branding
for f in (repo / 'branding/assets').glob('*.svg'):
    shutil.copy2(f, overlay / 'usr/share/icons/hicolor/scalable/apps' / f.name)
for f in (repo / 'branding/wallpapers').glob('*.svg'):
    shutil.copy2(f, overlay / 'usr/share/backgrounds/monodesk' / f.name)

# Themes
shutil.copy2(repo / 'desktop/appearance/gtk-3.0/gtk.css', overlay / 'usr/share/themes/Monodesk-Dark/gtk-3.0/gtk.css')
shutil.copy2(repo / 'desktop/appearance/gtk-3.0-light/gtk.css', overlay / 'usr/share/themes/Monodesk-Light/gtk-3.0/gtk.css')
shutil.copy2(repo / 'desktop/appearance/xfwm4/themerc', overlay / 'usr/share/themes/Monodesk-Dark/xfwm4/themerc')

# Shell & Themes
shutil.copytree(repo / 'desktop/shell', overlay / 'usr/share/monodesk/shell', dirs_exist_ok=True)
shutil.copytree(repo / 'themes', overlay / 'usr/share/monodesk/themes', dirs_exist_ok=True)
shutil.copy2(repo / 'desktop/shell/monodesk_shell.py', overlay / 'usr/bin/monodesk-shell')

# System scripts
shutil.copy2(repo / 'system/power/monodesk-profile-ctl', overlay / 'usr/bin/monodesk-profile-ctl')
shutil.copy2(repo / 'system/hardware/monodesk-hw-detect', overlay / 'usr/bin/monodesk-hw-detect')
shutil.copy2(repo / 'services/monodesk-shell.service', overlay / 'etc/systemd/user/monodesk-shell.service')
shutil.copy2(repo / 'services/monodesk-profile.service', overlay / 'etc/systemd/system/monodesk-profile.service')

# Calamares
calamares_src = repo / 'build/live-build/config/includes.chroot/etc/calamares'
if calamares_src.exists():
    shutil.copytree(calamares_src, overlay / 'etc/calamares', dirs_exist_ok=True)

# Applications
apps = [
    ('welcome', 'monodesk_welcome.py', 'monodesk-welcome'),
    ('control-centre', 'monodesk_control_centre.py', 'monodesk-control-centre'),
    ('hardware-report', 'monodesk_hardware_report.py', 'monodesk-hardware-report'),
    ('system-monitor', 'monodesk_system_monitor.py', 'monodesk-system-monitor'),
    ('settings', 'monodesk_settings.py', 'monodesk-settings'),
    ('update-manager', 'monodesk_update_manager.py', 'monodesk-update-manager'),
    ('software-manager', 'monodesk_software_manager.py', 'monodesk-software-manager'),
    ('privacy', 'monodesk_privacy.py', 'monodesk-privacy'),
    ('backup', 'monodesk_backup.py', 'monodesk-backup'),
    ('recovery', 'monodesk_recovery.py', 'monodesk-recovery'),
    ('workspace', 'monodesk_workspace.py', 'monodesk-workspace'),
    ('ai-assistant', 'monodesk_ai.py', 'monodesk-ai'),
    ('accounts', 'monodesk_accounts.py', 'monodesk-accounts'),
    ('disk-manager', 'monodesk_disk_manager.py', 'monodesk-disk-manager'),
    ('device-manager', 'monodesk_device_manager.py', 'monodesk-device-manager'),
    ('network-centre', 'monodesk_network_centre.py', 'monodesk-network-centre'),
    ('bluetooth-centre', 'monodesk_bluetooth_centre.py', 'monodesk-bluetooth-centre'),
    ('print-centre', 'monodesk_print_centre.py', 'monodesk-print-centre'),
    ('clipboard', 'monodesk_clipboard.py', 'monodesk-clipboard'),
    ('accessibility', 'monodesk_accessibility.py', 'monodesk-accessibility'),
    ('compatibility', 'monodesk_compatibility.py', 'monodesk-compatibility'),
    ('gaming', 'monodesk_gaming.py', 'monodesk-gaming'),
    ('developer-centre', 'monodesk_developer.py', 'monodesk-developer'),
]

for app_dir, py_name, bin_name in apps:
    p = repo / 'applications' / app_dir / py_name
    if p.exists():
        shutil.copy2(p, overlay / 'usr/bin' / bin_name)
    for d in (repo / 'applications' / app_dir).glob('*.desktop'):
        shutil.copy2(d, overlay / 'usr/share/applications' / d.name)

# Compatibility aliases
for alias, target in [('monodesk-hardware-centre', 'monodesk-hardware-report'),
                      ('monodesk-updater', 'monodesk-update-manager'),
                      ('monodesk-store', 'monodesk-software-manager')]:
    src = overlay / 'usr/bin' / target
    if src.exists():
        shutil.copy2(src, overlay / 'usr/bin' / alias)

nvidia_sh = repo / 'applications/nvidia-installer/monodesk-nvidia-installer.sh'
if nvidia_sh.exists():
    shutil.copy2(nvidia_sh, overlay / 'usr/bin/monodesk-nvidia-installer')
for d in (repo / 'applications/nvidia-installer').glob('*.desktop'):
    shutil.copy2(d, overlay / 'usr/share/applications' / d.name)

# OS identity files and live runtime fstab
(overlay / 'etc/issue').write_text("MONODESK OS 1.0 (Universal PC Edition) \\n \\l\n", encoding='utf-8')
(overlay / 'etc/hostname').write_text("monodesk-pc\n", encoding='utf-8')
(overlay / 'etc/fstab').write_text(
    "overlay / overlay rw 0 0\n"
    "tmpfs /tmp tmpfs nosuid,nodev 0 0\n",
    encoding='utf-8'
)
(overlay / 'etc/os-release').write_text(
    'PRETTY_NAME="MONODESK OS 1.0 (Universal PC Edition)"\n'
    'NAME="MONODESK OS"\n'
    'VERSION_ID="1.0.0"\n'
    'VERSION="1.0.0 (Universal PC Edition)"\n'
    'VERSION_CODENAME=bookworm\n'
    'ID=monodesk\n'
    'ID_LIKE=debian\n'
    'HOME_URL="https://github.com/albykl123/monodesk-os"\n',
    encoding='utf-8'
)

# Live session console autologin
getty_dir = overlay / 'etc/systemd/system/getty@tty1.service.d'
getty_dir.mkdir(parents=True, exist_ok=True)
(getty_dir / 'autologin.conf').write_text(
    "[Service]\n"
    "ExecStart=\n"
    "ExecStart=-/sbin/agetty --autologin root --noclear %I $TERM\n",
    encoding='utf-8'
)

serial_getty_dir = overlay / 'etc/systemd/system/serial-getty@ttyS0.service.d'
serial_getty_dir.mkdir(parents=True, exist_ok=True)
(serial_getty_dir / 'autologin.conf').write_text(
    "[Service]\n"
    "ExecStart=\n"
    "ExecStart=-/sbin/agetty --autologin root --keep-baud 115200,57600,38400,9600 %I $TERM\n",
    encoding='utf-8'
)

# Documentation copy into /monodesk/docs
doc_dst = pathlib.Path(r'F:\anti\iso_staging\monodesk\docs')
doc_dst.mkdir(parents=True, exist_ok=True)
for doc_file in (repo / 'docs').glob('*.md'):
    shutil.copy2(doc_file, doc_dst / doc_file.name)

count = sum(1 for _ in overlay.rglob('*') if _.is_file())
print(f'Successfully staged rootfs_overlay! Total files: {count}')
