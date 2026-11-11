# MONODESK OS 1.0 — Known Limitations & Scope Boundaries

---

### 1. Hardware Architecture Scope
- **64-bit AMD64 Only:** MONODESK OS 1.0 is engineered strictly for x86-64 / AMD64 processors. Legacy 32-bit only CPUs (such as Intel Pentium 4 or early Atom netbooks), ARM64 processors, and Apple Silicon Macs are **NOT SUPPORTED** in this edition. Modular architecture is maintained so ARM64 can be introduced in a future release.
- **Minimum Memory Requirement:**
  - MONODESK Lite requires an absolute minimum of **4 GB RAM** for stable operation. Systems with 2 GB RAM or less are not supported.
  - MONODESK Standard and the optional Local AI Assistant require **8 GB RAM** or greater.

---

### 2. Graphics & Driver Constraints
- **NVIDIA Dedicated GPUs:** Booting out-of-the-box utilizes the open-source `nouveau` kernel driver to guarantee display output across all personal computers. Full 3D acceleration and CUDA require running `sudo monodesk-nvidia-installer` after installation to build proprietary kernel modules via DKMS.
- **Optimus Hybrid Laptops:** Dual-GPU laptops (Intel + NVIDIA) operate on Intel integrated graphics by default to conserve battery life. GPU switching is managed via `prime-select`.
- **Legacy Intel HD 3000 Graphics (Sandy Bridge / Lenovo B590):** Hardware acceleration is provided via the Mesa Crocus OpenGL 3.3 driver. Vulkan is not supported by the physical hardware on Sandy Bridge or Ivy Bridge architectures.

---

### 3. Wireless Firmware
- **Broadcom BCM43xx Series:** Certain legacy Broadcom wireless chipsets (e.g., BCM43142) rely on proprietary Broadcom STA drivers not included in Debian's free firmware. Users with these adapters must connect via Ethernet or USB tethering to install `broadcom-sta-dkms`.

---

### 4. Optional Local AI Assistant
- **Hardware Prerequisites:** The local assistant is completely disabled by default. Running on-device language models (such as Mistral 7B or Llama 3 8B) requires at least **8 GB RAM** and approximately **4.5 GB of free disk storage**. It is automatically excluded from the default MONODESK Lite profile.
- **Zero Cloud Dependence:** The assistant does not connect to external APIs and will report "Offline" if no local runtime is running on `127.0.0.1:11434`.

---

### 5. Secure Boot
- Booting with UEFI Secure Boot enabled is fully supported using Debian's Microsoft-signed `shim-signed` bootloader. If proprietary NVIDIA DKMS drivers are compiled, the user must enroll a Machine Owner Key (MOK) during reboot to authorize the kernel module.
