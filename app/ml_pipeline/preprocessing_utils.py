import re
import string
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory, StopWordRemover, ArrayDictionary

# ==========================================
# 1. INISIALISASI SASTRAWI
# ==========================================
# Inisialisasi Stemmer (dieksekusi sekali saat module di-load)
stemmer_factory = StemmerFactory()
stemmer = stemmer_factory.create_stemmer()

# Inisialisasi Stopwords
stopword_factory = StopWordRemoverFactory()
base_stopwords = stopword_factory.get_stop_words()

# Kata-kata yang TIDAK BOLEH dihapus (Blacklist Stopword)
# Kata negasi, intensifier, kontradiksi, dll yang penting untuk sentimen
BLACKLIST_STOPWORDS = {
    "tidak", "bukan", "belum", "jangan", "kurang", "sangat", "banget", "amat", 
    "terlalu", "paling", "tapi", "namun", "cuma", "sayang", "saja", "lagi", 
    "terus", "sudah", "masih", "bisa", "ada"
}

# Hapus kata blacklist dari base_stopwords
filtered_stopwords = [word for word in base_stopwords if word not in BLACKLIST_STOPWORDS]

# Tambahkan custom stopword untuk domain review aplikasi
CUSTOM_STOPWORDS = [
    "nya", "sih", "dong", "deh", "lah", "kan", "ya", "yang", "di", "ke", 
    "dari", "pada", "dalam", "untuk", "dan", "atau", "serta", "ini", "itu", "dia"
]
filtered_stopwords.extend(CUSTOM_STOPWORDS)

# Buat custom remover
custom_dictionary = ArrayDictionary(filtered_stopwords)
custom_stopword_remover = StopWordRemover(custom_dictionary)

# ==========================================
# 2. KAMUS NORMALISASI (SLANG DICT)
# ==========================================
# Disusun dari urutan panjang (negasi ganda) ke pendek
SLANG_DICT = {
    # Negasi gabungan
    "ga bisa": "tidak bisa",
    "gak bisa": "tidak bisa",
    "gk bisa": "tidak bisa",
    "gabisa": "tidak bisa",
    "gbs": "tidak bisa",
    "gbsa": "tidak bisa",
    "ga ada": "tidak ada",
    "gak ada": "tidak ada",
    "gaada": "tidak ada",
    "gada": "tidak ada",
    "ga mau": "tidak mau",
    "gamau": "tidak mau",
    "gamo": "tidak mau",
    "ga tau": "tidak tahu",
    "gatau": "tidak tahu",
    "gtau": "tidak tahu",
    # Negasi tunggal
    "ga": "tidak",
    "gak": "tidak",
    "gk": "tidak",
    "ngga": "tidak",
    "nggak": "tidak",
    "kagak": "tidak",
    "tdk": "tidak",
    # Slang umum
    "yg": "yang",
    "apk": "aplikasi",
    "app": "aplikasi",
    "bgt": "banget",
    "bngt": "banget",
    "kalo": "kalau",
    "klo": "kalau",
    "udah": "sudah",
    "udh": "sudah",
    "dah": "sudah",
    "sy": "saya",
    "aq": "aku",
    "krn": "karena",
    "karna": "karena",
    "dgn": "dengan",
    "dg": "dengan",
    "dr": "dari",
    "dri": "dari",
    "bgs": "bagus",
    "bgus": "bagus",
    "jlk": "jelek",
    "jlek": "jelek",
    "bnyk": "banyak",
    "byk": "banyak",
    "sm": "sama",
    "sma": "sama",
    "blm": "belum",
    "blom": "belum",
    "kdg": "kadang",
    "gmn": "bagaimana",
    "bs": "bisa",
    "jd": "jadi",
    "jdi": "jadi",
    "aja": "saja",
    "jg": "juga",
    "krng": "kurang",
    "krg": "kurang",
    "trus": "terus",
    "trs": "terus",
    "bnr": "benar",
    "gt": "begitu",
    "gtu": "begitu",
    "gitu": "begitu",
    "gini": "begini",
    "mantep": "mantap",
    "oke": "baik",
    "ok": "baik",
    "thx": "terima kasih",
    "makasi": "terima kasih",
    "error": "error", # Serapan dipertahankan
    "bug": "bug",
    "login": "login"
}

# ==========================================
# 3. KAMUS EMOTICON KE TEKS
# ==========================================
EMOTICON_DICT = {
    "👍": " positif ",
    "😊": " positif ",
    "😍": " positif ",
    "😁": " positif ",
    "❤️": " positif ",
    "👎": " negatif ",
    "😡": " negatif ",
    "🤬": " negatif ",
    "😠": " negatif ",
    "😭": " negatif ",
    "😞": " negatif ",
    "💩": " negatif "
}

def preprocess_text(text):
    """
    Full pipeline preprocessing berdasarkan Pipeline_Preprocessing.md
    """
    if not isinstance(text, str):
        return ""
        
    # STEP 1: Text Cleaning
    # A. Lowercasing
    text = text.lower()
    
    # B. Penghapusan URL dan Email
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\S+@\S+', '', text)
    
    # C. Penghapusan Mention dan Hashtag
    text = re.sub(r'@\w+|#\w+', '', text)
    
    # D. Penanganan Emoticon (Mapping)
    for emo, word in EMOTICON_DICT.items():
        text = text.replace(emo, word)
        
    # E. Penghapusan Angka Murni
    text = re.sub(r'\b\d+\b', ' ', text)
    
    # F & G. Penghapusan Tanda Baca & Simbol Non-ASCII
    # Hapus semua tanda baca kecuali tanda hubung
    punct_to_remove = string.punctuation.replace('-', '')
    text = text.translate(str.maketrans(punct_to_remove, ' '*len(punct_to_remove)))
    # Hapus sisa non-ascii (termasuk emoji lain yang tidak terpetakan)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    
    # H. Penanganan Whitespace Berlebih
    text = re.sub(r'\s+', ' ', text).strip()
    
    # STEP 2: Normalisasi Bahasa
    # Normalisasi typo berulang (bagusss -> bagus)
    text = re.sub(r'([a-z])\1{2,}', r'\1', text)
    
    # Normalisasi slang berurutan
    for slang, formal in SLANG_DICT.items():
        pattern = r'\b' + re.escape(slang) + r'\b'
        text = re.sub(pattern, formal, text)
        
    # STEP 3: Tokenisasi (Split spasi, menangani tanda hubung utuh)
    tokens = text.split()
    
    # STEP 4: Stopword Removal (Custom Sastrawi)
    text = " ".join(tokens)
    text = custom_stopword_remover.remove(text)
    
    # STEP 5: Stemming (Sastrawi)
    text = stemmer.stem(text)
    
    return text.strip()
