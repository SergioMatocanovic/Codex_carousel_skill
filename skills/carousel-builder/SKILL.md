---
name: carousel-builder
description: Create and validate social-media carousel assets from Slides.md, a visual reference, or a brand brief. Use for Instagram carousel generation, carousel visual reviews, PNG exports, Markdown captions, and creating a visual profile when the user does not yet have a brand system.
---

# Carousel Builder

Create production-ready carousel assets from structured content while following the user's existing visual identity or a new visual profile created for the project.

## Help, installation, and usage

Treat `/skill/help` as a skill-level help request. It is a prompt convention, not a native ChatGPT or Codex slash command.

When the user writes `/skill/help`, do not generate assets. Read [references/help.md](references/help.md) and return the concise installation and usage guide.

For installation, explain both supported paths:

* **Codex:** install the `skills/carousel-builder` folder from the GitHub repository, then begin a new task.
* **ChatGPT Work:** upload a ZIP whose root contains `SKILL.md`, `assets`, `references`, and `scripts` through Plugins → Skills → Create → Upload.

## Brand profile

Before generating assets, determine which brand mode applies:

1. **Existing brand:** use the supplied logo, palette, fonts, templates, or visual reference.
2. **Brand brief:** create a profile from the user's business, audience, subject, and desired tone.
3. **Guided start:** when the user does not know what to choose, infer a practical starter profile from the carousel subject and explain the design choices in plain language.

For a new profile, read [references/brand-profile.md](references/brand-profile.md). Ask for confirmation before generating final assets when the profile was inferred rather than supplied.

Treat the bundled AIA assets as an optional example only. Read [references/aia-chatgpt-work-example.md](references/aia-chatgpt-work-example.md) only when the user explicitly requests that reference or provides the related assets.

## Inputs

Use these inputs when available:

* `Slides.md`: source content with one or more carousels and slides.
* Brand assets or visual reference: logo, palette, fonts, templates, or previous posts.
* Brand profile: supplied or created during onboarding.
* Output target: Instagram by default unless another channel is requested.

## Select the canvas format

Before generating visual assets, ask the user to choose one format. Do not assume a default.

1. **Vertical Principal:** `1080 x 1440 px`, ratio `3:4`.
2. **Vertical Classic:** `1080 x 1350 px`, ratio `4:5`.
3. **Square:** `1080 x 1080 px`, ratio `1:1`.

Use one command value in every generator and validation command: `vertical-principal`, `vertical-classic`, or `square`.

## Workflow

### 1. Parse content

Use `Carousel` and `Slide` headings:

```markdown
# Carousel 1
## Slide 1
```

```bash
python scripts/parse_slides.py Slides.md \
  --output-json parsed-slides.json \
  --scaffold "Social Media/Instagram/Carousel Series" \
  --create-descriptions
```

Stop and fix parser errors before generation. Review warnings before continuing.

### 2. Generate assets

Use the selected format. Example:

```bash
python scripts/generate_carousel_pngs.py \
  --parsed-json parsed-slides.json \
  --output-root "Social Media/Instagram/Carousel Series" \
  --format vertical-principal \
  --output-json generation-report.json
```

The generator creates PNG slides and `Description.md`. For HTML/CSS previews, use `scripts/generate_carousel_assets.js` with the same `--format` value.

Keep text within safe margins. Avoid tiny type, crowded blocks, clipped logos, and low contrast.

### 3. Create Markdown descriptions

Use one `Description.md` per carousel as the sole canonical caption source. Include a suggested caption, five hashtags unless another count is requested, and an optional publishing note.

Do not create Word documents.

### 4. Validate

```bash
python scripts/validate_carousel_output.py \
  "Social Media/Instagram/Carousel Series" \
  --parsed-json parsed-slides.json \
  --format vertical-principal \
  --output-json validation-report.json
```

Confirm the selected dimensions, expected PNG files, filename order, and `Description.md` presence. Create and inspect a contact sheet before delivery when visual QA matters.

## Delivery

Summarize the created files, selected canvas format, brand mode, and any assumptions requiring user review.
