#!/usr/bin/env python3
"""
MONODESK OS — Account Manager
Local user management, account creation, password management,
group permissions (sudo, audio, video, plugdev), and session controls.
"""

import sys
import os
import subprocess

try:
    import pwd
    import grp
except ImportError:
    pwd = None
    grp = None

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

def get_local_users():
    """Retrieve non-system human user accounts (UID >= 1000)."""
    users = []
    if pwd and grp:
        try:
            for p in pwd.getpwall():
                if 1000 <= p.pw_uid < 60000 and not p.pw_name.startswith("nobody"):
                    is_sudo = "sudo" in [g.gr_name for g in grp.getgrall() if p.pw_name in g.gr_mem]
                    users.append({
                        "username": p.pw_name,
                        "fullname": p.pw_gecos.split(",")[0] if p.pw_gecos else p.pw_name,
                        "uid": p.pw_uid,
                        "home": p.pw_dir,
                        "shell": p.pw_shell,
                        "is_admin": is_sudo
                    })
        except Exception:
            pass
    if not users:
        # Fallback default for testing or non-Linux
        users.append({
            "username": "monodesk",
            "fullname": "MONODESK Primary User",
            "uid": 1000,
            "home": "/home/monodesk",
            "shell": "/bin/bash",
            "is_admin": True
        })
    return users

class MonodeskAccountManager(WindowBase):
    def __init__(self):
        if Gtk is None:
            return
        super().__init__(title="MONODESK Account Manager")
        self.set_default_size(760, 520)
        self.set_position(Gtk.WindowPosition.CENTER)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        main_box.set_margin_start(20); main_box.set_margin_end(20); main_box.set_margin_top(20); main_box.set_margin_bottom(20)
        self.add(main_box)

        # Header
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        title = Gtk.Label(label="USER ACCOUNTS & PRIVILEGES")
        title.get_style_context().add_class("h2")
        title.set_alignment(0.0, 0.5)
        hdr.pack_start(title, True, True, 0)

        btn_add = Gtk.Button(label="+ Add New User")
        btn_add.get_style_context().add_class("suggested-action")
        btn_add.connect("clicked", self.on_add_user)
        hdr.pack_end(btn_add, False, False, 0)
        main_box.pack_start(hdr, False, False, 0)

        # Users List
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scroller, True, True, 0)

        self.store = Gtk.ListStore(str, str, str, str, str) # Full Name, Username, Type, Home, Shell
        self.tree = Gtk.TreeView(model=self.store)
        self.tree.set_rules_hint(True)

        for i, col_name in enumerate(["Full Name", "Username", "Account Type", "Home Directory", "Login Shell"]):
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(col_name, renderer, text=i)
            self.tree.append_column(col)

        scroller.add(self.tree)

        # User Actions Row
        action_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.pack_start(action_bar, False, False, 0)

        btn_passwd = Gtk.Button(label="Change Password")
        btn_passwd.connect("clicked", self.on_change_password)
        action_bar.pack_start(btn_passwd, False, False, 0)

        btn_toggle_admin = Gtk.Button(label="Toggle Administrator Privileges")
        btn_toggle_admin.connect("clicked", self.on_toggle_admin)
        action_bar.pack_start(btn_toggle_admin, False, False, 0)

        self.lbl_status = Gtk.Label(label="Ready.")
        self.lbl_status.set_alignment(0.0, 0.5)
        main_box.pack_start(self.lbl_status, False, False, 0)

        self.refresh_users()

    def refresh_users(self):
        self.store.clear()
        users = get_local_users()
        for u in users:
            role = "Administrator (sudo)" if u["is_admin"] else "Standard User"
            self.store.append([u["fullname"], u["username"], role, u["home"], u["shell"]])

    def on_add_user(self, button):
        dialog = Gtk.Dialog(title="Create New User Account", parent=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        box = dialog.get_content_area()
        box.set_spacing(10); box.set_margin_start(16); box.set_margin_end(16); box.set_margin_top(16); box.set_margin_bottom(16)

        entry_user = Gtk.Entry(); entry_user.set_placeholder_text("Username (lowercase, no spaces)")
        entry_name = Gtk.Entry(); entry_name.set_placeholder_text("Full Name")
        chk_admin = Gtk.CheckButton(label="Grant Administrator Privileges (sudo)")
        box.pack_start(Gtk.Label(label="Username:"), False, False, 0)
        box.pack_start(entry_user, False, False, 0)
        box.pack_start(Gtk.Label(label="Full Name:"), False, False, 0)
        box.pack_start(entry_name, False, False, 0)
        box.pack_start(chk_admin, False, False, 0)
        dialog.show_all()

        res = dialog.run()
        if res == Gtk.ResponseType.OK:
            username = entry_user.get_text().strip().lower()
            fullname = entry_name.get_text().strip()
            is_admin = chk_admin.get_active()
            if username:
                try:
                    cmd = ["pkexec", "useradd", "-m", "-c", fullname, username]
                    subprocess.Popen(cmd)
                    if is_admin:
                        subprocess.Popen(["pkexec", "usermod", "-aG", "sudo", username])
                    self.lbl_status.set_text(f"User creation task dispatched for: {username}")
                except Exception as e:
                    self.lbl_status.set_text(f"Error: {e}")
        dialog.destroy()
        GLib.timeout_add_seconds(2, self.refresh_users)

    def on_change_password(self, button):
        model, treeiter = self.tree.get_selection().get_selected()
        if not treeiter:
            return
        username = model[treeiter][1]
        try:
            subprocess.Popen(["xfce4-terminal", "-e", f"pkexec passwd {username}"])
        except Exception:
            pass

    def on_toggle_admin(self, button):
        model, treeiter = self.tree.get_selection().get_selected()
        if not treeiter:
            return
        username = model[treeiter][1]
        current_role = model[treeiter][2]
        if "Administrator" in current_role:
            cmd = ["pkexec", "gpasswd", "-d", username, "sudo"]
        else:
            cmd = ["pkexec", "usermod", "-aG", "sudo", username]
        try:
            subprocess.Popen(cmd)
            self.lbl_status.set_text(f"Admin privilege update dispatched for {username}")
            GLib.timeout_add_seconds(2, self.refresh_users)
        except Exception as e:
            self.lbl_status.set_text(f"Error: {e}")

if __name__ == "__main__":
    if Gtk is not None:
        app = MonodeskAccountManager()
        app.connect("destroy", Gtk.main_quit)
        app.show_all()
        Gtk.main()
