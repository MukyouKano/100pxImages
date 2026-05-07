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

GREEN = "\033[92m"
RED   = "\033[91m"
RESET = "\033[0m"

try:
    import cairosvg
    _HAS_CAIROSVG = True
except ImportError:
    _HAS_CAIROSVG = False


def select_from_list(prompt: str, options: list) -> str:
    import msvcrt
    idx = 0
    n = len(options)

    print(prompt, flush=True)
    for i, opt in enumerate(options):
        print(("  > " if i == idx else "    ") + opt, flush=True)

    while True:
        key = msvcrt.getwch()
        if key in ("\x00", "\xe0"):
            key2 = msvcrt.getwch()
            if key2 == "H":
                idx = (idx - 1) % n
            elif key2 == "P":
                idx = (idx + 1) % n
        elif key == "\r":
            print(flush=True)
            return options[idx]
        else:
            continue

        print(f"\033[{n}A", end="", flush=True)
        for i, opt in enumerate(options):
            print("\r\033[2K" + ("  > " if i == idx else "    ") + opt, flush=True)


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
        img.save(out_path, "PNG", optimize=True)
    return out_path


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    if sys.platform == "win32":
        import ctypes
        ctypes.windll.kernel32.SetConsoleMode(
            ctypes.windll.kernel32.GetStdHandle(-11), 7
        )

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
                src_size = src.stat().st_size
                result = process_raster(src)
            elif ext == SVG_EXT:
                if not _HAS_CAIROSVG:
                    print(f"  SKIP  {src.name}  (cairosvg not installed)")
                    skipped += 1
                    continue
                src_size = src.stat().st_size
                result = process_svg(src)
            else:
                skipped += 1
                continue

            out = save_image(result, src.stem, fmt, out_dir)
            out_size = out.stat().st_size

            src_kb = src_size / 1024
            out_kb = out_size / 1024
            color = GREEN if out_size <= src_size else RED
            size_str = f"{src_kb:.2f}KB → {color}{out_kb:.2f}KB{RESET}"
            print(f"  OK    {src.name} → {out.name}  ({size_str})")
            converted += 1
        except Exception as exc:
            print(f"  ERROR {src.name}: {exc}", file=sys.stderr)
            errors.append(src.name)

    print(f"\n{converted} converted, {skipped} skipped, {len(errors)} errors")
    if errors:
        print("Failed:", ", ".join(errors))


if __name__ == "__main__":
    main()
