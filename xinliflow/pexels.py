from __future__ import annotations
from pathlib import Path
import requests
from .config import settings

API = "https://api.pexels.com/videos/search"

def search_video(query: str) -> dict | None:
    if not settings.pexels_api_key:
        return None
    r = requests.get(
        API,
        headers={"Authorization": settings.pexels_api_key},
        params={"query": query, "orientation": "portrait", "per_page": 12, "size": "medium"},
        timeout=30,
    )
    r.raise_for_status()
    videos = r.json().get("videos", [])
    if not videos:
        return None
    # Prefer portrait and reasonably high resolution.
    videos.sort(key=lambda v: (v.get("height", 0) >= v.get("width", 0), v.get("height", 0)), reverse=True)
    return videos[0]

def best_file(video: dict) -> dict | None:
    files = [f for f in video.get("video_files", []) if f.get("link")]
    if not files:
        return None
    files.sort(
        key=lambda f: (
            (f.get("height") or 0) >= (f.get("width") or 0),
            min(f.get("height") or 0, 1920),
            min(f.get("width") or 0, 1080),
        ),
        reverse=True,
    )
    return files[0]

def download_video(query: str, output: Path) -> Path | None:
    video = search_video(query)
    if not video:
        return None
    f = best_file(video)
    if not f:
        return None
    with requests.get(f["link"], stream=True, timeout=90) as r:
        r.raise_for_status()
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("wb") as fh:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    fh.write(chunk)
    return output
