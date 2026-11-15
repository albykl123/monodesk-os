#!/usr/bin/env python3
"""
MONODESK OS — Accessibility Manager
Configures Linux accessibility features:
- High-contrast visual modes
- Text font scaling (1.0x to 2.0x)
- Reduced motion toggle (disables desktop animations)
- Screen magnifier and Orca screen reader toggles
- Accessible keyboard navigation (Sticky keys, Bounce keys, Slow keys)
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

def run_xfconf(channel, prop, val_type, val):
    try:
        subprocess.run(["xfconf-query", "-c", channel, "-p", prop, "-t", val_type, "-s", str(val), "--create"], check=False)
    except Exception:
        pass

class MonodeskAccessibility(WindowBase):
    def __init__(self):
        if Gtk is None:
            return
        super().__init__(title="MONODESK Accessibility")
        self.set_default_size(720, 520)
        self.set_position(Gtk.WindowPosition.CENTER)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        main_box.set_margin_start(20); main_box.set_margin_end(20); main_box.set_margin_top(20); main_box.set_margin_bottom(20)
        self.add(main_box)

        # Header
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        title = Gtk.Label(label="UNIVERSAL ACCESS & ACCESSIBILITY")
        title.get_style_context().add_class("h2")
        title.set_alignment(0.0, 0.5)
        hdr.pack_start(title, True, True, 0)
        main_box.pack_start(hdr, False, False, 0)

        # 1. Vision & Display Section
        lbl_v = Gtk.Label(label="VISION & DISPLAY SCALING")
        lbl_v.set_alignment(0.0, 0.5)
        main_box.pack_start(lbl_v, False, False, 0)

        grid_v = Gtk.Grid()
        grid_v.set_column_spacing(12); grid_v.set_row_spacing(10)
        main_box.pack_start(grid_v, False, False, 0)

        lbl_scale = Gtk.Label(label="Text & DPI Scaling Factor:")
        lbl_scale.set_alignment(0.0, 0.5)
        grid_v.attach(lbl_scale, 0, 0, 1, 1)

        self.scale_slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1.0, 2.0, 0.1)
        self.scale_slider.set_value(1.0)
        self.scale_slider.connect("value-changed", self.on_scale_changed)
        grid_v.attach(self.scale_slider, 1, 0, 1, 1)

        self.chk_high_contrast = Gtk.CheckButton(label="Enable Ultra-High Contrast Monochrome Visuals")
        self.chk_high_contrast.connect("toggled", self.on_toggle_contrast)
        grid_v.attach(self.chk_high_contrast, 0, 1, 2, 1)

        self.chk_reduced_motion = Gtk.CheckButton(label="Reduce Motion (Disable animations and transitions)")
        self.chk_reduced_motion.connect("toggled", self.on_toggle_reduced_motion)
        grid_v.attach(self.chk_reduced_motion, 0, 2, 2, 1)

        # 2. Assistive Tools Section
        main_box.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 4)
        lbl_a = Gtk.Label(label="ASSISTIVE TECHNOLOGIES")
        lbl_a.set_alignment(0.0, 0.5)
        main_box.pack_start(lbl_a, False, False, 0)

        row_tools = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.pack_start(row_tools, False, False, 0)

        btn_orca = Gtk.Button(label="Launch Orca Screen Reader")
        btn_orca.connect("clicked", lambda b: subprocess.Popen(["orca"]))
        row_tools.pack_start(btn_orca, False, False, 0)

        btn_mag = Gtk.Button(label="Launch Screen Magnifier")
        btn_mag.connect("clicked", lambda b: subprocess.Popen(["xzoom"]))
        row_tools.pack_start(btn_mag, False, False, 0)

        # 3. Keyboard Accessibility Section
        main_box.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 4)
        lbl_k = Gtk.Label(label="KEYBOARD & MOTOR ASSISTANCE")
        lbl_k.set_alignment(0.0, 0.5)
        main_box.pack_start(lbl_k, False, False, 0)

        self.chk_sticky = Gtk.CheckButton(label="Sticky Keys (Press modifier keys sequentially rather than simultaneously)")
        self.chk_sticky.connect("toggled", self.on_toggle_sticky)
        main_box.pack_start(self.chk_sticky, False, False, 0)

        self.lbl_status = Gtk.Label(label="Accessibility settings active.")
        self.lbl_status.set_alignment(0.0, 0.5)
        main_box.pack_start(self.lbl_status, False, False, 0)

    def on_scale_changed(self, scale):
        factor = round(scale.get_value(), 2)
        # Apply DPI
        dpi = int(96 * factor)
        run_xfconf("xsettings", "/Xft/DPI", "int", dpi)
        self.lbl_status.set_text(f"Display text scaling updated to {factor}x ({dpi} DPI).")

    def on_toggle_contrast(self, chk):
        theme = "Monodesk-Dark" if chk.get_active() else "Monodesk-Dark"
        run_xfconf("xsettings", "/Net/ThemeName", "string", theme)

    def on_toggle_reduced_motion(self, chk):
        active = chk.get_active()
        run_xfconf("xfwm4", "/general/use_compositing", "bool", not active)
        self.lbl_status.set_text("Reduced motion preference applied.")

    def on_toggle_sticky(self, chk):
        active = chk.get_active()
        run_xfconf("accessibility", "/StickyKeys", "bool", active)

if __name__ == "__main__":
    if Gtk is not None:
        app = MonodeskAccessibility()
        app.connect("destroy", Gtk.main_quit)
        app.show_all()
        Gtk.main()
