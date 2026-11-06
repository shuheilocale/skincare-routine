"""routine.yaml から dist/ にページを作る。

    uv run build.py

出力:
    dist/index.html   ダッシュボード(横置きの1枚。今日の曜日の夜を大きく出す)
    dist/guide.html   全部入りの手引き(A4 で印刷・PDF 化する用)
    dist/routine.json 同じ中身のデータ(ラズパイの壁の画面などから読む用)
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
WEEKDAY_JA = {"mon": "月", "tue": "火", "wed": "水", "thu": "木", "fri": "金", "sat": "土", "sun": "日"}
COLORS = {"rs", "acid", "retinol", "rest"}


def norm_step(step) -> dict:
    """手順を {text, note, from, from_label} にそろえる。"""
    if isinstance(step, str):
        step = {"text": step}
    out = {"text": str(step["text"]), "note": step.get("note"), "from": None, "from_label": None}
    start = step.get("from")
    if start is not None:
        if not isinstance(start, dt.date):
            raise ValueError(f"from は YYYY-MM-DD で書く: {step}")
        out["from"] = start.isoformat()
        out["from_label"] = f"{start.month}/{start.day}から"
    return out


def plan_label(value) -> str:
    if isinstance(value, dt.date):
        return f"{value.month}/{value.day}〜"
    text = str(value)
    if len(text) == 7 and text[4] == "-":  # 2026-12
        return f"{int(text[5:])}月〜"
    return text


def load() -> dict:
    data = yaml.safe_load((ROOT / "routine.yaml").read_text(encoding="utf-8"))

    for key, night in data["nights"].items():
        if night["color"] not in COLORS:
            raise ValueError(f"nights.{key}.color は {sorted(COLORS)} のどれか")
        night["key"] = key
        night["steps"] = [norm_step(s) for s in night["steps"]]

    week = data["week"]
    missing = [d for d in WEEKDAYS if d not in week]
    unknown = [d for d, n in week.items() if n not in data["nights"]]
    if missing or unknown:
        raise ValueError(f"week の曜日が足りない: {missing} / 知らない夜の種類: {unknown}")
    data["week_list"] = [
        {"day": d, "ja": WEEKDAY_JA[d], "night": data["nights"][week[d]]} for d in WEEKDAYS
    ]

    data["morning"]["steps"] = [norm_step(s) for s in data["morning"]["steps"]]
    for part in ("daily", "mist"):
        data["body"][part]["steps"] = [norm_step(s) for s in data["body"][part]["steps"]]
    for item in data["plan"]:
        item["label"] = plan_label(item["from"])
        item["from"] = item["from"].isoformat() if isinstance(item["from"], dt.date) else str(item["from"])

    for key in ("since", "updated"):
        data[key] = str(data[key])
    return data


def main() -> int:
    data = load()
    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    DIST.mkdir(exist_ok=True)

    # ページの JS が使う最小限のデータ(曜日→夜の種類)
    page_data = {"week": data["week"], "nights": {k: v["name"] for k, v in data["nights"].items()}}
    page_json = json.dumps(page_data, ensure_ascii=False).replace("</", "<\\/")

    for name in ("index.html", "guide.html"):
        html = env.get_template(f"{name}.j2").render(d=data, page_json=page_json)
        (DIST / name).write_text(html, encoding="utf-8")

    public = {k: v for k, v in data.items() if k != "week_list"}
    (DIST / "routine.json").write_text(
        json.dumps(public, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"built: {', '.join(sorted(p.name for p in DIST.iterdir()))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
