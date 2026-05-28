# SentimentApp - Aplikasi Analisis Sentimen dengan Flask

Aplikasi web sederhana untuk menganalisis sentimen teks menggunakan Python Flask.

## 📋 Persyaratan

- Python 3.7+
- pip (Python Package Manager)

## 🚀 Cara Memulai

### 1. Clone atau Download Project
```bash
cd sentiment-app
```

### 2. Buat Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# MacOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi
```bash
python app.py
```

Aplikasi akan berjalan di: **http://localhost:5000**

## 📁 Struktur Folder

```
sentiment-app/
├── app.py                  # Entry point aplikasi
├── extensions.py           # Inisialisasi Flask extensions
├── models.py               # Database models
├── auth.py                 # Authentication routes
├── routes.py               # Main routes
├── sentiment_model.py      # Sentiment analysis logic
├── requirements.txt        # Dependencies
├── static/
│   ├── css/style.css       # Main stylesheet
│   └── js/script.js        # JavaScript utilities
├── templates/
│   ├── base.html           # Base template
│   ├── index.html          # Home page
│   ├── login.html          # Login page
│   ├── register.html       # Register page
│   ├── dashboard.html      # Dashboard
│   ├── analyze.html        # Analysis page
│   ├── history.html        # History page
│   ├── about.html          # About page
│   └── dataset/
│       ├── index.html      # Dataset list
│       ├── add.html        # Add dataset
│       └── edit.html       # Edit dataset
└── instance/               # Database location (auto-created)
```

## 🔧 Fitur

✅ **Analisis Sentimen Real-time** - Analisis teks dengan hasil instan
✅ **Autentikasi Pengguna** - Registrasi dan login aman
✅ **Histori Analisis** - Simpan semua riwayat analisis
✅ **Dataset Management** - Kelola dataset teks Anda
✅ **Dashboard** - Statistik dan ringkasan analisis
✅ **Responsive Design** - Bekerja di desktop dan mobile

## 📝 Akun Contoh

Silakan daftar akun baru:
- Buka http://localhost:5000
- Klik "Register"
- Isi username, email, dan password
- Setelah login, mulai analisis teks

## 💡 Cara Menggunakan

1. **Login**: Masuk dengan akun Anda
2. **Analisis Teks**: 
   - Buka menu "Analisis"
   - Masukkan teks yang ingin dianalisis
   - Klik tombol "Analisis"
   - Lihat hasil sentimen (positif/negatif/netral) dengan persentase kepercayaan
3. **Lihat Riwayat**: Di menu "Riwayat" untuk melihat semua analisis sebelumnya
4. **Kelola Dataset**: Di menu "Dataset" untuk membuat/edit/hapus data

## 🎨 Teknologi

- **Backend**: Python Flask, Flask-SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 5, Font Awesome 6, Vanilla JavaScript
- **Database**: SQLite

## ⚙️ Konfigurasi

Edit `app.py` untuk mengubah konfigurasi:

```python
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
```

**Penting**: Ubah SECRET_KEY dengan nilai yang aman sebelum production!

## 📊 Analisis Sentimen

Aplikasi menggunakan pendekatan **rule-based** sederhana:
- Membaca kamus kata positif dan negatif
- Menghitung jumlah kata positif vs negatif
- Menentukan sentimen berdasarkan dominasi
- Confidence dihitung dari rasio kata sentimen terhadap total kata

## 🐛 Troubleshoot

**Port 5000 sudah digunakan?**
```python
# Edit di app.py
app.run(debug=True, port=5001)  # Ganti ke port lain
```

**Module tidak ditemukan?**
```bash
pip install -r requirements.txt
```

**Database error?**
Hapus folder `instance/` dan jalankan ulang:
```bash
python app.py
```

## 📄 Lisensi

Bebas digunakan untuk keperluan pribadi dan komersial.

## 💬 Support

Jika ada pertanyaan atau bug, silakan buat issue atau hubungi developer.

---

**Selamat menggunakan SentimentApp!** 🎉
