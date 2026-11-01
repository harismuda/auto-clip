import json
import re
import time
from pathlib import Path
from typing import List, Dict, Any

from .config import GEMINI_API_KEY, DEFAULT_MIN_CLIP_DURATION, DEFAULT_MAX_CLIP_DURATION
from .youtube import seconds_to_timestamp, time_to_seconds

class MomentAnalyzer:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.genai = None
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.genai = genai
            except Exception as e:
                print(f"[!] Gagal inisialisasi modul Gemini: {e}")

    def analyze(self, video_info: dict, audio_path: Path = None) -> List[Dict[str, Any]]:
        """Menganalisis momen terbaik untuk di-clip.
        Jika API key tersedia dan audio ada, gunakan AI Gemini.
        Jika tidak, gunakan analisis YouTube Heatmap / Smart Sampling."""
        if self.genai and audio_path and audio_path.exists():
            try:
                print("\n[AI] Mengirim audio ke Google Gemini untuk analisis momen & pembuatan judul viral...")
                moments = self._analyze_with_gemini(video_info, audio_path)
                if moments:
                    return moments
                print("[!] AI tidak mengembalikan momen valid, beralih ke analisis cadangan.")
            except Exception as e:
                err_str = str(e)
                print(f"\n[⚠️] Kendala pada Google Gemini AI: {err_str}")
                if "API_KEY_INVALID" in err_str or "API key not valid" in err_str:
                    print("\n" + "=" * 75)
                    print("🚨 PERHATIAN: API KEY GEMINI TIDAK VALID!")
                    print("   Key yang terpasang saat ini tidak dikenali oleh Google API.")
                    print("   Kunci resmi dari Google AI Studio selalu diawali dengan 'AIzaSy...'.")
                    print("   👉 Dapatkan API Key GRATIS di: https://aistudio.google.com/app/apikey")
                    print("   Lalu ganti isinya di file .env")
                    print("=" * 75 + "\n")
                print("[*] Menggunakan metode analisis cerdas alternatif sebagai cadangan...\n")

        # Cadangan: Analisis dari YouTube Heatmap Replay / Smart Sampling
        return self._analyze_with_heatmap(video_info)

    def _analyze_with_gemini(self, video_info: dict, audio_path: Path) -> List[Dict[str, Any]]:
        """Analisis audio menggunakan Gemini Flash untuk menemukan momen dan rekomendasi judul viral."""
        print(f"[*] Mengunggah audio ({audio_path.stat().st_size // 1024} KB) ke Gemini...")
        audio_file = self.genai.upload_file(path=str(audio_path))
        
        # Tunggu sampai file selesai diproses
        while audio_file.state.name == "PROCESSING":
            time.sleep(2)
            audio_file = self.genai.get_file(audio_file.name)

        if audio_file.state.name == "FAILED":
            raise ValueError("Gagal memproses file audio di Google Gemini.")

        prompt = f"""
Kamu adalah produser konten viral profesional untuk TikTok, YouTube Shorts, dan Instagram Reels.
Video ini berjudul: "{video_info.get('title')}" dari channel "{video_info.get('channel')}" dengan total durasi {video_info.get('duration_formatted')}.

Tugasmu:
Dengarkan dan analisis rekaman audio ini, lalu temukan 3 hingga 5 momen PALING BERPOTENSI VIRAL untuk dipotong menjadi video pendek (Shorts/Reels/TikTok).

Untuk SETIAP momen yang kamu temukan, buatkan minimal 3 PILIHAN REKOMENDASI JUDUL VIRAL yang sangat menarik (High Click-Through Rate / Hook Title).

Kriteria momen viral:
1. Durasi ideal: antara {DEFAULT_MIN_CLIP_DURATION} sampai {DEFAULT_MAX_CLIP_DURATION} detik.
2. Hook kuat di 3 detik pertama (pertanyaan menarik, pernyataan kontroversial, fakta mengejutkan, atau emosi tinggi).
3. Memiliki alur yang utuh: penonton paham konteksnya tanpa harus menonton seluruh video asli.
4. Diakhiri dengan punchline, klimaks, atau nasihat berharga.

Keluarkan HANYA format JSON valid tanpa tanda markdown luar:
[
  {{
    "start_time": "MM:SS",
    "end_time": "MM:SS",
    "duration_seconds": 45,
    "viral_score": 95,
    "recommended_titles": [
      "Judul 1: Gaya Penasaran / Hook Kuat",
      "Judul 2: Gaya Kontroversial / Tegas / Nasihat",
      "Judul 3: Gaya Pertanyaan / Relatable"
    ],
    "hook": "Kalimat pembuka di 3 detik pertama",
    "why_viral": "Alasan spesifik mengapa bagian ini akan viral",
    "suggested_caption": "Caption menarik untuk postingan medsos",
    "hashtags": ["#fyp", "#shorts", "#viral"]
  }}
]
"""

        models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"]
        response_text = None

        for model_name in models_to_try:
            try:
                model = self.genai.GenerativeModel(model_name=model_name)
                res = model.generate_content([audio_file, prompt])
                response_text = res.text
                if response_text:
                    break
            except Exception:
                continue

        # Bersihkan file dari server Google
        try:
            audio_file.delete()
        except Exception:
            pass

        if not response_text:
            raise ValueError("Tidak ada respons teks dari Gemini model.")

        # Parsing JSON
        clean_json = re.sub(r"^```json\s*", "", response_text.strip())
        clean_json = re.sub(r"\s*```$", "", clean_json.strip())
        parsed = json.loads(clean_json)

        results = []
        for item in parsed:
            start_sec = time_to_seconds(item.get("start_time"))
            end_sec = time_to_seconds(item.get("end_time"))
            dur = end_sec - start_sec
            if dur <= 0:
                dur = item.get("duration_seconds", 45)
                end_sec = start_sec + dur

            titles = item.get("recommended_titles", [])
            if not titles and item.get("title"):
                titles = [item.get("title")]

            results.append({
                "start_time": seconds_to_timestamp(start_sec),
                "end_time": seconds_to_timestamp(end_sec),
                "start_seconds": start_sec,
                "end_seconds": end_sec,
                "duration_seconds": int(dur),
                "viral_score": item.get("viral_score", 90),
                "title": titles[0] if titles else "Momen Menarik",
                "recommended_titles": titles,
                "hook": item.get("hook", ""),
                "why_viral": item.get("why_viral", "Konten menarik dan memancing interaksi."),
                "suggested_caption": item.get("suggested_caption", ""),
                "hashtags": item.get("hashtags", ["#fyp", "#shorts", "#viral"]),
                "source": "AI Gemini Analysis"
            })

        return sorted(results, key=lambda x: x["viral_score"], reverse=True)

    def _analyze_with_heatmap(self, video_info: dict) -> List[Dict[str, Any]]:
        """Mendeteksi momen paling banyak ditonton ulang oleh audiens YouTube (Most Replayed Heatmap)."""
        heatmap = video_info.get("heatmap", [])
        duration = video_info.get("duration", 0)
        raw_title = video_info.get("title", "Video")
        channel = video_info.get("channel", "Creator")

        if not heatmap or duration <= 0:
            return self._fallback_sampling(video_info)

        sorted_points = sorted(heatmap, key=lambda x: x.get("value", 0), reverse=True)
        selected_windows = []

        for idx, pt in enumerate(sorted_points):
            pt_start = pt.get("start_time", 0)
            pt_end = pt.get("end_time", pt_start + 5)
            peak_center = (pt_start + pt_end) / 2

            clip_start = max(0, peak_center - 20)
            clip_end = min(duration, clip_start + 45)

            overlap = False
            for w in selected_windows:
                if not (clip_end < w["start_seconds"] or clip_start > w["end_seconds"]):
                    overlap = True
                    break

            if not overlap:
                score = int(round(pt.get("value", 0.5) * 100))
                num = len(selected_windows) + 1
                
                # Rekomendasi judul bervariasi
                rec_titles = [
                    f"DETIK PALING BANYAK DIULANG PENONTON! - {raw_title[:45]}",
                    f"Bagian Ini Bikin Penonton Kaget! ({channel})",
                    f"Jangan Skip Bagian Ini! {raw_title[:50]}"
                ]

                selected_windows.append({
                    "start_time": seconds_to_timestamp(clip_start),
                    "end_time": seconds_to_timestamp(clip_end),
                    "start_seconds": clip_start,
                    "end_seconds": clip_end,
                    "duration_seconds": int(clip_end - clip_start),
                    "viral_score": max(75, min(99, score)),
                    "title": rec_titles[0],
                    "recommended_titles": rec_titles,
                    "hook": "Detik-detik yang paling sering diputar ulang oleh ribuan penonton YouTube!",
                    "why_viral": "Data YouTube Heatmap resmi mencatat lonjakan retensi dan replay drastis pada menit ini.",
                    "suggested_caption": f"Momen paling banyak di-replay di video '{raw_title}' oleh {channel}! Menurut kalian gimana?",
                    "hashtags": ["#fyp", "#shorts", "#trending", "#viral"],
                    "source": "YouTube Most Replayed Heatmap"
                })

            if len(selected_windows) >= 4:
                break

        return selected_windows

    def _fallback_sampling(self, video_info: dict) -> List[Dict[str, Any]]:
        """Sampling cerdas berdasarkan alur video jika belum ada heatmap/AI."""
        duration = video_info.get("duration", 180)
        raw_title = video_info.get("title", "Video")
        channel = video_info.get("channel", "Creator")
        
        sample_times = [
            (min(duration * 0.12, 20), "Pembukaan & Hook Awal", [
                f"PESAN PENTING: {raw_title[:50]}",
                f"Kalau Lu Nonton Ini, Dengerin Baik-Baik! ({channel})",
                f"Poin Penting Buat Kalian (Wajib Dengar!)"
            ]),
            (duration * 0.45, "Puncak Pembahasan", [
                f"POIN PALING MAHAL: {raw_title[:50]}",
                f"Realita Yang Jarang Diomongin Orang! ({channel})",
                f"Ini Alasan Kenapa Banyak Orang Sadar Setelah Nonton Ini"
            ]),
            (duration * 0.75, "Nasihat & Kesimpulan Krusial", [
                f"JANGAN SAMPAI NYESEL TERLAMBAT! [PENTING] - {raw_title[:45]}",
                f"Kesimpulan Penting Dari {channel}!",
                f"Catat Poin Terakhir Ini Baik-Baik!"
            ])
        ]

        clips = []
        for i, (st, phase, titles) in enumerate(sample_times):
            en = min(duration, st + 45)
            clips.append({
                "start_time": seconds_to_timestamp(st),
                "end_time": seconds_to_timestamp(en),
                "start_seconds": st,
                "end_seconds": en,
                "duration_seconds": int(en - st),
                "viral_score": 88 - (i * 4),
                "title": titles[0],
                "recommended_titles": titles,
                "hook": f"Bagian {phase} yang sarat akan makna dan pesan berbobot.",
                "why_viral": "Poin krusial dalam alur video yang memicu audiens berdiskusi di kolom komentar.",
                "suggested_caption": f"Dengerin nasihat ini dari {channel}: '{raw_title}'. Jangan lupa save & share ke teman kalian!",
                "hashtags": ["#shorts", "#fyp", "#trending", "#motivation", "#viral"],
                "source": "Smart Sampling"
            })
        return clips
