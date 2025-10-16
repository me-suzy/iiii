# Script pentru descarcarea unui binar msmtp static functional
Write-Host "Descarcare binar msmtp static pentru Linux x86_64..." -ForegroundColor Cyan
Write-Host ""

$outputPath = "E:\Downloads\msmtp-linux-static"

# URL-uri alternative pentru binare statice msmtp
# Vom incerca sa extragem din pachete Alpine (musl static)
$alpineVersion = "v3.19"
$packageUrl = "https://dl-cdn.alpinelinux.org/alpine/${alpineVersion}/community/x86_64/"

# Lista pachete msmtp disponibile
Write-Host "[INFO] Cautare pachete msmtp disponibile in Alpine Linux..." -ForegroundColor Yellow

try {
    # Descarca lista de pachete
    $packagesIndex = Invoke-WebRequest -Uri $packageUrl -UseBasicParsing
    $msmtpPackages = $packagesIndex.Links | Where-Object { $_.href -like "msmtp-*.apk" } | Select-Object -First 1
    
    if ($msmtpPackages) {
        $packageName = $msmtpPackages.href
        $fullUrl = $packageUrl + $packageName
        
        Write-Host "[OK] Gasit pachet: $packageName" -ForegroundColor Green
        Write-Host "[INFO] Descarcare din: $fullUrl" -ForegroundColor Yellow
        
        # Descarcare pachet APK
        $tempApk = Join-Path $env:TEMP "msmtp-temp.apk"
        Invoke-WebRequest -Uri $fullUrl -OutFile $tempApk -UseBasicParsing
        
        Write-Host "[OK] Pachet descarcat" -ForegroundColor Green
        
        # Extractie (APK este de fapt un arhiv tar.gz)
        Write-Host "[INFO] Extragere binar din pachet..." -ForegroundColor Yellow
        
        # Creaza director temporar
        $extractDir = Join-Path $env:TEMP "msmtp-extract"
        if (Test-Path $extractDir) {
            Remove-Item -Path $extractDir -Recurse -Force
        }
        New-Item -ItemType Directory -Path $extractDir | Out-Null
        
        # Folosim tar (disponibil in Windows 10+)
        Set-Location $extractDir
        tar -xf $tempApk
        
        # Gaseste binarul msmtp
        $msmtpBinary = Get-ChildItem -Path $extractDir -Recurse -Filter "msmtp" | Where-Object { $_.Extension -eq "" -and $_.Directory.Name -eq "bin" } | Select-Object -First 1
        
        if ($msmtpBinary) {
            # Copiaza binarul la destinatie
            Copy-Item -Path $msmtpBinary.FullName -Destination $outputPath -Force
            
            Write-Host ""
            Write-Host "======================================================================" -ForegroundColor Green
            Write-Host "  SUCCES! Binar msmtp static descarcat!" -ForegroundColor Green
            Write-Host "======================================================================"  -ForegroundColor Green
            Write-Host ""
            Write-Host "Locatie: $outputPath" -ForegroundColor White
            
            $fileInfo = Get-Item $outputPath
            Write-Host "Dimensiune: $([math]::Round($fileInfo.Length / 1KB, 2)) KB" -ForegroundColor White
            Write-Host ""
            
            # Curatare
            Remove-Item -Path $tempApk -Force -ErrorAction SilentlyContinue
            Remove-Item -Path $extractDir -Recurse -Force -ErrorAction SilentlyContinue
            
            Write-Host "[OK] Poti rula acum: python upload_and_test_msmtp.py" -ForegroundColor Cyan
            
        } else {
            Write-Host "[ERROR] Nu am gasit binarul msmtp in pachet!" -ForegroundColor Red
        }
        
    } else {
        Write-Host "[ERROR] Nu am gasit pachete msmtp in repository" -ForegroundColor Red
    }
    
} catch {
    Write-Host "[ERROR] Eroare la descarcare: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternativa: Descarca manual de pe:" -ForegroundColor Yellow
    Write-Host "  https://pkgs.alpinelinux.org/package/v3.19/community/x86_64/msmtp" -ForegroundColor White
    Write-Host "  Extrage fisierul 'usr/bin/msmtp' si salveaza-l ca:" -ForegroundColor White
    Write-Host "  $outputPath" -ForegroundColor White
}

