# UYAP Doküman Editörü & Java Hızlı Onarım ve Taşınabilir Paketleyici ⚖️⚡

[![Python CI](https://github.com/eimza-kep/uyap-editor-hizli-onarim/actions/workflows/ci.yml/badge.svg)](https://github.com/eimza-kep/uyap-editor-hizli-onarim/actions)
[![Lisans: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Win | Linux | Mac](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blue.svg)](https://github.com)
[![Blog](https://img.shields.io/badge/Rehber-UYAP%20Teknik%20Destek-red.svg)](https://uyapteknikdestek.site/)

Avukatlar, katipler ve vatandaşlar için UYAP Doküman Editörü'nün açılmama, Java bellek aşımı (`OutOfMemoryError`), donma ve bozuk önbellek (`.uyap` cache) sorunlarını tek komutla çözen; **adliyelerde ve duruşma salonlarında yabancı bilgisayarlarda yönetici yetkisi (admin) olmadan UDF açabilmek için kurulumsuz taşınabilir (portable) USB paketi hazırlayan** ve Java olmadan UDF okuyabilen açık kaynaklı teşhis asistanı.

---

## ✨ Öne Çıkan Özellikler (v1.3)

* 💼 **Kurulumsuz Taşınabilir (Portable) Paketleyici:** `--make-portable` ile OpenJDK ve UYAP JAR içeren, USB bellekten doğrudan çalışan ve admin yetkisi gerektirmeyen paket üretimi.
* 📄 **Java Gerektirmeyen Acil UDF Okuyucu:** Java bozuk veya yüklü olmadığında bile duruşma salonunda `--view dava.udf` komutuyla dilekçe ve kararları anında terminalde okuma.
* 🧹 **Tek Tıkla Önbellek Temizleme:** `--clear-cache` parametresi ile bozulmuş `.uyap`, Java deployment ve geçici kilit dosyalarını sıfırlar.
* 🚀 **Yüksek Bellekli Başlatıcı:** 200+ sayfalık devasa dava dosyalarında yaşanan RAM kilitlenmelerini önleyen `-Xmx2048m` optimize komutları üretir.
* 🖥️ **Çoklu Platform:** Windows (10/11), macOS (Apple Silicon M1-M4 & Intel) ve Linux ortamlarını otomatik tespit eder.
* 📊 **Otomasyon & CI/CD Desteği:** JSON ve Markdown formatında raporlama.

---

## 🛠️ Kurulum ve Yerel Geliştirme (Local Setup)

### Sistem Gereksinimleri
- Python 3.8 veya üzeri
- `git`
- (İsteğe bağlı) Windows PowerShell veya Bash

### 1. Depoyu Klonlama ve Çalışma Ortamı
```bash
# Depoyu klonlayın
git clone https://github.com/eimza-kep/uyap-editor-hizli-onarim.git
cd uyap-editor-hizli-onarim

# Sanal ortam (virtualenv) oluşturma ve aktifleştirme (Opsiyonel)
python -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
```

### 2. Birim Testleri Çalıştırma
```bash
python test_diagnose_uyap.py
```
veya `unittest` keşif mekanizmasıyla:
```bash
python -m unittest discover -v
```

---

## 💼 Kurulumsuz Taşınabilir (Portable) USB Paketi Hazırlama

Adliyelerdeki bilgisayarlarda Java kurma yetkiniz (admin parolası) yoksa flash belleğinizden doğrudan çalışan kurulumsuz UYAP paketi oluşturabilirsiniz:

```bash
# Taşınabilir paket klasörünü oluşturur (./uyap-portable)
python diagnose_uyap.py --make-portable
```

### USB Bellek Kurulum Adımları:
1. Oluşturulan `uyap-portable/` klasörünü flash belleğinize kopyalayınız.
2. `uyap/` klasörü içine Adalet Bakanlığı resmi sitesinden indirdiğiniz `editor.jar` (veya `uki.jar`) dosyasını koyunuz.
3. `jre/` klasörü içine taşınabilir OpenJDK 8 JRE (Adoptium / Zulu) dosyalarını yerleştiriniz (`jre/bin/java.exe`).
4. **Kullanım:** Duruşma salonundaki herhangi bir bilgisayarda `run-uyap.bat` dosyasına tıklayınız veya `.udf` dosyasını doğrudan bu `.bat` dosyasının üzerine sürükleyip bırakınız!

---

## 📄 Java Olmadan Acil Durumda UDF Belgesi Okuma

Bilgisayarda Java tamamen çökmüşse ve duruşma sırasında evrakı acilen görmeniz gerekiyorsa:

```bash
python diagnose_uyap.py --view ornek_dava.udf
```
*(Bu komut UDF dosyasını saf Python ile ayrıştırarak Mahkeme Adı, Esas No ve dava metnini anında terminalde gösterir).*

---

## 🚀 Hızlı Başlangıç ve Kullanım Kılavuzu

### 1. Java ve UYAP Ortam Teşhisi
```bash
python diagnose_uyap.py
```

### 2. Bozulmuş Önbelleği Temizleme (Açılmama Sorununu Çözer)
```bash
python diagnose_uyap.py --clear-cache
```

### 3. Yüksek Bellekli Başlatma Komutu Alma
```bash
python diagnose_uyap.py --high-mem
```

### 4. Tek Tıkla Platform Scriptleri
- **Windows Batch:** `fix-uyap.bat` çift tıklayarak çalıştırılabilir.
- **Windows PowerShell:**
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\Fix-UyapEditor.ps1 -ClearCache -LaunchEditor
  ```
- **macOS / Linux:**
  ```bash
  chmod +x fix-uyap.sh
  ./fix-uyap.sh --clean
  ```

---

## 🔧 Sık Karşılaşılan UYAP Hataları ve Çözüm Tablosu

| Hata Belirtisi | Temel Neden | Hızlı Çözüm |
|:---|:---|:---|
| **Editör açılır gibi olup kapanıyor** | Bozulmuş `.uyap` önbelleği | `python diagnose_uyap.py --clear-cache` |
| **`OutOfMemoryError` / Donma** | Yetersiz Java Heap belleği | `java -Xms512m -Xmx2048m -jar editor.jar` |
| **Duruşma salonunda Java yok** | Admin yetkisi eksikliği | `python diagnose_uyap.py --view dosya.udf` veya Taşınabilir USB |
| **UDF ikonları beyaz görünüyor** | Dosya ilişkilendirmesi kopuk | `Fix-UyapEditor.ps1 -RepairAssociations` |

---

## 🔗 E-Dönüşüm Açık Kaynak Ekosistemi

Bu araç [eimza-kep](https://github.com/eimza-kep) organizasyonunun açık kaynak LegalTech ekosisteminin bir parçasıdır:

* 🇹🇷 **[awesome-turkiye-e-donusum](https://github.com/eimza-kep/awesome-turkiye-e-donusum):** Türkiye E-Dönüşüm ve LegalTech kütüphaneleri listesi.
* ⚖️ **[udf2md](https://github.com/eimza-kep/udf2md):** UYAP UDF dosyalarını Markdown ve LLM formatına dönüştürücü.
* 🖥️ **[uyap-web-udf-editor](https://github.com/eimza-kep/uyap-web-udf-editor):** Tarayıcıda Java gerektirmeden çalışan modern web UDF editörü.
* 🔓 **[eimza-pin-bloke-asistani](https://github.com/eimza-kep/eimza-pin-bloke-asistani):** USB token PIN kilitlendiğinde PUK kodu ile sıfırlama terminali.
* 🩺 **[akilli-kart-surucu-teshis](https://github.com/eimza-kep/akilli-kart-surucu-teshis):** Akıllı kart okuyucu ve sürücü teşhis aracı.

---

## 📚 İlgili Teknik Rehberler
* 📄 [UYAP Editör Açılmıyor Hatası ve Java Bellek Sorunları Kesin Çözüm](https://uyapteknikdestek.site/yazilar/uyap-editor-acilmiyor-hatasi-kesin-cozum.html)
* 📄 [UDF Dosyası Nedir ve Telefondan/Mac'ten Nasıl Açılır?](https://uyapteknikdestek.site/yazilar/udf-dosyasi-nedir-telefondan-nasil-acilir.html)
* 📄 [DYS ve UYAP Uyuşmazlıkları: Doküman İmzalama Hataları Çözümü](https://uyapteknikdestek.site/yazilar/dys-dokuman-yonetim-sistemi-eimza-entegrasyonu.html)

---

## ⚖️ Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.
