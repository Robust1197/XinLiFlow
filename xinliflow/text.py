import re
from dataclasses import dataclass

@dataclass
class Scene:
    index: int
    text: str
    search_query: str

KEYWORDS = [
    (("同事", "会议", "工作", "能力"), "stressed office worker meeting alone"),
    (("朋友", "语气", "聊天"), "person reading message phone worried"),
    (("地铁", "走路", "吃饭"), "lonely commuter night city reflection"),
    (("注意力", "集中", "分心"), "distracted person desk laptop"),
    (("错误", "责怪", "失败"), "frustrated worker desk mistake"),
    (("嫉妒", "自卑", "不服气"), "thoughtful person comparing self to others"),
    (("生气", "愤怒", "委屈"), "upset person sitting alone window"),
    (("害怕", "否定"), "anxious person office alone"),
    (("写", "备忘录", "四句话"), "person writing journal notebook close up"),
    (("学习", "20分钟", "表达"), "focused person studying notes desk"),
    (("十分钟", "10分钟"), "clock timer notebook calm desk"),
    (("情绪", "内耗", "难受"), "pensive person alone moody room"),
]

def normalize(text: str) -> str:
    text = text.replace("\r\n", "\n").strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text

def strip_markdown(text: str) -> str:
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.M)
    text = text.replace("**", "").replace("__", "")
    return text.strip()

def split_for_scenes(text: str, max_chars: int = 95) -> list[str]:
    text = strip_markdown(normalize(text))
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    out: list[str] = []
    for block in blocks:
        sentences = [s.strip() for s in re.split(r"(?<=[。！？!?])", block) if s.strip()]
        current = ""
        for sentence in sentences or [block]:
            if current and len(current) + len(sentence) > max_chars:
                out.append(current)
                current = sentence
            else:
                current += sentence
        if current:
            out.append(current)
    return out

def search_query_for(text: str) -> str:
    best = None
    best_score = 0
    for words, query in KEYWORDS:
        score = sum(1 for w in words if w in text)
        if score > best_score:
            best, best_score = query, score
    return best or "pensive person alone cinematic everyday life"

def plan_scenes(text: str) -> list[Scene]:
    return [Scene(i + 1, chunk, search_query_for(chunk)) for i, chunk in enumerate(split_for_scenes(text))]
