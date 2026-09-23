#!/usr/bin/env python3
"""Generate first-pass Instagram carousel PNGs from parsed-slides.json."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from description_generator import description_markdown


SIZE = 1254
WHITE = (248, 250, 255, 255)
MUTED = (165, 170, 185, 255)
CYAN = (0, 239, 245, 255)
DARK = (2, 7, 18, 255)
PINK = (255, 78, 132, 255)
PURPLE = (221, 82, 255, 255)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(name, size)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=fnt)
    return right - left, bottom - top


def clean_line(line: str) -> str:
    return (
        line.replace("✅", "")
        .replace("✔", "")
        .replace("❤️", "")
        .replace("📤", "")
        .replace("📌", "")
        .replace("📄", "")
        .replace("💻", "")
        .replace("📊", "")
        .replace("✍️", "")
        .replace("❌", "")
        .replace("👉", "")
        .replace("👇", "")
        .replace("—", " ")
        .strip()
    )


def leading_marker(line: str) -> str:
    stripped = line.strip()
    return stripped[:2] if stripped.startswith("✍️") else stripped[:1]


def is_accent_line(line: str) -> bool:
    return bool(
        re.search(
            r"ChatGPT|Claude|AIA|delegar|trabalho|funcion[aá]rio|mudou|chatbot|Google|Docker|VS|5 tipos|Agora|Parte",
            line,
            re.IGNORECASE,
        )
    )


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    fnt: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        width, _ = text_size(draw, candidate, fnt)
        if width <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_glow_line(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    glow: bool = False,
) -> None:
    x, y = xy
    if glow:
        for offset in (4, 2):
            draw.text((x - offset, y), text, font=fnt, fill=(0, 220, 230, 36))
            draw.text((x + offset, y), text, font=fnt, fill=(0, 220, 230, 36))
            draw.text((x, y - offset), text, font=fnt, fill=(0, 220, 230, 36))
            draw.text((x, y + offset), text, font=fnt, fill=(0, 220, 230, 36))
    draw.text((x, y), text, font=fnt, fill=fill)


def draw_icon(draw: ImageDraw.ImageDraw, center: tuple[int, int], marker: str, color: tuple[int, int, int, int]) -> None:
    x, y = center
    draw.ellipse((x - 67, y - 67, x + 67, y + 67), outline=CYAN, width=3)
    if marker in {"📄", "✍️"}:
        draw.rounded_rectangle((x - 28, y - 38, x + 24, y + 36), radius=5, outline=color, width=4)
        draw.line((x - 14, y - 12, x + 12, y - 12), fill=color, width=3)
        draw.line((x - 14, y + 5, x + 13, y + 5), fill=color, width=3)
        if marker == "✍️":
            draw.line((x - 34, y + 34, x + 24, y - 24), fill=color, width=5)
    elif marker == "💻":
        draw.rounded_rectangle((x - 42, y - 28, x + 42, y + 22), radius=6, outline=color, width=4)
        draw.line((x - 18, y + 34, x + 18, y + 34), fill=color, width=4)
        draw.line((x - 8, y + 22, x - 18, y + 34), fill=color, width=4)
        draw.line((x + 8, y + 22, x + 18, y + 34), fill=color, width=4)
    elif marker == "📊":
        for offset, height in [(-28, 28), (0, 48), (28, 68)]:
            draw.rounded_rectangle((x + offset - 8, y + 34 - height, x + offset + 8, y + 34), radius=4, outline=color, width=4)
    elif marker in {"❌", "❤️"}:
        draw.text((x - 35, y - 49), "×" if marker == "❌" else "♡", font=font(86, True), fill=color)
    elif marker in {"✅", "✔"}:
        draw.ellipse((x - 39, y - 39, x + 39, y + 39), fill=CYAN)
        draw.text((x - 21, y - 33), "✓", font=font(58, True), fill=DARK)
    elif marker == "📤":
        draw.text((x - 31, y - 49), "↗", font=font(82, False), fill=color)
    elif marker == "📌":
        draw.text((x - 26, y - 45), "⌑", font=font(76, False), fill=color)
    else:
        draw.text((x - 34, y - 48), "››", font=font(70, False), fill=color)


def background() -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), DARK)
    pixels = img.load()
    for y in range(SIZE):
        for x in range(SIZE):
            nx = x / SIZE
            ny = y / SIZE
            glow = max(0, 1 - math.hypot(nx - 0.78, ny - 0.72) / 0.42)
            teal = int(44 * glow)
            blue = int(34 * (1 - ny) + 34 * glow)
            pixels[x, y] = (2, 7 + int(12 * nx), 18 + blue + teal, 255)

    overlay = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for x in range(770, 1200, 22):
        for y in range(135, 720, 22):
            alpha = int(max(0, 120 - abs(x - 1050) * 0.16 - abs(y - 310) * 0.08))
            if alpha > 10:
                od.ellipse((x, y, x + 2, y + 2), fill=(0, 239, 245, alpha))
    img.alpha_composite(overlay)

    vignette = Image.new("L", (SIZE, SIZE), 0)
    vd = ImageDraw.Draw(vignette)
    vd.ellipse((-260, -180, SIZE + 260, SIZE + 180), fill=180)
    vignette = vignette.filter(ImageFilter.GaussianBlur(120))
    dark = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 160))
    img = Image.composite(img, dark, Image.eval(vignette, lambda p: 255 - p))
    return img


def draw_header(draw: ImageDraw.ImageDraw, part: int) -> None:
    y = 42
    draw.text((43, y), "SÉRIE", font=font(30, True), fill=WHITE)
    draw.text((142, y), "CHATGPT WORK", font=font(30, True), fill=CYAN)
    x = 480
    for index in range(1, 5):
        fill = CYAN if index == part else (45, 52, 68, 255)
        draw.rounded_rectangle((x, y, x + 58, y + 30), radius=5, fill=fill)
        x += 76
    draw.text((1025, y), f"Parte {part}/4", font=font(30, False), fill=WHITE)
    draw.line((0, 106, SIZE, 106), fill=(0, 239, 245, 100), width=1)


def draw_footer(img: Image.Image, logo_path: Path, cover: bool = False) -> None:
    draw = ImageDraw.Draw(img)
    if cover:
        draw.text((64, 1180), "@sergiomatocanovic", font=font(28, False), fill=MUTED)
        return
    draw.line((15, 1108, 1238, 1108), fill=(0, 239, 245, 90), width=1)
    try:
        logo = Image.open(logo_path).convert("RGBA")
        logo.thumbnail((180, 82), Image.LANCZOS)
        img.alpha_composite(logo, (50, 1130))
    except Exception:
        draw.text((50, 1140), "AIA", font=font(60, True), fill=CYAN)
    draw.line((275, 1135, 275, 1210), fill=(0, 239, 245, 110), width=1)
    draw.text((322, 1160), "@sergiomatocanovic", font=font(29, False), fill=MUTED)
    draw.ellipse((1093, 1140, 1173, 1220), outline=CYAN, width=2)
    draw.text((1114, 1144), "→", font=font(56, False), fill=CYAN)


def draw_ai_mark_fallback(draw: ImageDraw.ImageDraw) -> None:
    # A stylized cyan geometry that keeps the right-side visual weight of the reference slides.
    box = (835, 355, 1300, 955)
    for shift, angle_color in enumerate(((0, 155, 160, 180), (0, 235, 226, 230), (0, 180, 190, 170))):
        offset = shift * 34
        draw.rounded_rectangle(
            (box[0] + offset, box[1] - offset, box[2] + offset, box[3] - offset),
            radius=155,
            outline=angle_color,
            width=40,
        )
    draw.rounded_rectangle((970, 520, 1190, 740), radius=38, outline=(0, 239, 245, 230), width=30)


def draw_ai_mark(img: Image.Image, draw: ImageDraw.ImageDraw, symbol_panel_path: Path) -> None:
    try:
        panel = Image.open(symbol_panel_path).convert("RGBA")
        alpha = panel.getchannel("A")
        mask = Image.new("L", panel.size, 255)
        mask_pixels = mask.load()
        fade_left = 150
        fade_bottom = 90
        for y in range(panel.height):
            for x in range(panel.width):
                factor = 1.0
                if x < fade_left:
                    factor *= x / fade_left
                if y > panel.height - fade_bottom:
                    factor *= max(0, (panel.height - y) / fade_bottom)
                mask_pixels[x, y] = int(255 * factor)
        alpha = Image.composite(alpha, Image.new("L", panel.size, 0), Image.eval(mask, lambda px: px))
        panel.putalpha(alpha)
        # Preserve the official crop size and position from the reference design.
        img.alpha_composite(panel, (620, 115))
    except Exception:
        draw_ai_mark_fallback(draw)


def content_without_series(slide: dict[str, Any]) -> list[str]:
    lines = slide.get("content_lines", [])
    if lines and re.match(r"S[eé]rie\s+ChatGPT Work", lines[0], re.IGNORECASE):
        return lines[1:]
    return lines


def draw_wrapped_lines(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    x: int,
    y: int,
    max_width: int,
    size: int,
    line_gap: int,
    bold: bool = True,
) -> int:
    fnt = font(size, bold)
    current_y = y
    for raw_line in lines:
        line = clean_line(raw_line)
        if not line:
            current_y += line_gap
            continue
        wrapped = wrap_text(draw, line, fnt, max_width)
        fill = CYAN if is_accent_line(line) else WHITE
        for part in wrapped:
            draw_glow_line(draw, (x, current_y), part, fnt, fill, glow=fill == CYAN)
            current_y += size + line_gap
    return current_y


def wrapped_height(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    max_width: int,
    size: int,
    line_gap: int,
) -> int:
    fnt = font(size, True)
    total = 0
    for raw_line in lines:
        line = clean_line(raw_line)
        if not line:
            total += line_gap
            continue
        total += len(wrap_text(draw, line, fnt, max_width)) * (size + line_gap)
    return total


def draw_fitted_text(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    x: int,
    y: int,
    max_width: int,
    max_height: int,
    start_size: int,
    min_size: int = 38,
) -> None:
    cleaned = [line for line in lines if clean_line(line)]
    size = start_size
    while size > min_size and wrapped_height(draw, cleaned, max_width, size, 8) > max_height:
        size -= 4
    draw_wrapped_lines(draw, cleaned, x, y, max_width, size, 8, True)


def draw_cover(draw: ImageDraw.ImageDraw, lines: list[str]) -> None:
    main = [line for line in lines if line.strip()]
    headline = main[:-1] if len(main) > 1 else main
    final = main[-1] if main else ""
    headline_chars = sum(len(line) for line in headline)
    final_chars = len(final)
    headline_size = 82 if headline_chars < 34 else 68
    final_size = 118 if final_chars < 24 else 72
    final_width = 760 if final_chars < 24 else 640
    y = draw_wrapped_lines(draw, headline, 60, 205, 650, headline_size, 8, True)
    draw.rectangle((64, y + 25, 232, y + 31), fill=CYAN)
    draw_wrapped_lines(draw, [final], 64, y + 88, final_width, final_size, 8, True)
    draw.ellipse((62, 1046, 162, 1146), outline=CYAN, width=3)
    draw.text((86, 1054), "→", font=font(68, False), fill=CYAN)
    draw.text((203, 1074), "Descubra por quê", font=font(38, True), fill=WHITE)
    draw.text((560, 1067), "→", font=font(58, False), fill=CYAN)


def draw_cta(draw: ImageDraw.ImageDraw, lines: list[str]) -> None:
    items = [line for line in lines if re.match(r"^[❤️📤📌]", line.strip())]
    y = 285
    colors = [PINK, CYAN, PURPLE]
    for index, item in enumerate(items):
        color = colors[index % len(colors)]
        draw_icon(draw, (135, y + 85), leading_marker(item), color)
        draw.line((258, y + 25, 258, y + 145), fill=CYAN, width=3)
        draw_wrapped_lines(draw, [clean_line(item)], 298, y + 32, 470, 50, 4, True)
        y += 262


def draw_topic_checklist(draw: ImageDraw.ImageDraw, lines: list[str]) -> None:
    heading_lines = [line for line in lines if line.strip() and not re.match(r"^[✅✔]", line.strip())]
    items = [clean_line(line) for line in lines if re.match(r"^[✅✔]", line.strip())]
    marker = leading_marker(heading_lines[0]) if heading_lines else ""
    heading = clean_line(heading_lines[0]) if heading_lines else ""
    draw_icon(draw, (132, 245), marker, CYAN)
    draw.line((238, 183, 238, 305), fill=CYAN, width=3)
    draw_wrapped_lines(draw, [heading], 278, 186, 420, 60, 5, True)
    draw.rectangle((278, 332, 420, 338), fill=CYAN)

    y = 395
    for item in items[:6]:
        draw.ellipse((84, y + 3, 126, y + 45), fill=CYAN)
        draw.text((95, y - 2), "✓", font=font(32, True), fill=DARK)
        draw_wrapped_lines(draw, [item], 153, y - 1, 500, 36, 3, True)
        draw.line((153, y + 65, 620, y + 65), fill=(0, 239, 245, 72), width=1)
        y += 82


def draw_standard_checklist(draw: ImageDraw.ImageDraw, lines: list[str]) -> None:
    title = [line for line in lines if line.strip() and not re.match(r"^[✅✔]", line.strip())]
    items = [clean_line(line) for line in lines if re.match(r"^[✅✔]", line.strip())]
    y = draw_wrapped_lines(draw, title[:4], 76, 165, 610, 58, 6, True)
    draw.rectangle((76, y + 22, 184, y + 28), fill=CYAN)
    y += 78
    for index, item in enumerate(items[:7]):
        draw.ellipse((78, y, 146, y + 68), outline=CYAN, width=2)
        draw.text((98, y + 8), "✓", font=font(42, True), fill=CYAN)
        draw.ellipse((208, y + 15, 248, y + 55), fill=CYAN)
        draw.text((218, y + 11), "✓", font=font(31, True), fill=DARK)
        draw_wrapped_lines(draw, [item], 272, y + 4, 390, 34, 4, True)
        draw.line((162, y + 78, 570, y + 78), fill=(0, 239, 245, 80), width=1)
        y += 92


def draw_list(draw: ImageDraw.ImageDraw, lines: list[str]) -> None:
    title = [line for line in lines if line.strip() and not re.match(r"^[✅✔]", line.strip())]
    if title and leading_marker(title[0]) in {"📄", "💻", "📊", "✍️"}:
        draw_topic_checklist(draw, lines)
    else:
        draw_standard_checklist(draw, lines)


def draw_before_after(draw: ImageDraw.ImageDraw, lines: list[str]) -> None:
    cleaned = [line for line in lines if line.strip()]
    marker = leading_marker(cleaned[0]) if cleaned else ""
    label = clean_line(cleaned[0]) if cleaned else ""
    quote = next((clean_line(line) for line in cleaned[1:] if '"' in line), clean_line(cleaned[1]) if len(cleaned) > 1 else "")
    color = PINK if marker == "❌" or "antes" in label.lower() else CYAN
    draw_icon(draw, (133, 345), marker, color)
    draw.line((258, 288, 258, 405), fill=color, width=3)
    draw_wrapped_lines(draw, [label], 298, 293, 350, 70, 5, True)
    draw.rounded_rectangle((72, 525, 720, 850), radius=24, outline=color, width=3)
    draw_glow_line(draw, (103, 565), "“", font(94, True), color, glow=color == CYAN)
    quote_text = quote.strip('"')
    size = 48
    while size > 34 and wrapped_height(draw, [quote_text], 470, size, 5) > 210:
        size -= 3
    current_y = 585
    quote_font = font(size, True)
    for part in wrap_text(draw, quote_text, quote_font, 470):
        draw_glow_line(draw, (184, current_y), part, quote_font, WHITE)
        current_y += size + 5


def draw_short_statement(draw: ImageDraw.ImageDraw, lines: list[str]) -> None:
    cleaned = [clean_line(line) for line in lines if clean_line(line)]
    if not cleaned:
        return
    heading = cleaned[0]
    body = cleaned[1:]
    heading_is_long = len(heading) > 42
    if heading_is_long and body:
        draw_fitted_text(draw, [heading], 76, 255, 610, 245, 58, 40)
        draw.rectangle((76, 555, 210, 561), fill=CYAN)
        draw_fitted_text(draw, body, 76, 640, 610, 295, 56, 38)
        return
    draw_wrapped_lines(draw, [heading], 76, 260, 610, 64, 6, True)
    draw.rectangle((76, 378, 210, 384), fill=CYAN)
    draw_fitted_text(draw, body, 76, 455, 610, 410, 60, 40)


def draw_centered_line(
    draw: ImageDraw.ImageDraw,
    text: str,
    box: tuple[int, int, int, int],
    size: int,
    fill: tuple[int, int, int, int],
    bold: bool = True,
    glow: bool = False,
) -> None:
    fnt = font(size, bold)
    width, height = text_size(draw, text, fnt)
    x = box[0] + (box[2] - box[0] - width) // 2
    y = box[1] + (box[3] - box[1] - height) // 2 - 3
    draw_glow_line(draw, (x, y), text, fnt, fill, glow=glow)


def draw_comparison_final(draw: ImageDraw.ImageDraw, cleaned: list[str]) -> None:
    next_part = next((line for line in cleaned if re.search(r"Na Parte", line, re.IGNORECASE)), cleaned[0])
    options = [line for line in cleaned if line.lower() not in {"vs", "versus"} and line != next_part]
    first = options[0] if options else "ChatGPT Work"
    second = options[1] if len(options) > 1 else "Claude Cowork"

    draw_icon(draw, (132, 270), "»", CYAN)
    draw_wrapped_lines(draw, [next_part], 245, 238, 490, 54, 5, True)
    draw.rectangle((245, 342, 380, 348), fill=CYAN)

    draw.rounded_rectangle((76, 420, 690, 555), radius=22, outline=CYAN, width=3)
    draw_centered_line(draw, first, (96, 430, 670, 545), 58, WHITE)

    draw.rounded_rectangle((235, 600, 530, 725), radius=20, outline=(0, 239, 245, 120), width=2)
    draw_centered_line(draw, "VS", (235, 600, 530, 725), 74, CYAN, glow=True)

    draw.rounded_rectangle((76, 770, 690, 905), radius=22, outline=PURPLE, width=3)
    draw_centered_line(draw, second, (96, 780, 670, 895), 56, WHITE)

    draw.rectangle((76, 985, 215, 991), fill=CYAN)
    draw_wrapped_lines(draw, ["Qual faz mais sentido no seu dia a dia?"], 245, 948, 460, 38, 4, True)


def draw_final(draw: ImageDraw.ImageDraw, lines: list[str]) -> None:
    cleaned = [clean_line(line) for line in lines if clean_line(line)]
    if not cleaned:
        return
    has_next_part = any(re.search(r"Na Parte", line, re.IGNORECASE) for line in cleaned)
    if has_next_part:
        if any(line.lower() in {"vs", "versus"} for line in cleaned):
            draw_comparison_final(draw, cleaned)
            return
        draw_icon(draw, (132, 290), "»", CYAN)
        draw_wrapped_lines(draw, cleaned[:2], 245, 245, 530, 54, 5, True)
        key_lines = cleaned[2:-1] if len(cleaned) > 3 else cleaned[2:]
        if key_lines:
            draw_fitted_text(draw, key_lines, 76, 410, 660, 330, 84, 52)
        if cleaned:
            draw.rectangle((76, 840, 225, 846), fill=CYAN)
            draw_icon(draw, (116, 980), "»", CYAN)
            draw_wrapped_lines(draw, [cleaned[-1]], 207, 934, 500, 42, 4, True)
        return
    draw_fitted_text(draw, cleaned, 76, 250, 660, 560, 68, 42)
    draw.rectangle((76, 880, 230, 886), fill=CYAN)


def draw_quote_or_text(draw: ImageDraw.ImageDraw, lines: list[str], slide_number: int) -> None:
    cleaned = [clean_line(line) for line in lines if line.strip()]
    has_quote = any('"' in line for line in cleaned)
    if has_quote:
        y = 230
        for line in cleaned:
            is_quote = '"' in line
            if is_quote:
                color = PINK if "prompt" in line.lower() or "explique" in line.lower() or "resumo" in line.lower() else CYAN
                draw.rounded_rectangle((70, y, 725, y + 150), radius=18, outline=color, width=3)
                draw_wrapped_lines(draw, [line], 112, y + 40, 580, 42, 4, True)
                y += 205
            else:
                y = draw_wrapped_lines(draw, [line], 76, y, 620, 58, 6, True) + 12
        return
    size = 72 if slide_number == 7 else 58
    top = 230 if slide_number == 7 else 255
    bottom_limit = 1080
    draw_fitted_text(draw, cleaned, 76, top, 650, bottom_limit - top, size, 38)


def draw_slide(
    carousel: dict[str, Any],
    slide: dict[str, Any],
    logo_path: Path,
    symbol_panel_path: Path,
    output_path: Path,
) -> None:
    img = background()
    draw = ImageDraw.Draw(img)
    draw_header(draw, carousel["number"])
    draw_ai_mark(img, draw, symbol_panel_path)

    lines = content_without_series(slide)
    slide_number = slide["number"]
    if slide_number == 1:
        draw_cover(draw, lines)
        draw_footer(img, logo_path, cover=True)
    elif slide_number == 4 and any(re.match(r"^[❤️📤📌]", line.strip()) for line in lines):
        draw_cta(draw, lines)
        draw_footer(img, logo_path)
    elif slide_number == 7:
        draw_final(draw, lines)
        draw_footer(img, logo_path)
    elif lines and leading_marker(lines[0]) in {"❌", "✅"} and any('"' in line for line in lines):
        draw_before_after(draw, lines)
        draw_footer(img, logo_path)
    elif any(re.match(r"^[✅✔]", line.strip()) for line in lines):
        draw_list(draw, lines)
        draw_footer(img, logo_path)
    elif len([line for line in lines if clean_line(line)]) <= 2:
        draw_short_statement(draw, lines)
        draw_footer(img, logo_path)
    else:
        draw_quote_or_text(draw, lines, slide_number)
        draw_footer(img, logo_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(output_path, "PNG")


def generate(
    parsed: dict[str, Any],
    output_root: Path,
    logo_path: Path,
    symbol_panel_path: Path,
    limit_carousel: int | None,
) -> dict[str, Any]:
    report: dict[str, Any] = {"output_root": str(output_root), "generated": []}
    for carousel in parsed.get("carousels", []):
        if limit_carousel is not None and carousel["number"] != limit_carousel:
            continue
        carousel_dir = output_root / f"Carrossel {carousel['number']}"
        slides_dir = carousel_dir / "slides"
        slides_dir.mkdir(parents=True, exist_ok=True)
        description_path = carousel_dir / "Descricao.md"
        if not description_path.exists():
            description_path.write_text(description_markdown(carousel), encoding="utf-8")
        for slide in carousel.get("slides", []):
            output_path = slides_dir / f"slide-{slide['number']:02d}.png"
            draw_slide(carousel, slide, logo_path, symbol_panel_path, output_path)
            report["generated"].append(
                {
                    "carousel": carousel["number"],
                    "slide": slide["number"],
                    "png": str(output_path),
                }
            )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate first-pass carousel PNG assets.")
    parser.add_argument("--parsed-json", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument(
        "--logo",
        type=Path,
        default=Path(__file__).resolve().parent.parent
        / "assets/instagram/serie-chatgpt-work/logo/aia-platform-logo.png",
    )
    parser.add_argument(
        "--symbol-panel",
        type=Path,
        default=Path(__file__).resolve().parent.parent
        / "assets/instagram/serie-chatgpt-work/extracted/right-symbol-panel.png",
    )
    parser.add_argument("--carousel", type=int, help="Generate only one carousel number")
    parser.add_argument("--output-json", type=Path, help="Where to write generation report")
    args = parser.parse_args()

    parsed = json.loads(args.parsed_json.read_text(encoding="utf-8"))
    report = generate(parsed, args.output_root, args.logo, args.symbol_panel, args.carousel)

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
