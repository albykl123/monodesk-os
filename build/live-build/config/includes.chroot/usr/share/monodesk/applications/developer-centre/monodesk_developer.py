#!/usr/bin/env python3
"""
MONODESK OS — Developer Centre
One-click developer toolchain management:
- GCC, Clang, Make, CMake (C/C++)
- Python 3 + Pip, Virtualenv
- Rust + Cargo toolchain
- Node.js + NPM
- Git, GitHub CLI
- Docker / Podman container runtimes
- VS Code / VSCodium / Geany IDEs
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

DEV_STACKS = [
    ("C/C++ Build Essentials", "build-essential gcc g++ gdb make cmake", "Standard compiler toolchains and debuggers."),
    ("Python Data & Dev Environment", "python3-dev python3-pip python3-venv", "Python development headers and virtual environments."),
    ("Rust Programming Language", "rustc cargo", "Safe systems programming toolchain and package manager."),
    ("Node.js & Web Runtime", "nodejs npm", "JavaScript and TypeScript server runtime."),
    ("Git & Version Control Tools", "git git-lfs gh", "Distributed source control and GitHub command-line interface."),
    ("Container Tools (Docker / Podman)", "podman podman-docker", "Rootless container engine compatible with Docker commands."),
    ("Geany Lightweight IDE", "geany geany-plugins", "Fast, resource-light development environment (<50MB RAM)."),
    ("OpenSSL & Cryptography SDK", "libssl-dev pkg-config", "Standard cryptographic development libraries.")
]

class MonodeskDeveloperCentre(WindowBase):
    def __init__(self):
        if Gtk is None:
            return
        super().__init__(title="MONODESK Developer Centre")
        self.set_default_size(860, 560)
        self.set_position(Gtk.WindowPosition.CENTER)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        main_box.set_margin_start(20); main_box.set_margin_end(20); main_box.set_margin_top(20); main_box.set_margin_bottom(20)
        self.add(main_box)

        # Header
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        title = Gtk.Label(label="DEVELOPER TOOLCHAINS & RUNTIMES")
        title.get_style_context().add_class("h2")
        title.set_alignment(0.0, 0.5)
        hdr.pack_start(title, True, True, 0)

        btn_term = Gtk.Button(label="Open Developer Terminal")
        btn_term.connect("clicked", lambda b: subprocess.Popen(["xfce4-terminal"]))
        hdr.pack_end(btn_term, False, False, 0)
        main_box.pack_start(hdr, False, False, 0)

        # Stack List
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scroller, True, True, 0)

        self.store = Gtk.ListStore(str, str, str, str) # Stack Name, Packages, Description, Status
        self.tree = Gtk.TreeView(model=self.store)
        self.tree.set_rules_hint(True)

        for i, col_name in enumerate(["Development Stack", "Package Dependencies", "Description", "Status"]):
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(col_name, renderer, text=i)
            self.tree.append_column(col)

        scroller.add(self.tree)

        # Actions Row
        action_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.pack_start(action_bar, False, False, 0)

        self.btn_install = Gtk.Button(label="Install Selected Development Toolchain")
        self.btn_install.get_style_context().add_class("suggested-action")
        self.btn_install.connect("clicked", self.on_install_stack)
        action_bar.pack_start(self.btn_install, False, False, 0)

        self.lbl_status = Gtk.Label(label="Select a toolchain to install from official Debian package sources.")
        self.lbl_status.set_alignment(0.0, 0.5)
        main_box.pack_start(self.lbl_status, False, False, 0)

        self.refresh_stacks()

    def is_stack_installed(self, packages_str):
        first_pkg = packages_str.split()[0]
        try:
            res = subprocess.run(["dpkg", "-s", first_pkg], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            return res.returncode == 0
        except Exception:
            return False

    def refresh_stacks(self):
        self.store.clear()
        for name, pkgs, desc in DEV_STACKS:
            status = "Installed" if self.is_stack_installed(pkgs) else "Available"
            self.store.append([name, pkgs, desc, status])

    def on_install_stack(self, button):
        model, treeiter = self.tree.get_selection().get_selected()
        if not treeiter:
            return
        pkgs = model[treeiter][1]
        cmd = ["pkexec", "apt-get", "install", "-y"] + pkgs.split()
        try:
            subprocess.Popen(cmd)
            self.lbl_status.set_text(f"Installing {model[treeiter][0]} via PackageKit / pkexec...")
        except Exception as e:
            self.lbl_status.set_text(f"Error: {e}")

if __name__ == "__main__":
    if Gtk is not None:
        app = MonodeskDeveloperCentre()
        app.connect("destroy", Gtk.main_quit)
        app.show_all()
        Gtk.main()
