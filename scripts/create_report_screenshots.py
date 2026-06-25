from __future__ import annotations

import os
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT_DIR / "reports" / "screenshots"
PYTHON = ROOT_DIR / ".venv" / "bin" / "python"

FONT_CANDIDATES = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for font_path in FONT_CANDIDATES:
        if Path(font_path).exists():
            return ImageFont.truetype(font_path, size=size)
    return ImageFont.load_default()


def run_command(args: list[str]) -> str:
    env = os.environ.copy()
    env["PYTHONWARNINGS"] = "ignore"
    completed = subprocess.run(
        args,
        cwd=ROOT_DIR,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return completed.stdout.strip()


def wrap_text(text: str, width: int = 82) -> str:
    lines: list[str] = []
    for raw_line in text.splitlines():
        if len(raw_line) <= width:
            lines.append(raw_line)
            continue
        lines.extend(textwrap.wrap(raw_line, width=width, replace_whitespace=False, drop_whitespace=False))
    return "\n".join(lines)


def make_text_image(title: str, body: str, out_path: Path) -> None:
    font = load_font(20)
    title_font = load_font(22)
    line_height = 30
    margin = 38
    wrapped = wrap_text(body)
    lines = [title, "=" * len(title), "", *wrapped.splitlines()]
    width = 1480
    height = margin * 2 + line_height * len(lines)
    image = Image.new("RGB", (width, height), "#FFFFFF")
    draw = ImageDraw.Draw(image)
    y = margin
    for index, line in enumerate(lines):
        current_font = title_font if index == 0 else font
        color = "#1F4D78" if index == 0 else "#222222"
        draw.text((margin, y), line, fill=color, font=current_font)
        y += line_height
    image.save(out_path)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    smoke_output = run_command([str(PYTHON), "src/smoke_test.py"])
    make_text_image("Smoke Test Output", smoke_output, OUT_DIR / "smoke_test_output.png")

    agent_output = run_command([str(PYTHON), "src/agent.py", "每个赛季的比赛数量是多少？"])
    make_text_image("DeepSeek Agent Output", agent_output, OUT_DIR / "deepseek_agent_output.png")

    print(OUT_DIR / "smoke_test_output.png")
    print(OUT_DIR / "deepseek_agent_output.png")


if __name__ == "__main__":
    main()
