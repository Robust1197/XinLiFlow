from dataclasses import dataclass
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    root: Path = Path(__file__).resolve().parents[1]
    voicestudio_url: str = os.getenv("VOICESTUDIO_URL", "http://localhost:3900").rstrip("/")
    voicestudio_voice: str = os.getenv("VOICESTUDIO_VOICE", "").strip()
    voicestudio_auth_header: str = os.getenv("VOICESTUDIO_AUTH_HEADER", "").strip()
    voicestudio_auth_value: str = os.getenv("VOICESTUDIO_AUTH_VALUE", "").strip()
    pexels_api_key: str = os.getenv("PEXELS_API_KEY", "").strip()
    ffmpeg_bin: str = os.getenv("FFMPEG_BIN", "ffmpeg")
    ffprobe_bin: str = os.getenv("FFPROBE_BIN", "ffprobe")
    width: int = int(os.getenv("OUTPUT_WIDTH", "1080"))
    height: int = int(os.getenv("OUTPUT_HEIGHT", "1920"))
    fps: int = int(os.getenv("FPS", "30"))
    brand_name: str = os.getenv("BRAND_NAME", "拒绝内耗")
    brand_tagline: str = os.getenv("BRAND_TAGLINE", "少一点内耗，保护有限的心力")

settings = Settings()
