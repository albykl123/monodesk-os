# MONODESK OS 1.0 — Gaming & Multimedia Compatibility Matrix

**Compatibility Engine:** Steam Proton 9.0+ / DXVK 2.3+ / VKD3D-Proton / Wine-GE  
**Audio Backend:** PipeWire Low-Latency Audio (<5.8ms buffer)  
**Graphics Acceleration:** Mesa RADV / RadeonSI (AMD) & Mesa Iris / Crocus (Intel) & NVIDIA 525+  

---

### 1. Popular PC Game Verification Matrix

| Game Title | Engine / API | Proton Version | Compatibility Status | Tested Hardware & Evidence | Notes / Launch Options |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Counter-Strike 2** | Source 2 (Vulkan) | Native Linux | **Verified (Native)** | AMD Ryzen 7 5700U (Radeon Vega 8) | 60+ FPS at 1080p. Perfect controller & mouse input. |
| **Cyberpunk 2077** | REDengine 4 (DX12) | Proton Experimental | **Verified (Proton)** | AMD / NVIDIA Vulkan 1.3 | Runs with FSR 2.1 balanced scaling. Stable 60 FPS. |
| **Grand Theft Auto V** | RAGE (DirectX 11) | Proton 9.0 | **Verified (Proton)** | Intel Core / AMD Ryzen | Full Rockstar Games Launcher authentication and GTA Online. |
| **Elden Ring** | FromSoftware (DX12) | Proton 9.0 | **Verified (Proton)** | Modern AMD/NVIDIA GPU | Easy Anti-Cheat Linux runtime enabled by publisher. 60 FPS. |
| **Dota 2** | Source 2 (Vulkan) | Native Linux | **Verified (Native)** | Intel HD 3000 (Low) & Ryzen | Native client with PipeWire low-latency spatial audio. |
| **Baldur's Gate 3** | Divinity 4.0 (Vulkan) | Proton 9.0 | **Verified (Proton)** | AMD / NVIDIA | Native Vulkan renderer selected in Larian launcher. |
| **Apex Legends** | Source (DX11) | Proton Experimental | **Verified (Proton)** | Modern x86-64 | EAC Linux runtime active. |
| **Valorant** | Unreal 4 (DirectX 11) | N/A | **Unsupported** | All Linux platforms | Blocked by Riot Vanguard kernel driver. |
| **Fortnite** | Unreal 5 (DirectX 12) | N/A | **Unsupported** | All Linux platforms | Epic Games has not enabled EAC Linux support for Fortnite. |

---

### 2. Gamepad & Controller Compatibility

MONODESK OS includes native kernel input drivers for:
- **Xbox Wireless / Wired Controllers:** Xbox 360, Xbox One, Xbox Series X/S via `xpad` kernel module.
- **Sony PlayStation Controllers:** DualShock 4 & DualSense (PS5) via `hid-playstation` kernel module, including touchpad and haptic feedback.
- **Nintendo Switch Pro Controller:** Supported via `hid-nintendo` kernel module.
- **Generic DirectInput / XInput USB Controllers:** Fully mapped via SDL2 game controller database.
