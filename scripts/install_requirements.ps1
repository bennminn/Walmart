$requirements = Get-Content requirements.txt
foreach ($package in $requirements) {
    $trimmed = $package.Trim()
    if ($trimmed -and -not $trimmed.StartsWith("#")) {
        Write-Host "Installing: $trimmed"
        pip install $trimmed
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Installation failed for package: $trimmed"
            break
        } else {
            Write-Host "✅ Successfully installed: $trimmed"
        }
    }
}
