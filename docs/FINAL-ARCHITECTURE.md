# MONODESK OS 1.0 — Final Product Architecture Specification
## The Monochrome Computing Experience (Universal PC Edition)

**Document Version:** 1.1.0 (Amended: Universal PC Baseline)  
**Classification:** Official Product Architecture Specification  
**Release:** 1.0.0 (Universal PC Edition)  
**Target Architecture:** AMD64 / x86-64  
**Base Distribution:** Debian 12 (Bookworm) Pinned Stable  
**Single Distributable Target:** `monodesk-os-1.0.0-universal-amd64.iso`

---

### 1. Executive Product Decision: Single Universal ISO

MONODESK OS 1.0 ships as **ONE UNIVERSAL AMD64/x86-64 INSTALLATION ISO**.

> [!IMPORTANT]
> **Non-Negotiable Architecture Amendment:**
> Separate laptop-specific distribution ISOs (such as one for Lenovo IdeaPad Slim 5 and another for Lenovo B590) are strictly forbidden. The Lenovo IdeaPad Slim 5 and Lenovo B590 serve as initial physical hardware validation targets only. They do not define or restrict the supported hardware range of MONODESK OS.
>
> The exact same ISO image provides:
> 1. Universal Live Boot Environment (runs in memory without altering disks).
> 2. Universal Calamares Graphical PC Installer with LUKS encryption.
> 3. Custom MONODESK Desktop Shell (Qt 6 / QML).
> 4. Hardware Detection & Adaptive Profile Service (`monodesk-hw-detect`).
> 5. Driver, Firmware, and Safe Fallback Mechanisms.
> 6. Emergency Recovery & Diagnostic Environment (`monodesk-recovery`).
> 7. Hardware-Adaptive Profiles (MONODESK Standard vs MONODESK Lite).
> 8. Curated Software Store and Cryptographically Signed Updater.
> 9. First-Boot Welcome and Setup Onboarding Wizard.

---

### 2. Four-Layer System Architecture

```text
+-------------------------------------------------------------------------------+
|                       LAYER 1: MONODESK EXPERIENCE                            |
|  MONODESK Shell (Qt 6 / QML) • Dock • Launcher • Quick Search (Alt+Space)     |
|  Control Centre • Notification Centre • Dot-Matrix Telemetry Widgets         |
+-------------------------------------------------------------------------------+
|                       LAYER 2: MONODESK APPLICATIONS                          |
|  Welcome Onboarding • Central Settings • Software Store • Safe Updater        |
|  Hardware Centre • System Monitor • Privacy Dashboard • Backup Manager        |
|  Recovery Centre • Smart Workspace • Compatibility Centre • Gaming Centre     |
|  Developer Centre • Device Manager • Disk Manager • Optional Local AI         |
+-------------------------------------------------------------------------------+
|                       LAYER 3: MONODESK SYSTEM PLATFORM                       |
|  Hardware Detection & Adaptive Profiler (monodesk-hw-detect)                  |
|  Profile Controller (monodesk-profile-ctl auto / lite / standard)             |
|  D-Bus Session Services (org.monodesk.Shell) • PolicyKit Helpers              |
|  Diagnostic Redaction Engine • Power Management Daemons (TLP / PPD)           |
+-------------------------------------------------------------------------------+
|                       LAYER 4: LINUX FOUNDATION                               |
|  Debian 12 Bookworm Pinned Stable • Linux 6.1 LTS Kernel with Universal Microcode |
|  XFWM4 Window Manager (Compositing/Snapping) • PipeWire Audio • NetworkManager|
|  Mesa 3D (OpenGL/Vulkan) • systemd Init • APT/dpkg • UFW & AppArmor Security  |
+-------------------------------------------------------------------------------+
```

---

### 3. Component Ownership & Boundary Model

1. **Desktop Surface, Dock, Launcher, Quick Search, Control Centre, and Widgets:**
   - Exclusively owned by `MONODESK Shell` (built with Qt 6 / QML).
   - Redundant default panels and notification applets from the base desktop are disabled during session configuration to prevent duplicate UI elements.
2. **Window Management, Snapping, and Compositing:**
   - Handled by `XFWM4` via X11. XFWM4 provides lightweight, reliable, hardware-accelerated window snapping, Alt+Tab previews, and border rendering.
3. **Session Coordination & User Daemons:**
   - Coordinated via `systemd --user` (`services/monodesk-shell.service`) with automatic recovery on failure. If the shell crashes, `systemd` restarts it within 2 seconds without terminating running user applications.
4. **Privilege Boundaries:**
   - No graphical application runs as `root`. Privileged actions (package installation, firewall reload, driver installation) are strictly mediated through PolicyKit (`pkexec`) and narrowly scoped helper scripts.

