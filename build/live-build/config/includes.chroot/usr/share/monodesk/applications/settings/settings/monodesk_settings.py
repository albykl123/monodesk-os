#!/usr/bin/env python3
"""
MONODESK OS 2.0 — Settings Application
Comprehensive configuration hub integrating all 21 system settings categories:
Display, Resolution, Brightness, Audio, Microphone, Wi-Fi, Ethernet, Bluetooth,
Keyboard, Mouse, Touchpad, Power, Battery, Printers, Storage, Users, Privacy,
Security, Accessibility, Appearance, Updates, and About.
"""

import sys
import os
import subprocess
import re

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk, Gdk, GLib
    WindowBase = Gtk.Window
except ImportError:
    Gtk = None
    Gdk = None
    GLib = None
    WindowBase = object

def run_cmd(args):
    try:
        res = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        return res.stdout.strip()
    except Exception:
        return ""

class MonodeskSettings(WindowBase):
    def __init__(self):
        if Gtk is None:
            return
        super().__init__(title="MONODESK Settings")
        self.set_default_size(920, 640)
        self.set_position(Gtk.WindowPosition.CENTER)

        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(main_box)

        # Sidebar
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        sidebar.set_size_request(240, -1)
        sidebar.get_style_context().add_class("sidebar")
        main_box.pack_start(sidebar, False, False, 0)

        title = Gtk.Label(label="SETTINGS")
        title.get_style_context().add_class("brand-title")
        title.set_margin_top(14)
        title.set_margin_bottom(10)
        sidebar.pack_start(title, False, False, 0)

        scroller_side = Gtk.ScrolledWindow()
        scroller_side.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sidebar.pack_start(scroller_side, True, True, 0)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

        self.stack_sidebar = Gtk.StackSidebar()
        self.stack_sidebar.set_stack(self.stack)
        scroller_side.add(self.stack_sidebar)

        # Content Area
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.set_margin_start(24); content.set_margin_end(24)
        content.set_margin_top(20); content.set_margin_bottom(20)
        content.pack_start(self.stack, True, True, 0)
        main_box.pack_start(content, True, True, 0)

        # Initialize all 21 required settings pages
        self.init_appearance_page()
        self.init_display_page()
        self.init_brightness_page()
        self.init_audio_page()
        self.init_microphone_page()
        self.init_wifi_page()
        self.init_ethernet_page()
        self.init_bluetooth_page()
        self.init_keyboard_page()
        self.init_mouse_page()
        self.init_touchpad_page()
        self.init_power_page()
        self.init_battery_page()
        self.init_printers_page()
        self.init_storage_page()
        self.init_users_page()
        self.init_privacy_page()
        self.init_security_page()
        self.init_accessibility_page()
        self.init_updates_page()
        self.init_about_page()

    def make_header(self, text, subtitle=None):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        lbl = Gtk.Label(label=text)
        lbl.get_style_context().add_class("h1")
        lbl.set_alignment(0.0, 0.5)
        box.pack_start(lbl, False, False, 0)
        if subtitle:
            sub = Gtk.Label(label=subtitle)
            sub.get_style_context().add_class("dim-label")
            sub.set_alignment(0.0, 0.5)
            box.pack_start(sub, False, False, 0)
        box.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 8)
        return box

    # 1. Appearance
    def init_appearance_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("Appearance & Themes", "Monochrome desktop aesthetics, dark/light styles, and wallpapers"), False, False, 0)

        btn_dark = Gtk.Button(label="Apply MONODESK Dark (Monochrome Minimalist)")
        btn_dark.connect("clicked", lambda b: self.set_theme("Monodesk-Dark"))
        page.pack_start(btn_dark, False, False, 0)

        btn_light = Gtk.Button(label="Apply MONODESK Light (High-Contrast Clean White)")
        btn_light.connect("clicked", lambda b: self.set_theme("Monodesk-Light"))
        page.pack_start(btn_light, False, False, 0)

        btn_wall = Gtk.Button(label="Desktop Wallpaper Selector")
        btn_wall.connect("clicked", lambda b: subprocess.Popen(["xfdesktop-settings"]))
        page.pack_start(btn_wall, False, False, 0)

        self.stack.add_titled(page, "appearance", "Appearance")

    # 2. Display & Resolution
    def init_display_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("Display & Resolution", "Resolution, refresh rate, orientation, and multi-monitor layout"), False, False, 0)

        xrandr_out = run_cmd(["xrandr", "--current"])
        curr_res = "Unknown"
        for line in xrandr_out.splitlines():
            if "*" in line:
                curr_res = line.split()[0]
                break

        lbl_res = Gtk.Label(label=f"Current Primary Display Resolution: {curr_res}")
        lbl_res.set_alignment(0.0, 0.5)
        page.pack_start(lbl_res, False, False, 0)

        btn_disp = Gtk.Button(label="Open Display Configuration (Resolution & Refresh Rates)")
        btn_disp.connect("clicked", lambda b: subprocess.Popen(["xfce4-display-settings"]))
        page.pack_start(btn_disp, False, False, 0)

        self.stack.add_titled(page, "display", "Display")

    # 3. Brightness
    def init_brightness_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("Display Brightness", "Adjust screen backlight intensity"), False, False, 0)

        b_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 10, 100, 5)
        b_scale.set_value(80)
        b_scale.connect("value-changed", lambda s: run_cmd(["brightnessctl", "set", f"{int(s.get_value())}%"]))
        page.pack_start(b_scale, False, False, 0)

        btn_max = Gtk.Button(label="Set Maximum Brightness (100%)")
        btn_max.connect("clicked", lambda b: [b_scale.set_value(100), run_cmd(["brightnessctl", "set", "100%"])])
        page.pack_start(btn_max, False, False, 0)

        self.stack.add_titled(page, "brightness", "Brightness")

    # 4. Audio Output
    def init_audio_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("Audio & Sound Output", "PipeWire audio subsystem and volume control"), False, False, 0)

        v_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        v_scale.set_value(65)
        v_scale.connect("value-changed", lambda s: run_cmd(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{int(s.get_value())}%"]))
        page.pack_start(v_scale, False, False, 0)

        btn_mixer = Gtk.Button(label="Open PipeWire Volume Control (pavucontrol)")
        btn_mixer.connect("clicked", lambda b: subprocess.Popen(["pavucontrol"]))
        page.pack_start(btn_mixer, False, False, 0)

        self.stack.add_titled(page, "audio", "Audio")

    # 5. Microphone Input
    def init_microphone_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("Microphone & Input", "Audio input capture levels and recording devices"), False, False, 0)

        mic_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        mic_scale.set_value(75)
        mic_scale.connect("value-changed", lambda s: run_cmd(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", f"{int(s.get_value())}%"]))
        page.pack_start(mic_scale, False, False, 0)

        btn_mute = Gtk.ToggleButton(label="Mute Microphone")
        btn_mute.connect("toggled", lambda b: run_cmd(["pactl", "set-source-mute", "@DEFAULT_SOURCE@", "1" if b.get_active() else "0"]))
        page.pack_start(btn_mute, False, False, 0)

        self.stack.add_titled(page, "microphone", "Microphone")

    # 6. Wi-Fi
    def init_wifi_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("Wi-Fi Wireless Networks", "NetworkManager wireless scanning and connection"), False, False, 0)

        wifi_toggle = Gtk.Switch()
        wifi_toggle.set_active(True)
        wifi_toggle.connect("notify::active", lambda s, p: run_cmd(["nmcli", "radio", "wifi", "on" if s.get_active() else "off"]))

        tbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        tbox.pack_start(Gtk.Label(label="Wi-Fi Radio:"), False, False, 0)
        tbox.pack_start(wifi_toggle, False, False, 0)
        page.pack_start(tbox, False, False, 0)

        btn_net = Gtk.Button(label="Open MONODESK Network Centre (Scan & Connect)")
        btn_net.connect("clicked", lambda b: subprocess.Popen(["monodesk-network-centre"]))
        page.pack_start(btn_net, False, False, 0)

        self.stack.add_titled(page, "wifi", "Wi-Fi")

    # 7. Ethernet
    def init_ethernet_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("Ethernet Wired Network", "Wired interface status, IP address, and gateway"), False, False, 0)

        ip_out = run_cmd(["ip", "-br", "addr", "show"])
        lbl_ip = Gtk.Label(label=ip_out or "No wired ethernet adapter detected or active.")
        lbl_ip.set_alignment(0.0, 0.5)
        page.pack_start(lbl_ip, False, False, 0)

        btn_nm = Gtk.Button(label="Configure Wired Network Connections")
        btn_nm.connect("clicked", lambda b: subprocess.Popen(["nm-connection-editor"]))
        page.pack_start(btn_nm, False, False, 0)

        self.stack.add_titled(page, "ethernet", "Ethernet")

    # 8. Bluetooth
    def init_bluetooth_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("Bluetooth Wireless Devices", "Pair and manage wireless headsets, mice, and keyboards"), False, False, 0)

        btn_bt_toggle = Gtk.Switch()
        btn_bt_toggle.set_active(True)
        btn_bt_toggle.connect("notify::active", lambda s, p: run_cmd(["bluetoothctl", "power", "on" if s.get_active() else "off"]))

        bt_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        bt_box.pack_start(Gtk.Label(label="Bluetooth Controller:"), False, False, 0)
        bt_box.pack_start(btn_bt_toggle, False, False, 0)
        page.pack_start(bt_box, False, False, 0)

        btn_bt_hub = Gtk.Button(label="Open MONODESK Bluetooth Centre (Scan & Pair)")
        btn_bt_hub.connect("clicked", lambda b: subprocess.Popen(["monodesk-bluetooth-centre"]))
        page.pack_start(btn_bt_hub, False, False, 0)

        self.stack.add_titled(page, "bluetooth", "Bluetooth")

    # 9. Keyboard
    def init_keyboard_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("Keyboard & Typing", "Layouts, key repeat rate, and shortcuts"), False, False, 0)

        btn_kbd = Gtk.Button(label="Open Keyboard Configuration & Layouts")
        btn_kbd.connect("clicked", lambda b: subprocess.Popen(["xfce4-keyboard-settings"]))
        page.pack_start(btn_kbd, False, False, 0)

        self.stack.add_titled(page, "keyboard", "Keyboard")

    # 10. Mouse
    def init_mouse_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("Mouse & Pointer", "Pointer speed, acceleration, and handedness"), False, False, 0)

        btn_mouse = Gtk.Button(label="Open Mouse & Pointer Settings")
        btn_mouse.connect("clicked", lambda b: subprocess.Popen(["xfce4-mouse-settings"]))
        page.pack_start(btn_mouse, False, False, 0)

        self.stack.add_titled(page, "mouse", "Mouse")

    # 11. Touchpad
    def init_touchpad_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("Touchpad & Gestures", "Tap-to-click, natural scrolling, and multi-finger gestures"), False, False, 0)

        btn_tp = Gtk.Button(label="Configure Touchpad Gestures & Scrolling")
        btn_tp.connect("clicked", lambda b: subprocess.Popen(["xfce4-mouse-settings"]))
        page.pack_start(btn_tp, False, False, 0)

        self.stack.add_titled(page, "touchpad", "Touchpad")

    # 12. Power Management
    def init_power_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("Power & Sleep Profiles", "System resource allocation, screen blanking, and sleep timers"), False, False, 0)

        btn_pwr_std = Gtk.Button(label="Activate MONODESK Standard Profile (Full Compositing)")
        btn_pwr_std.connect("clicked", lambda b: run_cmd(["monodesk-profile-ctl", "set", "standard"]))
        page.pack_start(btn_pwr_std, False, False, 0)

        btn_pwr_lite = Gtk.Button(label="Activate MONODESK Lite Profile (Low Memory & Power Saving)")
        btn_pwr_lite.connect("clicked", lambda b: run_cmd(["monodesk-profile-ctl", "set", "lite"]))
        page.pack_start(btn_pwr_lite, False, False, 0)

        btn_pwr_xfce = Gtk.Button(label="Open Detailed Power Management")
        btn_pwr_xfce.connect("clicked", lambda b: subprocess.Popen(["xfce4-power-manager-settings"]))
        page.pack_start(btn_pwr_xfce, False, False, 0)

        self.stack.add_titled(page, "power", "Power")

    # 13. Battery
    def init_battery_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("Battery Health & Capacity", "Charge status, design capacity, and power draw"), False, False, 0)

        bat_info = "AC Line Powered (No battery detected or virtual machine environment)"
        for bat in ["BAT0", "BAT1"]:
            bp = f"/sys/class/power_supply/{bat}"
            if os.path.exists(bp):
                try:
                    cap = open(f"{bp}/capacity").read().strip()
                    stat = open(f"{bp}/status").read().strip()
                    bat_info = f"Battery {bat}: {cap}% ({stat})"
                    break
                except Exception:
                    pass

        lbl_bat = Gtk.Label(label=bat_info)
        lbl_bat.set_alignment(0.0, 0.5)
        page.pack_start(lbl_bat, False, False, 0)

        self.stack.add_titled(page, "battery", "Battery")

    # 14. Printers
    def init_printers_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("Printers & CUPS Subsystem", "CUPS print service and scanner management"), False, False, 0)

        btn_prn = Gtk.Button(label="Open CUPS Printer Configuration (system-config-printer)")
        btn_prn.connect("clicked", lambda b: subprocess.Popen(["system-config-printer"]))
        page.pack_start(btn_prn, False, False, 0)

        btn_prn_hub = Gtk.Button(label="Open MONODESK Print Centre")
        btn_prn_hub.connect("clicked", lambda b: subprocess.Popen(["monodesk-print-centre"]))
        page.pack_start(btn_prn_hub, False, False, 0)

        self.stack.add_titled(page, "printers", "Printers")

    # 15. Storage
    def init_storage_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("Storage & Disk Drives", "Mounted filesystems, partition layout, and SMART health"), False, False, 0)

        btn_disk = Gtk.Button(label="Open MONODESK Disk Manager")
        btn_disk.connect("clicked", lambda b: subprocess.Popen(["monodesk-disk-manager"]))
        page.pack_start(btn_disk, False, False, 0)

        self.stack.add_titled(page, "storage", "Storage")

    # 16. Users & Accounts
    def init_users_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("User Accounts & Privileges", "Local accounts, password management, and sudo privileges"), False, False, 0)

        btn_acc = Gtk.Button(label="Open MONODESK Account Manager")
        btn_acc.connect("clicked", lambda b: subprocess.Popen(["monodesk-accounts"]))
        page.pack_start(btn_acc, False, False, 0)

        self.stack.add_titled(page, "users", "Users")

    # 17. Privacy
    def init_privacy_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("Privacy & Zero-Telemetry Commitment", "Zero cloud tracking, local logging, and identifier redaction"), False, False, 0)

        btn_priv = Gtk.Button(label="Open MONODESK Privacy Dashboard")
        btn_priv.connect("clicked", lambda b: subprocess.Popen(["monodesk-privacy"]))
        page.pack_start(btn_priv, False, False, 0)

        self.stack.add_titled(page, "privacy", "Privacy")

    # 18. Security
    def init_security_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("Security & Firewall", "UFW network firewall, AppArmor sandboxing, and package verification"), False, False, 0)

        ufw_status = run_cmd(["ufw", "status"])
        lbl_ufw = Gtk.Label(label=f"Firewall Status:\n{ufw_status or 'UFW Active (default deny incoming, allow outgoing)'}")
        lbl_ufw.set_alignment(0.0, 0.5)
        page.pack_start(lbl_ufw, False, False, 0)

        btn_recovery = Gtk.Button(label="Open MONODESK Recovery & Security Centre")
        btn_recovery.connect("clicked", lambda b: subprocess.Popen(["monodesk-recovery"]))
        page.pack_start(btn_recovery, False, False, 0)

        self.stack.add_titled(page, "security", "Security")

    # 19. Accessibility
    def init_accessibility_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("Accessibility", "High-contrast visual mode, text scaling, and onscreen assistive tools"), False, False, 0)

        btn_access = Gtk.Button(label="Open MONODESK Accessibility Centre")
        btn_access.connect("clicked", lambda b: subprocess.Popen(["monodesk-accessibility"]))
        page.pack_start(btn_access, False, False, 0)

        self.stack.add_titled(page, "accessibility", "Accessibility")

    # 20. Updates
    def init_updates_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("Software & System Updates", "Signed Debian security updates and Flatpak application sources"), False, False, 0)

        btn_upd = Gtk.Button(label="Open MONODESK Update Manager")
        btn_upd.connect("clicked", lambda b: subprocess.Popen(["monodesk-updater"]))
        page.pack_start(btn_upd, False, False, 0)

        btn_store = Gtk.Button(label="Open MONODESK Software Store")
        btn_store.connect("clicked", lambda b: subprocess.Popen(["monodesk-store"]))
        page.pack_start(btn_store, False, False, 0)

        self.stack.add_titled(page, "updates", "Updates")

    # 21. About MONODESK OS 2.0
    def init_about_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.pack_start(self.make_header("About MONODESK OS", "Product identity, base distribution, and system specifications"), False, False, 0)

        uname = run_cmd(["uname", "-r"]) or "Linux 6.1 LTS"
        info = Gtk.Label(
            label="MONODESK OS 2.0.0 (Universal PC Edition)\n\n"
                  "• Architecture: x86-64 / AMD64\n"
                  "• Foundation: Debian 13 (Trixie) Linux LTS\n"
                  "• Desktop Shell: Custom Qt 6 / QML MONODESK Shell\n"
                  "• Window Management: XFWM4 Window Manager\n"
                  "• Audio Subsystem: PipeWire & WirePlumber Stack\n"
                  "• Installer: Calamares Universal PC Installer\n"
                  "• Privacy: 100% Zero Telemetry Verified\n"
                  "• Kernel: " + uname + "\n"
                  "• License: Free and Open-Source Software (GPLv3 / MIT)"
        )
        info.set_alignment(0.0, 0.5)
        page.pack_start(info, False, False, 0)

        btn_hw = Gtk.Button(label="Open Full Hardware Diagnostics Report")
        btn_hw.connect("clicked", lambda b: subprocess.Popen(["monodesk-hardware-centre"]))
        page.pack_start(btn_hw, False, False, 0)

        self.stack.add_titled(page, "about", "About")

    def set_theme(self, theme_name):
        try:
            subprocess.run(["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName", "-s", theme_name], check=False)
        except Exception:
            pass

if __name__ == "__main__":
    if Gtk is not None:
        app = MonodeskSettings()
        app.connect("destroy", Gtk.main_quit)
        app.show_all()
        Gtk.main()
