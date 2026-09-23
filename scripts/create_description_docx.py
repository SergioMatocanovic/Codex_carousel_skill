#!/usr/bin/env python3
"""Create Descricao.docx files from canonical Descricao.md files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor


CAROUSEL_DIR_RE = re.compile(r"^Carrossel\s+(\d+)$", re.IGNORECASE)
BRAND_BLUE = RGBColor(46, 116, 181)
BRAND_DARK_BLUE = RGBColor(31, 77, 120)
MUTED_GRAY = RGBColor(100, 106, 120)


def set_paragraph_spacing(paragraph: Any, before: int = 0, after: int = 6, line_spacing: float = 1.25) -> None:
    paragraph.paragraph_format.space_before = Pt(before)
    paragraph.paragraph_format.space_after = Pt(after)
    paragraph.paragraph_format.line_spacing = line_spacing


def configure_document(doc: Document) -> None:
    section = doc.sections[0]
    section.top_margin = Inches(1.0)
    section.right_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor(0, 0, 0)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.25

    for style_name, size, color, before, after in [
        ("Heading 1", 16, BRAND_BLUE, 18, 10),
        ("Heading 2", 13, BRAND_BLUE, 14, 7),
        ("Heading 3", 12, BRAND_DARK_BLUE, 10, 5),
    ]:
        style = doc.styles[style_name]
        style.font.name = "Calibri"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = color
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.line_spacing = 1.25


def parse_markdown(markdown: str) -> tuple[str, list[tuple[str, list[str]]]]:
    title = "Descricao"
    sections: list[tuple[str, list[str]]] = []
    current_heading = ""
    current_lines: list[str] = []

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if line.startswith("# "):
            if current_heading or current_lines:
                sections.append((current_heading, current_lines))
            title = line[2:].strip() or title
            current_heading = ""
            current_lines = []
            continue
        if line.startswith("## "):
            if current_heading or current_lines:
                sections.append((current_heading, current_lines))
            current_heading = line[3:].strip()
            current_lines = []
            continue
        current_lines.append(line)

    if current_heading or current_lines:
        sections.append((current_heading, current_lines))
    return title, sections


def split_blocks(lines: list[str]) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for line in lines:
        if line.strip():
            current.append(line.strip())
            continue
        if current:
            blocks.append("\n".join(current))
            current = []
    if current:
        blocks.append("\n".join(current))
    return blocks


def add_body_block(doc: Document, block: str) -> None:
    block_lines = block.splitlines()
    if any(line.strip().startswith("- ") for line in block_lines):
        for line in block_lines:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("- "):
                paragraph = doc.add_paragraph(style="List Bullet")
                set_paragraph_spacing(paragraph, after=4, line_spacing=1.25)
                run = paragraph.add_run(stripped[2:].strip())
            else:
                paragraph = doc.add_paragraph()
                set_paragraph_spacing(paragraph, after=4, line_spacing=1.25)
                run = paragraph.add_run(stripped)
            run.font.name = "Calibri"
            run.font.size = Pt(11)
        return

    paragraph = doc.add_paragraph()
    set_paragraph_spacing(paragraph, after=6, line_spacing=1.25)
    if block.startswith("#") and " " in block and all(part.startswith("#") for part in block.split()):
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for index, hashtag in enumerate(block.split()):
            run = paragraph.add_run((" " if index else "") + hashtag)
            run.font.name = "Calibri"
            run.font.size = Pt(11)
            run.font.bold = True
            run.font.color.rgb = BRAND_DARK_BLUE
        return
    run = paragraph.add_run(block)
    run.font.name = "Calibri"
    run.font.size = Pt(11)


def build_docx(markdown: str, output_path: Path) -> None:
    title, sections = parse_markdown(markdown)
    doc = Document()
    configure_document(doc)

    title_paragraph = doc.add_paragraph()
    set_paragraph_spacing(title_paragraph, before=0, after=3, line_spacing=1.25)
    title_run = title_paragraph.add_run(title)
    title_run.font.name = "Calibri"
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    title_run.font.color.rgb = BRAND_DARK_BLUE

    metadata = doc.add_paragraph()
    set_paragraph_spacing(metadata, before=0, after=12, line_spacing=1.25)
    metadata_run = metadata.add_run("Instagram Carousel Builder · Plataforma AIA")
    metadata_run.font.name = "Calibri"
    metadata_run.font.size = Pt(9)
    metadata_run.font.color.rgb = MUTED_GRAY

    for heading, lines in sections:
        if heading:
            doc.add_heading(heading, level=2)
        for block in split_blocks(lines):
            add_body_block(doc, block)

    footer = doc.sections[0].footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_run = footer.add_run("Plataforma AIA · @sergiomatocanovic")
    footer_run.font.name = "Calibri"
    footer_run.font.size = Pt(9)
    footer_run.font.color.rgb = MUTED_GRAY

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)


def load_expected(parsed_json: Path | None) -> list[dict[str, Any]]:
    if parsed_json is None:
        return []
    data = json.loads(parsed_json.read_text(encoding="utf-8"))
    return data.get("carousels", [])


def discover_carousel_numbers(output_root: Path) -> list[int]:
    numbers: list[int] = []
    if not output_root.exists():
        return numbers
    for child in output_root.iterdir():
        if child.is_dir():
            match = CAROUSEL_DIR_RE.match(child.name)
            if match:
                numbers.append(int(match.group(1)))
    return sorted(numbers)


def convert_one(markdown_path: Path, output_path: Path, overwrite: bool) -> dict[str, Any]:
    result: dict[str, Any] = {
        "markdown": str(markdown_path),
        "docx": str(output_path),
        "created": False,
        "skipped": False,
    }
    if not markdown_path.exists():
        result["error"] = f"Missing Markdown source: {markdown_path}"
        return result
    if output_path.exists() and not overwrite:
        result["skipped"] = True
        return result
    markdown = markdown_path.read_text(encoding="utf-8")
    build_docx(markdown, output_path)
    result["created"] = True
    return result


def convert_all(
    output_root: Path,
    parsed_json: Path | None,
    overwrite: bool,
    limit_carousel: int | None,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "output_root": str(output_root),
        "errors": [],
        "warnings": [],
        "documents": [],
    }
    expected = load_expected(parsed_json)
    numbers = [carousel["number"] for carousel in expected] if expected else discover_carousel_numbers(output_root)
    if limit_carousel is not None:
        numbers = [number for number in numbers if number == limit_carousel]
    if not numbers:
        report["errors"].append(f"No carousel folders found in: {output_root}")
        return report

    for number in numbers:
        carousel_dir = output_root / f"Carrossel {number}"
        result = convert_one(carousel_dir / "Descricao.md", carousel_dir / "Descricao.docx", overwrite)
        report["documents"].append(result)
        if "error" in result:
            report["errors"].append(result["error"])
    return report


def write_json(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create Descricao.docx files from Descricao.md.")
    parser.add_argument("output_root", nargs="?", type=Path, help="Folder containing Carrossel N folders")
    parser.add_argument("--parsed-json", type=Path, help="parsed-slides.json generated by parse_slides.py")
    parser.add_argument("--carousel", type=int, help="Convert only one carousel number")
    parser.add_argument("--input-md", type=Path, help="Convert a single Markdown file")
    parser.add_argument("--output-docx", type=Path, help="Output DOCX when using --input-md")
    parser.add_argument("--no-overwrite", action="store_true", help="Skip existing DOCX files")
    parser.add_argument("--output-json", type=Path, help="Where to write a conversion report")
    args = parser.parse_args()

    overwrite = not args.no_overwrite
    if args.input_md:
        output_docx = args.output_docx or args.input_md.with_suffix(".docx")
        result = convert_one(args.input_md, output_docx, overwrite)
        report = {"errors": [], "warnings": [], "documents": [result]}
        if "error" in result:
            report["errors"].append(result["error"])
    else:
        if args.output_root is None:
            parser.error("output_root is required unless --input-md is used")
        report = convert_all(args.output_root, args.parsed_json, overwrite, args.carousel)

    if args.output_json:
        write_json(report, args.output_json)
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