---

### 4. Subsystem Specifications

#### 4.1 Hardware Detection & Diagnostic Service (`monodesk-hw-detect`)
The system includes a dedicated hardware diagnostic service that interrogates the host across ten distinct domains:
1. **CPU:** Architecture (`x86_64`), vendor, physical cores, logical threads, instruction capabilities (`avx`, `avx2`, `sse4_2`), frequencies, and low-power categorization.
2. **RAM:** Total memory, usable memory, swap allocation, and active zRAM compression.
3. **GPU & Graphics:** PCI controller enumeration, active kernel driver (`i915`, `amdgpu`, `nouveau`, `nvidia`), 3D hardware acceleration vs. software rasterizer fallback (`llvmpipe`, `softpipe`), and Vulkan ICD presence.
4. **Network:** Wired Ethernet adapters, Wi-Fi chipsets, kernel drivers, link states.
5. **Bluetooth:** Controller discovery, BlueZ status, `rfkill` states.
6. **Audio:** PipeWire 0.3+ sound server, WirePlumber session manager, sound cards.
7. **Storage:** NVMe vs SATA controllers, SSD vs rotational HDD status, capacity, and GPT vs MBR partition structures.
8. **Display & Input:** Display resolutions, refresh rates, primary monitors, touchpads with multitouch/libinput gesture support.
9. **Power & Battery:** Battery health and capacity percentage, AC power connection state, power-profiles-daemon status.
10. **Firmware:** Boot mode (UEFI vs Legacy BIOS) and Secure Boot state (`mokutil` / efivars).

All diagnostic logs are stored at `/var/log/monodesk-hardware.log` and `/var/log/monodesk-hardware.json` with sensitive identifiers (MAC addresses, UUIDs, serial numbers) automatically redacted.

#### 4.2 Multi-Factor Adaptive Profile Engine
Rather than relying on RAM alone, MONODESK OS evaluates the system holistically to recommend and apply performance profiles:

| Hardware Factor | MONODESK Lite Trigger | MONODESK Standard Trigger |
| :--- | :--- | :--- |
| **Available RAM** | `< 5.5 GB` (target 4 GB systems) | `>= 7.5 GB` (target 8 GB+ systems) |
| **CPU Capability** | `<= 2 threads` or no SSE4.2 / AVX | `>= 4 threads` with AVX / SSE4.2 |
| **GPU Acceleration** | Software rasterizer (`llvmpipe` / `swrast`) | Native DRM/KMS hardware acceleration (`amdgpu`, `i915`, `nouveau`, `nvidia`) |
| **Storage Medium** | Rotational mechanical HDD | Solid-state storage (NVMe / SATA SSD) |
| **Power State** | Low battery (`< 25%`) on DC power | AC mains power connected |

- **MONODESK Standard:** Full Qt Quick scenegraph compositor, subtle window shadows, fluid window snapping, rich desktop telemetry widgets, optional local AI, balanced power governor.
- **MONODESK Lite:** Window compositing shadows and heavy animations disabled, aggressive zRAM memory compression (zstd 50%), reduced background services, conservative power governor, target idle RAM ~700–900 MB.

Users can run `monodesk-profile-ctl auto` to automatically detect and apply the optimal profile, or manually switch via `monodesk-profile-ctl set lite` / `set standard`.

#### 4.3 Safe Driver & Firmware Fallback
- **Universal Graphics:** Intel HD/Iris and AMD Radeon GPUs operate out-of-the-box with kernel DRM/KMS and Mesa drivers. NVIDIA systems boot out-of-the-box via open-source Nouveau drivers; proprietary drivers are installed on demand via `monodesk-nvidia-installer`.
- **Software Rendering Fallback:** If hardware acceleration is unavailable, Mesa automatically falls back to `llvmpipe` modesetting; `monodesk-profile-ctl` automatically engages the Lite profile to maintain responsiveness.
- **Universal Microcode:** `intel-microcode` and `amd64-microcode` packages are integrated directly into the initramfs.

#### 4.4 Non-Destructive Installation Safety
- **Universal PC Installer:** Calamares 3.2+ configured with `prompt-install: true`.
- **Target Disk Transparency:** The installer displays the exact disk model, bus transport (NVMe/SATA/USB), capacity, and existing partition layouts.
- **Mandatory Confirmation Gate:** The user must explicitly review and confirm the destructive summary before any changes are committed to disk.
- **No Autonomous Overwrites:** Virtual machine tests run exclusively against disposable virtual disk images (`vm-disposable-test.qcow2`). Physical disks are never partitioned or modified automatically.

---
*Authored by Antigravity Operating System Engineering Team.*
