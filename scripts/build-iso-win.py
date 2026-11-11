import os
import sys
import time
import shutil
import hashlib
import pathlib
import pycdlib

def make_clean_iso_name(name, is_dir=False, used_names=None):
    if used_names is None:
        used_names = set()
    clean = ''
    for ch in name.upper():
        if ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_':
            clean += ch
        else:
            clean += '_'
    if is_dir:
        base = clean[:24] if clean else 'DIR'
        cand = base
        count = 1
        while cand in used_names:
            cand = f"{base[:18]}_{count}"
            count += 1
        used_names.add(cand)
        return cand
    else:
        parts = name.rsplit('.', 1)
        base = parts[0]
        ext = parts[1] if len(parts) > 1 else ''
        
        c_base = ''.join(ch if ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_' else '_' for ch in base.upper())
        c_ext = ''.join(ch if ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_' else '_' for ch in ext.upper())
        
        c_base = c_base[:22] if c_base else 'FILE'
        c_ext = c_ext[:4]
        
        cand_base = c_base
        count = 1
        cand = f"{cand_base}.{c_ext};1" if c_ext else f"{cand_base};1"
        while cand in used_names:
            cand_base = f"{c_base[:16]}_{count}"
            cand = f"{cand_base}.{c_ext};1" if c_ext else f"{cand_base};1"
            count += 1
        used_names.add(cand)
        return cand

def build_iso():
    staging_root = pathlib.Path(r'F:\anti\iso_staging')
    output_iso = pathlib.Path(r'F:\anti\monodesk-os\releases\monodesk-os-1.0.0-universal-amd64.iso')
    output_iso.parent.mkdir(parents=True, exist_ok=True)
    
    print("[*] Initializing PyCdlib for MONODESK OS 1.0 Universal PC Edition...")
    iso = pycdlib.PyCdlib()
    iso.new(interchange_level=3,
            joliet=3,
            rock_ridge='1.09',
            vol_ident='MONODESK_1_0_X64',
            sys_ident='LINUX',
            app_ident_str='MONODESK OS 1.0',
            preparer_ident_str='MONODESK ENG',
            pub_ident_str='MONODESK PROJECT')

    dir_map = {staging_root: ('', '')}
    used_names_per_dir = {'': set()}
    
    all_dirs = []
    for root, dirs, files in os.walk(staging_root):
        root_path = pathlib.Path(root)
        for d in sorted(dirs):
            all_dirs.append(root_path / d)
            
    print(f"[*] Creating {len(all_dirs)} directories...")
    for d_path in all_dirs:
        parent_dir = d_path.parent
        parent_iso, parent_joliet = dir_map[parent_dir]
        d_name = d_path.name
        
        used_set = used_names_per_dir[parent_iso]
        iso_name = make_clean_iso_name(d_name, is_dir=True, used_names=used_set)
        
        iso_dir_path = f"{parent_iso}/{iso_name}"
        joliet_dir_path = f"{parent_joliet}/{d_name}"
        
        used_names_per_dir[iso_dir_path] = set()
        dir_map[d_path] = (iso_dir_path, joliet_dir_path)
        
        iso.add_directory(iso_dir_path, rr_name=d_name, joliet_path=joliet_dir_path)

    all_files = []
    for root, dirs, files in os.walk(staging_root):
        root_path = pathlib.Path(root)
        for f in sorted(files):
            all_files.append(root_path / f)
            
    print(f"[*] Adding {len(all_files)} files to ISO filesystem...")
    bios_iso_file = None
    efi_iso_file = None

    for f_path in all_files:
        parent_dir = f_path.parent
        parent_iso, parent_joliet = dir_map[parent_dir]
        f_name = f_path.name
        
        used_set = used_names_per_dir[parent_iso]
        iso_file_name = make_clean_iso_name(f_name, is_dir=False, used_names=used_set)
        
        iso_file_path = f"{parent_iso}/{iso_file_name}"
        joliet_file_path = f"{parent_joliet}/{f_name}"
        
        # Track boot images
        rel = f_path.relative_to(staging_root).as_posix()
        if rel == 'boot/grub/cdboot.img':
            bios_iso_file = iso_file_path
        elif rel == 'boot/grub/efi.img':
            efi_iso_file = iso_file_path

        f_mode = 0o100755 if ('usr/bin/' in rel or rel.endswith('.sh')) else 0o100644
        iso.add_file(str(f_path), iso_file_path, rr_name=f_name, joliet_path=joliet_file_path, file_mode=f_mode)

    assert bios_iso_file is not None, "BIOS boot image not found!"
    assert efi_iso_file is not None, "EFI boot image not found!"

    print(f"[*] Registering El Torito BIOS boot record: {bios_iso_file}")
    iso.add_eltorito(bios_iso_file, platform_id=0, media_name='noemul', boot_load_size=4, boot_info_table=False)

    print(f"[*] Registering El Torito UEFI boot record: {efi_iso_file}")
    iso.add_eltorito(efi_iso_file, efi=True, platform_id=0xef, media_name='noemul', boot_load_size=0)

    print(f"[*] Writing hybrid bootable ISO directly on Disk F: -> {output_iso}")
    start_time = time.time()
    iso.write(str(output_iso))
    iso.close()
    elapsed = time.time() - start_time
    
    size_bytes = output_iso.stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    print(f"[✓] ISO generation completed in {elapsed:.2f} seconds!")
    print(f"[✓] Final ISO Size: {size_mb:.2f} MB ({size_bytes} bytes)")
    
    # Sync to src directories on Disk F as requested by user
    targets = [
        pathlib.Path(r'F:\anti\monodesk-os\src\monodesk-os-1.0.0-universal-amd64.iso'),
        pathlib.Path(r'F:\anti\src\monodesk-os-1.0.0-universal-amd64.iso'),
    ]
    for tgt in targets:
        tgt.parent.mkdir(parents=True, exist_ok=True)
        print(f"[*] Mirroring ISO to {tgt}...")
        shutil.copy2(output_iso, tgt)

    # Compute SHA-256 checksum
    print("[*] Computing SHA-256 verification checksum...")
    sha256 = hashlib.sha256()
    with open(output_iso, 'rb') as f:
        while chunk := f.read(1024 * 1024):
            sha256.update(chunk)
    hex_digest = sha256.hexdigest()
    print(f"[✓] SHA-256: {hex_digest}")

    sha_file = output_iso.parent / 'monodesk-os-1.0.0-universal-amd64.iso.sha256'
    sha_file.write_text(f"{hex_digest}  monodesk-os-1.0.0-universal-amd64.iso\n", encoding='utf-8')
    
    sums_file = output_iso.parent / 'SHA256SUMS.txt'
    sums_file.write_text(f"{hex_digest}  monodesk-os-1.0.0-universal-amd64.iso\n", encoding='utf-8')

if __name__ == '__main__':
    build_iso()
