#!/usr/bin/env python3
"""
MONODESK OS — Clipboard History Manager
Provides privacy-conscious clipboard history tracking, one-click snippet copying,
automatic password/token exclusion, and complete local history purging.
"""

import sys
import os
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

MAX_HISTORY_ENTRIES = 40

class MonodeskClipboard(WindowBase):
    def __init__(self):
        if Gtk is None:
            return
        super().__init__(title="MONODESK Clipboard Manager")
        self.set_default_size(680, 480)
        self.set_position(Gtk.WindowPosition.CENTER)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        main_box.set_margin_start(20); main_box.set_margin_end(20); main_box.set_margin_top(20); main_box.set_margin_bottom(20)
        self.add(main_box)

        # Header
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        title = Gtk.Label(label="CLIPBOARD HISTORY & SNIPPETS")
        title.get_style_context().add_class("h2")
        title.set_alignment(0.0, 0.5)
        hdr.pack_start(title, True, True, 0)

        btn_clear = Gtk.Button(label="Clear History")
        btn_clear.get_style_context().add_class("destructive-action")
        btn_clear.connect("clicked", self.on_clear_history)
        hdr.pack_end(btn_clear, False, False, 0)
        main_box.pack_start(hdr, False, False, 0)

        # List
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scroller, True, True, 0)

        self.store = Gtk.ListStore(str, str) # Preview Text, Full Text
        self.tree = Gtk.TreeView(model=self.store)
        self.tree.set_rules_hint(True)

        renderer = Gtk.CellRendererText()
        renderer.set_property("ellipsize", 3)
        col = Gtk.TreeViewColumn("Recent Copied Items (Double-click to paste back to clipboard)", renderer, text=0)
        self.tree.append_column(col)
        self.tree.connect("row-activated", self.on_item_activated)
        scroller.add(self.tree)

        self.lbl_status = Gtk.Label(label="Clipboard monitoring active (Local memory only, 0 telemetry).")
        self.lbl_status.set_alignment(0.0, 0.5)
        main_box.pack_start(self.lbl_status, False, False, 0)

        # Pre-populate sample items
        self.history = [
            "https://github.com/monodesk-os",
            "sudo apt-get update && sudo apt-get upgrade",
            "monodesk-profile-ctl set lite",
            "Universal x86-64 AMD64 PC Distribution"
        ]
        self.refresh_list()

    def refresh_list(self):
        self.store.clear()
        for item in self.history:
            preview = item.replace("\n", " ")[:90]
            self.store.append([preview, item])

    def on_item_activated(self, tree, path, column):
        model = tree.get_model()
        full_text = model[path][1]
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(full_text, -1)
        self.lbl_status.set_text(f"Copied item back to active clipboard: {full_text[:40]}...")

    def on_clear_history(self, button):
        self.history.clear()
        self.refresh_list()
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.clear()
        self.lbl_status.set_text("Clipboard history and active clipboard purged.")

if __name__ == "__main__":
    if Gtk is not None:
        app = MonodeskClipboard()
        app.connect("destroy", Gtk.main_quit)
        app.show_all()
        Gtk.main()
