#!/usr/bin/env bash
# ==============================================================================
# MONODESK OS — Source Code & Configuration Quality Check
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== [MONODESK OS] Running Source Validation Suite ==="
ERRORS=0

# 1. Python compilation check
echo "[1/4] Checking Python source code syntax..."
while IFS= read -r py_file; do
    if ! python3 -m py_compile "$py_file" 2>/dev/null; then
        echo "[-] Python syntax error in: $py_file"
        ERRORS=$((ERRORS + 1))
    fi
done < <(find "${REPO_ROOT}" -type f -name "*.py")

# 2. Shell script syntax check
echo "[2/4] Validating Shell script syntax..."
while IFS= read -r sh_file; do
    if ! bash -n "$sh_file" 2>/dev/null; then
        echo "[-] Shell syntax error in: $sh_file"
        ERRORS=$((ERRORS + 1))
    fi
done < <(find "${REPO_ROOT}" -type f \( -name "*.sh" -o -name "*-ctl" -o -name "*.hook.chroot" \))

# 3. Desktop entry validation
echo "[3/4] Validating .desktop application entries..."
while IFS= read -r desk_file; do
    if command -v desktop-file-validate >/dev/null 2>&1; then
        if ! desktop-file-validate "$desk_file" 2>/dev/null; then
            echo "[-] Desktop file validation error in: $desk_file"
            ERRORS=$((ERRORS + 1))
        fi
    fi
done < <(find "${REPO_ROOT}" -type f -name "*.desktop")

# 4. XML configuration validation
echo "[4/4] Validating XML configuration files..."
while IFS= read -r xml_file; do
    if command -v xmllint >/dev/null 2>&1; then
        if ! xmllint --noout "$xml_file" 2>/dev/null; then
            echo "[-] XML validation error in: $xml_file"
            ERRORS=$((ERRORS + 1))
        fi
    fi
done < <(find "${REPO_ROOT}" -type f -name "*.xml")

if [ "$ERRORS" -eq 0 ]; then
    echo "[✓] Source code and configuration validation passed with 0 errors."
    exit 0
else
    echo "[-] Source validation failed with ${ERRORS} error(s)."
    exit 1
fi
