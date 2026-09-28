# UYAP Doküman Editörü Hızlı Onarım & Teşhis Aracı ⚖️⚡

[![Lisans: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Win | Mac | Linux](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue.svg)](https://github.com)
[![Blog](https://img.shields.io/badge/Rehber-UYAP%20Teknik%20Destek-red.svg)](https://uyapteknikdestek.site/)

Avukatlar, kâtipler ve bilirkişiler için **UYAP UDF Doküman Editörü açılmama, donma, gri ekranda kalma, Java bellek aşımı (`OutOfMemoryError`), ekran ölçekleme ve bozuk `.uyap` önbellek sorunlarını** tek tıkla onaran açık kaynaklı asistan.

---

## ✨ Öne Çıkan Özellikler

* 🧹 **Tek Tıkla Önbellek Temizleme:** Bozulmuş UYAP geçici dosyalarını (`.uyap` ve Java cache) `--clear-cache` ile sıfırlar.
* 🚀 **Yüksek Bellek (2GB RAM) Desteği:** 500+ sayfalık ağır dava dosyalarını açarken oluşan Java `OutOfMemoryError` çökmesini önlemek için optimize başlatıcı parametreleri (`-Xms512m -Xmx2048m`) sunar.
* 🖥️ **Çoklu Platform:** Windows, macOS (Sequoia / Sonoma) ve Linux dağıtımlarında Java çalışma ortamını denetler.
* 🔍 **UDF Dosya İlişkilendirme:** Windows'ta çift tıklandığında UDF dosyalarının otomatik açılmasını sağlar.

---

## 🚀 Hızlı Başlangıç

### 1. Sistem Teşhisi ve Durum Raporu
```bash
python diagnose_uyap.py
```

### 2. Bozuk Önbelleği Temizleme (Hemen Onar)
```bash
python diagnose_uyap.py --clear-cache
```

### 3. Windows PowerShell Tek Tıkla Onarım
```powershell
powershell -ExecutionPolicy Bypass -File .\Fix-UyapEditor.ps1
```

---

## 🔗 E-Dönüşüm & LegalTech Açık Kaynak Ekosistemi

Bu araç [eimza-kep](https://github.com/eimza-kep) organizasyonunun açık kaynak LegalTech ekosisteminin bir parçasıdır:

* 📝 **[udf2md](https://github.com/eimza-kep/udf2md):** UYAP UDF dosyalarını yapay zekanın (LLM/RAG) okuyabileceği Markdown ve JSON formatına dönüştürücü.
* 🖥️ **[uyap-web-udf-editor](https://github.com/eimza-kep/uyap-web-udf-editor):** Tarayıcıda Java gerektirmeden çalışan açık kaynak web UDF editörü.
* ☕ **[gib-java-guvenlik-cozucu](https://github.com/eimza-kep/gib-java-guvenlik-cozucu):** UYAP ve GİB Java güvenlik istisna ekleyici.
* ⚖️ **[avukat-muvekkil-on-kayit-scripti](https://github.com/eimza-kep/avukat-muvekkil-on-kayit-scripti):** Avukatlar için müvekkil ön görüşme ve çıkar çatışması kontrol portalı.
* 📊 **[avukat-hukuk-excel-hesaplamalari](https://github.com/eimza-kep/avukat-hukuk-excel-hesaplamalari):** Avukatlar için serbest meslek makbuzu, kıdem ve vekalet ücreti hesaplayıcı şablonlar.

---

## 📚 İlgili Teknik Rehberler
* 📄 [UYAP Editör Açılmıyor Hatası ve Java Bellek Sorunları Kesin Çözüm](https://uyapteknikdestek.site/yazilar/uyap-editor-acilmiyor-hatasi-kesin-cozum.html)
* 📄 [UDF Dosyası Nedir ve Telefondan/Mac'ten Nasıl Açılır?](https://uyapteknikdestek.site/yazilar/udf-dosyasi-nedir-telefondan-nasil-acilir.html)
* 📄 [DYS Doküman Yönetim Sistemi ve E-İmza Entegrasyonu Hataları](https://uyapteknikdestek.site/yazilar/dys-dokuman-yonetim-sistemi-eimza-entegrasyonu.html)

---

## ⚖️ Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.
