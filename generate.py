import argparse
from pathlib import Path
from xinliflow.pipeline import generate

def main():
    p = argparse.ArgumentParser(description="XinLiFlow 小红书竖屏视频生成器")
    p.add_argument("article", type=Path, help="Markdown/TXT 文章")
    p.add_argument("-o", "--output", type=Path, default=Path("output/xinliflow.mp4"))
    args = p.parse_args()
    generate(args.article, args.output)

if __name__ == "__main__":
    main()
