import sys
from pathlib import Path

# Memastikan direktori backend ada dalam sys.path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.config import GEMINI_API_KEY, OUTPUT_DIR
from src.youtube import YouTubeService
from src.analyzer import MomentAnalyzer
from src.clipper import VideoClipper

def print_banner():
    print("""
===================================================================
        🎬 AUTO CLIP & VIRAL MOMENT FINDER (SHORTS/REELS/TIKTOK) 🎬
===================================================================
    """)

def run():
    print_banner()
    
    if not GEMINI_API_KEY:
        print("💡 INFO: GEMINI_API_KEY belum diisi di file .env")
        print("   -> Sistem akan mendeteksi momen menggunakan data 'YouTube Most Replayed Heatmap'.")
        print("   -> Jika ingin analisis transkrip & hook kalimat lebih mendalam, isi API key di .env.")
        print("-" * 67)
    elif not GEMINI_API_KEY.startswith("AIzaSy"):
        print("⚠️ PERINGATAN: GEMINI_API_KEY di .env tidak diawali dengan 'AIzaSy'.")
        print("   -> Pastikan key Anda berasal dari: https://aistudio.google.com/app/apikey")
        print("-" * 67)
    else:
        print("✨ GEMINI AI AKTIF: Deteksi hook kalimat, emosi, dan punchline otomatis aktif.")
        print("-" * 67)

    yt = YouTubeService()
    analyzer = MomentAnalyzer()
    clipper = VideoClipper()

    while True:
        try:
            url = input("\n🔗 Masukkan / Paste Link YouTube (atau ketik 'exit' untuk keluar): ").strip()
            if not url or url.lower() in ["exit", "q", "quit"]:
                print("Sampai jumpa!")
                break

            print("\n[*] Mengambil data video...")
            try:
                info = yt.get_video_info(url)
            except Exception as e:
                print(f"[❌] Gagal mengambil data video: {e}")
                continue

            print(f"🎬 Judul   : {info['title']}")
            print(f"👤 Channel : {info['channel']}")
            print(f"⏱️  Durasi  : {info['duration_formatted']}")

            # Jika memakai AI Gemini, download audio cepat untuk dianalisis
            audio_path = None
            if GEMINI_API_KEY:
                print("[*] Mendownload audio preview untuk analisis AI...")
                audio_path = yt.download_audio_for_analysis(url, info["id"])

            print("[*] Menganalisis momen-momen paling potensial viral...")
            moments = analyzer.analyze(info, audio_path)

            if not moments:
                print("[⚠️] Tidak ditemukan momen yang cukup menonjol pada video ini.")
                continue

            print(f"\n🔥 DITEMUKAN {len(moments)} MOMEN POTENSIAL VIRAL:")
            print("=" * 80)
            for idx, m in enumerate(moments, 1):
                print(f"[{idx}] ⏱️  {m['start_time']} -> {m['end_time']} ({m['duration_seconds']}s) | Viral Score: {m['viral_score']}/100")
                
                # Menampilkan Rekomendasi Judul
                titles = m.get('recommended_titles', [m.get('title', 'Klip Menarik')])
                print("    🏷️  Rekomendasi Judul:")
                for t_idx, t in enumerate(titles, 1):
                    print(f"        {t_idx}. \"{t}\"")
                
                if m.get('hook'):
                    print(f"    🎣 Hook Pembuka : \"{m['hook']}\"")
                print(f"    💡 Alasan Viral : {m['why_viral']}")
                print("-" * 80)

            # Pilihan untuk langsung meng-clip
            pilihan = input("\n✂️  Pilih nomor yang ingin di-clip ke format vertikal 9:16 (contoh: 1, 2, 'all', atau 'n' untuk batal): ").strip()
            
            if pilihan.lower() in ['n', 'batal', 'no', '']:
                continue

            to_clip = []
            if pilihan.lower() == 'all':
                to_clip = moments
            else:
                for num_str in pilihan.replace(",", " ").split():
                    if num_str.isdigit():
                        n = int(num_str)
                        if 1 <= n <= len(moments):
                            to_clip.append(moments[n - 1])

            if not to_clip:
                print("Tidak ada nomor yang dipilih.")
                continue

            print(f"\n🚀 Memulai proses clipping untuk {len(to_clip)} momen terpilih...\n")

            for m in to_clip:
                print(f"[*] Mendownload segmen {m['start_time']} - {m['end_time']} ...")
                clip_raw = yt.download_video_clip(
                    url,
                    m["start_seconds"],
                    m["end_seconds"],
                    f"{info['id']}_{m['start_time'].replace(':', '.')}"
                )

                # Format nama output
                safe_title = m['title'].replace(" ", "_")[:30]
                out_name = f"CLIP_{m['start_time'].replace(':', '.')}_{safe_title}"

                # Konversi ke 9:16 vertikal
                final_file = clipper.convert_to_vertical(clip_raw, out_name)

                # Simpan metadata teks (Judul + Caption + Hashtag) di samping file video
                meta_file = final_file.with_suffix(".txt")
                titles = m.get('recommended_titles', [m.get('title')])
                
                meta_content = f"JUDUL REKOMENDASI:\n"
                for i, t in enumerate(titles, 1):
                    meta_content += f"{i}. {t}\n"
                meta_content += f"\nHOOK PEMBUKA:\n\"{m.get('hook', '')}\"\n"
                meta_content += f"\nCAPTION MEDSOS:\n{m.get('suggested_caption', '')}\n\nHASHTAGS:\n{' '.join(m.get('hashtags', []))}\n"
                
                meta_file.write_text(meta_content, encoding="utf-8")

                print(f"\n✅ Klip Berhasil Dibuat: {final_file.name}")
                print(f"📁 Lokasi Video  : {final_file.resolve()}")
                print(f"📄 Lokasi Catatan: {meta_file.resolve()}")
                print(f"\n🏷️  PILIHAN JUDUL UNTUK POSTING KE MEDSOS:")
                for i, t in enumerate(titles, 1):
                    print(f"   👉 Opsi {i}: \"{t}\"")
                print(f"\n📝 Caption Siap Copas:\n{m.get('suggested_caption', '')} {' '.join(m.get('hashtags', []))}\n")
                print("=" * 80)

            print(f"\n🎉 Semua klip selesai diproses! Periksa folder: {OUTPUT_DIR.resolve()}\n")

        except KeyboardInterrupt:
            print("\nDibatalkan oleh user.")
            break
        except Exception as err:
            print(f"\n[❌] Terjadi kesalahan: {err}")

if __name__ == "__main__":
    run()
