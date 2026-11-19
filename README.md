# 🚨 Araç Çekici & Oto Kurtarma Web Sitesi (7/24 Özel Çözüm)

Şahsa ve işletmeye özel, modern araç çekici temalı, yönetici (admin) ve üye paneline sahip, resim yükleme ve online çekici çağırma sistemli eksiksiz web uygulaması.

---

## 🌟 Öne Çıkan Özellikler

1. **Çekiciye & Kurtarmaya Özel Tema ve Tasarım:**
   - Dikkat çekici sarı-siyah uyarı şeritleri, acil durum animasyonları ve modern koyu (dark mode) tasarım.
   - 7/24 Nöbetçi Çekici acil çağrı ve WhatsApp konum gönderme butonları.
   - %100 Mobil uyumlu (Responsive) yapı.

2. **Şahsa ve İşletmeye Özel Alanlar:**
   - Şahıs Adı Soyadı (Örn: **Semih Özcan**) hem web sitesinin başlığında, hem yönetici kartında hem de operasyon bilgilerinde otomatik yer alır.
   - 1. Acil Telefon Hattı, 2. Yedek Hat ve Doğrudan WhatsApp hattı.
   - Hizmet bölgesi, adres, tecrübe yılı ve kurtarma sayaçları **Yönetici Paneli'nden tek tıkla canlı olarak değiştirilebilir**.

3. **Yönetici (Admin) Paneli:**
   - **Gelen Talepler:** Müşterilerden gelen tüm acil çekici çağrılarını görüntüleme, durum değiştirme (*Beklemede*, *Yolda*, *Tamamlandı*, *İptal*), müşteri notu ekleme.
   - **Galeri / Resim Yönetimi:** Bilgisayardan dosya seçerek veya internet URL'si ile sahada çekilmiş kurtarma fotoğrafları ekleme/silme.
   - **Şahsi Ayarlar:** İsim, soyisim, unvan, telefon numaraları ve hakkımızda metinlerini anında güncelleme.
   - **Kayıtlı Üyeler:** Sistemi kullanan üyelerin listesi ve hızlı WhatsApp/arama butonları.

4. **Normal Üye Sistemi:**
   - Kolay kayıt ve güvenli şifreli giriş (Werkzeug PBKDF2/SHA-256).
   - Üye paneli: Önceki ve aktif çekici taleplerini anlık durumlarıyla (Çekici Yolda vb.) takip etme.
   - Profil bilgilerini (ad, telefon, şifre) güncelleme.

5. **Resim Yükleme Alanı:**
   - Müşteriler çekici çağırırken yolda kalan / hasarlı araçlarının fotoğraflarını yükleyebilir.
   - Yönetici sahadaki başarılı kurtarma operasyonlarının fotoğraflarını galeriye yükleyebilir.
   - Ziyaretçiler fotoğrafları büyüterek (Lightbox Modal) inceleyebilir.

---

## 🔑 Hazır Giriş Bilgileri

| Rol | Kullanıcı Adı | Şifre | Açıklama |
|---|---|---|---|
| **Yönetici (Admin)** | `admin` | `admin123` | Yönetici paneline tam erişim, ayarları ve talepleri düzenleme |
| **Normal Üye** | `uye` | `123456` | Müşteri paneli, kendi taleplerini görme ve yeni çağrı yapma |

*(Dilerseniz yeni bir üye kaydı oluşturabilir veya admin panelinden tüm bilgileri değiştirebilirsiniz.)*

---

## 🚀 Nasıl Çalıştırılır?

### Yöntem 1 (En Kolay):
Klasör içerisindeki **`baslat.bat`** dosyasına çift tıklayın!

### Yöntem 2 (Terminal / Komut Satırı):
```bash
python app.py
```

Ardından tarayıcınızdan şu adrese gidin:
👉 **`http://127.0.0.1:5000`**

---

## 📁 Proje Dizin Yapısı

```
TowTruck/
│
├── app.py                  # Flask backend motoru, yönlendirmeler ve oturum yönetimi
├── database.py             # SQLite veritabanı şeması ve başlangıç verileri
├── towtruck.db             # Otomatik oluşturulan SQLite veritabanı
├── baslat.bat              # Tek tıkla başlatma dosyası
├── requirements.txt        # Gerekli kütüphaneler
├── test_app.py             # Otomatik doğrulama testleri
│
├── static/
│   ├── css/style.css       # Özel çekici teması, animasyonlar ve şerit stilleri
│   ├── js/main.js          # Resim modalı (lightbox), mobil menü, önizleme
│   └── uploads/            # Yüklenen gerçek fotoğraflar
│
└── templates/
    ├── base.html           # Ana şablon, header, footer ve acil arama butonları
    ├── index.html          # Ana sayfa (Hero, Hizmetler, Form, Galeri, İletişim)
    ├── gallery.html        # Filtrelenebilir tam ekran galeri sayfası
    ├── login.html          # Yönetici & Üye giriş ekranı
    ├── register.html       # Yeni üye kayıt formu
    ├── admin/
    │   └── dashboard.html  # Yönetici kontrol merkezi (Talepler, Galeri, Ayarlar)
    └── member/
        └── dashboard.html  # Müşteri/Üye paneli ve talep geçmişi
```
