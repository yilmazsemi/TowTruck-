import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'towtruck.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Kullanıcılar tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT,
            role TEXT NOT NULL DEFAULT 'member',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Şahsa ve işletmeye özel site ayarları
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS site_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    # Galeri / Resimler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gallery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            image_url TEXT NOT NULL,
            category TEXT DEFAULT 'Kurtarma',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Çekici Çağrı / Hizmet Talepleri tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tow_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            car_info TEXT,
            location_from TEXT NOT NULL,
            location_to TEXT,
            issue_description TEXT,
            image_url TEXT,
            status TEXT DEFAULT 'Beklemede',
            admin_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Varsayılan site ayarları
    default_settings = {
        'owner_name': 'Emir Süzen',
        'business_title': 'EMİR OTO KURTARMA & ÇEKİCİ HİZMETLERİ',
        'primary_phone': '+90 545 955 36 52',
        'secondary_phone': '',
        'whatsapp_number': '905459553652',
        'service_city': 'Bağcılar / İstanbul & Çevre İller',
        'address': 'Yavuz Selim Mahallesi 3/4. Sokak No:14 Bağcılar / İstanbul',
        'slogan': 'Yolda Kaldığınızda Endişelenmeyin! En Kısa Sürede Yanınızdayız.',
        'about_text': 'Emir Oto Kurtarma olarak; kaskolu ve hidrolik kayar kasa çekicimiz ile aracınız nerede olursa olsun en güvenli ve hızlı şekilde dilediğiniz noktaya ulaştırıyoruz. Emir Süzen güvencesiyle daima yanınızdayız.',
        'experience_years': '12',
        'completed_jobs': '4850+'
    }

    for key, value in default_settings.items():
        cursor.execute('INSERT OR IGNORE INTO site_settings (key, value) VALUES (?, ?)', (key, value))

    # Varsayılan Yönetici (Admin) Hesabı: admin / admin123
    cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        admin_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, password_hash, full_name, phone, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', admin_hash, 'Emir Süzen (Yönetici)', '+90 545 955 36 52', 'admin'))

    # Örnek Standart Üye Hesabı: uye / 123456
    cursor.execute('SELECT id FROM users WHERE username = ?', ('uye',))
    if not cursor.fetchone():
        member_hash = generate_password_hash('123456')
        cursor.execute('''
            INSERT INTO users (username, password_hash, full_name, phone, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('uye', member_hash, 'Ahmet Yılmaz', '0555 111 22 33', 'member'))

    # Örnek Başlangıç Galeri Resimleri (Varsayılan profesyonel resimler)
    cursor.execute('SELECT COUNT(*) as count FROM gallery')
    gallery_count = cursor.fetchone()['count']
    if gallery_count == 0:
        sample_gallery = [
            (
                'Lüks Otomobil Güvenli Taşıma',
                'Kayar kasa çekicimiz ile sıfır hasar garantili transfer.',
                'https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?auto=format&fit=crop&w=800&q=80',
                'Oto Kurtarma'
            ),
            (
                'Gece 7/24 Acil Yol Yardım',
                'Otoyolda arızalanan SUV tipi aracın olay yerinden güvenle alınması.',
                'https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=800&q=80',
                'Acil Kurtarma'
            ),
            (
                'Şehirler Arası Araç Sevkiyatı',
                'Çoklu ve tekli özel aparatlı çekicilerimizle Türkiye geneli transfer.',
                'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=800&q=80',
                'Şehirler Arası'
            ),
            (
                'Ağır Vasıta ve Minibüs Çekici',
                'Yüksek tonajlı ticari araçların özel vinç ve aparatla kurtarılması.',
                'https://images.unsplash.com/photo-1580273916550-e323be2ae537?auto=format&fit=crop&w=800&q=80',
                'Ağır Vasıta'
            )
        ]
        for item in sample_gallery:
            cursor.execute('''
                INSERT INTO gallery (title, description, image_url, category)
                VALUES (?, ?, ?, ?)
            ''', item)

    conn.commit()
    conn.close()

def get_settings():
    conn = get_db()
    rows = conn.execute('SELECT key, value FROM site_settings').fetchall()
    conn.close()
    return {row['key']: row['value'] for row in rows}

def update_settings(settings_dict):
    conn = get_db()
    for key, value in settings_dict.items():
        conn.execute('INSERT OR REPLACE INTO site_settings (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Veritabanı başarıyla oluşturuldu ve hazırlandı.")
