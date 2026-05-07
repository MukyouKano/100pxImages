# 100pxImages

画像を 100×100px にリサイズ・センタリングして PNG または WebP 形式で出力するツールです。

## 機能

- ラスタ画像 (PNG / JPG / JPEG / WebP / GIF / BMP) を 100×100px に変換
- SVG 画像を PNG/WebP にラスタライズして変換 (cairosvg が必要)
- アスペクト比を維持したまま透明パディングでセンタリング
- 出力フォーマットを実行時に選択可能 (PNG / WebP)

## 必要な環境

- Python 3.8 以上
- [Pillow](https://pillow.readthedocs.io/)

```
pip install pillow
```

SVG を変換する場合は追加で cairosvg が必要です。

```
pip install cairosvg
```

## ディレクトリ構成

```
100pxImages/
├── convert.py        # メインスクリプト
├── <入力フォルダ>/   # 変換したい画像を入れたフォルダ（複数可）
└── .OutPut/
    └── <入力フォルダ名>/  # 変換後の画像が出力される
```

## 使い方

1. プロジェクトルートに変換対象の画像をフォルダにまとめて配置する
2. スクリプトを実行する

```
python convert.py
```

3. 対話形式で変換元フォルダと出力フォーマット (PNG / WebP) を選択する
4. `.OutPut/<フォルダ名>/` に変換済み画像が生成される

## 設定

`convert.py` 冒頭の `OUTPUT_FORMAT` を変更することで出力形式を固定できます。

| 値 | 動作 |
|----|------|
| `"select"` | 実行ごとにフォーマットを対話選択（デフォルト）|
| `"png"` | 常に PNG で出力 |
| `"webp"` | 常に WebP (ロスレス) で出力 |

---

> **このREADMEはAIによって生成されました。**
> - モデル: Claude Sonnet 4.6 (`claude-sonnet-4-6`)
> - 生成日: 2026-05-07
> - ツール: [Claude Code](https://claude.ai/claude-code) (Anthropic)
