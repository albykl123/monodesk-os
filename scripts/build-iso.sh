#!/usr/bin/env bash
# ==============================================================================
# MONODESK OS 1.0 (Universal PC Edition) — Master ISO Build Pipeline
# Orchestrates debian live-build, chroot asset staging, Qt 6 shell, and hybrid ISO generation
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BUILD_DIR="${REPO_ROOT}/build/live-build"
OUTPUT_DIR="${REPO_ROOT}/releases"
LOG_DIR="${REPO_ROOT}/build/logs"
DATE_TAG=$(date +"%Y%m%d_%H%M%S")
BUILD_LOG="${LOG_DIR}/build_${DATE_TAG}.log"

mkdir -p "${OUTPUT_DIR}" "${LOG_DIR}"

exec > >(tee -a "${BUILD_LOG}") 2>&1

echo "================================================================================"
echo "          MONODESK OS 1.0 — MASTER ISO BUILD PIPELINE                           "
echo "================================================================================"
echo "[*] Date: $(date)"
echo "[*] Repository Root: ${REPO_ROOT}"
echo "[*] Target Architecture: AMD64 / x86-64"

# 1. Pre-flight Checks
echo "[1/6] Running pre-flight system checks..."
if [[ $EUID -ne 0 ]]; then
    echo "[-] Error: Root privileges required for debootstrap chroot operations."
    echo "    Please run: sudo bash $0"
    exit 1
fi

ARCH=$(uname -m)
if [[ "$ARCH" != "x86_64" ]]; then
    echo "[-] Error: Host architecture is ${ARCH}. MONODESK OS 1.0 requires an x86_64 host."
    exit 1
fi

REQUIRED_TOOLS=(lb debootstrap mksquashfs xorriso)
for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "[-] Missing required build tool: ${tool}. Run scripts/install-build-deps.sh first."
        exit 1
    fi
done

# 2. Source Code Validation
echo "[2/6] Validating source code and configuration..."
bash "${REPO_ROOT}/scripts/check-source.sh"

# 3. Staging MONODESK Assets into live-build chroot overlay
echo "[3/6] Staging MONODESK Qt 6 / QML desktop shell, apps, and branding..."
INCLUDES_DIR="${BUILD_DIR}/config/includes.chroot"
mkdir -p \
    "${INCLUDES_DIR}/usr/bin" \
    "${INCLUDES_DIR}/usr/share/applications" \
    "${INCLUDES_DIR}/usr/share/backgrounds/monodesk" \
    "${INCLUDES_DIR}/usr/share/icons/hicolor/scalable/apps" \
    "${INCLUDES_DIR}/usr/share/themes/Monodesk-Dark/gtk-3.0" \
    "${INCLUDES_DIR}/usr/share/themes/Monodesk-Light/gtk-3.0" \
    "${INCLUDES_DIR}/usr/share/themes/Monodesk-Dark/xfwm4" \
    "${INCLUDES_DIR}/usr/share/monodesk/shell" \
    "${INCLUDES_DIR}/usr/share/monodesk/themes" \
    "${INCLUDES_DIR}/etc/monodesk" \
    "${INCLUDES_DIR}/etc/systemd/user"

# Copy branding
cp "${REPO_ROOT}/branding/assets/monodesk-icon.svg" "${INCLUDES_DIR}/usr/share/icons/hicolor/scalable/apps/"
cp "${REPO_ROOT}/branding/assets/monodesk-logo.svg" "${INCLUDES_DIR}/usr/share/icons/hicolor/scalable/apps/"
cp "${REPO_ROOT}/branding/wallpapers/"*.svg "${INCLUDES_DIR}/usr/share/backgrounds/monodesk/"

# Copy GTK & XFWM4 themes
cp "${REPO_ROOT}/desktop/appearance/gtk-3.0/gtk.css" "${INCLUDES_DIR}/usr/share/themes/Monodesk-Dark/gtk-3.0/"
cp "${REPO_ROOT}/desktop/appearance/gtk-3.0-light/gtk.css" "${INCLUDES_DIR}/usr/share/themes/Monodesk-Light/gtk-3.0/"
cp "${REPO_ROOT}/desktop/appearance/xfwm4/themerc" "${INCLUDES_DIR}/usr/share/themes/Monodesk-Dark/xfwm4/"

# Copy Qt 6 / QML Shell & Themes
cp -r "${REPO_ROOT}/desktop/shell/"* "${INCLUDES_DIR}/usr/share/monodesk/shell/"
cp -r "${REPO_ROOT}/themes/"* "${INCLUDES_DIR}/usr/share/monodesk/themes/"
cp "${REPO_ROOT}/desktop/shell/monodesk_shell.py" "${INCLUDES_DIR}/usr/bin/monodesk-shell"
chmod +x "${INCLUDES_DIR}/usr/bin/monodesk-shell"

# Copy system scripts and configs
cp "${REPO_ROOT}/system/power/monodesk-profile-ctl" "${INCLUDES_DIR}/usr/bin/"
cp "${REPO_ROOT}/system/hardware/monodesk-hw-detect" "${INCLUDES_DIR}/usr/bin/"
chmod +x "${INCLUDES_DIR}/usr/bin/monodesk-profile-ctl" "${INCLUDES_DIR}/usr/bin/monodesk-hw-detect"
cp "${REPO_ROOT}/services/monodesk-shell.service" "${INCLUDES_DIR}/etc/systemd/user/"

