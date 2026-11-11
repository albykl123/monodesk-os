#!/usr/bin/env python3
"""
MONODESK OS — Software Manager
Curated and search-driven graphical package manager for trusted Debian repositories.
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

FEATURED_SOFTWARE = [
    ("Firefox ESR", "firefox-esr", "Web Browser", "Official privacy-focused web browser from Mozilla."),
    ("LibreOffice", "libreoffice", "Productivity", "Full-featured office suite (documents, spreadsheets, presentations)."),
    ("GIMP", "gimp", "Graphics", "Professional GNU Image Manipulation Program."),
    ("VLC Media Player", "vlc", "Multimedia", "Universal multimedia player for audio and video."),
    ("Visual Studio Code", "code", "Development", "Code editor and developer environment."),
    ("Geany", "geany", "Development", "Fast and lightweight IDE and text editor."),
    ("Audacity", "audacity", "Audio", "Multi-track audio editor and recorder."),
    ("Inkscape", "inkscape", "Graphics", "Vector graphics editor using SVG standard."),
    ("Thunderbird", "thunderbird", "Productivity", "Cross-platform email and calendar client."),
    ("Transmission", "transmission-gtk", "Network", "Fast, lightweight BitTorrent client."),
    ("FileZilla", "filezilla", "Network", "FTP, FTPS and SFTP client."),
    ("OBS Studio", "obs-studio", "Multimedia", "Live streaming and screen recording software.")
]

class MonodeskSoftwareManager(WindowBase):
    def __init__(self):
        if Gtk is None:
            return
        super().__init__(title="MONODESK Software Manager")
        self.set_default_size(880, 580)
        self.set_position(Gtk.WindowPosition.CENTER)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_start(18)
        main_box.set_margin_end(18)
        main_box.set_margin_top(18)
        main_box.set_margin_bottom(18)
        self.add(main_box)

        # Search Bar
        search_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.entry_search = Gtk.SearchEntry()
        self.entry_search.set_placeholder_text("Search Debian software catalog...")
        self.entry_search.connect("search-changed", self.on_search)
        search_bar.pack_start(self.entry_search, True, True, 0)
        main_box.pack_start(search_bar, False, False, 0)

        # Scrolled view of packages
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scroller, True, True, 0)

        # ListStore: Name, Package ID, Category, Description, Status (Installed / Available)
        self.store = Gtk.ListStore(str, str, str, str, str)
        self.tree = Gtk.TreeView(model=self.store)
        self.tree.set_rules_hint(True)

        cols = [("Application", 0), ("Package Name", 1), ("Category", 2), ("Status", 4)]
        for title, idx in cols:
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(title, renderer, text=idx)
            self.tree.append_column(col)

        self.tree.connect("cursor-changed", self.on_select_package)
        scroller.add(self.tree)

        # Detail Panel
        detail_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.lbl_desc = Gtk.Label(label="Select an application to view details.")
        self.lbl_desc.set_line_wrap(True)
        self.lbl_desc.set_alignment(0.0, 0.5)
        detail_box.pack_start(self.lbl_desc, True, True, 0)

        self.btn_action = Gtk.Button(label="Install")
        self.btn_action.get_style_context().add_class("suggested-action")
        self.btn_action.set_sensitive(False)
        self.btn_action.connect("clicked", self.on_action_clicked)
        detail_box.pack_end(self.btn_action, False, False, 0)
        main_box.pack_start(detail_box, False, False, 0)

        self.populate_featured()

    def is_pkg_installed(self, pkg_name):
        try:
            res = subprocess.run(["dpkg", "-s", pkg_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            return res.returncode == 0
        except Exception:
            return False

    def populate_featured(self):
        self.store.clear()
        for name, pkg, cat, desc in FEATURED_SOFTWARE:
            status = "Installed" if self.is_pkg_installed(pkg) else "Available"
            self.store.append([name, pkg, cat, desc, status])

    def on_search(self, entry):
        query = entry.get_text().strip().lower()
        if not query:
            self.populate_featured()
            return

        self.store.clear()
        # Search featured first
        for name, pkg, cat, desc in FEATURED_SOFTWARE:
            if query in name.lower() or query in pkg.lower() or query in desc.lower():
                status = "Installed" if self.is_pkg_installed(pkg) else "Available"
                self.store.append([name, pkg, cat, desc, status])

        # Query apt-cache for live matches
        try:
            res = subprocess.run(["apt-cache", "search", "--names-only", query], stdout=subprocess.PIPE, text=True, check=False)
            for line in res.stdout.splitlines()[:20]:
                parts = line.split(" - ", 1)
                if len(parts) == 2:
                    pkg_id = parts[0].strip()
                    desc = parts[1].strip()
                    status = "Installed" if self.is_pkg_installed(pkg_id) else "Available"
                    self.store.append([pkg_id, pkg_id, "Debian Package", desc, status])
        except Exception:
            pass

    def on_select_package(self, tree):
        model, treeiter = tree.get_selection().get_selected()
        if treeiter:
            name, pkg, cat, desc, status = model[treeiter]
            self.lbl_desc.set_text(f"{name} ({pkg})\n{desc}")
            if status == "Installed":
                self.btn_action.set_label("Remove")
                self.btn_action.get_style_context().remove_class("suggested-action")
                self.btn_action.get_style_context().add_class("destructive-action")
            else:
                self.btn_action.set_label("Install")
                self.btn_action.get_style_context().remove_class("destructive-action")
                self.btn_action.get_style_context().add_class("suggested-action")
            self.btn_action.set_sensitive(True)

    def on_action_clicked(self, button):
        model, treeiter = self.tree.get_selection().get_selected()
        if not treeiter:
            return
        pkg = model[treeiter][1]
        action = button.get_label().lower()

        if action == "install":
            cmd = ["pkexec", "apt-get", "install", "-y", pkg]
        else:
            cmd = ["pkexec", "apt-get", "remove", "-y", pkg]

        try:
            subprocess.Popen(cmd)
            self.lbl_desc.set_text(f"Action triggered: {action.title()}ing {pkg}...")
        except Exception as e:
            self.lbl_desc.set_text(f"Error launching package action: {e}")

if __name__ == "__main__":
    if Gtk is not None:
        app = MonodeskSoftwareManager()
        app.connect("destroy", Gtk.main_quit)
        app.show_all()
        Gtk.main()
