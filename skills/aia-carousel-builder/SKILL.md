---
name: aia-carousel-builder
description: Build branded visual assets for Plataforma AIA from a fixed design system. Use when generating or validating Instagram carousels, YouTube thumbnails, LinkedIn or Facebook assets, landing page visuals, presentations, or reusable AIA visual pieces from source content, especially when the task mentions Slides.md, carousel slides, a visual reference, design consistency, PNG export, Markdown descriptions, or organized output folders.
---

# AIA Carousel Builder

Create reusable Plataforma AIA visual assets from structured source content while preserving a fixed design system. Treat this as a product skill for the AIA ecosystem, not as a one-off Instagram automation.

The first supported module is **Instagram Carousel Builder**. Future modules may include YouTube thumbnails, LinkedIn posts, Facebook assets, landing pages, and presentations.

## Core principles

Preserve visual identity before adding novelty. The official reference defines typography, hierarchy, spacing, color, logo placement, background treatment, and visual rhythm.

Generate production assets, not drafts that require manual cleanup. Every run must create organized PNG exports and an editable Markdown caption.

Validate the result automatically. Check dimensions, slide count, filename consistency, missing outputs, and obvious visual drift before delivery.

## Inputs

Use these inputs when available:

* `Slides.md`: the source file containing one or more carousels and their slides.
* Official reference carousel: the seven slides from Carousel 1.
* Brand assets: logo, palette, fonts, background images, or prior generated slides.
* Output target: Instagram carousel by default unless another channel is requested.

For the **Serie ChatGPT Work** Instagram carousel, read [references/instagram-carousel-design-system.md](references/instagram-carousel-design-system.md) before generating or validating assets.

## Select the canvas format

Before generating any visual asset, ask the user exactly which format they want. Do not assume a default and do not generate before receiving a selection.

1. **Vertical Principal:** `1080 x 1440 px` with a `3:4` ratio. Recommended for more screen coverage and content prominence.
2. **Vertical Classic:** `1080 x 1350 px` with a `4:5` ratio. Suitable for existing templates in that format.
3. **Square:** `1080 x 1080 px` with a `1:1` ratio. The traditional feed format with less screen coverage.

Map the response to one command value:

* `vertical-principal`
* `vertical-classic`
* `square`

Use the selected value in every generator and validation command.

## Instagram Carousel Builder

### 1. Parse Slides.md

Use `Carousel` and `Slide` headings, such as:

```markdown
# Carousel 1
## Slide 1
```

Parse the source and create Markdown descriptions:

```bash
python scripts/parse_slides.py Slides.md \
  --output-json parsed-slides.json \
  --scaffold "Social Media/Instagram/ChatGPT Work Series" \
  --create-descriptions
```

Stop and fix the source if the parser reports errors. Review warnings before generation.

### 2. Generate PNG assets

Use the selected canvas format. Example with the recommended Vertical Principal format:

```bash
python scripts/generate_carousel_pngs.py \
  --parsed-json parsed-slides.json \
  --output-root "Social Media/Instagram/ChatGPT Work Series" \
  --format vertical-principal \
  --output-json generation-report.json
```

The generator creates PNG slides and `Description.md` for each carousel. For HTML/CSS previews, use `scripts/generate_carousel_assets.js` with the same `--format` value. Add `--html-only` when Playwright is unavailable.

Keep text inside safe margins. Avoid tiny type, crowded blocks, clipped logos, and low contrast. Name slide files as `slide-01.png`, `slide-02.png`, and so on.

### 3. Markdown descriptions

Create one `Description.md` file per carousel. It is the sole canonical caption source and must contain:

* a suggested caption;
* exactly five hashtags unless another count is requested;
* an optional publishing note when useful.

Do not create or export Word documents. Keep descriptions editable in Markdown.

### 4. Validate output

Validate every generated carousel using the same selected format:

```bash
python scripts/validate_carousel_output.py \
  "Social Media/Instagram/ChatGPT Work Series" \
  --parsed-json parsed-slides.json \
  --format vertical-principal \
  --output-json validation-report.json
```

Validation must confirm the output folders, PNG count, selected dimensions, filename order, and `Description.md` presence.

Then create a visual review contact sheet:

```bash
python scripts/create_visual_review_sheet.py \
  "Social Media/Instagram/ChatGPT Work Series" \
  --parsed-json parsed-slides.json \
  --reference-dir assets/instagram/serie-chatgpt-work/reference-carousel-1 \
  --output visual-review-contact-sheet.png
```

Inspect the contact sheet for typography, spacing, logo placement, progress indicators, and text clipping.

## Delivery

Summarize what was created and validated. Include the output path, selected format, and any assumptions or missing inputs that still require review.

## Expansion

Keep future design-system modules in this skill when they reuse the Plataforma AIA visual identity. Planned modules include YouTube Thumbnail Builder, LinkedIn Asset Builder, Facebook Asset Builder, Landing Page Design Builder, and Presentation Builder.
