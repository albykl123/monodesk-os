with open(r'F:\anti\extracted_parts\2.img', 'rb') as f:
    data = bytearray(f.read())

orig = b"search.fs_uuid 5c987f1d-2633-4eec-a092-a4ba85ce499f root \nset prefix=($root)'/boot/grub'\nconfigfile $prefix/grub.cfg\n"
repl = b"search --no-floppy --file --set=root /.disk/info         \nset prefix=($root)'/boot/grub'\nconfigfile $prefix/grub.cfg\n"

assert len(orig) == len(repl) == 117
idx = data.find(orig)
assert idx != -1, "Target pattern not found in 2.img"
data[idx:idx+117] = repl

out_path = r'F:\anti\iso_staging\boot\grub\efi.img'
with open(out_path, 'wb') as f:
    f.write(data)

print('Patched efi.img successfully and written to', out_path)
