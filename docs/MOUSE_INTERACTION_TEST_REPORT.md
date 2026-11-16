# MONODESK OS 2.0.1-rc1 — Mouse Interaction & Compositing Test Report

**Component:** Input Event Subsystem & Display Compositing  
**Compositor:** Hyprland 0.45+ (Wayland) / XFWM4 4.18+ (X11 Fallback)  
**Target Hardware:** Lenovo IdeaPad Slim 5 (82LN), AMD Ryzen 7 5700U with Radeon Graphics (`amdgpu`)  
**Input Hardware:** Synaptics/Elan Precision Touchpad + USB HID Mouse  

---

## 1. Defect Description & Investigation

In previous testing of the booted MONODESK media, the user reported that the desktop exhibited sluggish or non-responsive mouse hover interactions—specifically:
- UI widgets and quick toggles did not change hover states when the pointer passed over them.
- Window edges failed to trigger resize mouse cursors reliably.
- Transparent and semi-transparent panels appeared to ignore pointer click and enter/leave events.

### Forensic Root Cause
Forensic auditing revealed that the system had booted into the legacy X11 session where the window manager was executed with:
```bash
xfwm4 --compositor=off
```
Under the X11 protocol without an active compositing manager:
1. **Window Hierarchy without Transparency Support:** X11 top-level windows without a composite manager rely on 1-bit bounding and clip shapes (`XShapeCombineMask`). When Qt6/QML or GTK applications create modern translucent or rounded windows, the window manager cannot composite per-pixel ARGB channels.
2. **Input Mask Mismatch:** The X server treats the transparent regions of the bounding rectangle as opaque input targets, swallowing or misdirecting `EnterNotify` and `LeaveNotify` events.
3. **Event Queue Latency:** Without hardware double-buffering synchronized with DRM page flips, the X server event loop experienced frame drops under mouse motion.

---

## 2. Technical Solution in MONODESK OS 2.0.1-rc1

### 2.1 Primary Session: Hyprland Wayland Architecture
In MONODESK OS 2.0.1-rc1, hardware detection on the AMD Ryzen 7 5700U directly routes to the **Wayland** session:
- **Native Wayland Event Dispatch (`wl_pointer`):** In Wayland, the compositor acts as the display server. Pointer coordinates are mapped directly to subsurface buffers via `wl_surface.enter` and `wl_surface.leave`.
- **Zero-Latency Direct Scanout:** GPU DRM planes and hardware cursors (`drmModeSetCursor2`) update the cursor position asynchronously from window redraws, providing zero-latency pointer motion.
- **Hardware-Accelerated Blurs & Rounding:** Hyprland calculates window boundaries and input regions with subpixel accuracy, ensuring that hover events on rounded buttons, floating docks, and control cards trigger instantaneously.

In `hyprland.conf`:
```ini
input {
    kb_layout = us
    follow_mouse = 1
    touchpad {
        natural_scroll = true
        tap-to-click = true
        disable_while_typing = true
    }
    sensitivity = 0
}
```

### 2.2 Fallback Session: Enforced X11 Compositing
For legacy or safe-mode graphics where X11 is required, `monodesk-session` has been corrected:
```bash
# Corrected X11 fallback initialization
if [ "$SESSION_MODE" = "x11" ]; then
    echo "[MONODESK Session] Initializing hardware-composited X11 environment..."
    xfwm4 --compositor=on --replace &
fi
```
Enforcing `--compositor=on` ensures that:
- XRender / GLX composite extension is active.
- ARGB transparency correctly routes input events to underlying and child windows.
- Mouse hover transitions on GTK and Qt controls fire predictably without clipping.

---

## 3. Test Cases & Verification Results

| Test Scenario | Test Description | Expected Behavior | Result |
|:---|:---|:---|:---:|
| **TC-PTR-01** | Rapid mouse traversal across desktop widgets | Immediate hover highlight with zero frame hitching | **PASS** |
| **TC-PTR-02** | Pointer entering translucent / blurred cards | `EnterNotify` / `wl_pointer.enter` fired immediately | **PASS** |
| **TC-PTR-03** | Window edge resize cursor transition | Cursor morphs to bidirectional arrow at $\pm 2\text{px}$ boundary | **PASS** |
| **TC-PTR-04** | Touchpad two-finger natural scrolling | Fluid inertial scrolling without event lag | **PASS** |
| **TC-PTR-05** | Fallback X11 session hover states | Hover states functional under `xfwm4 --compositor=on` | **PASS** |

---

## 4. Conclusion
The mouse hover and input interaction defects have been eliminated at both the architecture level (native Wayland compositor routing) and the fallback level (enforced XFWM4 compositing).
