#!/usr/bin/env python3
"""Validate generated Instagram carousel output folders."""

from __future__ import annotations

import argparse
import json
import re
import struct
import zipfile
from pathlib import Path
from typing import Any


CAROUSEL_DIR_RE = re.compile(r"^Carrossel\s+(\d+)$", re.IGNORECASE)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as file:
        signature = file.read(8)
        if signature != PNG_SIGNATURE:
            raise ValueError("not a PNG file")
        length = struct.unpack(">I", file.read(4))[0]
        chunk_type = file.read(4)
        if chunk_type != b"IHDR" or length < 8:
            raise ValueError("invalid PNG header")
        width, height = struct.unpack(">II", file.read(8))
        return width, height


def load_expected(parsed_json: Path | None) -> list[dict[str, Any]]:
    if parsed_json is None:
        return []
    data = json.loads(parsed_json.read_text(encoding="utf-8"))
    return data.get("carousels", [])


def discover_carousels(root: Path) -> list[dict[str, Any]]:
    carousels: list[dict[str, Any]] = []
    if not root.exists():
        return carousels
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        match = CAROUSEL_DIR_RE.match(child.name)
        if not match:
            continue
        number = int(match.group(1))
        slide_files = sorted((child / "slides").glob("slide-*.png"))
        carousels.append(
            {
                "number": number,
                "title": "",
                "slides": [{"number": index + 1} for index, _ in enumerate(slide_files)],
            }
        )
    return carousels


def add_error(report: dict[str, Any], message: str) -> None:
    report["errors"].append(message)


def add_warning(report: dict[str, Any], message: str) -> None:
    report["warnings"].append(message)


def validate_slide_png(
    report: dict[str, Any],
    path: Path,
    expected_width: int,
    expected_height: int,
) -> None:
    if not path.exists():
        add_error(report, f"Missing slide PNG: {path}")
        return
    try:
        width, height = png_size(path)
    except ValueError as exc:
        add_error(report, f"Invalid PNG {path}: {exc}")
        return
    if (width, height) != (expected_width, expected_height):
        add_error(
            report,
            f"Wrong PNG size {path}: {width}x{height}, expected {expected_width}x{expected_height}",
        )


def validate_docx(report: dict[str, Any], path: Path) -> None:
    if not path.exists():
        add_error(report, f"Missing Descricao.docx: {path}")
        return
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
    except zipfile.BadZipFile:
        add_error(report, f"Invalid DOCX {path}: not a valid ZIP package")
        return
    required_parts = {"[Content_Types].xml", "word/document.xml"}
    missing_parts = sorted(required_parts - names)
    if missing_parts:
        add_error(report, f"Invalid DOCX {path}: missing {', '.join(missing_parts)}")


def validate_carousel(
    root: Path,
    carousel: dict[str, Any],
    report: dict[str, Any],
    expected_width: int,
    expected_height: int,
    require_docx: bool,
) -> None:
    number = carousel["number"]
    carousel_dir = root / f"Carrossel {number}"
    slides_dir = carousel_dir / "slides"
    result: dict[str, Any] = {
        "number": number,
        "title": carousel.get("title", ""),
        "folder": str(carousel_dir),
        "expected_slides": len(carousel.get("slides", [])),
        "found_slides": 0,
    }
    report["carousels"].append(result)

    if not carousel_dir.exists():
        add_error(report, f"Missing carousel folder: {carousel_dir}")
        return
    if not slides_dir.exists():
        add_error(report, f"Missing slides folder: {slides_dir}")
        return

    description_md = carousel_dir / "Descricao.md"
    if not description_md.exists():
        add_error(report, f"Missing Descricao.md: {description_md}")

    description_docx = carousel_dir / "Descricao.docx"
    if require_docx:
        validate_docx(report, description_docx)

    expected_slides = carousel.get("slides", [])
    expected_numbers = [slide["number"] for slide in expected_slides]
    for slide_number in expected_numbers:
        slide_path = slides_dir / f"slide-{slide_number:02d}.png"
        validate_slide_png(report, slide_path, expected_width, expected_height)

    found_slide_files = sorted(slides_dir.glob("slide-*.png"))
    result["found_slides"] = len(found_slide_files)
    found_names = {path.name for path in found_slide_files}
    expected_names = {f"slide-{slide_number:02d}.png" for slide_number in expected_numbers}
    extra_names = sorted(found_names - expected_names)
    if extra_names:
        add_warning(
            report,
            f"Carousel {number}: unexpected slide files: {', '.join(extra_names)}",
        )


def validate_output(
    root: Path,
    expected_carousels: list[dict[str, Any]],
    expected_width: int,
    expected_height: int,
    require_docx: bool,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "root": str(root),
        "expected_width": expected_width,
        "expected_height": expected_height,
        "require_docx": require_docx,
        "errors": [],
        "warnings": [],
        "carousels": [],
    }

    if not root.exists():
        add_error(report, f"Missing output root: {root}")
        return report

    carousels = expected_carousels or discover_carousels(root)
    if not carousels:
        add_error(report, f"No carousel folders found in: {root}")
        return report

    for carousel in carousels:
        validate_carousel(
            root=root,
            carousel=carousel,
            report=report,
            expected_width=expected_width,
            expected_height=expected_height,
            require_docx=require_docx,
        )

    expected_dirs = {f"Carrossel {carousel['number']}" for carousel in carousels}
    actual_dirs = {
        child.name
        for child in root.iterdir()
        if child.is_dir() and CAROUSEL_DIR_RE.match(child.name)
    }
    extra_dirs = sorted(actual_dirs - expected_dirs)
    if extra_dirs:
        add_warning(report, f"Unexpected carousel folders: {', '.join(extra_dirs)}")

    return report


def write_json(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate carousel output folders, descriptions, and PNG dimensions.",
    )
    parser.add_argument("output_root", type=Path, help="Folder containing Carrossel N folders")
    parser.add_argument(
        "--parsed-json",
        type=Path,
        help="parsed-slides.json generated by parse_slides.py",
    )
    parser.add_argument("--width", type=int, default=1254, help="Expected PNG width")
    parser.add_argument("--height", type=int, default=1254, help="Expected PNG height")
    parser.add_argument(
        "--require-docx",
        action="store_true",
        help="Require Descricao.docx in each carousel folder",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        help="Where to write the validation report. Defaults to stdout.",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Exit with status 1 if warnings are found.",
    )
    args = parser.parse_args()

    expected_carousels = load_expected(args.parsed_json)
    report = validate_output(
        root=args.output_root,
        expected_carousels=expected_carousels,
        expected_width=args.width,
        expected_height=args.height,
        require_docx=args.require_docx,
    )

    if args.output_json:
        write_json(report, args.output_json)
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    if report["errors"] or (args.fail_on_warning and report["warnings"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
