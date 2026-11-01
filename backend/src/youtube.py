import os
import re
import yt_dlp
from pathlib import Path
from .config import TEMP_DIR

def time_to_seconds(t_str: str) -> float:
    """Konversi format HH:MM:SS atau MM:SS atau string detik menjadi float detik."""
    t_str = str(t_str).strip()
    parts = t_str.split(":")
    try:
        if len(parts) == 3:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        return float(parts[0])
    except ValueError:
        return 0.0

def seconds_to_timestamp(seconds: float) -> str:
    """Konversi detik ke format MM:SS atau HH:MM:SS."""
    seconds = int(round(seconds))
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"

class YouTubeService:
    def __init__(self):
        self.common_opts = {
            "quiet": True,
            "no_warnings": True,
        }

    def get_video_info(self, url: str) -> dict:
        """Mengambil info video, durasi, judul, dan data heatmap replay."""
        opts = {
            **self.common_opts,
            "skip_download": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            heatmap = info.get("heatmap") or []
            duration = info.get("duration", 0)
            title = info.get("title", "Unknown Title")
            channel = info.get("uploader", "Unknown Channel")
            
            return {
                "id": info.get("id"),
                "title": title,
                "channel": channel,
                "duration": duration,
                "duration_formatted": seconds_to_timestamp(duration),
                "heatmap": heatmap,
                "webpage_url": info.get("webpage_url", url)
            }

    def download_audio_for_analysis(self, url: str, video_id: str) -> Path:
        """Download audio mono bitrate rendah (32-64kbps) agar sangat cepat dan ringan diupload ke AI."""
        output_path = TEMP_DIR / f"{video_id}_analysis.mp3"
        if output_path.exists():
            return output_path

        opts = {
            **self.common_opts,
            "format": "ba/b",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "64",
            }],
            "outtmpl": str(TEMP_DIR / f"{video_id}_analysis.%(ext)s"),
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        return output_path

    def download_video_clip(self, url: str, start_sec: float, end_sec: float, clip_name: str) -> Path:
        """Download HANYA bagian segmen tertentu dari YouTube dengan kualitas terbaik (720p/1080p)."""
        start_ts = seconds_to_timestamp(start_sec)
        end_ts = seconds_to_timestamp(end_sec)
        
        safe_name = re.sub(r'[\\/*?:"<>|]', "_", clip_name)[:50]
        output_template = str(TEMP_DIR / f"{safe_name}_raw.%(ext)s")
        target_path = TEMP_DIR / f"{safe_name}_raw.mp4"

        # Hapus file lama jika ada
        if target_path.exists():
            target_path.unlink()

        opts = {
            **self.common_opts,
            "format": "bv*[height<=1080]+ba/b[height<=1080]/best",
            "download_ranges": yt_dlp.utils.download_range_func(None, [(start_sec, end_sec)]),
            "force_keyframes_at_cuts": True,
            "outtmpl": output_template,
            "merge_output_format": "mp4",
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        # Cari file mp4 yang dihasilkan
        candidates = list(TEMP_DIR.glob(f"{safe_name}_raw.*"))
        if candidates:
            return candidates[0]
        return target_path

