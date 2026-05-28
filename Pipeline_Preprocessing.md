# PIPELINE PREPROCESSING UNTUK MODEL RANDOM FOREST

## Analisis Sentimen Ulasan Aplikasi AI Chatbot (ChatGPT & Gemini)

### Bahasa Indonesia | Google Play Store Reviews

---

**Versi Dokumen:** 1.0  
**Tanggal:** 28 Mei 2026  
**Tujuan:** Mendokumentasikan alur preprocessing teks Bahasa Indonesia dari data mentah hingga siap training model Random Forest untuk klasifikasi sentimen tiga kelas (Positif / Negatif / Netral).

---

## DAFTAR ISI

1. [Overview Pipeline](#1-overview-pipeline)
2. [Step 1: Text Cleaning](#2-step-1-text-cleaning)
3. [Step 2: Normalisasi Bahasa](#3-step-2-normalisasi-bahasa)
4. [Step 3: Tokenisasi (Sastrawi)](#4-step-3-tokenisasi-sastrawi)
5. [Step 4: Stopword Removal](#5-step-4-stopword-removal)
6. [Step 5: Stemming (Sastrawi)](#6-step-5-stemming-sastrawi)
7. [Step 6: Ekstraksi Fitur (TF-IDF)](#7-step-6-ekstraksi-fitur-tf-idf)
8. [Step 7: Handling Class Imbalance](#8-step-7-handling-class-imbalance)
9. [Step 8: Train-Test Split](#9-step-8-train-test-split)
10. [Diagram Alur Lengkap](#10-diagram-alur-lengkap)
11. [Parameter & Hyperparameter Rekomendasi](#11-parameter--hyperparameter-rekomendasi)
12. [Checklist Pre-Training](#12-checklist-pre-training)

---

## 1. OVERVIEW PIPELINE

### 1.1 Konteks Domain

Data berasal dari ulasan pengguna aplikasi AI Chatbot (ChatGPT & Gemini) di Google Play Store dengan karakteristik:

- Bahasa Indonesia campuran (formal, informal, slang, singkatan, typo)
- Rating bintang 1–5 dengan teks ulasan
- Panjang bervariasi (1 kata hingga paragraf)
- Banyak emoticon, tanda baca tidak standar, dan simbol aneh
- Klasifikasi sentimen tiga kelas: **Positif**, **Negatif**, **Netral**

### 1.2 Prinsip Pipeline

- **Preservasi makna sentimen:** Setiap transformasi harus mempertahankan atau memperkuat sinyal sentimen.
- **Reproducibility:** Semua parameter (random seed, kamus normalisasi, daftar stopword) harus tersimpan dan dapat diulang.
- **Domain-aware:** Pipeline dioptimalkan untuk teks ulasan aplikasi mobile, bukan teks berita atau akademik.

### 1.3 Ringkasan 8 Langkah

| Step | Nama                         | Fungsi Utama                                                | Output                                              |
| ---- | ---------------------------- | ----------------------------------------------------------- | --------------------------------------------------- |
| 1    | **Text Cleaning**            | Membersihkan noise teknis dari teks mentah                  | Teks bersih, lowercase, bebas URL/email/simbol aneh |
| 2    | **Normalisasi Bahasa**       | Mengubah slang, singkatan, typo menjadi bentuk baku         | Teks standar Bahasa Indonesia                       |
| 3    | **Tokenisasi (Sastrawi)**    | Memecah teks menjadi unit kata/token                        | List token per dokumen                              |
| 4    | **Stopword Removal**         | Menghapus kata-kata fungsional yang tidak bermakna sentimen | List token tanpa stopword                           |
| 5    | **Stemming (Sastrawi)**      | Mengembalikan kata ke bentuk dasar (root word)              | List token stemmed                                  |
| 6    | **Ekstraksi Fitur (TF-IDF)** | Mengubah teks menjadi vektor numerik                        | Matriks sparse TF-IDF (N x V)                       |
| 7    | **Handling Class Imbalance** | Menyeimbangkan proporsi kelas sentimen                      | Dataset dengan distribusi kelas seimbang            |
| 8    | **Train-Test Split**         | Membagi data untuk training dan evaluasi                    | X_train, X_test, y_train, y_test                    |

---

## 2. STEP 1: TEXT CLEANING

### 2.1 Tujuan

Menghilangkan elemen teknis dan noise yang tidak mengandung informasi sentimen, sekaligus menstandarisasi format teks agar konsisten untuk tahap selanjutnya.

### 2.2 Input & Output

- **Input:** Teks ulasan mentah dari Google Play Store
- **Output:** Teks bersih, seragam, siap normalisasi

### 2.3 Proses Detail

#### A. Lowercasing

Mengubah seluruh karakter menjadi huruf kecil untuk menghindari duplikasi fitur akibat perbedaan kapitalisasi.

#### B. Penghapusan URL dan Email

Menghapus tautan web (`http://`, `https://`, `www.`) dan alamat email karena tidak mengandung sentimen terhadap aplikasi.

#### C. Penghapusan Mention dan Hashtag

Menghapus `@username` dan `#hashtag`. Untuk domain ulasan Play Store, mention jarang muncul; hashtag biasanya tidak relevan dengan evaluasi aplikasi.

#### D. Penanganan Emoticon

**Kebijakan:** Emoticon adalah sinyal sentimen yang kuat. Terdapat dua pendekatan:

- **Pendekatan A (Mapping):** Mengubah emoticon menjadi label tekstual (`👍` → `positif`, `😡` → `negatif`)
- **Pendekatan B (Preservasi):** Mempertahankan emoticon dan membiarkan TF-IDF memperlakukannya sebagai token
- **Pendekatan C (Penghapusan):** Menghapus emoticon jika menggunakan lexicon/embedding yang tidak mendukung simbol

> **Rekomendasi:** Gunakan Pendekatan A untuk Random Forest agar emoticon terekstrak sebagai fitur tekstual yang bermakna.

#### E. Penghapusan atau Normalisasi Angka

- Angka murni (tahun, versi, jumlah) dihapus karena jarang bermakna sentimen.
- Angka yang menjadi bagian kata slang (`4pp` → `app`) dinormalisasi manual jika diperlukan.

#### F. Penghapusan Tanda Baca

Menghapus tanda baca (`.,;:!?"'()[]{}`) dan mengganti dengan spasi. **Pengecualian:** tanda hubung dalam kata komposit (`user-friendly`) dipertahankan atau dipecah.

#### G. Penghapusan Simbol dan Karakter Non-ASCII

Menghapus karakter aneh, simbol matematika, dan karakter yang tidak termasuk dalam alfabet Indonesia atau emoticon yang telah dipetakan.

#### H. Penanganan Whitespace Berlebih

Mengganti multiple whitespace/tab/newline dengan single space dan melakukan `strip()` di awal/akhir teks.

### 2.4 Contoh Transformasi

| No  | Input (Teks Mentah)                                   | Output (Setelah Cleaning)                     |
| --- | ----------------------------------------------------- | --------------------------------------------- |
| 1   | `APLIKASI Bagus,Banget!!! 👍👍`                       | `aplikasi bagus banget positif positif`       |
| 2   | `cek https://chatgpt.com/login ya, gak bisa masuk 😡` | `cek login ya gak bisa masuk negatif`         |
| 3   | `Bug terus @dev_team, force close tiap 5 menit...`    | `bug terus force close tiap menit`            |
| 4   | `AalalapPAlQAAaqll / ( alq (%%) lqa)`                 | `aalalappalqaall alq lqa`                     |
| 5   | `Download GPT tiba-tiba ada APK Codex ngikut???`      | `download gpt tiba tiba ada apk codex ngikut` |

### 2.5 Catatan Penting

- **Jangan hapus emoticon sebelum mapping.** Jika emoticon dihapus tanpa mapping, sinyal sentimen hilang.
- **Karakter berulang (`bagusss`, `bangettt`)** belum ditangani di tahap ini; akan ditangani di Step 2 (Normalisasi).
- **Teks kosong atau hanya simbol** hasilkan string kosong. Dokumen dengan string kosong setelah cleaning harus ditandai untuk keputusan di Step 7 (drop atau netral).

---

## 3. STEP 2: NORMALISASI BAHASA

### 3.1 Tujuan

Mengubah variasi penulisan tidak baku (slang, singkatan, typo, bentuk gaul) menjadi bentuk standar Bahasa Indonesia agar lexicon dan model dapat mengenali makna kata secara konsisten.

### 3.2 Input & Output

- **Input:** Teks hasil Step 1 (cleaning)
- **Output:** Teks standar Bahasa Indonesia, slang ternormalisasi

### 3.3 Proses Detail

#### A. Normalisasi Slang Negasi (Prioritas Tinggi)

Slang negasi adalah komponen paling kritis dalam sentimen Bahasa Indonesia karena membalik polaritas. Normalisasi harus dilakukan secara **berurutan dari frasa panjang ke pendek** untuk menghindari partial replacement.

**Urutan normalisasi:**

1. Frasa gabungan 3+ kata: `gak bisa login` → `tidak bisa login`
2. Frasa gabungan 2 kata: `gak bisa` → `tidak bisa`
3. Kata tunggal slang: `gak` → `tidak`

#### B. Normalisasi Slang Umum (Non-Negasi)

Mengubah kata gaul atau singkatan umum di komunitas mobile/tech Indonesia menjadi bentuk baku.

#### C. Normalisasi Typo Berulang

Mengubah karakter berulang yang menunjukkan penekanan emosi menjadi bentuk standar.

- `bagusss` → `bagus`
- `bangettt` → `banget`
- `jelekkk` → `jelek`
- `tololll` → `tolol`

> **Catatan:** Penekanan berulang bisa dipertahankan sebagai intensifier (`bagusss` → `bagus banget`), tapi untuk Random Forest + TF-IDF, normalisasi ke bentuk dasar lebih stabil.

#### D. Normalisasi Kata Komposit

Memisahkan atau menggabungkan kata komposit yang menempel:

- `userfriendly` → `user friendly`
- `chatgpt` → `chat gpt` atau `chatgpt` (tetap jika dianggap proper noun)
- `apk` → `aplikasi`

#### E. Kamus Normalisasi Custom (Wajib)

Wajib membuat dan menyimpan kamus normalisasi dalam file JSON/CSV yang dapat digunakan kembali. Kamus harus didokumentasikan dan diperbarui berdasarkan eksplorasi data.

### 3.4 Contoh Transformasi

| No  | Input (Cleaning)                | Output (Normalisasi)            | Kategori                     |
| --- | ------------------------------- | ------------------------------- | ---------------------------- |
| 1   | `gak bisa login lagi`           | `tidak bisa login lagi`         | Slang negasi                 |
| 2   | `apk tolol lelet bgt`           | `aplikasi tolol lelet banget`   | Slang + singkatan            |
| 3   | `bagusss bangetttt`             | `bagus banget`                  | Typo berulang                |
| 4   | `pke gemini aja lah`            | `pakai gemini saja lah`         | Slang umum                   |
| 5   | `tiap cerita dibilang khayalan` | `tiap cerita dibilang khayalan` | (Tidak berubah — sudah baku) |
| 6   | `jelek,bego,ga asik`            | `jelek bego tidak asik`         | Slang negasi + tanda baca    |
| 7   | `plis kasih tau cara login`     | `tolong kasih tahu cara login`  | Slang permintaan             |
| 8   | `nggak kekirim chatnya`         | `tidak terkirim chatnya`        | Slang + typo                 |

### 3.5 Catatan Penting

- **Urutan replacement sangat penting.** Jika `ga` didahulukan sebelum `gak bisa`, maka `gak bisa` akan menjadi `tidak k bisa` (salah).
- **Kamus harus domain-specific.** Slang di komunitas gamer berbeda dengan komunitas pengguna aplikasi AI. Eksplorasi data mentah wajib dilakukan sebelum menyusun kamus.
- **Kata proper noun** (`ChatGPT`, `Gemini`, `OpenAI`) boleh dipertahankan atau dinormalisasi ke lowercase tergantung kebijakan. Untuk TF-IDF, lowercase lebih baik.
- **Simpan kamus versi 1.0** dan dokumentasikan setiap perubahan untuk reproducibility.

---

## 4. STEP 3: TOKENISASI (SASTRAWI)

### 4.1 Tujuan

Memecah teks yang sudah normal menjadi unit-unit kata (token) agar dapat diproses secara individual pada tahap stopword removal, stemming, dan ekstraksi fitur.

### 4.2 Input & Output

- **Input:** Teks normal hasil Step 2 (string)
- **Output:** List/array token per dokumen

### 4.3 Proses Detail

#### A. Tokenisasi dengan Sastrawi

Menggunakan `Tokenizer()` dari library PySastrawi. Tokenisasi berbasis whitespace dengan penanganan khusus untuk:

- Tanda hubung: `user-friendly` → `['user', 'friendly']` atau `['user-friendly']`
- Apostrof: `don't` → `['don', 't']` (jarang di Bahasa Indonesia)
- Angka yang menempel: `gpt4` → `['gpt', '4']` atau `['gpt4']`

#### B. Penanganan Token Kosong

Setelah tokenisasi, hapus token yang berupa:

- String kosong `''`
- Hanya whitespace `' '`
- Hanya angka `'4'` (jika kebijakan angka dihapus)

#### C. Preservasi Urutan Token

Urutan token dipertahankan karena urutan memiliki makna (terutama untuk negasi: `tidak` harus sebelum `bagus`).

### 4.4 Contoh Transformasi

| No  | Input (Normalisasi)       | Output (Tokenisasi)                    |
| --- | ------------------------- | -------------------------------------- |
| 1   | `aplikasi bagus banget`   | `['aplikasi', 'bagus', 'banget']`      |
| 2   | `tidak bisa login lagi`   | `['tidak', 'bisa', 'login', 'lagi']`   |
| 3   | `jelek bego tidak asik`   | `['jelek', 'bego', 'tidak', 'asik']`   |
| 4   | `user friendly dan mudah` | `['user', 'friendly', 'dan', 'mudah']` |
| 5   | `chat gpt error terus`    | `['chat', 'gpt', 'error', 'terus']`    |

### 4.5 Catatan Penting

- **Jangan gunakan tokenisasi berbasis karakter** (character-level) untuk Random Forest. Word-level tokenisasi lebih interpretable dan efisien.
- **Token dengan tanda hubung:** Kebijakan tergantung domain. Untuk ulasan aplikasi, memisahkan `user-friendly` menjadi `['user', 'friendly']` lebih baik karena TF-IDF akan menghitung kedua kata.
- **Tokenisasi Sastrawi vs NLTK:** Sastrawi lebih optimal untuk Bahasa Indonesia karena mengenali imbuhan dan morfologi, meskipun untuk tokenisasi murni perbedaannya minimal.

---

## 5. STEP 4: STOPWORD REMOVERY

### 5.1 Tujuan

Mengurangi dimensi fitur dengan menghapus kata-kata yang sangat sering muncul tetapi tidak membawa makna sentimen (kata fungsional/filler).

### 5.2 Input & Output

- **Input:** List token hasil Step 3
- **Output:** List token tanpa stopword

### 5.3 Proses Detail

#### A. Daftar Stopword Standar (Sastrawi)

Sastrawi menyediakan ~800 kata stopword Bahasa Indonesia. Namun, **tidak semua boleh dihapus** untuk analisis sentimen.

#### B. Kata yang WAJIB DIPERTAHANKAN (Blacklist dari Stopword Removal)

Berikut kata-kata yang muncul dalam daftar stopword standar tetapi **harus dipertahankan** karena krusial untuk sentimen:

| Kata      | Alasan Mempertahankan                                       |
| --------- | ----------------------------------------------------------- |
| `tidak`   | Negasi — membalik polaritas sentimen                        |
| `bukan`   | Negasi — membalik polaritas sentimen                        |
| `belum`   | Negasi — membalik polaritas sentimen                        |
| `jangan`  | Negasi — membalik polaritas sentimen                        |
| `kurang`  | Negasi lemah — mengurangi intensitas positif                |
| `sangat`  | Intensifier — memperkuat skor sentimen                      |
| `banget`  | Intensifier — memperkuat skor sentimen                      |
| `amat`    | Intensifier — memperkuat skor sentimen                      |
| `terlalu` | Intensifier — mengindikasikan over-limit (biasanya negatif) |
| `paling`  | Superlatif — intensitas ekstrem                             |
| `tapi`    | Kontradiksi — menandakan mixed sentiment                    |
| `namun`   | Kontradiksi — menandakan mixed sentiment                    |
| `cuma`    | Pembatas — mengindikasikan ekspektasi tidak terpenuhi       |
| `sayang`  | Kontradiksi — "sayangnya" = reversal marker                 |
| `saja`    | Pembatas — bisa mengindikasikan minimisasi                  |
| `lagi`    | Temporal — "error lagi" = pengulangan negatif               |
| `terus`   | Temporal — "error terus" = persistensi negatif              |
| `sudah`   | Aspek — "sudah bayar tapi" = keluhan berbayar               |
| `masih`   | Aspek — "masih error" = keluhan berkelanjutan               |
| `bisa`    | Modal — "tidak bisa" = kegagalan fungsional                 |
| `ada`     | Eksistensial — "tidak ada fitur" = keluhan                  |

#### C. Stopword Custom (Tambahan Domain)

Tambahkan kata-kata yang sangat sering muncul di ulasan Play Store tetapi tidak bermakna sentimen:

- `nya`, `sih`, `dong`, `deh`, `lah`, `kan`, `ya` (partikel penegas)
- `yang`, `di`, `ke`, `dari`, `pada`, `dalam`, `untuk` (preposisi murni)
- `dan`, `atau`, `serta` (konjungsi netral)
- `ini`, `itu`, `dia` (demonstratif — kecuali dalam konteks spesifik)

#### D. Proses Filtering

```
for token in tokens:
    if token not in STOPWORD_CUSTOM and token not in STOPWORD_SASTRAWI_BLACKLISTED:
        keep_token(token)
```

### 5.4 Contoh Transformasi

| No  | Input (Tokenisasi)                                    | Output (Stopword Removal)              | Keterangan                                       |
| --- | ----------------------------------------------------- | -------------------------------------- | ------------------------------------------------ |
| 1   | `['aplikasi', 'bagus', 'banget']`                     | `['aplikasi', 'bagus', 'banget']`      | Tidak ada stopword                               |
| 2   | `['tidak', 'bisa', 'login', 'lagi']`                  | `['tidak', 'bisa', 'login', 'lagi']`   | `tidak` & `lagi` DIPERTAHANKAN                   |
| 3   | `['saya', 'sangat', 'kecewa', 'dengan', 'pelayanan']` | `['sangat', 'kecewa', 'pelayanan']`    | `saya`, `dengan` dihapus; `sangat` DIPERTAHANKAN |
| 4   | `['bagus', 'tapi', 'sering', 'error']`                | `['bagus', 'tapi', 'sering', 'error']` | `tapi` DIPERTAHANKAN (mixed marker)              |
| 5   | `['chat', 'gpt', 'adalah', 'yang', 'terbaik']`        | `['chat', 'gpt', 'terbaik']`           | `adalah`, `yang` dihapus                         |

### 5.5 Catatan Penting

- **Jangan hapus semua stopword secara buta.** Penelitian sentimen menunjukkan bahwa menghapus negasi (`tidak`) mengurangi akurasi klasifikasi hingga 15–25%.
- **Buat daftar "stopword yang dipertahankan"** dan dokumentasikan. Daftar ini adalah aset penting untuk reproducibility.
- **Evaluasi dampak:** Lakukan eksperimen A/B (dengan vs tanpa selective stopword removal) untuk membuktikan manfaatnya.

---

## 6. STEP 5: STEMMING (SASTRAWI)

### 6.1 Tujuan

Mengembalikan kata ke bentuk dasar (root word / lemma) untuk mengurangi sparse matrix dan menggabungkan variasi morfologi menjadi satu fitur.

### 6.2 Input & Output

- **Input:** List token hasil Step 4 (tanpa stopword)
- **Output:** List token dalam bentuk dasar (stemmed)

### 6.3 Proses Detail

#### A. Stemming dengan Sastrawi Stemmer

Menggunakan algoritma Nazief-Adriani yang mengenali:

- **Prefiks (awalan):** `me-`, `di-`, `pe-`, `ter-`, `ke-`, `se-`, `ber-`
- **Sufiks (akhiran):** `-kan`, `-i`, `-an`
- **Konfiks (awalan+akhiran):** `me-...-kan`, `di-...-i`, `pe-...-an`
- **Infiks:** `-el-`, `-em-`, `-er-` (jarang)

#### B. Contoh Transformasi Stemming

| Input Token    | Output Stemmed | Pola Morfologi                 |
| -------------- | -------------- | ------------------------------ |
| `membantu`     | `bantu`        | me- + bantu                    |
| `mengecewakan` | `kecewa`       | me- + kecewa + -kan            |
| `berkualitas`  | `kualitas`     | ber- + kualitas                |
| `terbaik`      | `baik`         | ter- + baik                    |
| `login`        | `login`        | (Tidak berubah — kata serapan) |
| `error`        | `error`        | (Tidak berubah — kata serapan) |
| `aplikasi`     | `aplikasi`     | (Tidak berubah — sudah dasar)  |
| `menggunakan`  | `guna`         | me- + guna + -kan              |
| `pengguna`     | `guna`         | pe- + guna                     |

#### C. Handling Over-Stemming

Sastrawi terkadang terlalu agresif:

- `bisa` (modal) vs `bisa` (dari `membisa` — jarang) → aman
- `guna` (dari `menggunakan`) vs `guna` (dari `pengguna`) → **sama!**

> **Masalah:** `menggunakan` (verb) dan `pengguna` (noun) sama-sama jadi `guna`. Dalam konteks sentimen, perbedaan ini jarang krusial. Namun, jika ditemukan over-stemming yang merusak makna sentimen, pertimbangkan untuk **menonaktifkan stemming** pada kata tersebut.

#### D. Kebijakan untuk Kata Serapan dan Proper Noun

Kata serapan dari bahasa Inggris (`login`, `error`, `bug`, `chat`, `gpt`, `gemini`) biasanya tidak berubah setelah stemming. Kata ini boleh dipertahankan apa adanya.

### 6.4 Contoh Transformasi Lengkap

| No  | Input (Stopword Removal)               | Output (Stemming)                      |
| --- | -------------------------------------- | -------------------------------------- |
| 1   | `['aplikasi', 'bagus', 'banget']`      | `['aplikasi', 'bagus', 'banget']`      |
| 2   | `['tidak', 'bisa', 'login', 'lagi']`   | `['tidak', 'bisa', 'login', 'lagi']`   |
| 3   | `['sangat', 'kecewa', 'pelayanan']`    | `['sangat', 'kecewa', 'layan']`        |
| 4   | `['bagus', 'tapi', 'sering', 'error']` | `['bagus', 'tapi', 'sering', 'error']` |
| 5   | `['membantu', 'tugas', 'kuliah']`      | `['bantu', 'tugas', 'kuliah']`         |

### 6.5 Catatan Penting

- **Stemming opsional untuk Random Forest.** Eksperimen menunjukkan bahwa dengan TF-IDF + Random Forest, stemming memberikan peningkatan kecil (1–3%) tetapi mengurangi interpretability. Jika interpretasi fitur penting (feature importance) adalah tujuan, pertimbangkan untuk **melewati stemming**.
- **Sastrawi vs Lemmatization:** Lemmatization lebih akurat tapi resource untuk Bahasa Indonesia terbatas. Sastrawi adalah pilihan praktis terbaik saat ini.
- **Simpan hasil pre-stemming** sebagai backup jika perlu eksperimen tanpa stemming.

---

## 7. STEP 6: EKSTRAKSI FITUR (TF-IDF)

### 7.1 Tujuan

Mengubah koleksi dokumen teks (list token) menjadi matriks numerik yang dapat diproses oleh algoritma machine learning Random Forest.

### 7.2 Input & Output

- **Input:** List token hasil Step 5 (stemmed) untuk seluruh corpus
- **Output:** Matriks sparse TF-IDF dengan dimensi `(N_dokumen × V_vocabulary)`

### 7.3 Proses Detail

#### A. Penggabungan Token menjadi String

Sebelum vectorization, gabungkan kembali list token menjadi string dengan spasi sebagai pemisah:

```
['aplikasi', 'bagus', 'banget'] → "aplikasi bagus banget"
```

#### B. TF-IDF Vectorization

Menggunakan `TfidfVectorizer` dengan parameter yang dioptimalkan untuk Bahasa Indonesia:

**Komponen TF-IDF:**

- **TF (Term Frequency):** Frekuensi kata dalam dokumen
- **IDF (Inverse Document Frequency):** `log(N / df(t))` — penalti untuk kata yang muncul di terlalu banyak dokumen
- **TF-IDF Score:** `TF × IDF`

#### C. N-gram Range

Untuk menangkap frasa bermakna sentimen:

- **Unigram (1,1):** `['bagus']`, `['error']` — kata individual
- **Bigram (2,2):** `['tidak_bisa']`, `['bagus_banget']` — frasa dua kata
- **Trigram (3,3):** `['tidak_bisa_login']` — frasa tiga kata
- **Kombinasi (1,2):** Unigram + Bigram — **REKOMENDASI**
- **Kombinasi (1,3):** Unigram + Bigram + Trigram — jika corpus besar

> **Rekomendasi untuk sentimen:** Gunakan `ngram_range=(1, 2)`. Bigram menangkap negasi (`tidak_bisa`) dan intensifier (`bagus_banget`) yang krusial untuk akurasi.

#### D. Parameter TF-IDF

| Parameter      | Rekomendasi    | Alasan                                                               |
| -------------- | -------------- | -------------------------------------------------------------------- |
| `max_features` | 5.000 – 10.000 | Cukup untuk ulasan Play Store; lebih besar = overfit risk            |
| `min_df`       | 2 – 5          | Menghapus kata yang hanya muncul di 1 dokumen (noise)                |
| `max_df`       | 0.8 – 0.95     | Menghapus kata yang muncul di >80–95% dokumen (terlalu umum)         |
| `ngram_range`  | (1, 2)         | Menangkap negasi dan frasa intensifier                               |
| `sublinear_tf` | True           | Menggunakan `1 + log(tf)` untuk mengurangi dominasi frekuensi tinggi |
| `norm`         | `'l2'`         | Normalisasi Euclidean standar                                        |
| `use_idf`      | True           | Mengaktifkan komponen IDF                                            |
| `smooth_idf`   | True           | Menghindari division by zero                                         |

#### E. Handling Kata yang Tidak Muncul di Training (OOV)

TF-IDF tidak memiliki mekanisme built-in untuk Out-Of-Vocabulary words. Kata yang tidak ada di vocabulary training akan diabaikan di testing.

> **Solusi:** Pastikan corpus training cukup besar dan representatif. Untuk deployment, retrain model secara berkala dengan data baru.

### 7.4 Contoh Transformasi (Konseptual)

| Dokumen                     | Token (Stemmed)                   | TF-IDF Vector (Simplifikasi)  |
| --------------------------- | --------------------------------- | ----------------------------- |
| D1: `aplikasi bagus banget` | `['aplikasi', 'bagus', 'banget']` | `[0.45, 0.89, 0.0, ..., 0.0]` |
| D2: `tidak bisa login`      | `['tidak', 'bisa', 'login']`      | `[0.0, 0.0, 0.71, 0.71, 0.0]` |
| D3: `error terus bug`       | `['error', 'terus', 'bug']`       | `[0.0, 0.0, 0.0, ..., 0.58]`  |

_Dimensi vektor: ~5.000–10.000 fitur (sparse matrix)._

### 7.5 Catatan Penting

- **TF-IDF menghasilkan sparse matrix.** Random Forest dapat menangani sparse matrix, tapi training akan lebih lambat. Pertimbangkan dimensionality reduction (TruncatedSVD) jika `max_features > 15.000`.
- **Jangan gunakan CountVectorizer mentah** untuk Random Forest. TF-IDF memberikan bobot yang lebih informatif.
- **Feature importance** dari Random Forest pada TF-IDF fitur dapat digunakan untuk mengidentifikasi kata/frasa paling prediktif.

---

## 8. STEP 7: HANDLING CLASS IMBALANCE

### 8.1 Tujuan

Menyeimbangkan proporsi kelas sentimen agar model Random Forest tidak bias terhadap kelas mayoritas (biasanya Negatif di ulasan Play Store).

### 8.2 Input & Output

- **Input:** Matriks X (TF-IDF) dan label y dengan distribusi tidak seimbang
- **Output:** Matriks X_resampled dan y_resampled dengan distribusi lebih seimbang

### 8.3 Analisis Distribusi Kelas

Sebelum resampling, analisis distribusi awal:

| Kelas   | Jumlah | Proporsi |
| ------- | ------ | -------- |
| Negatif | 3.500  | 70%      |
| Positif | 1.000  | 20%      |
| Netral  | 500    | 10%      |

> **Threshold imbalance:** Jika kelas mayoritas > 60% atau rasio mayoritas:minoritas > 2:1, wajib dilakukan handling imbalance.

### 8.4 Metode Handling Imbalance

#### A. Random Oversampling (Minority Class)

**Cara:** Menduplikasi secara acak sampel dari kelas minoritas hingga jumlahnya mendekati kelas mayoritas.

- **Kelebihan:** Sederhana, tidak menghilangkan data
- **Kekurangan:** Risiko overfitting karena duplikasi
- **Rekomendasi:** Gunakan jika data < 5.000 dan tidak ada metode lain

#### B. Random Undersampling (Majority Class)

**Cara:** Mengurangi sampel kelas mayoritas secara acak.

- **Kelebihan:** Mengurangi waktu training
- **Kekurangan:** Kehilangan informasi berharga dari data mayoritas
- **Rekomendasi:** Hindari jika data total < 3.000

#### C. SMOTE (Synthetic Minority Over-sampling Technique)

**Cara:** Membuat sampel sintetis baru untuk kelas minoritas dengan interpolasi antar sampel minoritas yang ada (di ruang fitur TF-IDF).

- **Kelebihan:** Tidak duplikasi murni, menambah variasi
- **Kekurangan:** Bisa menghasilkan sampel "noise" jika data minoritas terlalu sedikit atau terlalu tersebar
- **Rekomendasi:** **Metode utama untuk data 3.000–20.000**

#### D. SMOTE + Tomek Links

**Cara:** SMOTE diikuti penghapusan Tomek Links (pasang sampel berbeda kelas yang terlalu dekat).

- **Kelebihan:** Membersihkan noise dari hasil SMOTE
- **Kekurangan:** Lebih kompleks
- **Rekomendasi:** Gunakan jika hasil SMOTE murni masih menunjukkan overfitting

#### E. Class Weight (Random Forest Parameter)

**Cara:** Memberikan bobot lebih tinggi pada kelas minoritas saat training Random Forest.

```python
class_weight='balanced'  # Bobot = n_samples / (n_classes * n_samples_class)
```

- **Kelebihan:** Tidak mengubah data, tidak menambah waktu preprocessing
- **Kekurangan:** Kurang efektif jika imbalance ekstrem (> 10:1)
- **Rekomendasi:** **Wajib digunakan** sebagai baseline, bahkan jika SMOTE juga diterapkan

#### F. Hybrid Approach (Rekomendasi Terbaik)

Kombinasi SMOTE + Class Weight:

1. Terapkan SMOTE pada training set (jangan pernah pada test set!)
2. Set `class_weight='balanced'` pada Random Forest
3. Evaluasi pada test set yang asli (tanpa SMOTE)

### 8.5 Catatan Penting

- **JANGAN PERNAH apply SMOTE pada test set!** SMOTE hanya boleh diterapkan pada training set. Test set harus tetap merepresentasikan distribusi real-world.
- **Stratified sampling wajib** saat train-test split untuk memastikan proporsi kelas terjaga di kedua set.
- **Evaluasi metrik:** Jangan gunakan accuracy sebagai metrik utama untuk data imbalance. Gunakan **F1-Score Macro**, **Precision/Recall per kelas**, dan **Confusion Matrix**.

---

## 9. STEP 8: TRAIN-TEST SPLIT

### 9.1 Tujuan

Membagi dataset menjadi subset training (untuk melatih model) dan subset testing (untuk mengevaluasi performa model secara objektif).

### 9.2 Input & Output

- **Input:** Matriks X (TF-IDF) dan label y (setelah imbalance handling pada training)
- **Output:** `X_train`, `X_test`, `y_train`, `y_test`

### 9.3 Proses Detail

#### A. Proporsi Split

Gunakan **80:20**.

#### B. Stratified Split

Wajib menggunakan `stratify=y` agar proporsi kelas Positif/Negatif/Netral di training dan testing **sama persis** dengan dataset asli.

#### C. Random Seed (Reproducibility)

Wajib set `random_state` dengan nilai tetap (misal: `42`, `123`, `2026`) agar split dapat direproduksi oleh peneliti lain.

#### D. Urutan yang Benar (Sangat Penting!)

```
1. Split data MENTAH menjadi Train dan Test (stratified)
2. Fit TF-IDF Vectorizer HANYA pada X_train
3. Transform X_train dan X_test menggunakan vectorizer yang sama
4. Apply SMOTE / oversampling HANYA pada X_train (jika diperlukan)
5. Train Random Forest pada X_train_resampled
6. Evaluate pada X_test (TIDAK pernah disentuh SMOTE)
```

> **Kesalahan fatal:** Jika TF-IDF difit pada seluruh data sebelum split, atau SMOTE diterapkan sebelum split, hasil evaluasi akan **overly optimistic** (data leakage).

### 9.4 Contoh Distribusi Setelah Split

**Asumsi:** Dataset 5.000 ulasan (70% Neg, 20% Pos, 10% Neu)

| Set              | Total  | Negatif | Positif | Netral |
| ---------------- | ------ | ------- | ------- | ------ | --------------------- |
| Full Dataset     | 5.000  | 3.500   | 1.000   | 500    |
| Training (80%)   | 4.000  | 2.800   | 800     | 400    |
| Testing (20%)    | 1.000  | 700     | 200     | 100    |
| Training + SMOTE | ~6.000 | 2.800   | 2.800   | 2.800  | _(setelah balancing)_ |

### 9.5 Catatan Penting

- **Data leakage prevention** adalah prioritas tertinggi. Setiap transformasi (TF-IDF, normalisasi, scaling) harus difit pada training dan diterapkan pada testing.
- **Cross-validation (CV):** Untuk hasil yang lebih robust, gunakan **Stratified K-Fold CV** (k=5 atau k=10) pada training set. Final evaluation tetap pada hold-out test set.
- **Simpan index split** agar dapat merekonstruksi dokumen mana yang masuk training vs testing untuk analisis error.

---

## 10. DIAGRAM ALUR LENGKAP

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA MENTAH (CSV Play Store)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ id_review   │  │ platform    │  │ rating      │  │ konten      │       │
│  │ (UUID)      │  │ ChatGPT/    │  │ (1-5)       │  │ (teks ulasan)│       │
│  │             │  │ Gemini      │  │             │  │             │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: TEXT CLEANING                                                      │
│  ├─ Lowercase                                                               │
│  ├─ Hapus URL, Email, Mention, Hashtag                                     │
│  ├─ Mapping Emoticon → Label Tekstual                                       │
│  ├─ Hapus Angka Murni                                                     │
│  ├─ Hapus Tanda Baca (kecuali tanda hubung)                                │
│  ├─ Hapus Simbol Non-ASCII                                                │
│  └─ Normalize Whitespace                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: NORMALISASI BAHASA                                                 │
│  ├─ Slang Negasi → Formal (ga/gak/gk → tidak)                              │
│  ├─ Slang Umum → Baku (apk → aplikasi, pke → pakai)                        │
│  ├─ Typo Berulang → Standar (bagusss → bagus)                              │
│  ├─ Kata Komposit → Pisah/Gabung (userfriendly → user friendly)            │
│  └─ Simpan ke Kamus Normalisasi v1.0 (JSON/CSV)                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: TOKENISASI (Sastrawi)                                                │
│  ├─ Tokenizer() → pecah berdasarkan whitespace                              │
│  ├─ Handle tanda hubung: user-friendly → [user, friendly]                   │
│  ├─ Hapus token kosong dan angka murni                                      │
│  └─ Output: List token per dokumen                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: STOPWORD REMOVAL                                                   │
│  ├─ Load Sastrawi Stopword List (~800 kata)                                │
│  ├─ BLACKLIST: Pertahankan negasi & intensifier                            │
│  │   (tidak, bukan, belum, sangat, banget, tapi, cuma, sayang)             │
│  ├─ Tambah Custom Stopword (nya, sih, dong, deh, lah)                      │
│  └─ Filter token yang tidak dalam daftar stopword                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 5: STEMMING (Sastrawi)                                                │
│  ├─ Stemmer() → kembalikan ke bentuk dasar                                 │
│  ├─ me-...-kan → dasar (mengecewakan → kecewa)                             │
│  ├─ ber- → dasar (berkualitas → kualitas)                                  │
│  ├─ ter- → dasar (terbaik → baik)                                          │
│  ├─ Kata serapan → tetap (login, error, bug)                               │
│  └─ Simpan hasil pre-stemming sebagai backup                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 6: EKSTRAKSI FITUR (TF-IDF)                                           │
│  ├─ Gabung token → string: "aplikasi bagus banget"                         │
│  ├─ TfidfVectorizer(                                                        │
│  │     ngram_range=(1,2),      ← Unigram + Bigram                          │
│  │     max_features=5000,      ← Vocabulary cap                             │
│  │     min_df=2,                ← Hapus kata jarang                        │
│  │     max_df=0.85,             ← Hapus kata terlalu umum                  │
│  │     sublinear_tf=True,       ← Log scaling                               │
│  │     norm='l2'                ← Euclidean normalization                    │
│  │  )                                                                        │
│  └─ Output: Sparse matrix (N × V)                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 7 & 8: SPLIT → BALANCE → TRAIN                                        │
│                                                                             │
│  ┌─────────────────────────┐         ┌─────────────────────────┐             │
│  │   SPLIT (Stratified)    │         │   SPLIT (Stratified)    │             │
│  │   random_state=42       │         │   random_state=42       │             │
│  │   test_size=0.20        │         │   test_size=0.20        │             │
│  └───────────┬─────────────┘         └───────────┬─────────────┘             │
│              │                                    │                         │
│              ▼                                    ▼                         │
│  ┌─────────────────────────┐         ┌─────────────────────────┐             │
│  │      X_train (80%)       │         │      X_test (20%)        │             │
│  │      y_train             │         │      y_test              │             │
│  └───────────┬─────────────┘         └─────────────────────────┘             │
│              │                                                               │
│              ▼                                                               │
│  ┌─────────────────────────┐                                               │
│  │   SMOTE (Training ONLY)  │                                               │
│  │   → Generate synthetic   │                                               │
│  │     minority samples     │                                               │
│  └───────────┬─────────────┘                                               │
│              │                                                               │
│              ▼                                                               │
│  ┌─────────────────────────┐                                               │
│  │  X_train_balanced        │                                               │
│  │  y_train_balanced        │                                               │
│  └───────────┬─────────────┘                                               │
│              │                                                               │
│              ▼                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  RANDOM FOREST CLASSIFIER                                               ││
│  │  ├─ n_estimators=200                                                    ││
│  │  ├─ max_depth=None                                                      ││
│  │  ├─ class_weight='balanced'                                             ││
│  │  ├─ random_state=42                                                     ││
│  │  └─ fit(X_train_balanced, y_train_balanced)                            ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│              │                                                               │
│              ▼                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  EVALUASI PADA X_test (data asli, tidak pernah disentuh SMOTE)         ││
│  │  ├─ Accuracy (referensi saja)                                         ││
│  │  ├─ Precision, Recall, F1 per kelas                                   ││
│  │  ├─ Macro F1-Score (primary metric)                                   ││
│  │  ├─ Confusion Matrix                                                    ││
│  │  └─ Feature Importance (interpretasi kata paling prediktif)            ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. PARAMETER & HYPERPARAMETER REKOMENDASI

### 11.1 Parameter Preprocessing

| Parameter                 | Nilai                | Keterangan                          |
| ------------------------- | -------------------- | ----------------------------------- |
| Lowercase                 | `True`               | Wajib                               |
| Hapus URL                 | `True`               | Wajib                               |
| Hapus Email               | `True`               | Wajib                               |
| Hapus Mention             | `True`               | Wajib                               |
| Hapus Hashtag             | `True`               | Wajib                               |
| Emoticon Mapping          | `True`               | Disarankan                          |
| Hapus Angka               | `True`               | Kecuali angka dalam kata            |
| Hapus Tanda Baca          | `True`               | Kecuali tanda hubung                |
| Normalisasi Slang         | `True`               | Wajib — domain critical             |
| Normalisasi Typo Berulang | `True`               | Disarankan                          |
| Tokenizer                 | `Sastrawi Tokenizer` | Disarankan                          |
| Stopword Source           | `Sastrawi + Custom`  | Custom list wajib didokumentasikan  |
| Stemmer                   | `Sastrawi Stemmer`   | Disarankan, tapi opsional           |
| N-gram Range              | `(1, 2)`             | Unigram + Bigram                    |
| Max Features TF-IDF       | `5.000 – 10.000`     | Tergantung ukuran corpus            |
| Min DF                    | `2`                  | Kata muncul di minimal 2 dokumen    |
| Max DF                    | `0.85`               | Kata muncul di maksimal 85% dokumen |
| Sublinear TF              | `True`               | Log scaling frekuensi               |

### 11.2 Parameter Random Forest

| Parameter           | Nilai Rekomendasi                   | Alasan                                           |
| ------------------- | ----------------------------------- | ------------------------------------------------ |
| `n_estimators`      | 200 – 500                           | Cukup besar untuk stabil, tidak perlu > 500      |
| `max_depth`         | `None` (grow until pure) atau 20–50 | `None` untuk data kecil, batasi untuk data besar |
| `min_samples_split` | 2 – 10                              | Mencegah overfitting pada leaf                   |
| `min_samples_leaf`  | 1 – 5                               | Mencegah leaf terlalu spesifik                   |
| `max_features`      | `'sqrt'`                            | Standar untuk klasifikasi                        |
| `class_weight`      | `'balanced'`                        | Wajib untuk data imbalance                       |
| `random_state`      | 42 (atau tetap)                     | Reproducibility                                  |
| `bootstrap`         | `True`                              | Standar                                          |
| `criterion`         | `'gini'` atau `'entropy'`           | `'gini'` lebih cepat, hasil serupa               |

---

## 12. CHECKLIST PRE-TRAINING

Sebelum menjalankan training Random Forest, pastikan semua item berikut telah dilakukan:

### Data Preparation

- [ ] Dataset telah melalui proses labeling dengan konsistensi tinggi (IAA ≥ 0.70)
- [ ] Data mentah telah dieksplorasi untuk mengidentifikasi slang, typo, dan noise domain
- [ ] Kamus normalisasi telah disusun dan didokumentasikan (versi 1.0)
- [ ] Daftar stopword yang dipertahankan telah ditentukan dan didokumentasikan
- [ ] Data kosong/gibberish telah diidentifikasi (drop atau label netral)

### Pipeline Execution

- [ ] Step 1 (Cleaning): Semua dokumen telah melalui lowercase, URL removal, emoticon mapping
- [ ] Step 2 (Normalisasi): Slang negasi telah ternormalisasi dengan urutan yang benar (frasa → tunggal)
- [ ] Step 3 (Tokenisasi): Token kosong dan noise token telah dihapus
- [ ] Step 4 (Stopword): Negasi dan intensifier DIPERTAHANKAN, bukan dihapus
- [ ] Step 5 (Stemming): Hasil stemming telah dicek untuk over-stemming krusial
- [ ] Step 6 (TF-IDF): N-gram (1,2) telah diterapkan, max_features sesuai ukuran corpus
- [ ] Step 7 (Imbalance): SMOTE hanya diterapkan pada training set (bukan test set!)
- [ ] Step 8 (Split): Stratified split dengan random_state tetap telah dilakukan

### Quality Control

- [ ] TF-IDF vectorizer hanya difit pada X_train (tidak pada seluruh data)
- [ ] X_test hanya ditransform (tidak difit ulang)
- [ ] Distribusi kelas di training dan testing telah diverifikasi (stratify berhasil)
- [ ] Cross-validation (Stratified K-Fold, k=5) telah direncanakan untuk training set
- [ ] Backup data pre-stemming tersedia untuk eksperimen alternatif

### Dokumentasi

- [ ] Versi library (Python, scikit-learn, Sastrawi) telah dicatat
- [ ] Random seed untuk setiap step telah ditetapkan dan didokumentasikan
- [ ] Kamus normalisasi tersimpan dalam format JSON/CSV
- [ ] Daftar stopword custom tersimpan dalam format teks
- [ ] Parameter TF-IDF tercatat dalam log eksperimen

---

## LAMPIRAN A: GLOSSARIUM

| Istilah              | Definisi                                                            |
| -------------------- | ------------------------------------------------------------------- |
| **Token**            | Unit terkecil teks yang diproses (biasanya kata)                    |
| **Stemming**         | Proses mengembalikan kata ke bentuk dasar (root)                    |
| **Stopword**         | Kata fungsional yang sering muncul tapi tidak bermakna sentimen     |
| **TF-IDF**           | Term Frequency-Inverse Document Frequency; bobot kata dalam corpus  |
| **N-gram**           | Sekuens n token berurutan (unigram=1, bigram=2, trigram=3)          |
| **SMOTE**            | Synthetic Minority Over-sampling Technique; membuat sampel sintetis |
| **Stratified Split** | Pembagian data yang mempertahankan proporsi kelas                   |
| **Data Leakage**     | Kejadian di mana informasi test set "bocor" ke training set         |
| **Class Imbalance**  | Kondisi di mana proporsi kelas tidak merata                         |
| **Sparse Matrix**    | Matriks yang sebagian besar elemennya nol (karakteristik TF-IDF)    |
| **OOV**              | Out-Of-Vocabulary; kata yang tidak ada di vocabulary training       |
| **IAA**              | Inter-Annotator Agreement; tingkat kesepakatan antar annotator      |

---
