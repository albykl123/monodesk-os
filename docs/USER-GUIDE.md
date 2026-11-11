# MONODESK OS 1.0 — Official User & Administrator Guide
## The Monochrome Computing Experience

---

### 1. The Desktop Experience

MONODESK OS introduces a refined, distraction-free desktop environment engineered for modern personal computers.

#### 1.1 The MONODESK Dock
Located at the bottom center of your screen, the dock provides one-click access to your core workspace tools:
- **Launcher Icon (Left):** Click the MONODESK logo or press the `Super` (Windows) key on your keyboard to reveal the full Application Launcher.
- **Pinned Applications:** Fast access to Files, Terminal, Browser, Software Store, Settings, and System Monitor. Running applications display a subtle dot-matrix indicator underneath their icon.
- **Quick Search Icon:** Click the magnifying glass or press `Alt + Space` anywhere to activate the instant Spotlight search.
- **Control Centre Icon (Right):** Quick access to Wi-Fi, Bluetooth, Audio Volume, Display Brightness, and Power Profiles.

#### 1.2 Universal Quick Search (`Alt + Space`)
Quick Search is your universal command center:
- Press `Alt + Space` to bring up the search bar.
- Type any application name, setting, or action (e.g. `terminal`, `displays`, `lock`, `power`).
- Use the `Up` and `Down` arrow keys to navigate and press `Enter` to execute.
- Press `Esc` to dismiss.

#### 1.3 Desktop Telemetry Widgets
Positioned in the upper right corner of your desktop, the telemetry widgets provide at-a-glance hardware monitoring:
- **Dot-Matrix Digital Clock & Calendar:** High-legibility 24-hour time and date display.
- **Hardware Gauge:** Live per-second CPU load, RAM utilization, and AC/battery power status.

---

### 2. Customizing Appearance

MONODESK OS features an adaptive appearance engine:
1. Open **MONODESK Settings** or click the **Theme Switch** pill in the Control Centre.
2. Select between:
   - **MONODESK Dark:** Deep graphite surfaces (`#0A0A0C`), high-contrast white typography, and subtle crimson accents (`#E63946`).
   - **MONODESK Light:** Clean soft-white surfaces (`#F6F6F8`) and deep charcoal typography.
   - **Auto Mode:** Automatically transitions between Light and Dark based on your local time of day.
3. Wallpaper selection: Choose from pre-installed dot-matrix vector wallpapers or set custom background images.

---

### 3. Performance Profiles (Lite vs. Standard)

You can customize your system's performance footprint dynamically without reinstalling:
- **MONODESK Lite:** Recommended for 4 GB RAM computers (e.g. Lenovo B590). Disables window drop shadows, stops non-essential background indexing, and engages aggressive in-memory zRAM compression. Idle memory consumption is optimized to approximately ~700–900 MB RAM.
- **MONODESK Standard:** Recommended for 8 GB+ RAM systems (e.g. Lenovo IdeaPad Slim 5). Enables rich window snapping effects, desktop widgets, and balanced power management.

To switch profiles:
```bash
# Set Lite profile:
monodesk-profile-ctl set lite

# Set Standard profile:
monodesk-profile-ctl set standard

# Check current active profile:
monodesk-profile-ctl get
```

---

### 4. Software Management & Updates

- **MONODESK Software Store:** Browse curated open-source software, search official Debian repositories, and install packages securely with full dependency checking.
- **MONODESK Update Manager:** Regularly scans official Debian security channels (`bookworm-security`). Notifies you of available updates, clearly separates security patches, and prevents accidental removal of essential system packages.
- **NVIDIA GPU Setup:** If your PC has an NVIDIA graphics card, launch `monodesk-nvidia-installer` from the application menu or terminal to install verified proprietary drivers with DKMS.

---

### 5. Privacy, Backup & Recovery

- **Privacy Dashboard:** Monitor your UFW firewall state, AppArmor profiles, and verify that zero telemetry is being transmitted.
- **Backup Manager:** Create automated or manual compressed snapshots (`.tar.gz`) of your home directory or critical folders to an external USB drive.
- **Recovery Centre:** In the event of an interrupted package installation, launch the Recovery Centre and click **Run Safe Package Repair** to execute non-destructive `dpkg` reconciliation.
