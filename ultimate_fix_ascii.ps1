Write-Host "Starting ASCII-SAFE Ultimate Fixer..."

$fileTypes = "*.html", "*.py", "*.txt", "*.md", "*.js", "*.css"

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "backup_$timestamp"
New-Item -ItemType Directory -Path $backupDir | Out-Null

$logFile = "repair_log_$timestamp.txt"
New-Item -ItemType File -Path $logFile | Out-Null

$fixMap = @{
    "Ã¢â‚¬â€œ" = "-"
    "Ã¢â‚¬â”" = "--"
    "Ã¢â‚¬Ëœ" = "'"
    "Ã¢â‚¬â„¢" = "'"
    "Ã¢â‚¬Å“" = "\""
    "Ã¢â‚¬Â " = "\""
    "Ã¢â‚¬Â¦" = "..."
    "Ã¢â‚¬Â¢" = "*"
    "Ã¢â€žÂ¢" = "TM"
    "â‚¹" = "Rs."
    "₹" = "Rs."
}

function Format-IndianNumber($number) {
    try { $num = [double]$number } catch { return $number }
    $n = "{0:N2}" -f $num
    return "Rs. $n"
}

$files = Get-ChildItem -Recurse -Include $fileTypes
$corruptedFiles = 0
$totalReplacements = 0

foreach ($file in $files) {

    $content = Get-Content $file.FullName -Raw
    $needsFix = $false

    foreach ($bad in $fixMap.Keys) {
        if ($content -match [regex]::Escape($bad)) {
            $needsFix = $true
        }
    }

    if ($needsFix) {

        $backupPath = Join-Path $backupDir ($file.FullName.Replace((Get-Location).Path, ""))
        $backupFolder = Split-Path $backupPath
        if (!(Test-Path $backupFolder)) { New-Item -ItemType Directory -Path $backupFolder | Out-Null }
        Copy-Item $file.FullName $backupPath -Force

        foreach ($bad in $fixMap.Keys) {
            $good = $fixMap[$bad]
            $count = ([regex]::Matches($content, [regex]::Escape($bad))).Count
            if ($count -gt 0) {
                $content = $content -replace [regex]::Escape($bad), $good
                $totalReplacements += $count
                Add-Content $logFile "[$($file.Name)] Replaced $bad -> $good ($count times)"
            }
        }

        Set-Content -Path $file.FullName -Value $content -Encoding UTF8
        
        $corruptedFiles++
        Write-Host "Fixed: $($file.FullName)"
    }
}

Write-Host ""
Write-Host "================ SUMMARY ================"
Write-Host "Backup folder: $backupDir"
Write-Host "Files repaired: $corruptedFiles"
Write-Host "Total replacements: $totalReplacements"
Write-Host "Log file: $logFile"
Write-Host "========================================="
Write-Host "ASCII-SAFE FIX COMPLETE"
