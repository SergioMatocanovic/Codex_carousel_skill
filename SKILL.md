---
name: aia-design-system-builder
description: Build branded visual assets for Plataforma AIA from a fixed design system. Use when Sergio asks to generate or validate Instagram carousels, YouTube thumbnails, LinkedIn or Facebook assets, landing page visuals, presentations, or other reusable AIA visual pieces from source content, especially when the task mentions Slides.md, carousel slides, a visual reference, design consistency, PNG export, Markdown or DOCX descriptions, or organized output folders.
---

# AIA Design System Builder

Create reusable Plataforma AIA visual assets from structured source content while preserving a fixed design system. Treat this as a product skill for the AIA ecosystem, not as a one-off Instagram automation.

The first supported module is **Instagram Carousel Builder**. Future modules may include YouTube thumbnails, LinkedIn posts, Facebook assets, landing pages, and presentations. Keep any implementation decision modular enough that a new output channel can reuse the same design system and validation logic.

## Core Principles

Preserve visual identity before adding novelty. The official reference is the source of truth for typography, hierarchy, spacing, color, logo placement, background treatment, and overall rhythm.

Generate production assets, not drafts that require manual cleanup. Each run should produce organized folders, square PNG exports, and publication copy where requested.

Validate the result automatically. Check dimensions, slide count, filename consistency, missing outputs, and obvious visual drift before saying the work is done.

Do not invent a new style unless Sergio explicitly asks to evolve the design system. When content does not fit the visual pattern, adapt the wording or layout density while keeping the identity intact.

## Inputs

Use these inputs when available:

- `Slides.md`: the source file containing one or more carousels and their slides.
- Official reference carousel: the 7 slides from Carrossel 1, used as the visual source of truth.
- Brand assets: Plataforma AIA logo, color palette, fonts, background images, or prior generated slides.
- Output target: Instagram carousel by default unless the user names another channel.

If `Slides.md` or the official reference slides are missing, ask for the missing file or image set before generating final assets. If the user only wants to draft the skill or plan the workflow, continue without asking.

For the **Serie ChatGPT Work** Instagram carousel, read [references/instagram-carousel-design-system.md](references/instagram-carousel-design-system.md) before generating or validating assets. Use its bundled reference slides and logo assets as the default visual source.

## Instagram Carousel Builder

Use this workflow when the user asks for Instagram carousels or provides `Slides.md`.

### 1. Read Slides.md

Parse the file into carousels and slides. Preserve the intended sequence and do not merge carousels unless the source clearly says to do so.

Use `scripts/parse_slides.py` as the default parser:

```bash
python3 scripts/parse_slides.py Slides.md \
  --output-json parsed-slides.json \
  --scaffold "Redes Sociais/Instagram/Serie ChatGPT Work" \
  --create-descriptions
```

The parser returns JSON with `carousels`, `slides`, `errors`, and `warnings`. Stop and fix the source if `errors` is not empty. Review `warnings` before generating visual assets.

Support headings such as:

- `# Carrossel 1`
- `## Slide 1`
- `Carrossel 2`
- `Slide 3`

If structure is ambiguous, infer conservatively and report the assumption before exporting. Keep the original slide text meaning intact, but shorten lines when needed to preserve readability.

### 2. Identify the Official Reference

Use the 7 slides from Carrossel 1 as the official visual reference. Extract and preserve:

- canvas ratio and export size;
- background style and texture;
- primary, secondary, and accent colors;
- typography scale and weight;
- title, subtitle, body, CTA, and footer hierarchy;
- logo position and safe margins;
- recurring shapes, dividers, badges, counters, or progress marks;
- slide-to-slide rhythm.

Do not treat Carrossel 1 as content to rewrite unless the user asks. Treat it as the design system specimen.

### 3. Generate Remaining Carousels

For each carousel after Carrossel 1, create slides that match the official reference exactly enough to feel like the same product family.

Use `scripts/generate_carousel_pngs.py` as the default PNG generator:

```bash
python3 scripts/generate_carousel_pngs.py \
  --parsed-json parsed-slides.json \
  --output-root "Redes Sociais/Instagram/Serie ChatGPT Work" \
  --output-json generation-report.json
```

This generator creates first-pass `1254x1254` PNGs and ensures `Descricao.md` exists. It uses the extracted official right-side symbol panel from the reference carousel by default. Use it as the dependable baseline for automated runs. For HTML/CSS preview or future browser-based refinement, use `scripts/generate_carousel_assets.js`; add `--html-only` when Playwright's browser runtime is unavailable.

Use square Instagram assets:

- Export every slide as PNG.
- Use `1254x1254` pixels.
- Keep text inside safe margins.
- Avoid tiny type, crowded blocks, clipped logo, and low-contrast text.
- Keep filenames sortable, such as `slide-01.png`, `slide-02.png`.

