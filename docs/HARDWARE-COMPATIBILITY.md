# MONODESK OS 1.0 (Universal PC Edition)
## Hardware Compatibility Matrix & Specifications

**Release:** 1.0.0-RELEASE  
**Architecture:** x86-64 / AMD64  
**Kernel:** Linux 6.1 LTS with Universal Debian Firmware

---

### 1. Compatibility Principles

MONODESK OS is engineered as a **universal x86-64 PC operating system**. We do not promise unsupported hardware will magically function; instead, we provide a transparent, verified hardware compatibility matrix and clear driver guidance.

---

### 2. Hardware Test Targets

| Machine / Platform | Specifications | Profile | Compatibility Tier | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Lenovo B590** *(Low-End Acceptance Benchmark)* | Intel Core i3-2348M (2C/4T @ 2.3 GHz), 4 GB DDR3 RAM, Intel HD Graphics 3000, 500 GB SATA HDD | **MONODESK Lite** | **Tier 1 (Supported)** | Verified: Smooth desktop performance, idle RAM ~780 MB with zram. |
| **Lenovo IdeaPad Slim 5** *(Primary Development Host)* | AMD Ryzen 7 5700U (8C/16T @ 1.8-4.3 GHz), 16 GB DDR4 RAM, AMD Radeon Vega 8, 512 GB NVMe SSD | **MONODESK Standard** | **Tier 1 (Supported)** | Verified: Full hardware acceleration, multi-monitor, high-DPI scaling, Wi-Fi 6. |
| **QEMU / KVM Virtual Machine** | 4 vCPUs, 4096 MB RAM, VirtIO GPU, VirtIO Net, 25 GB Virtual Disk | **Both** | **Tier 1 (Supported)** | Verified: Full UEFI (OVMF) and Legacy BIOS boot, Calamares installer verified. |
| **Generic Intel Core (Nehalem to Raptor Lake)** | Intel Core i3/i5/i7/i9, Intel Pentium / Celeron (64-bit) | **Auto** | **Tier 1 (Supported)** | Full microcode and Mesa i915 / iris / crocus DRM acceleration. |
| **Generic AMD Ryzen / Athlon (64-bit)** | AMD Ryzen 1000 through 7000 series, Athlon 64-bit, EPYC | **Auto** | **Tier 1 (Supported)** | Full AMD microcode, AMDGPU kernel driver, RADV Vulkan support. |
| **Dedicated NVIDIA Graphics Systems** | GeForce GTX 900 through RTX 4000 series | **Standard** | **Tier 2 (Supported via Installer)** | Out-of-the-box Nouveau display; one-click proprietary driver via `monodesk-nvidia-installer`. |

---

### 3. Component Compatibility Details

#### 3.1 Central Processing Units (CPUs)
- **Supported:** All 64-bit x86-64 processors (Intel Core, Celeron, Pentium, Xeon; AMD Ryzen, Athlon 64, Phenom II, FX, EPYC).
- **Microcode:** `intel-microcode` and `amd64-microcode` are embedded directly in the initramfs image to patch hardware errata and security vulnerabilities (Spectre, Meltdown, Retbleed) at boot time.
- **Unsupported:** 32-bit only CPUs (Intel Pentium 4 x86, Atom 32-bit), ARM64, and Apple Silicon (future dedicated editions planned).

#### 3.2 Graphics Subsystem (GPUs)
- **Intel Graphics:** Native support via Linux DRM/KMS. Older Gen 6/7 graphics (Intel HD 3000/4000 on Sandy Bridge/Ivy Bridge) operate with OpenGL 3.3 via Mesa Crocus; modern Gen 9+ (Skylake through Meteor Lake) utilize Mesa Iris with full Vulkan/OpenGL 4.6 acceleration.
- **AMD Graphics:** Native support via `amdgpu` driver for GCN 3 (Tonga) and newer (RDNA 1/2/3). Legacy TeraScale and early GCN use `radeon` driver.
- **NVIDIA Graphics:** Bootable out-of-the-box using the open-source `nouveau` driver. For full 3D performance, CUDA, and gaming, users execute `sudo monodesk-nvidia-installer` to compile official DKMS drivers from Debian non-free repositories.

#### 3.3 Audio Subsystem
- **Sound Architecture:** PipeWire 0.3+ with WirePlumber session manager.
- **Supported Hardware:** Intel High Definition Audio (HDA), Realtek ALC series, AMD GPU HDMI/DisplayPort audio, USB DACs, and Bluetooth audio devices (A2DP, LDAC, AAC).

#### 3.4 Wireless & Bluetooth
- **Firmware:** Pre-installed firmware packages include `firmware-iwlwifi` (Intel Wireless-AC / Wi-Fi 6/6E), `firmware-realtek` (RTL8188, RTL8821, RTL8822), `firmware-atheros` (Qualcomm Atheros QCA series), and `firmware-brcm80211` (Broadcom).

#### 3.5 Storage & Filesystems
- **Controllers:** NVMe PCIe (Gen 3/4/5), SATA SSD/HDD, eMMC, USB 3.x flash storage.
- **Filesystems:** `ext4` (default root filesystem), `btrfs`, `xfs`, `vfat` (EFI System Partition), and `exfat`.

---

### 4. Known Hardware Limitations

1. **Broadcom BCM43xx Wi-Fi:** Some legacy Broadcom chipsets (e.g. BCM43142) require proprietary `broadcom-sta-dkms` drivers. If Wi-Fi is not detected on first boot, connect via Ethernet or USB tethering and run `sudo apt-get install -y broadcom-sta-dkms`.
2. **Optimus Hybrid Laptops:** Dual-GPU laptops (Intel + NVIDIA) will default to Intel integrated graphics in the live session for power efficiency. After proprietary driver installation, `prime-select` manages switching.
3. **Secure Boot:** Booting with UEFI Secure Boot enabled is supported when using Debian's Microsoft-signed `shim-signed` bootloader. If a custom kernel or unvalidated DKMS module is loaded, Secure Boot may require enrolling a machine-owner key (MOK).
