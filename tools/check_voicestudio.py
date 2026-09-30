import json
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from xinliflow.config import settings
from xinliflow.voicestudio import VoiceStudioClient

c = VoiceStudioClient()

try:
    print("health:")
    print(json.dumps(c.health(), ensure_ascii=False, indent=2))
    print("\nvoices:")
    print(json.dumps(c.voices(), ensure_ascii=False, indent=2))
except requests.exceptions.ConnectionError:
    print(f"\n[ERROR] VoiceStudio 后端无法连接：{settings.voicestudio_url}")
    print("请先安装并启动 VoiceStudio。启动后再运行这个检查。")
    sys.exit(1)
except requests.HTTPError as exc:
    print(f"\n[ERROR] VoiceStudio 返回 HTTP 错误：{exc}")
    sys.exit(1)
