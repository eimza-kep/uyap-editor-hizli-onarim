#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UYAP Doküman Editörü & Java Ortam Teşhis, Hızlı Onarım ve Taşınabilir Paketleyici v1.3
====================================================================================
Windows, macOS ve Linux üzerinde Java sürümünü, UYAP Editör kurulumunu,
bozuk önbellek klasörlerini (`.uyap`, Java cache) denetler; bellek aşımı
(OutOfMemoryError) ve açılmama sorunlarını çözer; kurulumsuz taşınabilir
(portable) UYAP paketleri hazırlar ve acil durum UDF terminal okuyucusu sunar.

Özellikler:
- Java JRE/JDK çalışma ve sürüm denetimi (PATH ve alternatif dizinler)
- UYAP Editör tespiti ve UDF dosya ilişkilendirme kontrolü
- Otomatik bozuk önbellek temizleme (--clear-cache)
- Yüksek bellekli başlatıcı komutu üretme (--high-mem)
- Kurulumsuz Taşınabilir (Portable) Paketleyici (--make-portable)
- Java gerektirmeyen acil durum UDF metin görüntüleyici (--view)
- JSON ve Markdown formatında raporlama

Yazar: E-İmza & Dijital Dönüşüm Portalı (https://uyapteknikdestek.site/)
Lisans: MIT
"""

import sys
import os
import re
import shutil
import zipfile
import subprocess
import platform
import json
import argparse
from pathlib import Path

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

def check_java():
    """Java JRE/JDK çalışma durumunu ve sürümünü kontrol eder."""
    # 1. Standart PATH üzerinden dene
    try:
        res = subprocess.run(["java", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        out = res.stderr or res.stdout
        first_line = out.strip().split("\n")[0] if out else "Bilinmiyor"
        return {"installed": True, "version_string": first_line, "path": "java"}
    except Exception:
        pass

    # 2. macOS Homebrew ve Linux JVM dizinlerini tara
    fallback_paths = [
        "/opt/homebrew/opt/openjdk@8/bin/java",
        "/opt/homebrew/opt/openjdk@11/bin/java",
        "/opt/homebrew/opt/openjdk@17/bin/java",
        "/opt/homebrew/bin/java",
        "/usr/local/opt/openjdk@8/bin/java",
        "/usr/lib/jvm/default-java/bin/java"
    ]
    for fb in fallback_paths:
        if os.path.exists(fb) and os.access(fb, os.X_OK):
            try:
                res = subprocess.run([fb, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
                out = res.stderr or res.stdout
                first_line = out.strip().split("\n")[0] if out else "Bilinmiyor"
                return {"installed": True, "version_string": first_line, "path": fb}
            except Exception:
                pass

    return {"installed": False, "version_string": None, "path": None}

def find_uyap_editor():
    """Sistemde kurulu UYAP Editör uygulamasını veya editor.jar dosyasını arar."""
    candidates = []
    sys_name = platform.system()

    if sys_name == "Windows":
        candidates = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\UYAP Dokuman Editoru\uyap.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\UYAP Doküman Editörü\uyap.exe"),
            os.path.expandvars(r"%ProgramFiles%\UYAP Dokuman Editoru\uyap.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\UYAP Dokuman Editoru\uyap.exe"),
            os.path.expandvars(r"%USERPROFILE%\uyap\editor.jar")
        ]
    elif sys_name == "Darwin":
        candidates = [
            "/Applications/UYAP Editor.app",
            "/Applications/UyapEditor.app",
            "/Applications/UYAP.app",
            "/Applications/UyapDokumanEditor.app",
            "/Applications/UYAP Doküman Editörü.app",
            os.path.expanduser("~/Applications/UYAP Editor.app"),
            os.path.expanduser("~/Applications/UYAP Doküman Editörü.app"),
            os.path.expanduser("~/uyap/editor.jar")
        ]
    else: # Linux
        candidates = [
            "/opt/uyap/uyap.jar",
            "/usr/local/bin/uyap",
            os.path.expanduser("~/uyap/uyap.jar"),
            os.path.expanduser("~/.local/bin/uyap")
        ]

    for cand in candidates:
        if cand and os.path.exists(cand):
            return {"found": True, "path": cand}

    return {"found": False, "path": None}

def get_cache_directories():
    """Temizlenebilir UYAP ve Java önbellek dizinlerini tespit eder."""
    home = os.path.expanduser("~")
    sys_name = platform.system()
    dirs = [
        os.path.join(home, ".uyap"),
        os.path.join(home, ".uyap_cache"),
        os.path.join(home, ".oracle_jre_usage")
    ]
    
    if sys_name == "Windows":
        dirs.append(os.path.join(home, "AppData", "Local", "Sun", "Java", "Deployment", "cache"))
        dirs.append(os.path.join(home, "AppData", "Roaming", "UYAP", "cache"))
    elif sys_name == "Darwin":
        dirs.append(os.path.join(home, "Library", "Caches", "Oracle", "Java", "Deployment", "cache"))
        dirs.append(os.path.join(home, "Library", "Application Support", "UYAP", "cache"))
    else:
        dirs.append(os.path.join(home, ".java", "deployment", "cache"))

    status = []
    for d in dirs:
        if d:
            status.append({"path": d, "exists": os.path.exists(d)})
    return status

def clear_uyap_caches():
    """Bozuk UYAP ve Java önbellek dosyalarını temizler."""
    cleaned = []
    for item in get_cache_directories():
        p = item["path"]
        if os.path.exists(p):
            try:
                if os.path.isdir(p):
                    shutil.rmtree(p, ignore_errors=True)
                else:
                    os.remove(p)
                cleaned.append(p)
            except Exception:
                pass
    return cleaned

def quick_view_udf(file_path):
    """
    Java veya UYAP kurulu olmadan UDF (.udf) dosyasının metin içeriğini
    acil durumlarda (duruşma salonu vb.) doğrudan terminalde görüntüler.
    """
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"UDF dosyası bulunamadı: {file_path}")

    xml_text = None
    with open(p, "rb") as f:
        file_bytes = f.read()

    # 1. Zip kontrolü
    if zipfile.is_zipfile(p):
        with zipfile.ZipFile(p, "r") as zf:
            for name in zf.namelist():
                if name.lower().endswith("content.xml") or name.lower().endswith(".xml"):
                    raw = zf.read(name)
                    try:
                        xml_text = raw.decode("utf-8")
                    except UnicodeDecodeError:
                        xml_text = raw.decode("windows-1254", errors="replace")
                    break
    else:
        try:
            xml_text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            xml_text = file_bytes.decode("windows-1254", errors="replace")

    if not xml_text:
        raise ValueError("UDF içeriğinde XML metin akışı tespit edilemedi.")

    # Metin temizleme
    # <content ...>metin</content>
    content_matches = re.findall(r'<content\b[^>]*>([\s\S]*?)<\/content>', xml_text, re.IGNORECASE)
    if content_matches:
        raw_text = " ".join(content_matches)
    else:
        raw_text = re.sub(r'<[^>]+>', ' ', xml_text)

    # XML entity çözücü
    clean = (raw_text.replace("&lt;", "<")
                     .replace("&gt;", ">")
                     .replace("&quot;", '"')
                     .replace("&apos;", "'")
                     .replace("&amp;", "&"))
    clean = re.sub(r'[ \t]+', ' ', clean)
    clean = re.sub(r'\n{3,}', '\n\n', clean).strip()

    # Mahkeme ve Esas No tespiti
    court_match = re.search(r'([A-ZÇĞİÖŞÜ0-9\.\s]{3,70}\s+(?:MAHKEMESİNE|HAKİMLİĞİNE|BAŞKANLIĞINA|MÜDÜRLÜĞÜNE))', clean, re.IGNORECASE)
    esas_match = re.search(r'(?:ESAS\s*NO?\s*[:\.\/]?\s*([0-9]{4}\s*[\/\-]\s*[0-9]+))', clean, re.IGNORECASE)

    return {
        "file_name": p.name,
        "court": court_match.group(1).strip() if court_match else None,
        "case_number": esas_match.group(1).replace(" ", "") if esas_match else None,
        "text": clean
    }

def create_portable_bundle(target_dir, memory_mb=1024):
    """
    Yabancı bilgisayarlarda Java kurma yetkisi (admin) olmadan UDF açabilmek için
    taşınabilir (portable) klasör ve tek tıkla başlatıcı scriptleri üretir.
    """
    out_dir = Path(target_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    jre_dir = out_dir / "jre"
    uyap_dir = out_dir / "uyap"
    jre_dir.mkdir(exist_ok=True)
    uyap_dir.mkdir(exist_ok=True)

    # 1. Windows run-uyap.bat
    bat_content = f"""@echo off
chcp 65001 >nul
title UYAP Doküman Editörü (Kurulumsuz Taşınabilir)
set SCRIPT_DIR=%~dp0
set JAVA_EXE=%SCRIPT_DIR%jre\\bin\\java.exe

if not exist "%JAVA_EXE%" (
    where java >nul 2>&1
    if %errorlevel% equ 0 (
        set JAVA_EXE=java
    ) else (
        echo ======================================================================
        echo [HATA] Taşınabilir Java (jre\\bin\\java.exe) veya sistem Java'sı bulunamadı!
        echo Lütfen 'jre' klasörüne taşınabilir OpenJDK 8 / 11 JRE runtime kopyalayınız.
        echo ======================================================================
        pause
        exit /b 1
    )
)

set UYAP_JAR=%SCRIPT_DIR%uyap\\editor.jar
if not exist "%UYAP_JAR%" (
    set UYAP_JAR=%SCRIPT_DIR%uyap\\uki.jar
)
if not exist "%UYAP_JAR%" (
    echo ======================================================================
    echo [UYARI] 'uyap' klasöründe 'editor.jar' veya 'uki.jar' bulunamadı!
    echo Lütfen resmi UYAP Editör JAR dosyasını bu klasöre kopyalayınız.
    echo İndirme: https://uyap.gov.tr/Uyap-Editor
    echo ======================================================================
    pause
    exit /b 1
)

echo [UYAP Taşınabilir] Başlatılıyor (Bellek: {memory_mb} MB)...
start "" "%JAVA_EXE%" -Xms256m -Xmx{memory_mb}m -Dsun.java2d.uiScale=1.0 -jar "%UYAP_JAR%" %*
"""
    with open(out_dir / "run-uyap.bat", "w", encoding="utf-8") as f:
        f.write(bat_content)

    # 2. Linux / macOS run-uyap.sh
    sh_content = f"""#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
JAVA_BIN="$SCRIPT_DIR/jre/bin/java"

if [ ! -f "$JAVA_BIN" ]; then
    if command -v java >/dev/null 2>&1; then
        JAVA_BIN="java"
    else
        echo "Hata: Taşınabilir Java ($SCRIPT_DIR/jre/bin/java) veya sistem Java'sı bulunamadı."
        exit 1
    fi
fi

UYAP_JAR="$SCRIPT_DIR/uyap/editor.jar"
if [ ! -f "$UYAP_JAR" ]; then
    UYAP_JAR="$SCRIPT_DIR/uyap/uki.jar"
fi

if [ ! -f "$UYAP_JAR" ]; then
    echo "Hata: '$SCRIPT_DIR/uyap/' klasöründe editor.jar bulunamadı."
    exit 1
fi

"$JAVA_BIN" -Xms256m -Xmx{memory_mb}m -Dsun.java2d.uiScale=1.0 -jar "$UYAP_JAR" "$@"
"""
    with open(out_dir / "run-uyap.sh", "w", encoding="utf-8") as f:
        f.write(sh_content)
    try:
        os.chmod(out_dir / "run-uyap.sh", 0o755)
    except Exception:
        pass

    # 3. PowerShell run-uyap.ps1
    ps_content = f"""# UYAP Taşınabilir PowerShell Başlatıcı
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$JavaExe = Join-Path $ScriptDir "jre\\bin\\java.exe"
if (-not (Test-Path $JavaExe)) {{
    $JavaExe = "java"
}}

$UyapJar = Join-Path $ScriptDir "uyap\\editor.jar"
if (-not (Test-Path $UyapJar)) {{
    $UyapJar = Join-Path $ScriptDir "uyap\\uki.jar"
}}

& $JavaExe -Xms256m -Xmx{memory_mb}m -Dsun.java2d.uiScale=1.0 -jar $UyapJar $args
"""
    with open(out_dir / "run-uyap.ps1", "w", encoding="utf-8") as f:
        f.write(ps_content)

    # 4. Kullanım Kılavuzu
    guide_content = """UYAP DOKÜMAN EDİTÖRÜ (KURULUMSUZ TAŞINABİLİR USB PAKETİ)
======================================================================
Bu paket, adliyelerde veya yabancı bilgisayarlarda yönetici (admin) yetkisi
ve Java kurulumu olmadan UDF dosyalarını açabilmeniz için tasarlanmıştır.

NASIL KULLANILIR?
1. 'jre' klasörüne taşınabilir OpenJDK 8 JRE içeriğini kopyalayınız (bin\\java.exe).
2. 'uyap' klasörüne resmi 'editor.jar' veya 'uki.jar' dosyasını koyunuz.
3. Windows'ta 'run-uyap.bat' dosyasına çift tıklayınız veya bir .udf dosyasını
   bu .bat dosyası üzerine sürükleyip bırakınız.
4. Linux/macOS üzerinde './run-uyap.sh' betiğini çalıştırınız.

Açık Kaynak Destek:
- https://github.com/eimza-kep/uyap-editor-hizli-onarim
- https://github.com/eimza-kep/udf2md
======================================================================
"""
    with open(out_dir / "KULLANIM_KILAVUZU.txt", "w", encoding="utf-8") as f:
        f.write(guide_content)

    # 5. Manifest
    manifest = {
        "bundle_name": "UYAP-Portable-Bundle",
        "version": "1.3",
        "memory_mb": memory_mb,
        "directories": ["jre", "uyap"],
        "launchers": ["run-uyap.bat", "run-uyap.sh", "run-uyap.ps1"]
    }
    with open(out_dir / "portable_config.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return {
        "target_dir": str(out_dir),
        "files_created": ["run-uyap.bat", "run-uyap.sh", "run-uyap.ps1", "KULLANIM_KILAVUZU.txt", "portable_config.json"],
        "memory_mb": memory_mb
    }

def run_diagnostics():
    """Java ortamı ve UYAP editör teşhisini çalıştırır."""
    java_info = check_java()
    editor_info = find_uyap_editor()
    caches = get_cache_directories()

    return {
        "os": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "python_version": platform.python_version(),
        "java": java_info,
        "editor": editor_info,
        "cache_dirs": caches,
        "recommended_command": "java -Xms512m -Xmx2048m -Dsun.java2d.uiScale=1.0 -jar <editor.jar>"
    }


def clean_javaws_cache():
    """Java Web Start geçici önbelleğini temizler."""
    import shutil
    user_home = os.path.expanduser("~")
    javaws_dir = os.path.join(user_home, "AppData", "LocalLow", "Sun", "Java", "Deployment", "cache")
    if os.path.exists(javaws_dir):
        try:
            shutil.rmtree(javaws_dir)
            return True
        except Exception:
            return False
    return False

def main():
    parser = argparse.ArgumentParser(description="UYAP Doküman Editörü, Java Teşhis ve Taşınabilir Paketleyici v1.3")
    parser.add_argument("--json", action="store_true", help="JSON formatında çıktı verir")
    parser.add_argument("--clear-cache", action="store_true", help="Bozulmuş UYAP ve Java önbelleğini sıfırlar")
    parser.add_argument("--high-mem", action="store_true", help="Büyük dosyalar için yüksek bellekli başlatma komutu önerir")
    parser.add_argument("--make-portable", nargs="?", const="./uyap-portable", help="Kurulumsuz taşınabilir paket klasörü oluşturur (varsayılan: ./uyap-portable)")
    parser.add_argument("--view", help="Java olmadan UDF belgesinin metnini acil durumda terminalde görüntüler")

    args = parser.parse_args()

    # Acil durum UDF görüntüleme
    if args.view:
        try:
            udf_data = quick_view_udf(args.view)
            if args.json:
                print(json.dumps(udf_data, indent=2, ensure_ascii=False))
            else:
                print("=" * 75)
                print(f"      UYAP UDF ACİL GÖRÜNTÜLEYİCİ: {udf_data['file_name']}")
                print("=" * 75)
                if udf_data["court"]:
                    print(f"🏛️ Mahkeme : {udf_data['court']}")
                if udf_data["case_number"]:
                    print(f"⚖️ Esas No : {udf_data['case_number']}")
                print("-" * 75)
                print(udf_data["text"][:2500] + ("\n\n[... Belgenin devamı için udf2md veya UYAP Editör kullanınız ...]" if len(udf_data["text"]) > 2500 else ""))
                print("=" * 75)
        except Exception as e:
            print(f"[!] Hata: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # Taşınabilir Paketleyici
    if args.make_portable:
        res = create_portable_bundle(args.make_portable)
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print("=" * 70)
            print("       UYAP TAŞINABİLİR (PORTABLE) PAKET HAZIRLANDI v1.3")
            print("=" * 70)
            print(f"Hedef Klasör   : {res['target_dir']}")
            print(f"Bellek Limiti  : {res['memory_mb']} MB")
            print("Oluşturulanlar : " + ", ".join(res["files_created"]))
            print("\nAdliye Kullanım Adımları:")
            print("1. 'uyap/' klasörüne resmi 'editor.jar' dosyasını kopyalayınız.")
            print("2. 'jre/' klasörüne taşınabilir OpenJDK JRE runtime koyunuz.")
            print("3. Flash belleği takıp 'run-uyap.bat' ile doğrudan başlatınız.")
            print("=" * 70)
        return

    # Önbellek temizleme
    if args.clear_cache:
        cleaned = clear_uyap_caches()
        print("=" * 65)
        print("          UYAP & JAVA ÖNBELLEK TEMİZLEME İŞLEMİ")
        print("=" * 65)
        if cleaned:
            for c in cleaned:
                print(f"  ✓ Temizlendi: {c}")
            print("\n[OK] Önbellek sıfırlandı. UYAP Editörü yeniden başlatabilirsiniz.")
        else:
            print("[INFO] Önbellek zaten temiz veya silinecek dizin bulunamadı.")
        print("=" * 65)
        return

    diag = run_diagnostics()

    if args.json:
        print(json.dumps(diag, indent=2, ensure_ascii=False))
        return

    print("=" * 70)
    print("  UYAP Doküman Editörü & Java Ortam Teşhis Aracı v1.3")
    print("=" * 70)
    print(f"İşletim Sistemi: {diag['os']}")
    print(f"Python Sürümü:   {diag['python_version']}")

    print("\n[1/3] Java Durumu:")
    if diag["java"]["installed"]:
        print(f"  ✅ Java Kurulu: {diag['java']['version_string']}")
    else:
        print("  ❌ Java bulunamadı! PATH ortam değişkeninde 'java' yer almıyor.")
        print("     Öneri: UYAP için Java 8 (1.8) veya Eclipse Temurin JRE kurunuz.")

    print("\n[2/3] UYAP Editör Kurulumu:")
    if diag["editor"]["found"]:
        print(f"  ✅ UYAP Editör Bulundu: {diag['editor']['path']}")
    else:
        print("  ⚠️  UYAP Editör standart dizinlerde bulunamadı.")
        print("     Resmi İndirme: https://uyap.gov.tr/Uyap-Editor")

    print("\n[3/3] Önbellek Klasörleri:")
    for c in diag["cache_dirs"]:
        icon = "📁 Bulundu" if c["exists"] else "ℹ️ Temiz"
        print(f"  {icon:<10}: {c['path']}")

    if args.high_mem:
        print("\n[+] Büyük UDF Belgeleri İçin Optimize Başlatma Komutu:")
        print(f"    {diag['recommended_command']}")

    print("\n" + "=" * 70)
    print("Önbellek temizlemek için         : python diagnose_uyap.py --clear-cache")
    print("Kurulumsuz USB paketi oluşturmak : python diagnose_uyap.py --make-portable")
    print("Acil durumda UDF okumak için     : python diagnose_uyap.py --view dava.udf")

if __name__ == "__main__":
    main()
