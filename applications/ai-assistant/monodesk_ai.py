#!/usr/bin/env python3
"""
MONODESK OS — Local AI Assistant (Optional, 100% Offline)
Strictly opt-in, disabled by default. Interacts with local inference engines
(e.g., local Ollama or llama-server at http://127.0.0.1:11434).
Zero cloud requirements, zero API keys, zero telemetry, and zero privileged operations.
"""

import sys
import os
import subprocess
import json
import urllib.request
import urllib.error
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

LOCAL_ENDPOINT = "http://127.0.0.1:11434/api/generate"

class MonodeskLocalAI(Gtk.Window):
    def __init__(self):
        super().__init__(title="MONODESK Local AI Assistant")
        self.set_default_size(780, 560)
        self.set_position(Gtk.WindowPosition.CENTER)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_start(20); main_box.set_margin_end(20); main_box.set_margin_top(20); main_box.set_margin_bottom(20)
        self.add(main_box)

        # Header
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        title = Gtk.Label(label="LOCAL AI ASSISTANT (OPTIONAL & PRIVATE)")
        title.get_style_context().add_class("h2")
        title.set_alignment(0.0, 0.5)
        hdr.pack_start(title, True, True, 0)

        badge = Gtk.Label(label="[ 100% ON-DEVICE / OFFLINE ]")
        hdr.pack_end(badge, False, False, 0)
        main_box.pack_start(hdr, False, False, 0)

        # Privacy Notice Banner
        notice = Gtk.Label(
            label="NOTICE: This assistant runs exclusively on your local CPU/GPU hardware. "
                  "No data, prompts, or files ever leave your PC. It is completely independent "
                  "and not required for normal operating system functionality."
        )
        notice.set_line_wrap(True)
        notice.set_alignment(0.0, 0.5)
        main_box.pack_start(notice, False, False, 0)

        # Local Runtime Status Row
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.lbl_status = Gtk.Label(label="Checking local inference runtime...")
        self.lbl_status.set_alignment(0.0, 0.5)
        status_box.pack_start(self.lbl_status, True, True, 0)

        self.btn_check_runtime = Gtk.Button(label="Check Local Engine")
        self.btn_check_runtime.connect("clicked", self.check_engine)
        status_box.pack_end(self.btn_check_runtime, False, False, 0)
        main_box.pack_start(status_box, False, False, 0)

        # Chat Conversation View
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scroller, True, True, 0)

        self.chat_view = Gtk.TextView()
        self.chat_view.set_editable(False)
        self.chat_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        scroller.add(self.chat_view)

        # Input Row
        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.entry_prompt = Gtk.Entry()
        self.entry_prompt.set_placeholder_text("Ask a question, write a script, or query system documentation...")
        self.entry_prompt.connect("activate", self.send_prompt)
        input_box.pack_start(self.entry_prompt, True, True, 0)

        self.btn_send = Gtk.Button(label="Send")
        self.btn_send.get_style_context().add_class("suggested-action")
        self.btn_send.connect("clicked", self.send_prompt)
        input_box.pack_end(self.btn_send, False, False, 0)
        main_box.pack_start(input_box, False, False, 0)

        self.check_engine(None)

    def append_chat(self, sender, text):
        buf = self.chat_view.get_buffer()
        tag = f"\n[{sender}]: {text}\n"
        buf.insert(buf.get_end_iter(), tag)

    def check_engine(self, button):
        try:
            req = urllib.request.Request("http://127.0.0.1:11434/api/tags")
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                data = json.loads(resp.read().decode())
                models = [m.get("name") for m in data.get("models", [])]
                self.lbl_status.set_text(f"✓ Local inference active. Available models: {', '.join(models) if models else 'None loaded'}")
                self.btn_send.set_sensitive(True)
        except Exception:
            self.lbl_status.set_text("○ Local engine offline (Ollama/llama.cpp not running on localhost:11434).")
            self.append_chat("System", "To enable local AI, install an open weights model (e.g. `ollama run mistral` or `llama-server`). The OS functions fully without it.")
            self.btn_send.set_sensitive(False)

    def send_prompt(self, widget):
        prompt = self.entry_prompt.get_text().strip()
        if not prompt:
            return
        self.append_chat("User", prompt)
        self.entry_prompt.set_text("")

        # Query local engine
        try:
            payload = json.dumps({"model": "mistral", "prompt": prompt, "stream": False}).encode("utf-8")
            req = urllib.request.Request(LOCAL_ENDPOINT, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                res = json.loads(resp.read().decode())
                reply = res.get("response", "No response generated.")
                self.append_chat("MONODESK AI", reply)
        except Exception as e:
            self.append_chat("System", f"Inference query error: {e}")

if __name__ == "__main__":
    app = MonodeskLocalAI()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
