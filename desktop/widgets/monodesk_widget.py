#!/usr/bin/env python3
"""
MONODESK OS — Desktop System Widget
Lightweight, low-overhead desktop telemetry widget in dot-matrix aesthetic.
Displays CPU, RAM, Disk, and Battery usage.
"""

import sys
import os
import time
try:
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("GLib", "2.0")
    from gi.repository import Gtk, GLib, Gdk
    WindowBase = Gtk.Window
except ImportError:
    Gtk = None
    GLib = None
    Gdk = None
    WindowBase = object

def get_cpu_usage():
    try:
        with open("/proc/stat", "r") as f:
            line = f.readline()
        parts = [float(x) for x in line.strip().split()[1:8]]
        idle = parts[3] + parts[4]
        total = sum(parts)
        return idle, total
    except Exception:
        return 0.0, 1.0

def get_ram_usage():
    try:
        meminfo = {}
        with open("/proc/meminfo", "r") as f:
            for line in f:
                parts = line.split(":")
                if len(parts) == 2:
                    meminfo[parts[0].strip()] = int(parts[1].strip().split()[0])
        total = meminfo.get("MemTotal", 1024)
        available = meminfo.get("MemAvailable", 512)
        used = total - available
        pct = (used / total) * 100.0
        return pct, used / 1024, total / 1024
    except Exception:
        return 0.0, 0.0, 1.0

def get_disk_usage():
    try:
        st = os.statvfs("/")
        total = (st.f_blocks * st.f_frsize) / (1024**3)
        free = (st.f_bavail * st.f_frsize) / (1024**3)
        used = total - free
        pct = (used / total) * 100.0 if total > 0 else 0
        return pct, used, total
    except Exception:
        return 0.0, 0.0, 1.0

def get_battery_info():
    bat_path = "/sys/class/power_supply/BAT0"
    if not os.path.exists(bat_path):
        bat_path = "/sys/class/power_supply/BAT1"
    if not os.path.exists(bat_path):
        return None, "AC"
    try:
        capacity = 100
        if os.path.exists(f"{bat_path}/capacity"):
            with open(f"{bat_path}/capacity") as f:
                capacity = int(f.read().strip())
        status = "Discharging"
        if os.path.exists(f"{bat_path}/status"):
            with open(f"{bat_path}/status") as f:
                status = f.read().strip()
        return capacity, status
    except Exception:
        return None, "AC"

class MonodeskWidget(WindowBase):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("MONODESK Widget")
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_below(True)
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.set_default_size(260, 200)

        # Style context
        css = b"""
        window {
            background-color: rgba(18, 18, 20, 0.75);
            border: 1px solid #2A2A30;
            border-radius: 12px;
            padding: 14px;
        }
        label {
            color: #FFFFFF;
            font-family: 'JetBrains Mono', 'Courier New', monospace;
        }
        .header {
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 3px;
            color: #8E8E93;
        }
        .metric-title {
            font-size: 11px;
            color: #A0A0A5;
        }
        .metric-val {
            font-size: 14px;
            font-weight: 700;
            color: #FFFFFF;
        }
        levelbar block.filled {
            background-color: #E63946;
            border-radius: 2px;
        }
        levelbar trough {
            background-color: #26262C;
            border-radius: 2px;
            min-height: 4px;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        lbl_hdr = Gtk.Label(label="MONODESK // TELEMETRY")
        lbl_hdr.get_style_context().add_class("header")
        lbl_hdr.set_alignment(0.0, 0.5)
        vbox.pack_start(lbl_hdr, False, False, 0)

        self.last_idle, self.last_total = get_cpu_usage()

        # CPU
        self.cpu_label = Gtk.Label(label="CPU: --%")
        self.cpu_label.get_style_context().add_class("metric-val")
        self.cpu_bar = Gtk.LevelBar(min_value=0.0, max_value=100.0)
        vbox.pack_start(self.cpu_label, False, False, 0)
        vbox.pack_start(self.cpu_bar, False, False, 0)

        # RAM
        self.ram_label = Gtk.Label(label="RAM: -- / -- GB")
        self.ram_label.get_style_context().add_class("metric-val")
        self.ram_bar = Gtk.LevelBar(min_value=0.0, max_value=100.0)
        vbox.pack_start(self.ram_label, False, False, 0)
        vbox.pack_start(self.ram_bar, False, False, 0)

        # Storage
        self.disk_label = Gtk.Label(label="DISK: -- / -- GB")
        self.disk_label.get_style_context().add_class("metric-val")
        self.disk_bar = Gtk.LevelBar(min_value=0.0, max_value=100.0)
        vbox.pack_start(self.disk_label, False, False, 0)
        vbox.pack_start(self.disk_bar, False, False, 0)

        # Battery / Power
        self.pwr_label = Gtk.Label(label="POWER: --")
        self.pwr_label.get_style_context().add_class("metric-title")
        vbox.pack_start(self.pwr_label, False, False, 0)

        GLib.timeout_add_seconds(2, self.update_telemetry)
        self.update_telemetry()

    def update_telemetry(self):
        # CPU
        idle, total = get_cpu_usage()
        diff_idle = idle - self.last_idle
        diff_total = total - self.last_total
        self.last_idle, self.last_total = idle, total
        cpu_pct = 0.0
        if diff_total > 0:
            cpu_pct = (1.0 - (diff_idle / diff_total)) * 100.0
        cpu_pct = max(0.0, min(100.0, cpu_pct))
        self.cpu_label.set_text(f"CPU: {cpu_pct:.1f}%")
        self.cpu_bar.set_value(cpu_pct)

        # RAM
        ram_pct, ram_used, ram_total = get_ram_usage()
        self.ram_label.set_text(f"RAM: {ram_used:.1f} / {ram_total:.1f} GB ({ram_pct:.0f}%)")
        self.ram_bar.set_value(ram_pct)

        # Disk
        disk_pct, disk_used, disk_total = get_disk_usage()
        self.disk_label.set_text(f"SSD: {disk_used:.1f} / {disk_total:.1f} GB")
        self.disk_bar.set_value(disk_pct)

        # Battery
        bat, status = get_battery_info()
        if bat is not None:
            self.pwr_label.set_text(f"BATTERY: {bat}% ({status.upper()})")
        else:
            self.pwr_label.set_text("POWER SOURCE: AC MAINS")

        return True

if __name__ == "__main__":
    win = MonodeskWidget()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
