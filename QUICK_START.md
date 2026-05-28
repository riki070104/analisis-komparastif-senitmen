# 🚀 Quick Start Guide - SentimentApp

Panduan cepat untuk menjalankan aplikasi SentimentApp di komputer Anda.

## ⏱️ Waktu Setup: ~5 menit

### LANGKAH 1: Installation Dependencies
Buka Command Prompt/Terminal di folder `sentiment-app` lalu jalankan:

```bash
pip install -r requirements.txt
```

Tunggu sampai semua library terinstall (akan terlihat "Successfully installed...").

### LANGKAH 2: Jalankan Aplikasi
```bash
python run.py
```

Anda akan melihat output seperti:
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### LANGKAH 3: Buka Browser
Buka browser Anda (Chrome, Firefox, Edge, dll) dan buka:
```
http://localhost:5000
```

### LANGKAH 4: Daftar Akun Baru
1. Klik tombol "Register" atau "Daftar di sini"
2. Isi form:
   - Username: contoh_user
   - Email: contoh@email.com
   - Password: minimal 6 karakter
3. Klik "Register"
4. Anda akan diarahkan ke halaman login

### LANGKAH 5: Login
1. Masukkan username dan password
2. Klik "Login"
3. Berhasil! Anda sudah bisa menggunakan aplikasi

### LANGKAH 6: Coba Fitur Utama

#### 🧠 Coba Analisis Sentimen
1. Klik menu "Analisis"
2. Masukkan contoh teks:
   - Positif: "Saya sangat senang dengan produk ini, bagus sekali!"
   - Negatif: "Produk ini jelek dan kecewa dengan layanannya"
   - Netral: "Produk ini tersedia di toko"
3. Klik tombol "Analisis"
4. Lihat hasilnya!

#### 📊 Lihat Dashboard
1. Klik menu "Dashboard"
2. Lihat statistik analisis Anda

#### 📜 Lihat Riwayat
1. Klik menu "Riwayat"
2. Lihat semua analisis sebelumnya
3. Anda bisa menghapus data dengan klik "Hapus"

#### 💾 Kelola Dataset
1. Klik menu "Dataset"
2. Klik "Tambah Data"
3. Masukkan teks dan pilih label (Positif/Negatif/Netral)
4. Klik "Simpan"
5. Lihat dataset Anda dan bisa edit/hapus

#### ℹ️ Baca Tentang Aplikasi
Klik menu "Tentang" untuk membaca informasi lengkap

## ❓ Troubleshoot

### Error: "Module not found flask"
**Solusi**: Install ulang dependencies
```bash
pip install -r requirements.txt
```

### Error: "Port 5000 already in use"
**Solusi**: Gunakan port berbeda, edit app.py:
```python
# Ubah baris terakhir dari:
app.run(debug=True)
# Menjadi:
app.run(debug=True, port=5001)
```

### Halaman login tidak muncul dengan benar
**Solusi**: Clear cache browser (Ctrl+Shift+Delete)

### Database error
**Solusi**: Hapus folder `instance/`, aplikasi akan membuat database baru

## 📱 Responsive Design
Aplikasi sudah responsive dan bisa dibuka di:
- ✅ Desktop (1920x1080, dll)
- ✅ Tablet (iPad, dll)
- ✅ Mobile (iPhone, Android, dll)

## 🛑 Cara Menghentikan Aplikasi
Tekan `CTRL+C` di terminal/command prompt

## ⚙️ Tips Penggunaan

### Sidebar Collapse
Klik tombol panah di sidebar untuk collapse/expand

### Sentiment Detection
- **Positif**: Ada kata-kata positif (bagus, senang, hebat, dll)
- **Negatif**: Ada kata-kata negatif (jelek, buruk, benci, dll)
- **Netral**: Tidak ada kata positif atau negatif yang dominan

### Text Limit
- Maksimal 5000 karakter per analisis
- Dataset juga maksimal 5000 karakter

## 📖 Dokumentasi Lengkap
Baca `README.md` untuk dokumentasi lebih lengkap

## ✅ Checklist

- [ ] pip install -r requirements.txt
- [ ] python app.py
- [ ] Buka http://localhost:5000
- [ ] Register akun baru
- [ ] Login
- [ ] Coba Analisis
- [ ] Lihat Dashboard
- [ ] Lihat Riwayat
- [ ] Kelola Dataset

---

**Selamat! Aplikasi SentimentApp siap digunakan!** 🎉

Jika ada pertanyaan atau masalah, baca README.md atau ubah konfigurasi di app.py
