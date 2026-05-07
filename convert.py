OUTPUT_FORMAT = "select"  # "png", "webp", or "select"

import io
import sys
from pathlib import Path

from PIL import Image

BASE_DIR = Path(__file__).resolve().parent
OUT_BASE = BASE_DIR / ".OutPut"
SIZE = 100

RASTER_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
SVG_EXT = ".svg"

try:
    import cairosvg
    _HAS_CAIROSVG = True
except ImportError:
    _HAS_CAIROSVG = False


def select_from_list(prompt: str, options: list) -> str:
    print(prompt, flush=True)
    for i, opt in enumerate(options, 1):
        print(f"  {i}: {opt}", flush=True)
    while True:
        try:
            raw = input("> ").strip()
        except EOFError:
            print("\n[ERROR] 対話的ターミナルが必要です。PowerShell/コマンドプロンプトから直接実行してください。", flush=True)
            sys.exit(1)
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print(f"  1〜{len(options)} を入力してください", flush=True)


def fit_and_center(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    img.thumbnail((SIZE, SIZE), Image.LANCZOS)
    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    x = (SIZE - img.width) // 2
    y = (SIZE - img.height) // 2
    canvas.paste(img, (x, y), img)
    return canvas


def process_raster(src: Path) -> Image.Image:
    with Image.open(src) as img:
        if hasattr(img, "n_frames") and img.n_frames > 1:
            img.seek(0)
        return fit_and_center(img.copy())


def process_svg(src: Path) -> Image.Image:
    png_bytes = cairosvg.svg2png(url=str(src))
    with Image.open(io.BytesIO(png_bytes)) as img:
        return fit_and_center(img.copy())


def save_image(img: Image.Image, stem: str, fmt: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{stem}.{fmt}"
    if fmt == "webp":
        img.save(out_path, "WEBP", lossless=True)
    else:
        img.save(out_path, "PNG")
    return out_path


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    dirs = sorted(d for d in BASE_DIR.iterdir() if d.is_dir() and not d.name.startswith("."))
    if not dirs:
        print("変換対象のディレクトリが見つかりません")
        return
    chosen_name = select_from_list("変換元ディレクトリを選択:", [d.name for d in dirs])
    src_dir = BASE_DIR / chosen_name
    out_dir = OUT_BASE / chosen_name

    fmt = OUTPUT_FORMAT
    if fmt == "select":
        fmt = select_from_list("出力フォーマットを選択:", ["png", "webp"])

    converted, skipped, errors = 0, 0, []
    for src in sorted(src_dir.iterdir()):
        ext = src.suffix.lower()
        try:
            if ext in RASTER_EXTS:
                result = process_raster(src)
            elif ext == SVG_EXT:
                if not _HAS_CAIROSVG:
                    print(f"  SKIP  {src.name}  (cairosvg not installed)")
                    skipped += 1
                    continue
                result = process_svg(src)
            else:
                skipped += 1
                continue

            out = save_image(result, src.stem, fmt, out_dir)
            print(f"  OK    {src.name} → {out.name}")
            converted += 1
        except Exception as exc:
            print(f"  ERROR {src.name}: {exc}", file=sys.stderr)
            errors.append(src.name)

    print(f"\n{converted} converted, {skipped} skipped, {len(errors)} errors")
    if errors:
        print("Failed:", ", ".join(errors))


if __name__ == "__main__":
    main()
