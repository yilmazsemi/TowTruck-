import os
import uuid
import urllib.parse
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, send_from_directory
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
from database import get_db, init_db, get_settings, update_settings

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'towtruck-secret-key-super-secure-2026')

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file_storage):
    if file_storage and file_storage.filename and allowed_file(file_storage.filename):
        unique_name = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        
        try:
            # Fotoğrafı aç, yönünü (EXIF) düzelt ve optimize et
            image = Image.open(file_storage.stream)
            image = ImageOps.exif_transpose(image)
            
            # RGB moduna dönüştür (RGBA veya PNG uyumluluğu için)
            if image.mode in ('RGBA', 'P', 'LA'):
                image = image.convert('RGB')
                
            # Aşırı büyük fotoğrafları (örn: 4K/8K telefon çekimlerini) max 1920px genişliğe küçült
            max_size = (1920, 1920)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Kalite 85 ile sıkıştırarak kaydet (10 MB'lık fotoğrafı 200-300 KB yapar)
            image.save(filepath, format='JPEG', quality=85, optimize=True)
            return f"/static/uploads/{unique_name}"
        except Exception as e:
            # Olası bir resim okuma hatasında standart kaydetme fallback'i
            file_storage.seek(0)
            file_storage.save(filepath)
            return f"/static/uploads/{unique_name}"
    return None

# Context processor for global settings available in every template
@app.context_processor
def inject_global_data():
    settings = get_settings()
    current_user = None
    if 'user_id' in session:
        conn = get_db()
        current_user = conn.execute(
            'SELECT id, username, full_name, phone, role FROM users WHERE id = ?',
            (session['user_id'],)
        ).fetchone()
        conn.close()
    return dict(settings=settings, current_user=current_user)

# Auth Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Bu sayfayı görüntülemek için giriş yapmalısınız.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Yönetici girişi gereklidir.', 'warning')
            return redirect(url_for('login', next=request.url))
        if session.get('role') != 'admin':
            flash('Bu alana erişim yetkiniz bulunmuyor.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static', 'images'),
        'favicon.svg',
        mimetype='image/svg+xml'
    )

# ==================== PUBLIC ROUTES ====================

@app.route('/')
def index():
    conn = get_db()
    # Son galeri fotoğraflarından 6 adet
    gallery_items = conn.execute(
        'SELECT * FROM gallery ORDER BY id DESC LIMIT 6'
    ).fetchall()
    # İstatistikler
    requests_count = conn.execute('SELECT COUNT(*) as c FROM tow_requests').fetchone()['c']
    conn.close()
    return render_template('index.html', gallery_items=gallery_items, requests_count=requests_count)

@app.route('/gallery')
def gallery():
    category = request.args.get('category', 'all')
    conn = get_db()
    if category != 'all':
        items = conn.execute(
            'SELECT * FROM gallery WHERE category = ? ORDER BY id DESC', (category,)
        ).fetchall()
    else:
        items = conn.execute('SELECT * FROM gallery ORDER BY id DESC').fetchall()
    
    categories = conn.execute('SELECT DISTINCT category FROM gallery').fetchall()
    conn.close()
    return render_template('gallery.html', items=items, categories=categories, selected_category=category)

