<#
.SYNOPSIS
    UYAP Doküman Editörü (.udf) ve Dosya İlişkilendirme Hızlı Onarım Aracı

.DESCRIPTION
    Bu betik, Adalet Bakanlığı UYAP Doküman Editörü'nün açılmama, UDF dosyalarının
    çift tıklandığında tanınmama, bozuk Java oturum önbelleği ve büyük dosyalarda
    yaşanan kilitlenme/yetersiz bellek (OutOfMemory) sorunlarını otomatik onarır.

.NOTES
    Yazar: E-İmza & Dijital Dönüşüm Portalı (https://uyap-teknik-destek.pages.dev/yazilar/uyap-dokuman-editoru-udf-acilmiyor-java-bellek-ayari.html)
    Lisans: MIT
#>

[CmdletBinding()]
param(
    [switch]$SkipCacheClear,
    [switch]$SkipAssociation,
    [string]$MemoryLimit = "",
    [switch]$Launch = $false
)

try {
    $OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}

Write-Host "==========================================================================================" -ForegroundColor Cyan
Write-Host "       UYAP DOKÜMAN EDİTÖRÜ (.udf) VE JAVA OTURUM ONARIM ARACI v1.1                       " -ForegroundColor Yellow
Write-Host "==========================================================================================`n" -ForegroundColor Cyan

# ------------------------------------------------------------------------------
# 1. UYAP Editör Kurulumunu Tespit Et
# ------------------------------------------------------------------------------
Write-Host "[1/4] UYAP Doküman Editörü Kurulumu Taranıyor..." -ForegroundColor White

$possiblePaths = @(
    "$env:LOCALAPPDATA\Programs\UYAP Dokuman Editoru\uyap.exe",
    "$env:LOCALAPPDATA\Programs\UYAP Doküman Editörü\uyap.exe",
    "$env:ProgramFiles\UYAP Dokuman Editoru\uyap.exe",
    "${env:ProgramFiles(x86)}\UYAP Dokuman Editoru\uyap.exe",
    "$env:USERPROFILE\UYAP Dokuman Editoru\uyap.exe"
)

$installedExe = $null
foreach ($p in $possiblePaths) {
    if (Test-Path $p) {
        $installedExe = $p
        break
    }
}

if ($installedExe) {
    Write-Host "  [OK] UYAP Editör bulundu: $installedExe" -ForegroundColor Green
} else {
    Write-Host "  [!] UYAP Editör varsayılan dizinlerde bulunamadı." -ForegroundColor Yellow
    Write-Host "      Resmi İndirme Linki: https://uyap.gov.tr/Uyap-Editor" -ForegroundColor Cyan
}

# ------------------------------------------------------------------------------
# 2. .udf Dosya İlişkilendirmesini Onar (Windows Registry)
# ------------------------------------------------------------------------------
if (-not $SkipAssociation -and $installedExe) {
    Write-Host "`n[2/4] .udf Dosya Uzantısı ve Simge İlişkilendirmesi Onarılıyor..." -ForegroundColor White
    try {
        # HKCU:\Software\Classes\.udf
        New-Item -Path "HKCU:\Software\Classes\.udf" -Value "UDF.Document" -Force | Out-Null
        Set-ItemProperty -Path "HKCU:\Software\Classes\.udf" -Name "Content Type" -Value "application/x-udf" -Force | Out-Null
        
        # HKCU:\Software\Classes\UDF.Document
        New-Item -Path "HKCU:\Software\Classes\UDF.Document" -Value "UYAP Dokümanı (.udf)" -Force | Out-Null

        # DefaultIcon
        $iconKey = "HKCU:\Software\Classes\UDF.Document\DefaultIcon"
        New-Item -Path $iconKey -Value "`"$installedExe`",0" -Force | Out-Null

        # Open Command
        $cmdKey = "HKCU:\Software\Classes\UDF.Document\shell\open\command"
        New-Item -Path $cmdKey -Value "`"$installedExe`" `"%1`"" -Force | Out-Null

        Write-Host "  [OK] .udf dosyaları ve sistem simgesi UYAP Editör ile başarıyla ilişkilendirildi!" -ForegroundColor Green
        Write-Host "       Artık .udf dosyalarına çift tıkladığınızda doğrudan UYAP Editör açılacaktır." -ForegroundColor Gray
    } catch {
        Write-Host "  [HATA] Kayıt defteri düzenlenemedi: $_" -ForegroundColor Red
    }
}

# ------------------------------------------------------------------------------
# 3. Bozuk UYAP ve Java Önbelleğini Temizle
# ------------------------------------------------------------------------------
if (-not $SkipCacheClear) {
    Write-Host "`n[3/4] Bozuk UYAP Oturum Dosyaları ve Geçici Önbellek Taranıyor..." -ForegroundColor White
    
    $uyapProfileDir = Join-Path $env:USERPROFILE ".uyap"
    if (Test-Path $uyapProfileDir) {
        # Sadece geçici/kilit dosyalarını temizle, kullanıcı ayarlarını koru
        $tempFiles = Get-ChildItem -Path $uyapProfileDir -Include "*.tmp", "*.lock", "*cache*", "*.log" -Recurse -ErrorAction SilentlyContinue
        if ($tempFiles.Count -gt 0) {
            $tempFiles | Remove-Item -Force -ErrorAction SilentlyContinue
            Write-Host "  [OK] $($tempFiles.Count) adet geçici kilit ve önbellek dosyası temizlendi." -ForegroundColor Green
        } else {
            Write-Host "  [OK] UYAP profil dizini temiz durumda." -ForegroundColor Green
        }
    } else {
        Write-Host "  [i] .uyap profil dizini henüz oluşmamış veya temiz." -ForegroundColor Gray
    }

    # Java Geçici Applet Önbelleğini Temizle
    $javaCache = Join-Path $env:LOCALAPPDATA "Sun\Java\Deployment\cache"
    if (Test-Path $javaCache) {
        Remove-Item "$javaCache\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  [OK] Java geçici önbelleği sıfırlandı." -ForegroundColor Green
    }
}

# ------------------------------------------------------------------------------
# 4. Java Bellek (Heap Memory) Yapılandırması (OutOfMemory Önleme)
# ------------------------------------------------------------------------------
Write-Host "`n[4/4] Java Bellek ve Performans Ayarları..." -ForegroundColor White
if ($MemoryLimit) {
    $uyapDir = if ($installedExe) { Split-Path $installedExe -Parent } else { $null }
    $targetVmOptions = if ($uyapDir -and (Test-Path $uyapDir)) { Join-Path $uyapDir "uyap.vmoptions" } else { Join-Path $env:USERPROFILE ".uyap\uyap.vmoptions" }
    
    try {
        $parentDir = Split-Path $targetVmOptions -Parent
        if (-not (Test-Path $parentDir)) { New-Item -ItemType Directory -Path $parentDir -Force | Out-Null }
        
        $vmContent = @("-Xms256m", "-Xmx$MemoryLimit", "-XX:+UseG1GC")
        $vmContent | Set-Content -Path $targetVmOptions -Encoding ASCII -Force
        Write-Host "  [OK] Java bellek sınırı ($MemoryLimit) yapılandırıldı: $targetVmOptions" -ForegroundColor Green
    } catch {
        Write-Host "  [!] Bellek yapılandırma dosyası yazılamadı: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [i] Özel bellek sınırı belirtilmedi. (Büyük dosyalar için '-MemoryLimit 2048m' kullanabilirsiniz)." -ForegroundColor Gray
}

if ($Launch -and $installedExe) {
    Write-Host "`n[*] UYAP Editör başlatılıyor: $installedExe" -ForegroundColor Green
    Start-Process $installedExe
}

Write-Host "`n==========================================================================================" -ForegroundColor Cyan
Write-Host " UYAP ONARIM İŞLEMİ TAMAMLANDI!                                                           " -ForegroundColor Green
Write-Host " UYAP Editörünü veya .udf dosyalarınızı artık sorunsuz açabilirsiniz.                     " -ForegroundColor White
Write-Host " Resmi UYAP İndirme Portalı: https://uyap.gov.tr/Uyap-Editor                               " -ForegroundColor Cyan
Write-Host "==========================================================================================`n" -ForegroundColor Cyan
