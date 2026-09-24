#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UYAP Editor & Java Environment Diagnostic Tool (Cross-Platform)
Checks Java version, UYAP installation, file associations, and environment.
Works on Windows, macOS, and Linux.
"""
import sys
import os
import subprocess
import platform

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

def diagnose():
    print("=" * 70)
    print(" UYAP Doküman Editörü & Java Ortam Teşhis Aracı (Çoklu Platform)")
    print("=" * 70)
    print(f"İşletim Sistemi: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Python Sürümü:   {platform.python_version()}")

    # 1. Java check
    print("\n[1/3] Java (JRE/JDK) Kontrolü:")
    java_found = False
    try:
        res = subprocess.run(["java", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out = res.stderr or res.stdout
        first_line = out.strip().split("\n")[0] if out else "Bilinmiyor"
        print(f"  ✅ Java kurulu: {first_line}")
        java_found = True
    except FileNotFoundError:
        print("  ❌ Java bulunamadı! PATH ortam değişkeninde 'java' komutu yer almıyor.")
        print("     İpucu: UYAP için Java 8 (1.8) veya Temurin/Adoptium JRE önerilir.")

    # 2. UYAP cache check
    print("\n[2/3] UYAP & Java Önbellek Durumu:")
    home = os.path.expanduser("~")
    cache_dirs = [
        os.path.join(home, ".uyap"),
        os.path.join(home, ".oracle_jre_usage"),
        os.path.join(home, "AppData", "Local", "Sun", "Java", "Deployment", "cache") if platform.system() == "Windows" else ""
    ]
    for c in cache_dirs:
        if c and os.path.exists(c):
            print(f"  📁 Önbellek klasörü bulundu: {c}")
        elif c:
            print(f"  ℹ️  Önbellek temiz: {c}")

    # 3. UYAP installation search
    print("\n[3/3] UYAP Editör Kurulumu:")
    found_editor = False
    if platform.system() == "Windows":
        candidates = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\UYAP Dokuman Editoru\uyap.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\UYAP Doküman Editörü\uyap.exe"),
            os.path.expandvars(r"%ProgramFiles%\UYAP Dokuman Editoru\uyap.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\UYAP Dokuman Editoru\uyap.exe")
        ]
    elif platform.system() == "Darwin": # macOS
        candidates = [
            "/Applications/UYAP Editor.app",
            "/Applications/UyapEditor.app",
            os.path.expanduser("~/Applications/UYAP Editor.app")
        ]
    else: # Linux
        candidates = [
            "/opt/uyap/uyap.jar",
            "/usr/local/bin/uyap",
            os.path.expanduser("~/uyap/uyap.jar")
        ]

    for cand in candidates:
        if cand and os.path.exists(cand):
            print(f"  ✅ UYAP Editör bulundu: {cand}")
            found_editor = True
            break

    if not found_editor:
        print("  ⚠️  UYAP Editör standart dizinlerde bulunamadı.")
        print("     Resmi indirme adresi: https://uyap.gov.tr/Uyap-Editor")

    print("\n" + "=" * 70)
    print("Teşhis tamamlandı.")

if __name__ == "__main__":
    diagnose()
