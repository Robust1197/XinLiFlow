# XinLiFlow / 拒绝内耗

把一篇中文文章自动变成小红书 9:16 旁白视频。

第一版流程：

**文章 → 自动分镜 → VoiceStudio 自己的克隆声音 → Pexels 合法 B-roll → 中文字幕 → 1080×1920 MP4**

> 不自动抓取电影/电视剧画面。长期做账号时，版权风险不值得。这里优先使用 Pexels 的可授权素材。

## 1. 前置条件

- Windows / macOS / Linux
- Python 3.11+
- FFmpeg（命令行能执行 `ffmpeg -version`）
- VoiceStudio 正在本机运行，默认后端 `http://localhost:3900`
- 你已经在 VoiceStudio 保存了自己有权使用的克隆声音
- 可选：Pexels API Key。没有 Key 时仍能生成视频，但使用纯色背景。

## 2. 安装

```powershell
cd C:\Users\fukur\XinLiFlow
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

编辑 `.env`：

```env
VOICESTUDIO_URL=http://localhost:3900
VOICESTUDIO_VOICE=
PEXELS_API_KEY=你的_Pexels_Key
```

`VOICESTUDIO_VOICE` 留空时会自动读取 `/v1/audio/voices` 并选择第一个声音。第一次建议先运行下面的检查命令，看一下你保存的声音 ID。

## 3. 检查 VoiceStudio

```powershell
python tools/check_voicestudio.py
```

## 4. 生成第一条视频

```powershell
python generate.py "examples/01_一句话内耗一整天.md" -o "output/01_拒绝内耗.mp4"
```

生成过程会保留：

```text
work/01_一句话内耗一整天/
  scenes.json   # 自动分镜 + 每段 B-roll 搜索词
  audio/        # VoiceStudio 旁白
  media/        # Pexels B-roll
  subs/         # ASS 中文字幕
  clips/        # 每个分镜的视频
output/
  01_拒绝内耗.mp4
```

## 5. 日常使用

以后只需要把文章保存为 Markdown：

```powershell
python generate.py "我的文章.md" -o "output/今天的视频.mp4"
```

### 如何调整自动配图

程序会把每个段落映射为英文视觉搜索词，例如：

- “同事/会议/工作” → `stressed office worker meeting alone`
- “手机/朋友/聊天” → `person reading message phone worried`
- “写下来/备忘录” → `person writing journal notebook close up`
- “注意力/分心” → `distracted person desk laptop`

每次生成前后都可以查看 `work/<文章名>/scenes.json`。下一版会加入“修改 scenes.json 后只重新下载画面、不重新生成声音”的模式。

## VoiceStudio 兼容策略

VoiceStudio 的原生 cloning/profile API 会持续演进，因此本项目不自己创建克隆声音，而是：

1. `GET /health`
2. `GET /v1/audio/voices`
3. 使用已经保存的 Voice profile ID
4. `POST /v1/audio/speech`

这样升级 VoiceStudio 后更稳定，也避免重复建立你的声音 profile。

## 版权

Pexels 素材仍需遵守 Pexels 当前许可条款和平台规则。不要把“能下载”理解为任意二次使用都没有限制。

电影/电视剧截图与片段默认不纳入自动素材源。若以后你提供自己拥有版权或已经取得授权的素材，可以增加本地素材库模式。
