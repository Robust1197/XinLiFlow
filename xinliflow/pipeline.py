from __future__ import annotations
from pathlib import Path
import json
from .config import settings
from .text import plan_scenes
from .voicestudio import VoiceStudioClient
from .pexels import download_video
from .media import duration, write_ass, render_scene, concat_videos

def generate(article: Path, output: Path) -> Path:
    raw = article.read_text(encoding="utf-8")
    scenes = plan_scenes(raw)

    work = settings.root / "work" / article.stem
    audio_dir, media_dir, sub_dir, clip_dir = [work / n for n in ("audio", "media", "subs", "clips")]
    for d in (audio_dir, media_dir, sub_dir, clip_dir):
        d.mkdir(parents=True, exist_ok=True)

    (work / "scenes.json").write_text(
        json.dumps(
            [{"index": s.index, "text": s.text, "search_query": s.search_query} for s in scenes],
            ensure_ascii=False, indent=2,
        ),
        encoding="utf-8",
    )

    vs = VoiceStudioClient()
    vs.health()
    voice = vs.choose_voice()
    print(f"[VoiceStudio] voice = {voice}")

    clips: list[Path] = []
    for scene in scenes:
        stem = f"{scene.index:03d}"
        audio = audio_dir / f"{stem}.wav"
        video = media_dir / f"{stem}.mp4"
        ass = sub_dir / f"{stem}.ass"
        clip = clip_dir / f"{stem}.mp4"

        print(f"[{scene.index}/{len(scenes)}] voice")
        if not audio.exists():
            vs.synthesize(scene.text, audio, voice)

        d = duration(audio)
        write_ass(scene.text, d, ass)

        if settings.pexels_api_key and not video.exists():
            print(f"[{scene.index}/{len(scenes)}] b-roll: {scene.search_query}")
            downloaded = download_video(scene.search_query, video)
            if not downloaded:
                video = None
        elif not video.exists():
            video = None

        print(f"[{scene.index}/{len(scenes)}] render")
        render_scene(video, audio, ass, clip)
        clips.append(clip)

    output.parent.mkdir(parents=True, exist_ok=True)
    concat_videos(clips, output, work)
    print(f"\n完成: {output}")
    print(f"分镜: {work / 'scenes.json'}")
    return output