@app.route('/request-tow', methods=['POST'])
def request_tow():
    full_name = request.form.get('full_name', '').strip()
    phone = request.form.get('phone', '').strip()
    car_info = request.form.get('car_info', '').strip()
    location_from = request.form.get('location_from', '').strip()
    location_to = request.form.get('location_to', '').strip()
    issue_description = request.form.get('issue_description', '').strip()

    if not full_name or not phone or not location_from:
        flash('Lütfen zorunlu alanları (Ad Soyad, Telefon, Bulunulan Konum) eksiksiz doldurunuz.', 'danger')
        return redirect(request.referrer or url_for('index'))

    # Müşteriden resim alınmıyor; fotoğraflar yönetici Emir tarafından galeriye yüklenir
    image_url = None

    user_id = session.get('user_id')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tow_requests 
        (user_id, full_name, phone, car_info, location_from, location_to, issue_description, image_url, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Beklemede')
    ''', (user_id, full_name, phone, car_info, location_from, location_to, issue_description, image_url))
    request_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # WhatsApp önceden doldurulmuş mesaj hazırlama
    msg_lines = [
        "Merhaba Emir Bey, web sitenizden size ulaşıyorum.",
        "",
        f"📋 Form Bilgilerim:",
        f"👤 Adım: {full_name}",
        f"📞 Telefon: {phone}",
        f"📍 Bulunduğum Konum: {location_from}",
    ]
    if location_to:
        msg_lines.append(f"🏁 Götürülecek Yer: {location_to}")
    if car_info:
        msg_lines.append(f"🚗 Araç Bilgisi: {car_info}")
    if issue_description:
        msg_lines.append(f"🔧 Sorun: {issue_description}")

    msg_lines += [
        "",
        "Çekici talebim hakkında bilgi almak istiyorum. "
    ]

    msg_text = "\n".join(msg_lines)
    encoded_msg = urllib.parse.quote(msg_text)

    settings = get_settings()
    wa_number = settings.get('whatsapp_number', '905459553652')
    wa_url = f"https://wa.me/{wa_number}?text={encoded_msg}"

    return redirect(wa_url)

# ==================== AUTH ROUTES ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('member_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            flash(f"Hoş geldiniz, Sayın {user['full_name']}!", 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('member_dashboard'))
        else:
            flash('Kullanıcı adı veya şifre hatalı.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not full_name or not username or not phone or not password:
            flash('Lütfen tüm alanları doldurunuz.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Girdiğiniz şifreler eşleşmiyor.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Şifre en az 6 karakter olmalıdır.', 'danger')
            return render_template('register.html')

        conn = get_db()
        existing = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        if existing:
            conn.close()
            flash('Bu kullanıcı adı zaten alınmış. Farklı bir kullanıcı adı deneyin.', 'danger')
            return render_template('register.html')

        password_hash = generate_password_hash(password)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, password_hash, full_name, phone, role)
            VALUES (?, ?, ?, ?, 'member')
        ''', (username, password_hash, full_name, phone))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Otomatik oturum açma
        session['user_id'] = user_id
        session['username'] = username
        session['full_name'] = full_name
        session['role'] = 'member'

        flash('Üyeliğiniz başarıyla oluşturuldu!', 'success')
        return redirect(url_for('member_dashboard'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Güvenli bir şekilde çıkış yapıldı.', 'info')
    return redirect(url_for('index'))

# ==================== ADMIN ROUTES ====================

@app.route('/admin')
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db()
    # Özet istatistikler
    total_requests = conn.execute('SELECT COUNT(*) as c FROM tow_requests').fetchone()['c']
    pending_requests = conn.execute("SELECT COUNT(*) as c FROM tow_requests WHERE status = 'Beklemede'").fetchone()['c']
    on_the_way = conn.execute("SELECT COUNT(*) as c FROM tow_requests WHERE status = 'Yolda'").fetchone()['c']
    completed_requests = conn.execute("SELECT COUNT(*) as c FROM tow_requests WHERE status = 'Tamamlandı'").fetchone()['c']
    total_members = conn.execute("SELECT COUNT(*) as c FROM users WHERE role = 'member'").fetchone()['c']
    total_photos = conn.execute('SELECT COUNT(*) as c FROM gallery').fetchone()['c']

    # Çekici talepleri
    requests = conn.execute('''
        SELECT r.*, u.username as member_username 
        FROM tow_requests r
        LEFT JOIN users u ON r.user_id = u.id
        ORDER BY r.id DESC LIMIT 20
    ''').fetchall()

    # Galeri fotoğrafları
    gallery_items = conn.execute('SELECT * FROM gallery ORDER BY id DESC').fetchall()

    # Üyeler listesi
    members = conn.execute("SELECT * FROM users WHERE role = 'member' ORDER BY id DESC LIMIT 20").fetchall()

    conn.close()

    return render_template(
        'admin/dashboard.html',
        stats={
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'on_the_way': on_the_way,
            'completed_requests': completed_requests,
            'total_members': total_members,
            'total_photos': total_photos
        },
        requests=requests,
        gallery_items=gallery_items,
        members=members
    )

@app.route('/admin/settings/update', methods=['POST'])
@admin_required
def admin_update_settings():
    new_settings = {
        'owner_name': request.form.get('owner_name', '').strip(),
        'business_title': request.form.get('business_title', '').strip(),
        'primary_phone': request.form.get('primary_phone', '').strip(),
        'secondary_phone': request.form.get('secondary_phone', '').strip(),
        'whatsapp_number': request.form.get('whatsapp_number', '').strip(),
        'service_city': request.form.get('service_city', '').strip(),
        'address': request.form.get('address', '').strip(),
        'slogan': request.form.get('slogan', '').strip(),
        'about_text': request.form.get('about_text', '').strip(),
        'experience_years': request.form.get('experience_years', '').strip(),
        'completed_jobs': request.form.get('completed_jobs', '').strip()
    }
    update_settings(new_settings)
    flash('Site ve şahıs bilgileri başarıyla güncellendi!', 'success')
    return redirect(url_for('admin_dashboard') + '#settings')

@app.route('/admin/gallery/add', methods=['POST'])
@admin_required
def admin_add_gallery():
    title = request.form.get('title', '').strip()
    category = request.form.get('category', 'Oto Kurtarma').strip()
    description = request.form.get('description', '').strip()
    image_url = request.form.get('image_url', '').strip()

    # Eğer dosya yüklenmişse dosyayı kaydet
    if 'gallery_image' in request.files:
        photo = request.files['gallery_image']
        uploaded_path = save_uploaded_file(photo)
        if uploaded_path:
            image_url = uploaded_path

    if not title or not image_url:
        flash('Lütfen resim başlığı ve geçerli bir fotoğraf (yükleme veya URL) giriniz.', 'danger')
        return redirect(url_for('admin_dashboard') + '#gallery')

    conn = get_db()
    conn.execute('''
        INSERT INTO gallery (title, description, image_url, category)
        VALUES (?, ?, ?, ?)
    ''', (title, description, image_url, category))
    conn.commit()
    conn.close()

    flash('Yeni galeri fotoğrafı başarıyla eklendi!', 'success')
    return redirect(url_for('admin_dashboard') + '#gallery')

@app.route('/admin/gallery/delete/<int:item_id>', methods=['POST'])
@admin_required
def admin_delete_gallery(item_id):
    conn = get_db()
    conn.execute('DELETE FROM gallery WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    flash('Fotoğraf galeriden silindi.', 'info')
    return redirect(url_for('admin_dashboard') + '#gallery')

@app.route('/admin/request/update-status/<int:req_id>', methods=['POST'])
@admin_required
def admin_update_request_status(req_id):
    status = request.form.get('status')
    admin_notes = request.form.get('admin_notes', '').strip()

    conn = get_db()
    conn.execute('''
        UPDATE tow_requests 
        SET status = ?, admin_notes = ?
        WHERE id = ?
    ''', (status, admin_notes, req_id))
    conn.commit()
    conn.close()

    flash(f'Talep #{req_id} durumu "{status}" olarak güncellendi.', 'success')
    return redirect(url_for('admin_dashboard') + '#requests')

@app.route('/admin/request/delete/<int:req_id>', methods=['POST'])
@admin_required
def admin_delete_request(req_id):
    conn = get_db()
    conn.execute('DELETE FROM tow_requests WHERE id = ?', (req_id,))
    conn.commit()
    conn.close()
    flash(f'Talep #{req_id} silindi.', 'info')
    return redirect(url_for('admin_dashboard') + '#requests')

# ==================== MEMBER ROUTES ====================

@app.route('/member')
@app.route('/member/dashboard')
@login_required
def member_dashboard():
    user_id = session['user_id']
    conn = get_db()
    my_requests = conn.execute('''
        SELECT * FROM tow_requests 
        WHERE user_id = ? 
        ORDER BY id DESC
    ''', (user_id,)).fetchall()
    
    user_info = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    return render_template('member/dashboard.html', requests=my_requests, user=user_info)

@app.route('/member/profile/update', methods=['POST'])
@login_required
def member_update_profile():
    user_id = session['user_id']
    full_name = request.form.get('full_name', '').strip()
    phone = request.form.get('phone', '').strip()
    new_password = request.form.get('new_password', '')

    if not full_name or not phone:
        flash('Ad Soyad ve Telefon boş bırakılamaz.', 'danger')
        return redirect(url_for('member_dashboard'))

    conn = get_db()
    if new_password:
        if len(new_password) < 6:
            flash('Yeni şifre en az 6 karakter olmalıdır.', 'danger')
            return redirect(url_for('member_dashboard'))
        new_hash = generate_password_hash(new_password)
        conn.execute('UPDATE users SET full_name = ?, phone = ?, password_hash = ? WHERE id = ?',
                     (full_name, phone, new_hash, user_id))
    else:
        conn.execute('UPDATE users SET full_name = ?, phone = ? WHERE id = ?',
                     (full_name, phone, user_id))
    
    conn.commit()
    conn.close()

    session['full_name'] = full_name
    flash('Profil bilgileriniz güncellendi.', 'success')
    return redirect(url_for('member_dashboard'))

if __name__ == '__main__':
    init_db()
    print("TowTruck Araç Çekici Web Uygulaması Başlatılıyor...")
    print("Tarayıcınızda açmak için: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
