#!/usr/bin/env python3
"""
MONODESK OS — Settings Application
Centralized configuration manager integrating XFCE, systemd, and native MONODESK tools.
"""

import sys
import os
import subprocess
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

class MonodeskSettings(WindowBase):
    def __init__(self):
        if Gtk is None:
            return
        super().__init__(title="MONODESK Settings")
        self.set_default_size(860, 580)
        self.set_position(Gtk.WindowPosition.CENTER)

        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(main_box)

        # Sidebar
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        sidebar.set_size_request(240, -1)
        sidebar.get_style_context().add_class("sidebar")
        main_box.pack_start(sidebar, False, False, 0)

        title = Gtk.Label(label="SETTINGS")
        title.get_style_context().add_class("brand-title")
        title.set_margin_top(18)
        title.set_margin_bottom(12)
        sidebar.pack_start(title, False, False, 0)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

        self.stack_sidebar = Gtk.StackSidebar()
        self.stack_sidebar.set_stack(self.stack)
        sidebar.pack_start(self.stack_sidebar, True, True, 0)

        # Content Area
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.set_margin_start(20)
        content.set_margin_end(20)
        content.set_margin_top(20)
        content.set_margin_bottom(20)
        content.pack_start(self.stack, True, True, 0)
        main_box.pack_start(content, True, True, 0)

        self.init_appearance_page()
        self.init_display_page()
        self.init_sound_page()
        self.init_power_page()
        self.init_security_page()
        self.init_about_page()

    def init_appearance_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        lbl = Gtk.Label(label="Appearance & Themes")
        lbl.get_style_context().add_class("h1")
        lbl.set_alignment(0.0, 0.5)
        page.pack_start(lbl, False, False, 0)

        btn_dark = Gtk.Button(label="Apply MONODESK Dark (Standard Monochrome)")
        btn_dark.connect("clicked", lambda b: self.set_theme("Monodesk-Dark"))
        page.pack_start(btn_dark, False, False, 0)

        btn_light = Gtk.Button(label="Apply MONODESK Light (High-Contrast White)")
        btn_light.connect("clicked", lambda b: self.set_theme("Monodesk-Light"))
        page.pack_start(btn_light, False, False, 0)

        btn_wall = Gtk.Button(label="Change Desktop Wallpaper")
        btn_wall.connect("clicked", lambda b: subprocess.Popen(["xfdesktop-settings"]))
        page.pack_start(btn_wall, False, False, 10)

        self.stack.add_titled(page, "appearance", "Appearance")

    def init_display_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        lbl = Gtk.Label(label="Display & Resolution")
        lbl.get_style_context().add_class("h1")
        lbl.set_alignment(0.0, 0.5)
        page.pack_start(lbl, False, False, 0)

        btn_disp = Gtk.Button(label="Launch Native Display Configuration")
        btn_disp.connect("clicked", lambda b: subprocess.Popen(["xfce4-display-settings"]))
        page.pack_start(btn_disp, False, False, 0)

        self.stack.add_titled(page, "display", "Displays")

    def init_sound_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        lbl = Gtk.Label(label="Audio & Sound Devices")
        lbl.get_style_context().add_class("h1")
        lbl.set_alignment(0.0, 0.5)
        page.pack_start(lbl, False, False, 0)

        btn_vol = Gtk.Button(label="Open PipeWire Audio Mixer (pavucontrol)")
        btn_vol.connect("clicked", lambda b: subprocess.Popen(["pavucontrol"]))
        page.pack_start(btn_vol, False, False, 0)

        self.stack.add_titled(page, "sound", "Sound")

    def init_power_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        lbl = Gtk.Label(label="Power & Battery Management")
        lbl.get_style_context().add_class("h1")
        lbl.set_alignment(0.0, 0.5)
        page.pack_start(lbl, False, False, 0)

        btn_pwr = Gtk.Button(label="Open Power Manager Settings")
        btn_pwr.connect("clicked", lambda b: subprocess.Popen(["xfce4-power-manager-settings"]))
        page.pack_start(btn_pwr, False, False, 0)

        self.stack.add_titled(page, "power", "Power")

    def init_security_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        lbl = Gtk.Label(label="Security & Privacy Policy")
        lbl.get_style_context().add_class("h1")
        lbl.set_alignment(0.0, 0.5)
        page.pack_start(lbl, False, False, 0)

        sec_text = Gtk.Label(
            label="MONODESK OS Security Hardening:\n\n"
                  "• UFW Firewall: Enabled by default (incoming rejected, outgoing allowed)\n"
                  "• Telemetry: 100% Zero telemetry, zero usage tracking, no remote phoning home\n"
                  "• APT Package Signatures: Strictly verified against official Debian keys\n"
                  "• Full Disk Encryption: Optional LUKS encryption at install time"
        )
        sec_text.set_line_wrap(True)
        sec_text.set_alignment(0.0, 0.5)
        page.pack_start(sec_text, False, False, 0)

        self.stack.add_titled(page, "security", "Security & Privacy")

    def init_about_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        lbl = Gtk.Label(label="About MONODESK OS")
        lbl.get_style_context().add_class("h1")
        lbl.set_alignment(0.0, 0.5)
        page.pack_start(lbl, False, False, 0)

        info = Gtk.Label(
            label="MONODESK OS 1.0 (Universal PC Edition)\n"
                  "Base: Debian 12 (Bookworm) Stable x86-64\n"
                  "Desktop: XFCE 4.18 + MONODESK Shell\n"
                  "Kernel: Linux LTS with Universal Microcode\n"
                  "License: Free and Open-Source Software (FOSS)"
        )
        info.set_alignment(0.0, 0.5)
        page.pack_start(info, False, False, 0)

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
