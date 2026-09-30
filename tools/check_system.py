import shutil
import sys
import requests
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from xinliflow.config import settings

def ok(label, value):
    print(f"[OK] {label}: {value}")

def fail(label, value):
    print(f"[!!] {label}: {value}")

print("XinLiFlow system check\n")

python_version = ".".join(map(str, sys.version_info[:3]))
ok("Python", python_version)

ffmpeg = shutil.which(settings.ffmpeg_bin)
ffprobe = shutil.which(settings.ffprobe_bin)
(ok if ffmpeg else fail)("FFmpeg", ffmpeg or "not found in PATH")
(ok if ffprobe else fail)("FFprobe", ffprobe or "not found in PATH")

try:
    r = requests.get(f"{settings.voicestudio_url}/health", timeout=3)
    if r.ok:
        ok("VoiceStudio", f"{settings.voicestudio_url} ({r.status_code})")
    else:
        fail("VoiceStudio", f"HTTP {r.status_code}")
except Exception:
    fail("VoiceStudio", f"not reachable at {settings.voicestudio_url}")

if settings.pexels_api_key:
    ok("Pexels", "API key configured")
else:
    fail("Pexels", "PEXELS_API_KEY is empty; fallback background will be used")

print("\nFix missing items, then run:")
print('python generate.py "examples/01_一句话内耗一整天.md" -o "output/01_拒绝内耗.mp4"')
