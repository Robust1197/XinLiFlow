from __future__ import annotations
from pathlib import Path
import json
import subprocess
from .config import settings

def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode:
        raise RuntimeError("命令失败:\n" + " ".join(cmd) + "\n" + proc.stderr[-2000:])

def duration(path: Path) -> float:
    proc = subprocess.run(
        [settings.ffprobe_bin, "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
        text=True, capture_output=True,
    )
    if proc.returncode:
        raise RuntimeError(f"ffprobe 失败: {proc.stderr}")
    return float(json.loads(proc.stdout)["format"]["duration"])

def ass_escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}").replace("\n", r"\N")

def subtitle_chunks(text: str, max_chars: int = 18) -> list[str]:
    chunks, buf = [], ""
    for ch in text.replace("\n", ""):
        buf += ch
        if len(buf) >= max_chars or ch in "。！？；，":
            if buf.strip():
                chunks.append(buf.strip())
            buf = ""
    if buf.strip():
        chunks.append(buf.strip())
    return chunks

def ass_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def write_ass(text: str, total: float, output: Path) -> None:
    chunks = subtitle_chunks(text)
    weights = [max(len(c), 3) for c in chunks]
    total_weight = sum(weights) or 1
    cur = 0.0
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {settings.width}",
        f"PlayResY: {settings.height}",
        "WrapStyle: 2",
        "",
        "[V4+ Styles]",
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding",
        "Style: Default,Microsoft YaHei,62,&H00FFFFFF,&H000000FF,&H00181818,&H78000000,-1,0,0,0,100,100,0,0,1,4,0,2,90,90,250,1",
        "",
        "[Events]",
        "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
    ]
    for i, (chunk, weight) in enumerate(zip(chunks, weights)):
        span = total * weight / total_weight
        end = total if i == len(chunks) - 1 else min(total, cur + span)
        lines.append(f"Dialogue: 0,{ass_time(cur)},{ass_time(end)},Default,,0,0,0,,{ass_escape(chunk)}")
        cur = end
    output.write_text("\n".join(lines), encoding="utf-8-sig")

def render_scene(video: Path | None, audio: Path, ass: Path, output: Path) -> None:
    d = duration(audio)
    output.parent.mkdir(parents=True, exist_ok=True)
    vf = (
        f"scale={settings.width}:{settings.height}:force_original_aspect_ratio=increase,"
        f"crop={settings.width}:{settings.height},"
        "eq=brightness=-0.06:saturation=0.82,"
        f"ass='{str(ass).replace('\\', '/').replace(':', '\\:')}'"
    )
    if video:
        cmd = [
            settings.ffmpeg_bin, "-y", "-stream_loop", "-1", "-i", str(video), "-i", str(audio),
            "-t", f"{d:.3f}", "-vf", vf, "-r", str(settings.fps),
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-shortest", str(output),
        ]
    else:
        cmd = [
            settings.ffmpeg_bin, "-y", "-f", "lavfi", "-i",
            f"color=c=0x171717:s={settings.width}x{settings.height}:r={settings.fps}",
            "-i", str(audio), "-t", f"{d:.3f}",
            "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-shortest", str(output),
        ]
    run(cmd)

def concat_videos(inputs: list[Path], output: Path, workdir: Path) -> None:
    manifest = workdir / "concat.txt"
    manifest.write_text("\n".join([f"file '{str(p.resolve()).replace(chr(39), chr(39)+chr(92)+chr(39)+chr(39))}'" for p in inputs]), encoding="utf-8")
    run([
        settings.ffmpeg_bin, "-y", "-f", "concat", "-safe", "0", "-i", str(manifest),
        "-c", "copy", str(output),
    ])
