#!/usr/bin/env bash
# ==============================================================================
# MONODESK OS — Source Code & Configuration Quality Check
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== [MONODESK OS] Running Source Validation Suite ==="
ERRORS=0

# Determine working Python binary
PYTHON_BIN=""
for cmd in python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
        if "$cmd" -c "import sys" >/dev/null 2>&1; then
            PYTHON_BIN="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "[-] Error: No functional Python interpreter found."
    exit 1
fi

cd "${REPO_ROOT}"

# 1. Python compilation check
echo "[1/4] Checking Python source code syntax..."
while IFS= read -r py_file; do
    if ! "$PYTHON_BIN" -m py_compile "$py_file" 2>/dev/null; then
        echo "[-] Python syntax error in: $py_file"
        ERRORS=$((ERRORS + 1))
    fi
done < <(find . -type f \( -name "*.py" -o -name "monodesk-hw-detect" -o -name "monodesk-profile-ctl" \))

# 2. Shell script syntax check
echo "[2/4] Validating Shell script syntax..."
while IFS= read -r sh_file; do
    # Skip python scripts
    first_line=$(head -n 1 "$sh_file" 2>/dev/null || true)
    if [[ "$first_line" =~ python ]]; then
        continue
    fi
    if ! bash -n "$sh_file" 2>/dev/null; then
        echo "[-] Shell syntax error in: $sh_file"
        ERRORS=$((ERRORS + 1))
    fi
done < <(find . -type f \( -name "*.sh" -o -name "*.hook.chroot" -o -name "*-ctl" \) ! -name "monodesk-profile-ctl")

# 3. Desktop entry validation
echo "[3/4] Validating .desktop application entries..."
while IFS= read -r desk_file; do
    if command -v desktop-file-validate >/dev/null 2>&1; then
        if ! desktop-file-validate "$desk_file" 2>/dev/null; then
            echo "[-] Desktop file validation error in: $desk_file"
            ERRORS=$((ERRORS + 1))
        fi
    fi
done < <(find . -type f -name "*.desktop")

# 4. XML configuration validation
echo "[4/4] Validating XML configuration files..."
while IFS= read -r xml_file; do
    if command -v xmllint >/dev/null 2>&1; then
        if ! xmllint --noout "$xml_file" 2>/dev/null; then
            echo "[-] XML validation error in: $xml_file"
            ERRORS=$((ERRORS + 1))
        fi
    fi
done < <(find . -type f -name "*.xml")

if [ "$ERRORS" -eq 0 ]; then
    echo "[✓] Source code and configuration validation passed with 0 errors."
    exit 0
else
    echo "[-] Source validation failed with ${ERRORS} error(s)."
    exit 1
fi
