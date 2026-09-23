#!/usr/bin/env python3
"""Parse Slides.md into structured carousel data."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from description_generator import description_markdown


CAROUSEL_RE = re.compile(
    r"^(?:#{1,6}\s*)?Carousel\s+(\d+)(?:\s*[-:–—]\s*(.+?))?\s*$",
    re.IGNORECASE,
)
SLIDE_RE = re.compile(
    r"^(?:#{1,6}\s*)?Slide\s+(\d+)(?:\s*\((.+?)\))?\s*$",
    re.IGNORECASE,
)


def is_separator(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    without_escapes = stripped.replace("\\", "").replace("_", "").strip()
    return not without_escapes and stripped.count("_") >= 8


def trim_blank_edges(lines: list[str]) -> list[str]:
    start = 0
    end = len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return lines[start:end]


def non_empty(lines: list[str]) -> list[str]:
    return [line.strip() for line in lines if line.strip()]


def new_carousel(number: int, source_line: int, inline_title: str | None = None) -> dict[str, Any]:
    return {
        "number": number,
        "title": inline_title or "",
        "source_line": source_line,
        "slides": [],
        "_title_lines": [],
    }


def new_slide(number: int, source_line: int, note: str | None = None) -> dict[str, Any]:
    return {
        "number": number,
        "note": note or "",
        "source_line": source_line,
        "content_lines": [],
        "raw_text": "",
    }


def finish_slide(slide: dict[str, Any] | None) -> dict[str, Any] | None:
    if slide is None:
        return None
    lines = trim_blank_edges(slide["content_lines"])
    slide["content_lines"] = non_empty(lines)
    slide["raw_text"] = "\n".join(lines).strip()
    return slide


def finish_carousel(carousel: dict[str, Any] | None) -> dict[str, Any] | None:
    if carousel is None:
        return None
    title_lines = non_empty(carousel.pop("_title_lines", []))
    if not carousel["title"] and title_lines:
        carousel["title"] = " ".join(title_lines)
    return carousel


def parse_slides(text: str, source_name: str = "Slides.md") -> dict[str, Any]:
    carousels: list[dict[str, Any]] = []
    errors: list[str] = []
    warnings: list[str] = []
    current_carousel: dict[str, Any] | None = None
    current_slide: dict[str, Any] | None = None

    for line_number, original_line in enumerate(text.splitlines(), start=1):
        line = original_line.rstrip()

        if is_separator(line):
            continue

        carousel_match = CAROUSEL_RE.match(line.strip())
        if carousel_match:
            finished_slide = finish_slide(current_slide)
            if finished_slide and current_carousel:
                current_carousel["slides"].append(finished_slide)
            finished_carousel = finish_carousel(current_carousel)
            if finished_carousel:
                carousels.append(finished_carousel)

            current_carousel = new_carousel(
                number=int(carousel_match.group(1)),
                source_line=line_number,
                inline_title=carousel_match.group(2),
            )
            current_slide = None
            continue

        slide_match = SLIDE_RE.match(line.strip())
        if slide_match:
            if current_carousel is None:
                errors.append(f"Line {line_number}: slide found before any carousel")
                continue
            finished_slide = finish_slide(current_slide)
            if finished_slide:
                current_carousel["slides"].append(finished_slide)
            current_slide = new_slide(
                number=int(slide_match.group(1)),
                source_line=line_number,
                note=slide_match.group(2),
            )
            continue

        if current_carousel is None:
            if line.strip():
                warnings.append(f"Line {line_number}: text ignored before first carousel")
            continue

        if current_slide is None:
            current_carousel["_title_lines"].append(line)
        else:
            current_slide["content_lines"].append(line)

    finished_slide = finish_slide(current_slide)
    if finished_slide and current_carousel:
        current_carousel["slides"].append(finished_slide)
    finished_carousel = finish_carousel(current_carousel)
    if finished_carousel:
        carousels.append(finished_carousel)

    validate_structure(carousels, errors, warnings)

    return {
        "source": source_name,
        "carousel_count": len(carousels),
        "slide_count": sum(len(carousel["slides"]) for carousel in carousels),
        "errors": errors,
        "warnings": warnings,
        "carousels": carousels,
    }


def validate_structure(
    carousels: list[dict[str, Any]],
    errors: list[str],
    warnings: list[str],
    expected_slides: int = 7,
) -> None:
    if not carousels:
        errors.append("No carousels found")
        return

    seen_carousels: set[int] = set()
    for carousel in carousels:
        number = carousel["number"]
        if number in seen_carousels:
            errors.append(f"Duplicate carousel number: {number}")
        seen_carousels.add(number)

        if not carousel["title"]:
            warnings.append(f"Carousel {number}: missing title")
        if not carousel["slides"]:
            errors.append(f"Carousel {number}: no slides found")
            continue

        seen_slides: set[int] = set()
        slide_numbers = [slide["number"] for slide in carousel["slides"]]
        for slide in carousel["slides"]:
            slide_number = slide["number"]
            if slide_number in seen_slides:
                errors.append(f"Carousel {number}: duplicate slide number {slide_number}")
            seen_slides.add(slide_number)
            if not slide["raw_text"]:
                warnings.append(f"Carousel {number}, slide {slide_number}: empty slide")

        expected_sequence = list(range(1, len(slide_numbers) + 1))
        if slide_numbers != expected_sequence:
            warnings.append(
                f"Carousel {number}: slide sequence is {slide_numbers}, expected {expected_sequence}"
            )
        if len(slide_numbers) != expected_slides:
            warnings.append(
                f"Carousel {number}: has {len(slide_numbers)} slides, expected {expected_slides}"
            )


def write_json(data: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def scaffold_output(data: dict[str, Any], root: Path, create_descriptions: bool) -> None:
    for carousel in data["carousels"]:
        carousel_dir = root / f"Carousel {carousel['number']}"
        slides_dir = carousel_dir / "slides"
        slides_dir.mkdir(parents=True, exist_ok=True)
        if create_descriptions:
            description_path = carousel_dir / "Description.md"
            if not description_path.exists():
                description_path.write_text(
                    description_markdown(carousel),
                    encoding="utf-8",
                )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse Slides.md into JSON and optionally create carousel folders.",
    )
    parser.add_argument("slides_md", type=Path, help="Path to Slides.md")
    parser.add_argument(
        "--output-json",
        type=Path,
        help="Where to write parsed JSON. Defaults to stdout.",
    )
    parser.add_argument(
        "--scaffold",
        type=Path,
        help="Root folder for Carousel N folders.",
    )
    parser.add_argument(
        "--create-descriptions",
        action="store_true",
        help="Create Description.md files when using --scaffold.",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Exit with status 1 if warnings are found.",
    )
    args = parser.parse_args()

    text = args.slides_md.read_text(encoding="utf-8-sig")
    data = parse_slides(text, source_name=str(args.slides_md))

    if args.output_json:
        write_json(data, args.output_json)
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))

    if args.scaffold:
        scaffold_output(data, args.scaffold, args.create_descriptions)

    if data["errors"] or (args.fail_on_warning and data["warnings"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
