"""dist/ のページから画像と PDF を作る(build.py のあとに動かす)。

    uv run --group render render.py
    # Mac で、入っている Google Chrome を使うとき(ブラウザを落とさずに済む)
    RENDER_CHANNEL=chrome uv run --group render render.py

出力:
    dist/dashboard.png  ダッシュボードの1枚絵(2560x1600。作った日の曜日で出る)
    dist/dashboard.pdf  同じものを PDF 1ページで
    dist/guide.pdf      手引き(A4)

あわせて、どの曜日でもダッシュボードの枠から文字がはみ出していないかを確かめ、
はみ出していたら失敗にする。
"""

from __future__ import annotations

import datetime as dt
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

DIST = Path(__file__).parent / "dist"
SIZES = [(2560, 1600), (1920, 1080), (1280, 800)]  # 16:10 と 16:9 の壁の画面

OVERFLOW_JS = """
() => [...document.querySelectorAll('.panel')]
  .filter(el => el.offsetParent !== null && el.scrollHeight > el.clientHeight + 1)
  .map(el => (el.querySelector('h2, .name')?.textContent || el.className).trim())
"""


def check_overflow(browser) -> list[str]:
    problems = []
    monday = dt.date(2026, 11, 16)  # GGエッセンスが始まったあとの週で確かめる
    for w, h in SIZES:
        page = browser.new_page(viewport={"width": w, "height": h})
        for i in range(7):
            day = (monday + dt.timedelta(days=i)).isoformat()
            page.goto(f"{(DIST / 'index.html').as_uri()}?date={day}")
            for name in page.evaluate(OVERFLOW_JS):
                problems.append(f"{w}x{h} {day}: 「{name}」がはみ出している")
        # ページ全体の高さも画面に収まっているか
        if page.evaluate("document.documentElement.scrollHeight") > h + 1:
            problems.append(f"{w}x{h}: ページが画面の高さを超えている")
        page.close()
    return problems


def main() -> int:
    channel = os.environ.get("RENDER_CHANNEL") or None
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=channel)
        ctx = dict(timezone_id="Asia/Tokyo", locale="ja-JP")

        problems = check_overflow(browser)

        page = browser.new_page(viewport={"width": 2560, "height": 1600}, **ctx)
        page.goto((DIST / "index.html").as_uri())
        page.screenshot(path=DIST / "dashboard.png")
        page.close()

        page = browser.new_page(viewport={"width": 1600, "height": 1000}, **ctx)
        page.goto((DIST / "index.html").as_uri())
        page.emulate_media(media="screen")
        page.pdf(path=DIST / "dashboard.pdf", width="1600px", height="1000px", print_background=True)
        page.close()

        page = browser.new_page(**ctx)
        page.goto((DIST / "guide.html").as_uri())
        page.pdf(path=DIST / "guide.pdf", format="A4", print_background=True, prefer_css_page_size=True)
        page.close()
        browser.close()

    print("rendered: dashboard.png, dashboard.pdf, guide.pdf")
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
