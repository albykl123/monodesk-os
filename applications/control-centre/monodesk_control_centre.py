#!/usr/bin/env python3
"""
MONODESK OS — Control Centre
Unified quick-settings panel for NetworkManager, PipeWire audio,
display brightness, power profiles, and appearance modes.
"""

import sys
import os
import subprocess
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

def run_cmd(args):
    try:
        res = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        return res.stdout.strip()
    except Exception:
        return ""

class MonodeskControlCentre(Gtk.Window):
    def __init__(self):
        super().__init__(title="Control Centre")
        self.set_default_size(380, 560)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.set_icon_name("preferences-system")

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        main_box.set_margin_start(18)
        main_box.set_margin_end(18)
        main_box.set_margin_top(18)
        main_box.set_margin_bottom(18)
        self.add(main_box)

        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        title = Gtk.Label(label="QUICK CONTROLS")
        title.get_style_context().add_class("h2")
        title.set_alignment(0.0, 0.5)
        header.pack_start(title, True, True, 0)

        theme_btn = Gtk.Button(label="Theme Switch")
        theme_btn.connect("clicked", self.toggle_theme)
        header.pack_end(theme_btn, False, False, 0)
        main_box.pack_start(header, False, False, 0)

        # 1. Connectivity Tiles (Wi-Fi, Bluetooth)
        grid_conn = Gtk.Grid()
        grid_conn.set_column_spacing(12)
        grid_conn.set_row_spacing(12)
        grid_conn.set_column_homogeneous(True)
        main_box.pack_start(grid_conn, False, False, 0)

        self.btn_wifi = Gtk.ToggleButton(label="Wi-Fi: Scanning...")
        self.btn_wifi.connect("toggled", self.on_wifi_toggled)
        grid_conn.attach(self.btn_wifi, 0, 0, 1, 1)

        self.btn_bt = Gtk.ToggleButton(label="Bluetooth: Off")
        self.btn_bt.connect("toggled", self.on_bt_toggled)
        grid_conn.attach(self.btn_bt, 1, 0, 1, 1)

        # 2. Audio Volume (PipeWire / ALSA)
        lbl_vol = Gtk.Label(label="Audio Output Volume")
        lbl_vol.set_alignment(0.0, 0.5)
        main_box.pack_start(lbl_vol, False, False, 0)

        self.scale_vol = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.scale_vol.set_value(65)
        self.scale_vol.connect("value-changed", self.on_volume_changed)
        main_box.pack_start(self.scale_vol, False, False, 0)

        # 3. Display Brightness
        lbl_bright = Gtk.Label(label="Display Brightness")
        lbl_bright.set_alignment(0.0, 0.5)
        main_box.pack_start(lbl_bright, False, False, 0)

        self.scale_bright = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 10, 100, 1)
        self.scale_bright.set_value(80)
        self.scale_bright.connect("value-changed", self.on_brightness_changed)
        main_box.pack_start(self.scale_bright, False, False, 0)

        # 4. Power Profile Mode
        lbl_power = Gtk.Label(label="System Power Profile")
        lbl_power.set_alignment(0.0, 0.5)
        main_box.pack_start(lbl_power, False, False, 0)

        self.combo_power = Gtk.ComboBoxText()
        self.combo_power.append("power-saver", "Power Saver (Conservative, Extended Battery)")
        self.combo_power.append("balanced", "Balanced (Default System Profile)")
        self.combo_power.append("performance", "Performance (Full Turbo Clock Frequency)")
        self.combo_power.set_active(1)
        self.combo_power.connect("changed", self.on_power_profile_changed)
        main_box.pack_start(self.combo_power, False, False, 0)

        # 5. Quick Links (Settings, Hardware Report, Terminal)
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.pack_start(sep, False, False, 6)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        main_box.pack_start(btn_box, False, False, 0)

        btn_settings = Gtk.Button(label="System Settings")
        btn_settings.connect("clicked", lambda b: subprocess.Popen(["monodesk-settings"]))
        btn_box.pack_start(btn_settings, True, True, 0)

        btn_hw = Gtk.Button(label="Hardware Report")
        btn_hw.connect("clicked", lambda b: subprocess.Popen(["monodesk-hardware-report"]))
        btn_box.pack_start(btn_hw, True, True, 0)

        self.sync_initial_state()

    def sync_initial_state(self):
        # Check wifi
        res = run_cmd(["nmcli", "radio", "wifi"])
        wifi_on = (res == "enabled")
        self.btn_wifi.set_active(wifi_on)
        self.btn_wifi.set_label("Wi-Fi: ON" if wifi_on else "Wi-Fi: OFF")

        # Check bluetooth
        res_bt = run_cmd(["bluetoothctl", "show"])
        bt_on = "Powered: yes" in res_bt
        self.btn_bt.set_active(bt_on)
        self.btn_bt.set_label("Bluetooth: ON" if bt_on else "Bluetooth: OFF")

    def on_wifi_toggled(self, widget):
        state = "on" if widget.get_active() else "off"
        run_cmd(["nmcli", "radio", "wifi", state])
        widget.set_label(f"Wi-Fi: {state.upper()}")

    def on_bt_toggled(self, widget):
        state = "power on" if widget.get_active() else "power off"
        run_cmd(["bluetoothctl", state.split()[0], state.split()[1]])
        widget.set_label("Bluetooth: " + ("ON" if widget.get_active() else "OFF"))

    def on_volume_changed(self, widget):
        vol = int(widget.get_value())
        # Set pipewire / pactl volume
        run_cmd(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{vol}%"])

    def on_brightness_changed(self, widget):
        val = int(widget.get_value())
        run_cmd(["brightnessctl", "set", f"{val}%"])

    def on_power_profile_changed(self, widget):
        active_id = widget.get_active_id()
        if active_id:
            run_cmd(["powerprofilesctl", "set", active_id])

    def toggle_theme(self, widget):
        # Read current xfce theme
        current = run_cmd(["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName"])
        target = "Monodesk-Light" if "Dark" in current else "Monodesk-Dark"
        run_cmd(["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName", "-s", target])

if __name__ == "__main__":
    win = MonodeskControlCentre()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