If a carousel has more or fewer than 7 slides, keep the reference identity while adapting the slide roles. Do not force filler slides just to reach seven unless the content needs a standard opening/body/CTA arc.

### 4. Create Description Files

Create one `Descricao.md` per carousel as the editable source file. Generate a first-pass Instagram caption from the carousel title and slide content instead of leaving placeholders. Also create `Descricao.docx` when a final document artifact is useful or explicitly requested. Include:

- suggested Instagram caption;
- exactly 5 hashtags unless Sergio requests another count;
- optional short posting note when useful;
- no excessive explanation of the design process.

Use Markdown for the canonical description because it is faster to edit, easier to copy into social platforms, and easier to version. Use DOCX as an export format, not as the only source of truth.

Use `scripts/create_description_docx.py` to export DOCX files from existing `Descricao.md` files:

```bash
python3 scripts/create_description_docx.py \
  "Redes Sociais/Instagram/Serie ChatGPT Work" \
  --parsed-json parsed-slides.json \
  --output-json description-docx-report.json
```

The script overwrites `Descricao.docx` by default so the DOCX stays synchronized with the Markdown source. Add `--no-overwrite` only when preserving manually edited DOCX files matters more than synchronization.

Use `scripts/description_generator.py` as the shared source for generated Markdown descriptions. Keep the output editable: the generated caption should be useful on its own, but still easy for Sergio to revise before posting.

Write in Sergio's voice when the topic is his own content: direct, technical, warm, lightly humorous, and grounded in real experience. Avoid hype that sounds detached from what he actually built.

### 5. Organize Output Folders

For Serie ChatGPT Work, use this folder convention by default:

```text
Redes Sociais/
  Instagram/
    Serie ChatGPT Work/
      Carrossel 1/
        slides/
          slide-01.png
          slide-02.png
        Descricao.md
        Descricao.docx
      Carrossel 2/
        slides/
          slide-01.png
          slide-02.png
        Descricao.md
        Descricao.docx
```

For other series or channels, create a clean output structure using the same pattern:

```text
<Channel>/<Series Name>/<Carrossel X>/
    slides/
      slide-01.png
      slide-02.png
    Descricao.md
    Descricao.docx
```

If the user provides an existing folder convention, follow it instead and keep names consistent with that project.

## Validation

Before delivering, validate:

- every expected carousel has an output folder;
- every expected slide has one PNG;
- every PNG is exactly `1254x1254`;
- slide filenames sort in the intended reading order;
- each carousel has `Descricao.md`;
- each carousel has `Descricao.docx` when DOCX export was requested or required by the workflow;
- logo, footer, counters, and recurring visual elements are present when required by the reference;
- text is legible and not clipped;
- the generated carousels visually match the official reference.

Use `scripts/validate_carousel_output.py` for automated checks after generating slide PNGs:

```bash
python3 scripts/validate_carousel_output.py \
  "Redes Sociais/Instagram/Serie ChatGPT Work" \
  --parsed-json parsed-slides.json \
  --output-json validation-report.json
```

Add `--require-docx` only when `Descricao.docx` is required for that run. The validator checks output folders, `Descricao.md`, optional valid `Descricao.docx`, expected slide filenames, PNG validity, and exact `1254x1254` dimensions.

After automated validation passes, create a visual review contact sheet:

```bash
python3 scripts/create_visual_review_sheet.py \
  "Redes Sociais/Instagram/Serie ChatGPT Work" \
  --parsed-json parsed-slides.json \
  --reference-dir assets/instagram/serie-chatgpt-work/reference-carousel-1 \
  --output visual-review-contact-sheet.png
```

Inspect the contact sheet before delivery. Compare the generated rows against the reference row for identity, spacing, hierarchy, logo placement, progress indicator, and text clipping. If visual QA fails, fix the generator or the generated files and run validation again.

## Delivery

Summarize only what was created and validated. Include the output path and mention any assumptions, missing inputs, or manual review still needed.

Do not over-explain the workflow after successful generation. The user cares about usable assets and confidence that the design system stayed intact.

## Expansion Rules

When adding a new module, keep it under this same skill if it uses Plataforma AIA's design system. Add a clear section for the module and preserve the shared principles, input parsing, validation, and folder organization patterns.

Use these module names as the roadmap:

- Instagram Carousel Builder
- YouTube Thumbnail Builder
- LinkedIn Asset Builder
- Facebook Asset Builder
- Landing Page Design Builder
- Presentation Builder

If a future module requires deterministic generation or validation, add scripts only for the repeatable parts and keep this `SKILL.md` as the routing and workflow layer.
