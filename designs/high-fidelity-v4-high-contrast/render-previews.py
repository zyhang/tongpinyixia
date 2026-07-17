from __future__ import annotations

import os
import subprocess
from pathlib import Path
from urllib.parse import urlencode

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "previews"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
RUNTIME = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies"
NODE = RUNTIME / "node/bin/node"
NODE_MODULES = RUNTIME / "node/node_modules"
VIEWPORT = (390, 844)
SCALE = 3
PAGES = {
    "question": ("01-today-question", "01 今日一问"),
    "result": ("02-result-and-reason", "02 选择结果＋答案之外"),
    "reacted": ("02b-reason-reacted", "02B 这句话说中了我"),
    "posting-empty": ("03a-posting-empty", "03A 写下答案之外"),
    "posting-ready": ("03b-posting-ready", "03B 可以飘进去了"),
    "posting-success": ("04-posting-success", "04 这句话飘出去了"),
    "sample-insufficient": ("05a-sample-insufficient", "05A 样本不足"),
    "reason-insufficient": ("05b-reason-insufficient", "05B 理由不足"),
    "load-failed": ("05c-load-failed", "05C 加载失败"),
}


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_page(page_id: str, destination: Path) -> None:
    source = (ROOT / "index.html").as_uri()
    url = f"{source}?{urlencode({'page': page_id})}"
    script = """
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: process.argv[1] });
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 3,
    isMobile: true,
    hasTouch: true,
    locale: 'zh-CN'
  });
  const page = await context.newPage();
  await page.goto(process.argv[2], { waitUntil: 'load' });
  await page.waitForTimeout(450);
  await page.screenshot({ path: process.argv[3] });
  await browser.close();
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
"""
    environment = os.environ.copy()
    environment["NODE_PATH"] = str(NODE_MODULES)
    command = [
        str(NODE),
        "-e",
        script,
        str(CHROME),
        url,
        str(destination),
    ]
    subprocess.run(command, check=True, env=environment, stdout=subprocess.DEVNULL)


def build_overview() -> None:
    page_width, page_height = VIEWPORT[0] * SCALE, VIEWPORT[1] * SCALE
    gap = 54
    label_height = 92
    columns = 3
    rows = (len(PAGES) + columns - 1) // columns
    canvas = Image.new(
        "RGB",
        (columns * page_width + (columns + 1) * gap, rows * (page_height + label_height) + (rows + 1) * gap),
        "#05080e",
    )
    draw = ImageDraw.Draw(canvas)
    title_font = font(38)
    for index, (_, (filename, label)) in enumerate(PAGES.items()):
        row, column = divmod(index, columns)
        x = gap + column * (page_width + gap)
        y = gap + row * (page_height + label_height + gap)
        draw.text((x, y), label, fill="#f4f7fa", font=title_font)
        preview = Image.open(OUTPUT / f"{filename}.png").convert("RGB")
        canvas.paste(preview, (x, y + label_height))
    canvas.save(ROOT / "flow-overview.png", quality=94)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for stale in OUTPUT.glob("*.png"):
        stale.unlink()
    for page_id, (filename, _) in PAGES.items():
        render_page(page_id, OUTPUT / f"{filename}.png")
    build_overview()
    print(f"已生成 {len(PAGES)} 张高保真手机预览和流程总览：{ROOT}")


if __name__ == "__main__":
    main()
