#!/usr/bin/env python3
"""Create a contact sheet for visual review of generated carousel slides."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


CAROUSEL_DIR_RE = re.compile(r"^Carousel\s+(\d+)$", re.IGNORECASE)
BG = (12, 16, 28)
PANEL = (24, 31, 48)
WHITE = (245, 248, 255)
MUTED = (160, 168, 184)
CYAN = (0, 224, 235)
RED = (255, 88, 118)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(name, size)


def load_expected(parsed_json: Path | None) -> list[dict[str, Any]]:
    if parsed_json is None:
        return []
    data = json.loads(parsed_json.read_text(encoding="utf-8"))
    return data.get("carousels", [])


def discover_carousels(output_root: Path) -> list[dict[str, Any]]:
    carousels: list[dict[str, Any]] = []
    for child in sorted(output_root.iterdir()):
        if not child.is_dir():
            continue
        match = CAROUSEL_DIR_RE.match(child.name)
        if not match:
            continue
        slide_files = sorted((child / "slides").glob("slide-*.png"))
        carousels.append(
            {
                "number": int(match.group(1)),
                "title": "",
                "slides": [{"number": index + 1} for index, _ in enumerate(slide_files)],
            }
        )
    return carousels


def load_slide(path: Path, thumb_size: int) -> Image.Image:
    if not path.exists():
        missing = Image.new("RGB", (thumb_size, thumb_size), (55, 20, 34))
        draw = ImageDraw.Draw(missing)
        draw.rectangle((0, 0, thumb_size - 1, thumb_size - 1), outline=RED, width=4)
        draw.text((18, thumb_size // 2 - 12), "MISSING", font=font(20, True), fill=WHITE)
        return missing
    image = Image.open(path).convert("RGB")
    image.thumbnail((thumb_size, thumb_size), Image.LANCZOS)
    tile = Image.new("RGB", (thumb_size, thumb_size), (5, 8, 16))
    x = (thumb_size - image.width) // 2
    y = (thumb_size - image.height) // 2
    tile.paste(image, (x, y))
    return tile


def reference_row(reference_dir: Path | None, thumb_size: int) -> tuple[str, list[Image.Image]] | None:
    if reference_dir is None:
        return None
    files = sorted(reference_dir.glob("slide-*.png"))
    if not files:
        return None
    return "Reference - Carousel 1", [load_slide(path, thumb_size) for path in files]


def carousel_row(
    output_root: Path,
    carousel: dict[str, Any],
    thumb_size: int,
) -> tuple[str, list[Image.Image]]:
    number = carousel["number"]
    title = carousel.get("title") or f"Carousel {number}"
    label = f"Carousel {number} - {title}"
    tiles = []
    for slide in carousel.get("slides", []):
        slide_path = output_root / f"Carousel {number}" / "slides" / f"slide-{slide['number']:02d}.png"
        tiles.append(load_slide(slide_path, thumb_size))
    return label, tiles


def draw_row(
    sheet: Image.Image,
    y: int,
    label: str,
    tiles: list[Image.Image],
    thumb_size: int,
    gap: int,
    margin: int,
    label_height: int,
) -> None:
    draw = ImageDraw.Draw(sheet)
    draw.rounded_rectangle(
        (margin - 14, y - 8, sheet.width - margin + 14, y + label_height + thumb_size + 18),
        radius=14,
        fill=PANEL,
    )
    draw.text((margin, y), label, font=font(26, True), fill=WHITE)
    x = margin
    tile_y = y + label_height
    for index, tile in enumerate(tiles, start=1):
        sheet.paste(tile, (x, tile_y))
        draw.rectangle((x, tile_y, x + thumb_size - 1, tile_y + thumb_size - 1), outline=(55, 68, 92), width=1)
        draw.text((x + 8, tile_y + 8), f"{index:02d}", font=font(18, True), fill=CYAN)
        x += thumb_size + gap


def create_sheet(
    output_root: Path,
    parsed_json: Path | None,
    reference_dir: Path | None,
    output_path: Path,
    thumb_size: int,
) -> dict[str, Any]:
    carousels = load_expected(parsed_json) or discover_carousels(output_root)
    rows: list[tuple[str, list[Image.Image]]] = []
    ref = reference_row(reference_dir, thumb_size)
    if ref:
        rows.append(ref)
    rows.extend(carousel_row(output_root, carousel, thumb_size) for carousel in carousels)

    if not rows:
        raise SystemExit(f"No slides found under {output_root}")

    max_tiles = max(len(tiles) for _, tiles in rows)
    margin = 36
    gap = 14
    label_height = 44
    row_height = label_height + thumb_size + 38
    width = margin * 2 + max_tiles * thumb_size + max(0, max_tiles - 1) * gap
    height = margin * 2 + 64 + len(rows) * row_height

    sheet = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(sheet)
    draw.text((margin, 24), "AIA Visual Review Sheet", font=font(34, True), fill=WHITE)
    draw.text(
        (margin, 66),
        f"Root: {output_root}",
        font=font(18, False),
        fill=MUTED,
    )

    y = margin + 70
    for label, tiles in rows:
        draw_row(sheet, y, label, tiles, thumb_size, gap, margin, label_height)
        y += row_height

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, "PNG")
    return {
        "output": str(output_path),
        "rows": len(rows),
        "carousels": len(carousels),
        "thumb_size": thumb_size,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a PNG contact sheet for carousel visual QA.")
    parser.add_argument("output_root", type=Path, help="Folder containing Carousel N folders")
    parser.add_argument("--parsed-json", type=Path, help="parsed-slides.json generated by parse_slides.py")
    parser.add_argument("--reference-dir", type=Path, help="Folder containing reference slide-*.png files")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("visual-review-contact-sheet.png"),
        help="Output contact sheet PNG",
    )
    parser.add_argument("--thumb-size", type=int, default=180, help="Thumbnail size in pixels")
    args = parser.parse_args()

    report = create_sheet(
        output_root=args.output_root,
        parsed_json=args.parsed_json,
        reference_dir=args.reference_dir,
        output_path=args.output,
        thumb_size=args.thumb_size,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
