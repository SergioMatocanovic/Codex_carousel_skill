#!/usr/bin/env python3
"""Compose theme-led carousel PNGs from content, a visual plan, and optional images."""

from __future__ import annotations

import argparse
import json
import textwrap
from datetime import date
from pathlib import Path
from shutil import copy2
from typing import Any

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

from description_generator import description_markdown
from formats import CanvasFormat, format_choices, get_format


DEFAULT_PALETTE = ["#101828", "#344054", "#F9FAFB", "#F97316"]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = ("DejaVuSans-Bold.ttf", "arialbd.ttf") if bold else ("DejaVuSans.ttf", "arial.ttf")
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def color(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Expected a six-digit hex color, received {value!r}")
    return tuple(int(value[index : index + 2], 16) for index in range(0, 6, 2)) + (alpha,)


def draw_text_block(draw: ImageDraw.ImageDraw, text: str, box: tuple[int, int, int, int], size: int, fill: tuple[int, int, int, int]) -> None:
    current_size = size
    while current_size >= 34:
        active_font = font(current_size, True)
        average_character = max(1, int(draw.textlength("ABCDEFGHIJKLMNOPQRSTUVWXYZ", font=active_font) / 26))
        columns = max(12, (box[2] - box[0]) // average_character)
        lines = textwrap.wrap(text, width=columns) or [text]
        line_height = int(current_size * 1.16)
        if len(lines) * line_height <= box[3] - box[1]:
            y = box[1]
            for line in lines:
                draw.text((box[0], y), line, font=active_font, fill=fill)
                y += line_height
            return
        current_size -= 4
    draw.multiline_text((box[0], box[1]), text, font=font(34, True), fill=fill, spacing=8)


def crop_to_canvas(source: Image.Image, canvas: CanvasFormat) -> Image.Image:
    source = source.convert("RGBA")
    source_ratio = source.width / source.height
    target_ratio = canvas.width / canvas.height
    if source_ratio > target_ratio:
        width = int(source.height * target_ratio)
        left = (source.width - width) // 2
        source = source.crop((left, 0, left + width, source.height))
    else:
        height = int(source.width / target_ratio)
        top = (source.height - height) // 2
        source = source.crop((0, top, source.width, top + height))
    return source.resize((canvas.width, canvas.height), Image.Resampling.LANCZOS)


def palette(plan: dict[str, Any]) -> list[str]:
    selected = plan.get("direction", {}).get("palette", [])
    return selected[:4] if isinstance(selected, list) and len(selected) >= 4 else DEFAULT_PALETTE


def slide_plan(plan: dict[str, Any], carousel: int, slide: int) -> dict[str, Any]:
    return next((item for item in plan.get("slides", []) if item.get("carousel") == carousel and item.get("slide") == slide), {})


def image_for_slide(image_dir: Path | None, item: dict[str, Any], carousel: int, slide: int) -> Path | None:
    if image_dir is None:
        return None
    candidates = [item.get("image"), f"carousel-{carousel:02d}-slide-{slide:02d}.png"]
    return next((image_dir / candidate for candidate in candidates if candidate and (image_dir / candidate).is_file()), None)


def background(canvas: CanvasFormat, colors: list[str], source: Path | None) -> Image.Image:
    if source is not None:
        image = ImageEnhance.Color(crop_to_canvas(Image.open(source), canvas)).enhance(0.9)
    else:
        image = Image.new("RGBA", (canvas.width, canvas.height), color(colors[0]))
        pixels = image.load()
        primary, secondary = color(colors[0]), color(colors[1])
        for y in range(canvas.height):
            for x in range(canvas.width):
                blend = (x / max(1, canvas.width - 1) + y / max(1, canvas.height - 1)) / 2
                pixels[x, y] = tuple(int(primary[index] * (1 - blend) + secondary[index] * blend) for index in range(4))
    return Image.alpha_composite(image, Image.new("RGBA", image.size, color(colors[0], 172)))


def compose_slide(carousel: dict[str, Any], slide: dict[str, Any], plan: dict[str, Any], image_dir: Path | None, canvas: CanvasFormat, output: Path) -> str | None:
    colors = palette(plan)
    item = slide_plan(plan, carousel["number"], slide["number"])
    source = image_for_slide(image_dir, item, carousel["number"], slide["number"])
    image = background(canvas, colors, source)
    draw = ImageDraw.Draw(image)
    light, accent = color(colors[2]), color(colors[3])
    margin = max(54, canvas.width // 18)
    brand = plan.get("brand", {})
    name, handle = str(brand.get("name") or ""), str(brand.get("handle") or "")
    total = len(carousel.get("slides", []))
    if name:
        draw.text((margin, margin), name.upper(), font=font(26, True), fill=light)
    counter = f"{slide['number']:02d}/{total:02d}"
    draw.text((canvas.width - margin - draw.textlength(counter, font=font(26, True)), margin), counter, font=font(26, True), fill=light)
    draw.line((margin, margin + 48, canvas.width - margin, margin + 48), fill=accent, width=3)
    lines = [str(line).strip() for line in slide.get("content_lines", []) if str(line).strip()]
    copy = "\n".join(lines) or carousel.get("title") or "Carousel"
    draw_text_block(draw, copy, (margin, canvas.height // 4, canvas.width - margin, canvas.height - 240), 92 if slide["number"] == 1 else 68, light)
    if handle:
        draw.text((margin, canvas.height - margin - 32), handle, font=font(24), fill=light)
    draw.rectangle((margin, canvas.height - margin - 5, margin + 160, canvas.height - margin), fill=accent)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output, "PNG")
    return str(source) if source else None


def archive_source_image(source: str | None, carousel_dir: Path) -> str | None:
    if not source:
        return None
    original = Path(source)
    archive = carousel_dir / "generated-images" / original.name
    archive.parent.mkdir(parents=True, exist_ok=True)
    copy2(original, archive)
    return str(archive)


def table_cell(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ").strip()


def update_history(root: Path, carousel: dict[str, Any], mode: str) -> None:
    history = root / "historico.md"
    today = date.today().isoformat()
    key = f"Carousel {carousel['number']}"
    title = table_cell(str(carousel.get("title") or "Sem tema"))
    slides = str(len(carousel.get("slides", [])))
    header = [
        "# Histórico de carrosséis",
        "",
        "| Carrossel | Criado em | Atualizado em | Tema | Slides | Status |",
        "| --- | --- | --- | --- | ---: | --- |",
    ]
    lines = history.read_text(encoding="utf-8").splitlines() if history.exists() else header
    entry_prefix = f"| {key} |"
    replacement = f"| {key} | {today} | {today} | {title} | {slides} | {'Criado' if mode == 'create' else 'Revisado'} |"
    replaced = False
    for index, line in enumerate(lines):
        if line.startswith(entry_prefix):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            created = cells[1] if len(cells) > 1 else today
            replacement = f"| {key} | {created} | {today} | {title} | {slides} | Revisado |"
            lines[index] = replacement
            replaced = True
            break
    if not replaced:
        lines.append(replacement)
    history.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compose theme-led carousel PNG assets.")
    parser.add_argument("--parsed-json", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--visual-plan", type=Path, required=True)
    parser.add_argument("--image-dir", type=Path)
    parser.add_argument("--carousel", type=int)
    parser.add_argument("--mode", choices=("create", "revise"), default="create")
    parser.add_argument("--format", required=True, choices=format_choices())
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    parsed = json.loads(args.parsed_json.read_text(encoding="utf-8"))
    plan = json.loads(args.visual_plan.read_text(encoding="utf-8"))
    canvas = get_format(args.format)
    if args.mode == "revise" and args.carousel is None:
        parser.error("--mode revise requires --carousel so an existing carousel is updated in place")
    report: dict[str, Any] = {"output_root": str(args.output_root), "format": canvas.key, "dimensions": [canvas.width, canvas.height], "generated": []}
    for carousel in parsed.get("carousels", []):
        if args.carousel is not None and carousel["number"] != args.carousel:
            continue
        carousel_dir = args.output_root / f"Carousel {carousel['number']}"
        if args.mode == "create" and carousel_dir.exists():
            raise FileExistsError(f"{carousel_dir} already exists. Use --mode revise --carousel {carousel['number']} to update it in place.")
        if args.mode == "revise" and not carousel_dir.exists():
            raise FileNotFoundError(f"{carousel_dir} does not exist, so it cannot be revised.")
        description = carousel_dir / "Description.md"
        carousel_dir.mkdir(parents=True, exist_ok=True)
        description.write_text(description_markdown(carousel), encoding="utf-8")
        slides_dir = carousel_dir / "slides"
        expected = {f"slide-{slide['number']:02d}.png" for slide in carousel.get("slides", [])}
        if args.mode == "revise" and slides_dir.exists():
            for stale in slides_dir.glob("slide-*.png"):
                if stale.name not in expected:
                    stale.unlink()
        for slide in carousel.get("slides", []):
            output = slides_dir / f"slide-{slide['number']:02d}.png"
            source = compose_slide(carousel, slide, plan, args.image_dir, canvas, output)
            report["generated"].append({"carousel": carousel["number"], "slide": slide["number"], "png": str(output), "source_image": archive_source_image(source, carousel_dir)})
        update_history(args.output_root, carousel, args.mode)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
