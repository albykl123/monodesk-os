# MONODESK OS 2.0.0 — Final ISO Release Asset Upload Verification

**Verification Date:** Mon Nov 16 04:45:31 UTC 2026 (10:15:31 IST)  
**Target Repository:** [albykl123/monodesk-os](https://github.com/albykl123/monodesk-os)  
**GitHub Release Tag:** [v2.0.0](https://github.com/albykl123/monodesk-os/releases/tag/v2.0.0)  

---

## 1. Asset Metadata & Integrity

| Property | Value |
| :--- | :--- |
| **Asset Name** | `monodesk-os-2.0.0-universal-amd64.iso` |
| **Local File Path** | `D:\anti\monodesk-os\releases\monodesk-os-2.0.0-universal-amd64.iso` |
| **File Size (Exact Bytes)** | `1,190,991,872 bytes` (1.11 GiB) |
| **File Size (Reported by GitHub)** | `1,190,991,872 bytes` |
| **SHA-256 Checksum** | `c3ca6813983f2518d2b5b27993231dc104d8041618c5ee974353423797847ac2` |
| **Volume ID** | `MONODESK_2_0_AMD64` |
| **Format** | Bootable Hybrid ISO (UEFI + BIOS / MBR El Torito) |
| **Target Distribution** | Debian 13 (Trixie) AMD64 |

---

## 2. GitHub Release Asset Verification

Asset record queried via GitHub CLI (`gh release view v2.0.0 --repo albykl123/monodesk-os --json assets`):

```json
{
  "id": "RA_kwDOVqtlz84s6PCF",
  "name": "monodesk-os-2.0.0-universal-amd64.iso",
  "size": 1190991872,
  "state": "uploaded",
  "contentType": "application/octet-stream",
  "createdAt": "2026-11-16T04:37:29Z",
  "updatedAt": "2026-11-16T04:45:19Z",
  "digest": "sha256:c3ca6813983f2518d2b5b27993231dc104d8041618c5ee974353423797847ac2",
  "url": "https://github.com/albykl123/monodesk-os/releases/download/v2.0.0/monodesk-os-2.0.0-universal-amd64.iso"
}
```

---

## 3. Public Download URL & HTTP Verification

- **Direct Download URL:**  
  [https://github.com/albykl123/monodesk-os/releases/download/v2.0.0/monodesk-os-2.0.0-universal-amd64.iso](https://github.com/albykl123/monodesk-os/releases/download/v2.0.0/monodesk-os-2.0.0-universal-amd64.iso)

- **HTTP HEAD Verification:**
  - **HTTP Status:** `302 Found` -> `200 OK`
  - **Content-Length:** `1190991872`
  - **Content-Type:** `application/octet-stream`
  - **Content-Disposition:** `attachment; filename=monodesk-os-2.0.0-universal-amd64.iso`
  - **Status:** **LIVE, VERIFIED AND READY FOR DEPLOYMENT**

---

## 4. Complete Release Asset Manifest on v2.0.0

| Filename | Size | Purpose / Description |
| :--- | :--- | :--- |
| `monodesk-os-2.0.0-universal-amd64.iso` | 1,190,991,872 bytes | Full installable Debian 13 Universal AMD64 ISO image |
| `monodesk-os-2.0.0-universal-amd64.iso.sha256` | 132 bytes | SHA-256 verification checksum file |
| `monodesk-os-2.0.0-universal-amd64.iso.boot_report.txt` | 724 bytes | QEMU automated UEFI + BIOS boot test verification report |
| `BUILD-MANIFEST-2.0.0.json` | 2,284 bytes | Build configuration and reproducible metadata manifest |
| `INSTALLATION-GUIDE.md` | 4,627 bytes | Hardware requirements and step-by-step flashing / installation guide |
| `RELEASE-NOTES-2.0.0.md` | 4,027 bytes | Detailed release notes and architecture documentation |
