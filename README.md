# JagaKata

## Transformer-based Hate Speech Detection System for Indonesian Language

**JagaKata** adalah aplikasi cerdas berbasis web yang dirancang untuk mendeteksi dan menganalisis ujaran kebencian (*hate speech*) dalam teks berbahasa Indonesia. Aplikasi ini tidak hanya menentukan apakah sebuah teks mengandung ujaran kebencian, tetapi juga mengklasifikasikannya secara mendalam berdasarkan **Target**, **Kategori**, dan **Tingkat Kekerasan**. 
JagaKata dibangun menggunakan model **IndoBERTweet** yang telah di-*fine-tune*, dan mampu memproses input dari berbagai sumber seperti teks langsung, komentar YouTube, serta dokumen.

---

## Fitur Utama

###  Deteksi Multi-Label

* Mengidentifikasi teks sebagai **Hate Speech** atau **Non-Hate Speech**

###  Analisis Mendalam

* **Target**: Individu (*Individual*) atau Kelompok (*Group*)
* **Kategori**: Agama, Ras, Fisik, Gender, atau Lainnya
* **Level**: Lemah (*Weak*), Sedang (*Moderate*), atau Kuat (*Strong*)

### Multi-Input Support

*  **Teks**: Ketik langsung untuk analisis cepat
*  **YouTube**: Analisis otomatis komentar video YouTube hanya dengan URL
*  **File**: Unggah berkas `.csv`, `.xlsx`, `.txt` untuk analisis massal

###  Visualisasi & Laporan

* Diagram lingkaran dan tabel interaktif
* Unduh hasil analisis ke format **CSV**

---

##  Struktur Repositori

Repositori ini terdiri dari dua bagian utama:

### 1️⃣ `FrontEnd/` – Aplikasi Web

Berisi kode aplikasi web beserta backend server yang siap untuk *deployment*.

```
FrontEnd/
├── app.py                 # Server utama berbasis FastAPI
├── templates/             # File HTML (Jinja2)
├── static/                # CSS, JavaScript, aset frontend
├── utils/                 # Pemrosesan model, file, dan API YouTube
├── saved-model/           # Model hasil fine-tuning
└── requirements.txt
```

### 2️⃣ `Training/` – Pengembangan Model

Berisi dokumentasi proses penelitian dan pengembangan model dalam bentuk *Notebook* (Google Colab).

* **Data Scraping** – Pengumpulan data
* **Preprocessing** – Pembersihan dan persiapan data
* **Training** – Fine-tuning model IndoBERTweet
* **Evaluasi** – Confusion Matrix, F1-Score, Threshold Tuning
* **Human Evaluation** – Validasi manual oleh manusia

---


## 🌐 Demo Aplikasi

Aplikasi ini telah di-*deploy* dan dapat dicoba secara langsung melalui **Hugging Face Spaces**:

👉 **Akses JagaKata di Hugging Face**
*[(Aplikasi JagaKata)](https://huggingface.co/spaces/Yona1201/JagaKata)*

---

## 💻 Instalasi Lokal

Ikuti langkah berikut untuk menjalankan JagaKata secara lokal:

### 1️⃣ Clone Repositori

```bash
git clone https://github.com/username-anda/JagaKata.git
cd JagaKata/FrontEnd
```

### 2️⃣ Buat Virtual Environment *(Opsional, Disarankan)*

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Atur API Key YouTube

Buat file `.env` lalu tambahkan API Key dari Google Cloud:

```env
YOUTUBE_API_KEY=Kunci_API_Anda_Disini
```

### 5️⃣ Jalankan Aplikasi

```bash
uvicorn app:app --reload
```

Buka browser dan akses:

```
http://127.0.0.1:8000
```

---

##  Catatan

* Pastikan model sudah tersedia di folder `saved-model/`
* Fitur YouTube membutuhkan API Key yang aktif
* Sistem ini mendukung klasifikasi **multi-label**, bukan klasifikasi tunggal

---

## Konteks Penelitian

JagaKata dikembangkan sebagai bagian dari penelitian dan skripsi dengan fokus pada:

* Deteksi ujaran kebencian multi-label
* Fine-tuning IndoBERTweet
* Cost-Sensitive Learning
* Threshold Tuning untuk label tidak seimbang

---

✨ *JagaKata — Menjaga Bahasa, Merawat Keberagaman* ✨
