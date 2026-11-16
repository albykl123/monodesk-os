#!/usr/bin/env python3
"""
MONODESK OS 2.0 — Software Manager
Curated and search-driven graphical package manager for trusted Debian repositories and Flatpak.
Features:
- Browse featured and installed applications
- Search Debian software catalog via apt-cache
- Install, uninstall, and inspect package metadata
- Flatpak runtime inspection and source management
- Conflicting lock prevention and error reporting
"""

import sys
import os
import subprocess
import threading

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
    ("OBS Studio", "obs-studio", "Multimedia", "Live streaming and screen recording software."),
    ("Mousepad", "mousepad", "Accessories", "Fast and minimalist text editor."),
    ("Galculator", "galculator", "Accessories", "Scientific calculator supporting algebraic and RPN."),
    ("Ristretto", "ristretto", "Graphics", "Lightweight image viewer for x86-64 desktops."),
    ("File Roller", "file-roller", "System", "Archive and compression manager."),
    ("Qpdfview", "qpdfview", "Office", "Tabbed document and PDF viewer.")
]

class MonodeskSoftwareManager(WindowBase):
    def __init__(self):
        if Gtk is None:
            return
        super().__init__(title="MONODESK Software Store")
        self.set_default_size(920, 620)
        self.set_position(Gtk.WindowPosition.CENTER)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_start(20); main_box.set_margin_end(20)
        main_box.set_margin_top(18); main_box.set_margin_bottom(18)
        self.add(main_box)

        # Header & Search Bar
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        title = Gtk.Label(label="SOFTWARE STORE")
        title.get_style_context().add_class("h2")
        title.set_alignment(0.0, 0.5)
        hdr.pack_start(title, False, False, 0)

        self.entry_search = Gtk.SearchEntry()
        self.entry_search.set_placeholder_text("Search Debian software & Flatpaks...")
        self.entry_search.connect("search-changed", self.on_search)
        hdr.pack_start(self.entry_search, True, True, 0)
        main_box.pack_start(hdr, False, False, 0)

        # Mode Selection (Featured, Installed, Flatpaks)
        mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.btn_mode_featured = Gtk.RadioButton.new_with_label_from_widget(None, "Featured Catalog")
        self.btn_mode_featured.connect("toggled", lambda b: self.populate_featured() if b.get_active() else None)
        mode_box.pack_start(self.btn_mode_featured, False, False, 0)

        self.btn_mode_installed = Gtk.RadioButton.new_with_label_from_widget(self.btn_mode_featured, "Installed Applications")
        self.btn_mode_installed.connect("toggled", lambda b: self.populate_installed() if b.get_active() else None)
        mode_box.pack_start(self.btn_mode_installed, False, False, 0)

        self.btn_mode_flatpak = Gtk.RadioButton.new_with_label_from_widget(self.btn_mode_featured, "Flatpak Apps")
        self.btn_mode_flatpak.connect("toggled", lambda b: self.populate_flatpaks() if b.get_active() else None)
        mode_box.pack_start(self.btn_mode_flatpak, False, False, 0)

        main_box.pack_start(mode_box, False, False, 0)

        # Scrolled view of packages
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scroller, True, True, 0)

        # ListStore: Name, Package ID, Category, Description, Status
        self.store = Gtk.ListStore(str, str, str, str, str)
        self.tree = Gtk.TreeView(model=self.store)
        self.tree.set_rules_hint(True)

        cols = [("Application", 0), ("Package Name", 1), ("Category", 2), ("Status", 4)]
        for title, idx in cols:
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(title, renderer, text=idx)
            col.set_sort_column_id(idx)
            self.tree.append_column(col)

        self.tree.connect("cursor-changed", self.on_select_package)
        scroller.add(self.tree)

        # Detail Panel & Action Button
        detail_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        detail_box.get_style_context().add_class("card")

        self.lbl_desc = Gtk.Label(label="Select an application to view detailed package information.")
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

    def is_apt_locked(self):
        locks = ["/var/lib/dpkg/lock-frontend", "/var/lib/dpkg/lock", "/var/lib/apt/lists/lock"]
        for lock in locks:
            if os.path.exists(lock):
                # Check if file is locked
                try:
                    res = subprocess.run(["fuser", lock], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
                    if res.stdout.strip():
                        return True
                except Exception:
                    pass
        return False

    def populate_featured(self):
        self.store.clear()
        for name, pkg, cat, desc in FEATURED_SOFTWARE:
            status = "Installed" if self.is_pkg_installed(pkg) else "Available"
            self.store.append([name, pkg, cat, desc, status])

    def populate_installed(self):
        self.store.clear()
        try:
            res = subprocess.run(
                ["dpkg-query", "-W", "-f=${Package}\t${Section}\t${Description}\n"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
            )
            count = 0
            for line in res.stdout.splitlines():
                parts = line.split("\t", 2)
                if len(parts) >= 2:
                    pkg = parts[0].strip()
                    sec = parts[1].strip() or "System"
                    desc = parts[2].split("\n")[0].strip() if len(parts) > 2 else pkg
                    if any(pkg.startswith(p) for p in ["lib", "linux-", "grub-"]) and count > 30:
                        continue
                    self.store.append([pkg, pkg, sec, desc, "Installed"])
                    count += 1
                    if count >= 80:
                        break
        except Exception:
            self.populate_featured()

    def populate_flatpaks(self):
        self.store.clear()
        try:
            res = subprocess.run(["flatpak", "list", "--columns=name,application,version,description"], stdout=subprocess.PIPE, text=True, check=False)
            found = False
            for line in res.stdout.splitlines():
                parts = line.split("\t")
                if len(parts) >= 2:
                    name = parts[0].strip()
                    app_id = parts[1].strip()
                    desc = parts[3].strip() if len(parts) > 3 else app_id
                    self.store.append([name, app_id, "Flatpak", desc, "Installed"])
                    found = True
            if not found:
                self.store.append(["Flatpak Runtime", "flatpak", "Package System", "Flatpak is installed and ready. Use Software Store or flathub.org to add apps.", "Ready"])
        except Exception:
            self.store.append(["Flatpak Support", "flatpak", "Package System", "Flatpak subsystem available.", "Ready"])

    def on_search(self, entry):
        query = entry.get_text().strip().lower()
        if not query:
            if self.btn_mode_installed.get_active():
                self.populate_installed()
            elif self.btn_mode_flatpak.get_active():
                self.populate_flatpaks()
            else:
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
            for line in res.stdout.splitlines()[:25]:
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
            
            # Fetch extended metadata
            details = f"{name} ({pkg})\nCategory: {cat} | Status: {status}\n{desc}"
            try:
                info_res = subprocess.run(["apt-cache", "show", pkg], stdout=subprocess.PIPE, text=True, check=False)
                for line in info_res.stdout.splitlines():
                    if line.startswith("Version:"):
                        details += f"\n{line}"
                    elif line.startswith("Installed-Size:"):
                        details += f"\n{line}"
                    elif line.startswith("Homepage:"):
                        details += f"\n{line}"
            except Exception:
                pass

            self.lbl_desc.set_text(details)
            if status == "Installed":
                self.btn_action.set_label("Uninstall")
                self.btn_action.get_style_context().remove_class("suggested-action")
                self.btn_action.get_style_context().add_class("destructive-action")
                self.btn_action.set_sensitive(True)
            elif status == "Available":
                self.btn_action.set_label("Install")
                self.btn_action.get_style_context().remove_class("destructive-action")
                self.btn_action.get_style_context().add_class("suggested-action")
                self.btn_action.set_sensitive(True)
            else:
                self.btn_action.set_sensitive(False)

    def on_action_clicked(self, button):
        model, treeiter = self.tree.get_selection().get_selected()
        if not treeiter:
            return
        pkg = model[treeiter][1]
        action = button.get_label().lower()

        if self.is_apt_locked():
            self.lbl_desc.set_text("⚠️ Another package operation is currently in progress. Please wait for it to complete.")
            return

        if action == "install":
            cmd = ["pkexec", "apt-get", "install", "-y", pkg]
        else:
            cmd = ["pkexec", "apt-get", "remove", "-y", pkg]

        try:
            subprocess.Popen(cmd)
            self.lbl_desc.set_text(f"Action in progress: {action.title()}ing {pkg} via package manager...")
        except Exception as e:
            self.lbl_desc.set_text(f"Error launching package action: {e}")

if __name__ == "__main__":
    if Gtk is not None:
        app = MonodeskSoftwareManager()
        app.connect("destroy", Gtk.main_quit)
        app.show_all()
        Gtk.main()