# Copy Full First-Party Applications Suite
APPS=(
    "welcome:monodesk_welcome.py:monodesk-welcome"
    "control-centre:monodesk_control_centre.py:monodesk-control-centre"
    "hardware-report:monodesk_hardware_report.py:monodesk-hardware-centre"
    "system-monitor:monodesk_system_monitor.py:monodesk-system-monitor"
    "settings:monodesk_settings.py:monodesk-settings"
    "update-manager:monodesk_update_manager.py:monodesk-updater"
    "software-manager:monodesk_software_manager.py:monodesk-store"
    "privacy:monodesk_privacy.py:monodesk-privacy"
    "backup:monodesk_backup.py:monodesk-backup"
    "recovery:monodesk_recovery.py:monodesk-recovery"
    "workspace:monodesk_workspace.py:monodesk-workspace"
    "ai-assistant:monodesk_ai.py:monodesk-ai"
    "accounts:monodesk_accounts.py:monodesk-accounts"
    "disk-manager:monodesk_disk_manager.py:monodesk-disk-manager"
    "device-manager:monodesk_device_manager.py:monodesk-device-manager"
    "network-centre:monodesk_network_centre.py:monodesk-network-centre"
    "bluetooth-centre:monodesk_bluetooth_centre.py:monodesk-bluetooth-centre"
    "print-centre:monodesk_print_centre.py:monodesk-print-centre"
    "clipboard:monodesk_clipboard.py:monodesk-clipboard"
    "accessibility:monodesk_accessibility.py:monodesk-accessibility"
    "compatibility:monodesk_compatibility.py:monodesk-compatibility"
    "gaming:monodesk_gaming.py:monodesk-gaming"
    "developer-centre:monodesk_developer.py:monodesk-developer"
)

for item in "${APPS[@]}"; do
    IFS=":" read -r app_dir script_name bin_name <<< "$item"
    if [[ -f "${REPO_ROOT}/applications/${app_dir}/${script_name}" ]]; then
        cp "${REPO_ROOT}/applications/${app_dir}/${script_name}" "${INCLUDES_DIR}/usr/bin/${bin_name}"
    fi
    find "${REPO_ROOT}/applications/${app_dir}" -name "*.desktop" -exec cp {} "${INCLUDES_DIR}/usr/share/applications/" \;
done

if [[ -f "${REPO_ROOT}/applications/nvidia-installer/monodesk-nvidia-installer.sh" ]]; then
    cp "${REPO_ROOT}/applications/nvidia-installer/monodesk-nvidia-installer.sh" "${INCLUDES_DIR}/usr/bin/monodesk-nvidia-installer"
    cp "${REPO_ROOT}/applications/nvidia-installer/monodesk-nvidia-installer.desktop" "${INCLUDES_DIR}/usr/share/applications/" || true
fi

chmod +x "${INCLUDES_DIR}/usr/bin/monodesk-"*

# 4. Live-Build Execution
echo "[4/6] Initializing live-build configuration and chroot..."
cd "${BUILD_DIR}"
lb clean --purge
lb config
lb build

# 5. Locate Output ISO and Move to Releases
echo "[5/6] Finalizing installation media artifacts..."
RAW_ISO=$(find "${BUILD_DIR}" -maxdepth 1 -name "*.iso" | head -n 1)
FINAL_ISO_NAME="monodesk-os-1.0.0-universal-amd64.iso"
FINAL_ISO_PATH="${OUTPUT_DIR}/${FINAL_ISO_NAME}"

if [[ -f "${RAW_ISO}" ]]; then
    mv "${RAW_ISO}" "${FINAL_ISO_PATH}"
    ISO_BYTES=$(stat -c%s "${FINAL_ISO_PATH}")
    ISO_MB=$((ISO_BYTES / 1024 / 1024))
    echo "[+] Generated Bootable ISO: ${FINAL_ISO_PATH}"
    echo "[+] Verified Size: ${ISO_MB} MB (${ISO_BYTES} bytes)"
else
    echo "[-] Error: Expected ISO file was not generated by live-build."
    exit 1
fi

# 6. Checksum and Manifest Generation
echo "[6/6] Generating SHA-256 verification checksums and manifest..."
cd "${OUTPUT_DIR}"
sha256sum "${FINAL_ISO_NAME}" > "${FINAL_ISO_NAME}.sha256"
cat "${FINAL_ISO_NAME}.sha256"

bash "${REPO_ROOT}/scripts/generate-manifest.sh" "${FINAL_ISO_PATH}"

echo "================================================================================"
echo "[✓] BUILD SUCCESSFUL: MONODESK OS 1.0 Universal PC Edition"
echo "[*] Image: ${FINAL_ISO_PATH}"
echo "[*] Checksum: ${OUTPUT_DIR}/${FINAL_ISO_NAME}.sha256"
echo "================================================================================"
