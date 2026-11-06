# skincare-routine

自分用のスキンケアルーティン。`routine.yaml` を書き換えて push すると、GitHub Actions がページ・画像・PDF を作り直して GitHub Pages に出す。

| 出力 | 中身 | URL |
|---|---|---|
| ダッシュボード | 横置きの1枚。今日の曜日の「今夜」を大きく出す。壁のモニタ用(暗い配色・2〜3m 先から読める字) | https://shuheilocale.github.io/skincare-routine/ |
| 1枚絵 | ダッシュボードを画像と PDF にしたもの(毎朝 4:30 に作り直すので、その日の曜日で出る) | [dashboard.png](https://shuheilocale.github.io/skincare-routine/dashboard.png) / [dashboard.pdf](https://shuheilocale.github.io/skincare-routine/dashboard.pdf) |
| 手引き | 全部入りの A4。頓服ケア・在庫・リセット手順など | [guide.html](https://shuheilocale.github.io/skincare-routine/guide.html) / [guide.pdf](https://shuheilocale.github.io/skincare-routine/guide.pdf) |
| データ | 同じ中身の JSON(ラズパイの壁の画面から読む用) | [routine.json](https://shuheilocale.github.io/skincare-routine/routine.json) |

## 書き換え方

正本は `routine.yaml` だけ。書き方は先頭のコメントを参照。

- 曜日ごとの夜は `week`、夜の中身は `nights`
- 手順に `from: 2026-11-14` を付けると、その日までは「11/14から」の印が付いて薄く出る
- 新しく足すものは `plan` に書く。始めてから1週間たつと、ダッシュボードからは消える(手引きには残る)

## 手元で作る

```sh
uv run build.py                                          # dist/ に HTML と JSON
RENDER_CHANNEL=chrome uv run --group render render.py    # 画像と PDF(Mac の Chrome を使う)
open dist/index.html
open "dist/index.html?date=2026-11-07"                   # 日付を差し替えて確かめる
```

`render.py` は、16:10 と 16:9 のいくつかの画面サイズ・全曜日で、ダッシュボードの枠から文字がはみ出していないかも確かめる。はみ出していると失敗し、Actions も赤くなる。

## ラズパイで出す

ダッシュボードは外部のフォント・スクリプトを読まない1枚の HTML。

- そのまま出すなら、Chromium のキオスクモードで上の URL を開く。ページは6時間ごとに自分で読み直す。日本語フォント(`fonts-noto-cjk`)が要る
- 家の壁の画面(home-network の wall)のページの1つとして組み込むなら、`routine.json` をサーバー側で取ってきて描く

## 置かないもの

公開リポジトリなので、顔や肌の写真・購入履歴・名前などの個人を特定できるものは置かない(`.gitignore` で画像と `private/` は除外してある)。

## archive/

`routine.yaml` を作る前の版(2026-08 に作った PDF)。いまの中身ではないので見るだけ。
