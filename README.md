# UYAP Doküman Editörü (.udf) ve Java Onarım Aracı ⚖️📁

[![Lisans: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue.svg)](https://microsoft.com)
[![PowerShell](https://img.shields.io/badge/PowerShell-5.1%2B%20%7C%207%2B-blueviolet.svg)](https://github.com/PowerShell/PowerShell)
[![Portal](https://img.shields.io/badge/Adalet%20Bakanl%C4%B1%C4%9F%C4%B1-UYAP-red.svg)](https://uyap.gov.tr)

Avukatların, hukuk bürolarının, adliye personelinin ve vatandaşların en çok karşılaştığı:

> **"UDF dosyası çift tıklanınca açılmıyor / birlikte aç uyarısı veriyor"**  
> **"UYAP Editör açılış ekranında takılı kalıyor / tepki vermiyor"**  
> **"Java heap space / yetersiz bellek hatası"**

sorunlarını **tek tıkla** otomatik olarak çözen açık kaynaklı Windows onarım aracıdır.

---

## 🛠️ Ne İşe Yarar?

1. **UDF Dosya İlişkilendirmesini Onarır:** Windows Kayıt Defteri'nde (Registry) `.udf` uzantısını UYAP Editör'e bağlar. Artık dosyalara çift tıkladığınızda doğrudan UYAP açılır.
2. **Bozuk Oturum Dosyalarını Temizler:** `%USERPROFILE%\.uyap` altındaki kilitlenmiş geçici `.tmp`, `.lock` ve bozuk önbellek dosyalarını temizleyerek açılış takılmalarını giderir.
3. **Java Önbelleğini Sıfırlar:** UYAP e-imza bileşenlerinin güncel ve sorunsuz çalışması için eski applet önbelleğini temizler.

---

## 🚀 Hızlı Kullanım

1. Repoyu yeşil **`Code > Download ZIP`** butonundan indirin.
2. İndirdiğiniz klasördeki **`fix-uyap.bat`** dosyasına **çift tıklayın**.
3. İşlem saniyeler içinde tamamlanır ve UYAP Editör kullanıma hazır hale gelir.

### Gelişmiş Komut Satırı Kullanımı (PowerShell)
```powershell
# Büyük dosyalarda kilitlenmeyi önlemek için Java bellek sınırını 2GB (2048 MB) yapma
.\Fix-UyapEditor.ps1 -MemoryLimit 2048m

# Onarım sonrası UYAP Editörünü hemen başlatma
.\Fix-UyapEditor.ps1 -Launch

# Dosya ilişkilendirmesini değiştirmeden sadece bozuk oturumları temizleme
.\Fix-UyapEditor.ps1 -SkipAssociation
```


---

## 📥 Resmi UYAP Doküman Editörü İndirme Bağlantıları

Eğer sisteminizde UYAP Editör hiç kurulu değilse, Adalet Bakanlığı'nın resmi güncel sürümlerini indirebilirsiniz:

* 🏛️ [Adalet Bakanlığı UYAP Editör İndirme Sayfası](https://uyap.gov.tr/Uyap-Editor)
* ⚖️ [UYAP Avukat Portalı](https://avukat.uyap.gov.tr/)
* 👤 [UYAP Vatandaş Portalı](https://vatandas.uyap.gov.tr/)

---

## ⚖️ Lisans

Bu proje [MIT Lisansı](LICENSE) kapsamında tamamen ücretsiz ve açık kaynaklıdır.


### 📚 İlgili Rehber ve Çözümler
* 📄 [UYAP Doküman Editörü (.udf) Açılmıyor Sorununda Java Bellek Ayarı](https://uyap-teknik-destek.pages.dev/yazilar/uyap-dokuman-editoru-udf-acilmiyor-java-bellek-ayari.html)
* 📄 [UYAP Avukat Portala Girişte 'Kart Okuyucu Bulunamadı' Hatası Çözümü](https://uyap-teknik-destek.pages.dev/yazilar/uyap-avukat-portal-kart-okuyucu-bulunamadi-hatasi.html)
* 📄 [e-Duruşmaya Katılırken Mikrofon ve Kamera İzinleri Nasıl Ayarlanır?](https://uyap-teknik-destek.pages.dev/yazilar/e-durusmaya-katilirken-mikrofon-kamera-izinleri.html)
* 📄 [UDF Formatındaki Dava Dilekçesi PDF'e Nasıl Dönüştürülür?](https://uyap-teknik-destek.pages.dev/yazilar/udf-formatindaki-dava-dilekcesi-pdf-donusturme.html)
