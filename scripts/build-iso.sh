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
chmod +x "${INCLUDES_DIR}/usr/bin/monodesk-profile-ctl"
cp "${REPO_ROOT}/services/monodesk-shell.service" "${INCLUDES_DIR}/etc/systemd/user/"

# Copy Full First-Party Applications Suite
cp "${REPO_ROOT}/applications/welcome/monodesk_welcome.py" "${INCLUDES_DIR}/usr/bin/monodesk-welcome"
cp "${REPO_ROOT}/applications/welcome/monodesk-welcome.desktop" "${INCLUDES_DIR}/usr/share/applications/"

cp "${REPO_ROOT}/applications/control-centre/monodesk_control_centre.py" "${INCLUDES_DIR}/usr/bin/monodesk-control-centre"
cp "${REPO_ROOT}/applications/control-centre/monodesk-control-centre.desktop" "${INCLUDES_DIR}/usr/share/applications/"

cp "${REPO_ROOT}/applications/hardware-report/monodesk_hardware_report.py" "${INCLUDES_DIR}/usr/bin/monodesk-hardware-centre"
cp "${REPO_ROOT}/applications/hardware-report/monodesk-hardware-report.desktop" "${INCLUDES_DIR}/usr/share/applications/"

cp "${REPO_ROOT}/applications/system-monitor/monodesk_system_monitor.py" "${INCLUDES_DIR}/usr/bin/monodesk-system-monitor"
cp "${REPO_ROOT}/applications/system-monitor/monodesk-system-monitor.desktop" "${INCLUDES_DIR}/usr/share/applications/"

cp "${REPO_ROOT}/applications/settings/monodesk_settings.py" "${INCLUDES_DIR}/usr/bin/monodesk-settings"
cp "${REPO_ROOT}/applications/settings/monodesk-settings.desktop" "${INCLUDES_DIR}/usr/share/applications/"

cp "${REPO_ROOT}/applications/update-manager/monodesk_update_manager.py" "${INCLUDES_DIR}/usr/bin/monodesk-updater"
cp "${REPO_ROOT}/applications/update-manager/monodesk-update-manager.desktop" "${INCLUDES_DIR}/usr/share/applications/"

cp "${REPO_ROOT}/applications/software-manager/monodesk_software_manager.py" "${INCLUDES_DIR}/usr/bin/monodesk-store"
cp "${REPO_ROOT}/applications/software-manager/monodesk-software-manager.desktop" "${INCLUDES_DIR}/usr/share/applications/"

cp "${REPO_ROOT}/applications/privacy/monodesk_privacy.py" "${INCLUDES_DIR}/usr/bin/monodesk-privacy"
cp "${REPO_ROOT}/applications/privacy/monodesk-privacy.desktop" "${INCLUDES_DIR}/usr/share/applications/"

cp "${REPO_ROOT}/applications/backup/monodesk_backup.py" "${INCLUDES_DIR}/usr/bin/monodesk-backup"
cp "${REPO_ROOT}/applications/backup/monodesk-backup.desktop" "${INCLUDES_DIR}/usr/share/applications/"

cp "${REPO_ROOT}/applications/recovery/monodesk_recovery.py" "${INCLUDES_DIR}/usr/bin/monodesk-recovery"
cp "${REPO_ROOT}/applications/recovery/monodesk-recovery.desktop" "${INCLUDES_DIR}/usr/share/applications/"

cp "${REPO_ROOT}/applications/workspace/monodesk_workspace.py" "${INCLUDES_DIR}/usr/bin/monodesk-workspace"
cp "${REPO_ROOT}/applications/workspace/monodesk-workspace.desktop" "${INCLUDES_DIR}/usr/share/applications/"

cp "${REPO_ROOT}/applications/ai-assistant/monodesk_ai.py" "${INCLUDES_DIR}/usr/bin/monodesk-ai"
cp "${REPO_ROOT}/applications/ai-assistant/monodesk-ai.desktop" "${INCLUDES_DIR}/usr/share/applications/"

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
