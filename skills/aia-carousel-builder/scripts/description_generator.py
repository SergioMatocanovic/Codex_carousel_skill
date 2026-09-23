#!/usr/bin/env python3
"""Generate editable Instagram description Markdown from parsed carousel data."""

from __future__ import annotations

import re
from typing import Any


DEFAULT_HASHTAGS = "#chatgpt #inteligenciaartificial #chatgptwork #plataformaaia #produtividade"
CTA_MARKERS = ("❤️", "📤", "📌")
CHECK_MARKERS = ("✅", "✔")


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


def normalize_sentence(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return text
    if text.endswith((".", "?", "!", ":")):
        return text
    return f"{text}."


def content_without_series(slide: dict[str, Any]) -> list[str]:
    lines = slide.get("content_lines", [])
    if lines and re.match(r"S[eé]rie\s+ChatGPT Work", lines[0], re.IGNORECASE):
        return lines[1:]
    return lines


def title_from_carousel(carousel: dict[str, Any]) -> str:
    title = clean_line(str(carousel.get("title", "")))
    if title:
        return normalize_sentence(title)
    return f"Carousel {carousel.get('number', '')}".strip()


def slide_takeaway(slide: dict[str, Any]) -> str:
    lines = [line for line in content_without_series(slide) if clean_line(line)]
    if not lines:
        return ""

    first = clean_line(lines[0])
    quoted = next((clean_line(line).strip('"') for line in lines[1:] if '"' in line), "")
    checked = [clean_line(line) for line in lines if line.strip().startswith(CHECK_MARKERS)]
    label = first.rstrip(".:")

    if first.lower() in {"antes", "agora"} and quoted:
        return normalize_sentence(f"{first}: {quoted}")
    if checked:
        return normalize_sentence(f"{label}: {', '.join(checked[:3])}") if label else normalize_sentence(", ".join(checked[:3]))
    if len(lines) > 1:
        second = clean_line(lines[1])
        if second.lower().startswith("parece") and label:
            return normalize_sentence(f"{label}: {second}")
        if second and len(first) < 36:
            return normalize_sentence(f"{first} {second}")
    return normalize_sentence(first)


def main_idea(carousel: dict[str, Any]) -> str:
    slides = carousel.get("slides", [])
    first_slide = next((slide for slide in slides if slide.get("number") == 1), slides[0] if slides else {})
    lines = [clean_line(line) for line in content_without_series(first_slide) if clean_line(line)]
    if not lines:
        return title_from_carousel(carousel)
    joined = " ".join(lines[:6])
    if len(joined) > 180:
        joined = " ".join(lines[:3])
    return normalize_sentence(joined)


def key_points(carousel: dict[str, Any], limit: int = 4) -> list[str]:
    points: list[str] = []
    for slide in carousel.get("slides", []):
        number = slide.get("number")
        if number in {1, 4, 7}:
            continue
        lines = content_without_series(slide)
        if lines and lines[0].strip().startswith(CTA_MARKERS):
            continue
        point = slide_takeaway(slide)
        if point and point not in points:
            points.append(point)
        if len(points) >= limit:
            break
    return points


def closing_question(carousel: dict[str, Any]) -> str:
    title = title_from_carousel(carousel).lower()
    if "vs" in title or "cowork" in title or "claude" in title:
        return "E você: qual dessas ferramentas faz mais sentido para o seu dia a dia?"
    if "tipos de trabalho" in title:
        return "Salve para consultar depois e escolha um trabalho para delegar ainda esta semana."
    if "respostas" in title:
        return "Na próxima vez que abrir o ChatGPT, teste trocar pedido por delegação."
    return "Salve para consultar depois e me conta: qual trabalho você já delegaria hoje?"


def description_markdown(carousel: dict[str, Any]) -> str:
    title = title_from_carousel(carousel)
    idea = main_idea(carousel)
    points = key_points(carousel)
    caption_lines = [
        title,
        "",
        f"A ideia aqui é simples: {idea}",
        "",
    ]
    if points:
        caption_lines.append("In this carousel:")
        for point in points:
            caption_lines.append(f"- {point}")
        caption_lines.append("")
    caption_lines.append(closing_question(carousel))

    return "\n".join(
        [
            f"# Carousel {carousel['number']} - {clean_line(str(carousel.get('title', '')))}",
            "",
            "## Caption",
            "",
            *caption_lines,
            "",
            "## Hashtags",
            "",
            DEFAULT_HASHTAGS,
            "",
            "## Notes",
            "",
            "Caption generated automatically from Slides.md. Review it before publishing and adjust the final voice when needed.",
            "",
        ]
    )
