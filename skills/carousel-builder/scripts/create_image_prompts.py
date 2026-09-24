#!/usr/bin/env python3
"""Create text-free image prompts from parsed carousel content and a visual plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Create image prompts for a theme-led carousel.")
    parser.add_argument("--parsed-json", type=Path, required=True)
    parser.add_argument("--visual-plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    parsed = json.loads(args.parsed_json.read_text(encoding="utf-8"))
    plan = json.loads(args.visual_plan.read_text(encoding="utf-8"))
    direction = plan.get("direction", {})
    palette = ", ".join(direction.get("palette", [])) or "a restrained palette chosen for the subject"
    mood = direction.get("mood", "clear, editorial, and human")
    by_slide = {(item.get("carousel"), item.get("slide")): item for item in plan.get("slides", [])}
    lines = ["# Image prompts", "", "Generate each image as a text-free background or illustration. Do not include words, logos, watermarks, interface chrome, or borders.", ""]
    for carousel in parsed.get("carousels", []):
        for slide in carousel.get("slides", []):
            item = by_slide.get((carousel["number"], slide["number"]), {})
            prompt = item.get("image_prompt") or " ".join(slide.get("content_lines", []))
            filename = item.get("image") or f"carousel-{carousel['number']:02d}-slide-{slide['number']:02d}.png"
            lines.extend([f"## {filename}", "", f"Create a social-media background for this idea: {prompt}", f"Art direction: {mood}. Palette: {palette}. Leave calm negative space for an editorial text overlay.", ""])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
