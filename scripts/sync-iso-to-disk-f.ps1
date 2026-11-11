param (
    [string]$VmKey = "C:\anti\builder_key",
    [string]$VmHost = "127.0.0.1",
    [int]$VmPort = 2222,
    [string]$DestDirReleases = "F:\anti\monodesk-os\releases",
    [string]$DestDirSrc = "F:\anti\monodesk-os\src"
)

New-Item -ItemType Directory -Force -Path $DestDirReleases | Out-Null
New-Item -ItemType Directory -Force -Path $DestDirSrc | Out-Null

Write-Host "[*] Checking for generated ISO in builder VM..."
$remoteOutput = & "C:\Windows\System32\OpenSSH\ssh.exe" -i $VmKey -o StrictHostKeyChecking=no -p $VmPort root@$VmHost "find /root/monodesk-os/releases /root/monodesk-os/build/live-build -maxdepth 2 -name '*.iso' 2>/dev/null"

if ($remoteOutput) {
    $firstIso = ($remoteOutput -split "`n")[0].Trim()
    if ($firstIso) {
        Write-Host "[+] Found remote ISO: $firstIso"
        $targetPath = Join-Path $DestDirReleases "monodesk-os-1.0.0-universal-amd64.iso"
        Write-Host "[*] Syncing ISO to Disk F: ($targetPath)..."
        & "C:\Windows\System32\OpenSSH\scp.exe" -i $VmKey -o StrictHostKeyChecking=no -P $VmPort "root@${VmHost}:${firstIso}" "$targetPath"
        
        $targetSrc = Join-Path $DestDirSrc "monodesk-os-1.0.0-universal-amd64.iso"
        Write-Host "[*] Copying ISO to Disk F: src folder ($targetSrc)..."
        Copy-Item $targetPath $targetSrc -Force

        # Also copy checksums and manifests
        & "C:\Windows\System32\OpenSSH\scp.exe" -i $VmKey -o StrictHostKeyChecking=no -P $VmPort "root@${VmHost}:/root/monodesk-os/releases/*" "$DestDirReleases/" 2>$null

        $size = (Get-Item $targetPath).Length
        $mb = [math]::Round($size / 1MB, 2)
        Write-Host "[✓] ISO SUCCESSFUL ON DISK F: $targetPath ($mb MB)"
    }
} else {
    Write-Host "[-] ISO compilation in progress inside builder VM. Not ready yet."
}
