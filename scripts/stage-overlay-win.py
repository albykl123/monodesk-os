import argparse
import os
import shutil
import pathlib

parser = argparse.ArgumentParser(description="Stage MONODESK OS rootfs_overlay onto Disk D staging directory")
parser.add_argument("--staging", default=r"D:\anti\iso_staging", help="Staging root directory")
args = parser.parse_args()

repo = pathlib.Path(r'D:\anti\monodesk-os')
staging_root = pathlib.Path(args.staging)
overlay = staging_root / 'monodesk' / 'rootfs_overlay'

def write_lf(path: pathlib.Path, content: str) -> None:
    """Write UTF-8 text with strict Unix LF line endings (even when executed on Windows)."""
    path.write_bytes(content.replace('\r\n', '\n').encode('utf-8'))

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
    overlay / 'usr/share/monodesk/dock',
    overlay / 'usr/share/monodesk/launcher',
    overlay / 'usr/share/monodesk/quick-search',
    overlay / 'usr/share/monodesk/control-centre',
    overlay / 'usr/share/monodesk/notifications',
    overlay / 'usr/share/monodesk/widgets',
    overlay / 'usr/share/monodesk/taskbar',
    overlay / 'usr/share/monodesk/themes',
    overlay / 'etc/monodesk',
    overlay / 'etc/live/config.conf.d',
    overlay / 'etc/systemd/user',
    overlay / 'etc/systemd/system',
    overlay / 'etc/calamares',
    overlay / 'etc/xdg/autostart',
    overlay / 'etc/xdg/xfce4/xfconf/xfce-perchannel-xml',
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

# Shell, QML Modules & Themes
for comp in ('shell', 'dock', 'launcher', 'quick-search', 'control-centre', 'notifications', 'widgets', 'taskbar'):
    shutil.copytree(repo / 'desktop' / comp, overlay / 'usr/share/monodesk' / comp, dirs_exist_ok=True)
shutil.copytree(repo / 'themes', overlay / 'usr/share/monodesk/themes', dirs_exist_ok=True)
shutil.copy2(repo / 'desktop/shell/monodesk_shell.py', overlay / 'usr/bin/monodesk-shell')

# Graphical session autostart & XFCE config
write_lf(overlay / 'etc/xdg/autostart/monodesk-shell.desktop',
    "[Desktop Entry]\n"
    "Type=Application\n"
    "Name=MONODESK Desktop Shell\n"
    "Comment=The Monochrome Computing Experience Desktop Shell\n"
    "Exec=/usr/bin/monodesk-shell\n"
    "OnlyShowIn=XFCE;\n"
    "Terminal=false\n"
    "StartupNotify=false\n"
    "X-XFCE-Autostart-Override=true\n"
)
write_lf(overlay / 'etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-session.xml',
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<channel name="xfce4-session" version="1.0">\n'
    '  <property name="general" type="empty">\n'
    '    <property name="FailsafeSessionName" type="string" value="Failsafe"/>\n'
    '  </property>\n'
    '  <property name="sessions" type="empty">\n'
    '    <property name="Failsafe" type="empty">\n'
    '      <property name="IsFailsafe" type="bool" value="true"/>\n'
    '      <property name="Count" type="int" value="2"/>\n'
    '      <property name="Client0_Command" type="array">\n'
    '        <value type="string" value="xfwm4"/>\n'
    '      </property>\n'
    '      <property name="Client0_PerScreen" type="bool" value="false"/>\n'
    '      <property name="Client1_Command" type="array">\n'
    '        <value type="string" value="xfsettingsd"/>\n'
    '      </property>\n'
    '      <property name="Client1_PerScreen" type="bool" value="false"/>\n'
    '    </property>\n'
    '  </property>\n'
    '</channel>\n'
)

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
write_lf(overlay / 'etc/issue', "MONODESK OS 1.0.1 (Universal PC Edition) \\n \\l\n")
write_lf(overlay / 'etc/hostname', "monodesk-pc\n")
write_lf(overlay / 'etc/fstab',
    "overlay / overlay rw 0 0\n"
    "tmpfs /tmp tmpfs nosuid,nodev 0 0\n"
)
write_lf(overlay / 'etc/os-release',
    'PRETTY_NAME="MONODESK OS 1.0.1 (Universal PC Edition)"\n'
    'NAME="MONODESK OS"\n'
    'VERSION_ID="1.0.1"\n'
    'VERSION="1.0.1 (Universal PC Edition)"\n'
    'VERSION_CODENAME=bookworm\n'
    'ID=monodesk\n'
    'ID_LIKE=debian\n'
    'HOME_URL="https://github.com/albykl123/monodesk-os"\n'
)

# Live-only non-root user configuration (used strictly by live-config during boot=live; never installed by unpackfs)
write_lf(overlay / 'etc/live/config.conf.d/10-monodesk.conf',
    'LIVE_HOSTNAME="monodesk-pc"\n'
    'LIVE_USERNAME="monodesk"\n'
    'LIVE_USER_FULLNAME="MONODESK Live User"\n'
    'LIVE_USER_DEFAULT_GROUPS="audio cdrom dip floppy video plugdev netdev powerdev scanner bluetooth sudo"\n'
)

# Documentation copy into /monodesk/docs
doc_dst = staging_root / 'monodesk' / 'docs'
doc_dst.mkdir(parents=True, exist_ok=True)
for doc_file in (repo / 'docs').glob('*.md'):
    shutil.copy2(doc_file, doc_dst / doc_file.name)

count = sum(1 for _ in overlay.rglob('*') if _.is_file())
print(f'Successfully staged rootfs_overlay at {overlay}! Total files: {count}')
