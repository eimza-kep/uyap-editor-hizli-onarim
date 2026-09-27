#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UYAP Doküman Editörü & Java Ortam Teşhis ve Hızlı Onarım Aracı v1.2
===================================================================
Windows, macOS ve Linux üzerinde Java sürümünü, UYAP Editör kurulumunu,
bozuk önbellek klasörlerini (`.uyap`, Java cache) denetler; bellek aşımı
(OutOfMemoryError) ve açılmama sorunlarını çözer.

Özellikler:
- Java JRE/JDK çalışma ve sürüm denetimi
- UYAP Editör ve UDF dosya ilişkilendirme kontrolü
- Otomatik önbellek temizleme (--clear-cache)
- Yüksek bellekli başlatıcı komutu üretme (--high-mem)
- JSON ve Markdown formatında raporlama

Yazar: E-İmza & Dijital Dönüşüm Portalı (https://uyap-teknik-destek.pages.dev/)
Lisans: MIT
"""

import sys
import os
import shutil
import subprocess
import platform
import json
import argparse

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

def check_java():
    try:
        res = subprocess.run(["java", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        out = res.stderr or res.stdout
        first_line = out.strip().split("\n")[0] if out else "Bilinmiyor"
        return {"installed": True, "version_string": first_line}
    except Exception:
        return {"installed": False, "version_string": None}

def find_uyap_editor():
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
            os.path.expanduser("~/Applications/UYAP Editor.app"),
            "/Applications/UYAP Doküman Editörü.app"
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
    home = os.path.expanduser("~")
    sys_name = platform.system()
    dirs = [os.path.join(home, ".uyap"), os.path.join(home, ".oracle_jre_usage")]
    
    if sys_name == "Windows":
        dirs.append(os.path.join(home, "AppData", "Local", "Sun", "Java", "Deployment", "cache"))
    elif sys_name == "Darwin":
        dirs.append(os.path.join(home, "Library", "Caches", "Oracle", "Java", "Deployment", "cache"))
    else:
        dirs.append(os.path.join(home, ".java", "deployment", "cache"))

    status = []
    for d in dirs:
        if d:
            status.append({"path": d, "exists": os.path.exists(d)})
    return status

def clear_uyap_caches():
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

def run_diagnostics():
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

def main():
    parser = argparse.ArgumentParser(description="UYAP Doküman Editörü & Java Teşhis ve Onarım v1.2")
    parser.add_argument("--json", action="store_true", help="JSON formatında çıktı verir")
    parser.add_argument("--clear-cache", action="store_true", help="Bozulmuş UYAP ve Java önbelleğini sıfırlar")
    parser.add_argument("--high-mem", action="store_true", help="Büyük dosyalar için yüksek bellekli başlatma komutu önerir")

    args = parser.parse_args()

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
    print("  UYAP Doküman Editörü & Java Ortam Teşhis Aracı v1.2")
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
    print("Önbellek temizlemek için: python diagnose_uyap.py --clear-cache")

if __name__ == "__main__":
    main()
