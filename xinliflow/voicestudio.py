from __future__ import annotations
from pathlib import Path
import requests
from .config import settings

class VoiceStudioError(RuntimeError):
    pass

class VoiceStudioClient:
    def __init__(self):
        self.base = settings.voicestudio_url
        self.headers = {}
        if settings.voicestudio_auth_header and settings.voicestudio_auth_value:
            self.headers[settings.voicestudio_auth_header] = settings.voicestudio_auth_value

    def health(self) -> dict:
        r = requests.get(f"{self.base}/health", headers=self.headers, timeout=10)
        r.raise_for_status()
        return r.json() if "json" in r.headers.get("content-type", "") else {"status": r.text}

    def voices(self):
        r = requests.get(f"{self.base}/v1/audio/voices", headers=self.headers, timeout=20)
        r.raise_for_status()
        data = r.json()
        return data.get("data", data) if isinstance(data, dict) else data

    def choose_voice(self) -> str:
        if settings.voicestudio_voice:
            return settings.voicestudio_voice
        voices = self.voices()
        if not voices:
            raise VoiceStudioError("VoiceStudio 没有发现可用声音。请先在 VoiceStudio 保存你的克隆声音。")
        v = voices[0]
        if isinstance(v, str):
            return v
        for key in ("id", "voice_id", "profile_id", "name"):
            if v.get(key):
                return str(v[key])
        raise VoiceStudioError(f"无法从 VoiceStudio voice 对象识别 ID: {v}")

    def synthesize(self, text: str, output: Path, voice: str | None = None) -> Path:
        voice = voice or self.choose_voice()
        payload = {
            "model": "tts-1",
            "voice": voice,
            "input": text,
            "response_format": "wav",
        }
        headers = {"Content-Type": "application/json", **self.headers}
        r = requests.post(f"{self.base}/v1/audio/speech", json=payload, headers=headers, timeout=900)
        if not r.ok:
            raise VoiceStudioError(f"VoiceStudio TTS 失败 {r.status_code}: {r.text[:500]}")
        if "json" in r.headers.get("content-type", ""):
            raise VoiceStudioError(f"VoiceStudio 返回了 JSON 而不是音频: {r.text[:500]}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(r.content)
        if output.stat().st_size < 1000:
            raise VoiceStudioError("VoiceStudio 生成的音频异常小，已停止。")
        return output
