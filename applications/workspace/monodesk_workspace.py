#!/usr/bin/env python3
"""
MONODESK OS — Smart Workspace Manager
Manages virtual desktops, multi-monitor display placement,
window tiling shortcuts, and keyboard navigation.
"""

import sys
import os
import subprocess
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

def run_cmd(args):
    try:
        proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        return proc.stdout.strip()
    except Exception:
        return ""

class MonodeskWorkspaceManager(Gtk.Window):
    def __init__(self):
        super().__init__(title="MONODESK Smart Workspace")
        self.set_default_size(720, 480)
        self.set_position(Gtk.WindowPosition.CENTER)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        main_box.set_margin_start(18); main_box.set_margin_end(18); main_box.set_margin_top(18); main_box.set_margin_bottom(18)
        self.add(main_box)

        # Header
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        title = Gtk.Label(label="SMART WORKSPACE & WINDOW MANAGEMENT")
        title.get_style_context().add_class("h2")
        title.set_alignment(0.0, 0.5)
        hdr.pack_start(title, True, True, 0)
        main_box.pack_start(hdr, False, False, 0)

        # 1. Workspace Count Controller
        grid = Gtk.Grid()
        grid.set_column_spacing(12); grid.set_row_spacing(10)
        main_box.pack_start(grid, False, False, 0)

        lbl_ws = Gtk.Label(label="Number of Virtual Desktops:")
        lbl_ws.set_alignment(0.0, 0.5)
        grid.attach(lbl_ws, 0, 0, 1, 1)

        self.spin_ws = Gtk.SpinButton.new_with_range(1, 8, 1)
        self.spin_ws.set_value(4)
        self.spin_ws.connect("value-changed", self.on_ws_count_changed)
        grid.attach(self.spin_ws, 1, 0, 1, 1)

        # 2. Window Tiling & Snapping Shortcuts
        lbl_tiling = Gtk.Label(label="KEYBOARD NAVIGATION & TILING SHORTCUTS")
        lbl_tiling.set_alignment(0.0, 0.5)
        main_box.pack_start(lbl_tiling, False, False, 6)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scroller, True, True, 0)

        store = Gtk.ListStore(str, str, str) # Shortcut, Action, Category
        tree = Gtk.TreeView(model=store)
        tree.set_rules_hint(True)

        shortcuts = [
            ("Super + Left", "Tile active window to Left half of display", "Tiling"),
            ("Super + Right", "Tile active window to Right half of display", "Tiling"),
            ("Super + Up", "Maximize active window", "Window State"),
            ("Super + Down", "Restore or minimize window", "Window State"),
            ("Super + 1..4", "Switch directly to Virtual Desktop 1 through 4", "Navigation"),
            ("Alt + Tab", "Fast window switcher with dot-matrix preview", "Switching"),
            ("Alt + Space", "Open MONODESK Quick Search spotlight", "Search"),
            ("Super", "Toggle MONODESK Application Launcher", "Launcher"),
            ("Super + C", "Open Quick Control Centre", "Settings")
        ]
        for sc, act, cat in shortcuts:
            store.append([sc, act, cat])

        for i, col_name in enumerate(["Keyboard Shortcut", "Function / Action", "Category"]):
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(col_name, renderer, text=i)
            tree.append_column(col)

        scroller.add(tree)

        # Multi-monitor settings shortcut
        btn_disp = Gtk.Button(label="Configure Multi-Monitor Placement (Displays)")
        btn_disp.connect("clicked", lambda b: subprocess.Popen(["xfce4-display-settings"]))
        main_box.pack_start(btn_disp, False, False, 0)

    def on_ws_count_changed(self, spin):
        val = int(spin.get_value())
        run_cmd(["xfconf-query", "-c", "xfwm4", "-p", "/general/workspace_count", "-s", str(val)])

if __name__ == "__main__":
    app = MonodeskWorkspaceManager()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
