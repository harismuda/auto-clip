import subprocess
import re
from pathlib import Path
from .config import OUTPUT_DIR, TARGET_WIDTH, TARGET_HEIGHT

class VideoClipper:
    def __init__(self):
        self.output_dir = OUTPUT_DIR

    def convert_to_vertical(self, input_video: Path, output_filename: str, hook_title: str = None) -> Path:
        """Mengubah video 16:9 menjadi 9:16 vertikal (1080x1920) dengan efek Blurred Background."""
        safe_name = re.sub(r'[\\/*?:"<>|]', "_", output_filename)[:60]
        output_path = self.output_dir / f"{safe_name}.mp4"

        # Filter FFmpeg:
        # 1. Background diperbesar memenuhi 1080x1920 lalu diburamkan (boxblur)
        # 2. Video asli diskalakan selebar 1080px dan ditaruh di tengah
        # 3. Keduanya digabung (overlay)
        filter_complex = (
            f"[0:v]scale={TARGET_WIDTH}:{TARGET_HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={TARGET_WIDTH}:{TARGET_HEIGHT},boxblur=20:20[bg];"
            f"[0:v]scale={TARGET_WIDTH}:-2[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
        )

        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(input_video),
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            str(output_path)
        ]

        print(f"[*] Merender video vertikal 9:16: {output_path.name} ...")
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            print(f"[!] Warning: FFmpeg render error:\n{proc.stderr[-400:]}")
            raise RuntimeError(f"Gagal memproses video dengan FFmpeg: {proc.stderr[-200:]}")

        return output_path

