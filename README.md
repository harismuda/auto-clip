# 🎬 Auto Clip - Viral Moment Finder & Reframe

Sistem otomatis untuk mendeteksi momen-momen potensial viral dari link video YouTube, menentukan menit-menit terbaik untuk di-clip, dan otomatis mengubahnya ke format vertikal **9:16 (Shorts / TikTok / Reels)** dengan efek blurred background profesional.

---

### 📁 Struktur Proyek
```
auto clip/
├── backend/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── analyzer.py       # Deteksi momen viral (AI Gemini & YouTube Heatmap)
│   │   ├── clipper.py        # Render video vertikal 9:16 via FFmpeg
│   │   ├── config.py         # Konfigurasi durasi & path direktori
│   │   └── youtube.py        # Pengambilan metadata & download audio/video segmen
│   ├── .env                  # API Key konfigurasi
│   ├── .env.example          # Template konfigurasi
│   ├── main.py               # Entrypoint backend utama
│   ├── requirements.txt      # Dependensi Python
│   └── temp/                 # File sementara saat proses
├── output/                   # Folder hasil video klip vertikal siap upload
├── .env                      # API Key (disinkronkan di root)
├── main.py                   # Shortcut runner dari root
└── README.md
```

---

### ✨ Fitur Utama

1. **Paste Link YouTube Saja:**
   - Cukup paste link YouTube (podcast, gameplay, talkshow, ceramah, dsb).
   - Sistem akan menganalisis durasi, judul, dan isi video.

2. **Dua Mode Deteksi Menit Viral:**
   - **Mode AI Gemini (Aktif):** Menggunakan model AI Google Gemini untuk menganalisis kalimat pembuka (*Hook* 3 detik pertama), emosi, punchline, dan memberikan skor viral (1-100) serta alasan mengapa momen tersebut viral.
   - **Mode YouTube Heatmap (Cadangan/Tanpa API Key):** Mengambil data grafik *Most Replayed* resmi dari YouTube untuk mengetahui detik-detik yang paling sering ditonton ulang oleh jutaan penonton.

3. **Auto Download Bagian Terpilih:**
   - Anda tidak perlu mendownload video 1 jam penuh! Sistem hanya mendownload bagian menit yang Anda pilih.

4. **Auto Reframe ke Vertikal 9:16 (Shorts / Reels / TikTok):**
   - Menggunakan FFmpeg dengan teknik *Blurred Background* beresolusi 1080x1920 (subjek di tengah tetap jelas dan proporsional).

5. **Auto Caption & Hashtags:**
   - Menyediakan rekomendasi teks caption dan hashtag siap copas ke media sosial.

---

### 🚀 Cara Menjalankan

Anda bisa menjalankan dari root ataupun masuk ke folder `backend`:

**Dari root folder:**
```powershell
python main.py
```

**Atau dari dalam folder backend:**
```powershell
cd backend
python main.py
```

---

### 🔑 Konfigurasi API Key
File `.env` sudah siap dan bisa diisi `GEMINI_API_KEY`:
```env
GEMINI_API_KEY=AIzaSy...
```
*(Daftar gratis di [Google AI Studio](https://aistudio.google.com/))*.
