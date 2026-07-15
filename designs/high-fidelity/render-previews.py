from pathlib import Path
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "previews"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PAGES = {
    "question": "01-today-question",
    "result": "02-result-and-reason",
    "reacted": "02b-reason-reacted",
    "posting-empty": "03a-posting-empty",
    "posting-ready": "03b-posting-ready",
    "posting-success": "04-posting-success",
}


def main() -> None:
    for stale in OUTPUT.glob("*.png"):
        stale.unlink()
    source = (ROOT / "index.html").as_uri()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=CHROME)
        context = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3, locale="zh-CN")
        page = context.new_page()
        for page_id, filename in PAGES.items():
            page.goto(f"{source}?{urlencode({'page': page_id})}", wait_until="load")
            page.wait_for_timeout(120)
            page.screenshot(path=OUTPUT / f"{filename}.png")
        browser.close()
    print(f"已生成 {len(PAGES)} 张高保真手机预览：{OUTPUT}")


if __name__ == "__main__":
    main()
