from pathlib import Path
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright


SOURCE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SOURCE_DIR.parent / "previews"
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

STYLES = {
    "warm": "warm-handwritten",
    "editorial": "quiet-editorial",
    "lab": "light-lab",
    "soft": "soft-digital",
    "neon": "neon-night",
    "neon-v2": "neon-night-v2",
}

PAGES = {
    "question": "01-question",
    "result": "02-result",
    "reason": "03-reason",
    "echo-empty": "04-echo-empty",
    "echo-ready": "05-echo-ready",
    "echo-success": "06-echo-success",
    "share": "07-share-card",
}


def main() -> None:
    source_url = (SOURCE_DIR / "index.html").as_uri()

    for stale_preview in OUTPUT_DIR.glob("*/*.png"):
        stale_preview.unlink()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH,
        )
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=3,
            locale="zh-CN",
            color_scheme="light",
        )
        page = context.new_page()

        for style, style_dir in STYLES.items():
            output_dir = OUTPUT_DIR / style_dir
            output_dir.mkdir(parents=True, exist_ok=True)

            for page_key, filename in PAGES.items():
                query = urlencode({"style": style, "page": page_key})
                page.goto(f"{source_url}?{query}", wait_until="load")
                page.wait_for_timeout(200)
                page.screenshot(path=output_dir / f"{filename}.png")

        browser.close()

    print(f"已生成 {len(STYLES) * len(PAGES)} 张手机预览图：{OUTPUT_DIR}")


if __name__ == "__main__":
    main()
