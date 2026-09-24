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
* **ChatGPT Work:** upload a ZIP whose root contains `SKILL.md`, `references`, `scripts`, and `requirements.txt` through Plugins → Skills → Create → Upload.

## Brand profile

Before generating assets, determine which brand mode applies:

1. **Existing brand:** use the supplied logo, palette, fonts, templates, or visual reference.
2. **Brand brief:** create a profile from the user's business, audience, subject, and desired tone.
3. **Guided start:** when the user does not know what to choose, infer a practical starter profile from the carousel subject and explain the design choices in plain language.

For a new profile, read [references/brand-profile.md](references/brand-profile.md). Ask for confirmation before generating final assets when the profile was inferred rather than supplied.

## Autonomous visual direction

Do not reuse a fixed visual template. Create a topic-specific `visual-plan.json` using the current brand profile, audience, theme, and canvas format. Read [references/visual-direction.md](references/visual-direction.md) for its compact schema.

Choose which slides need generated imagery and write a specific `image_prompt` for each of them. The prompt must request a text-free source image, with no logo, watermark, UI, border, or typography. Use the generated image as visual material only; place the exact editorial copy with the compositor.

In ChatGPT Work, use ChatGPT Images 2.5 when the workspace makes image generation available in the conversation. This workflow does not require an API key, API configuration, or separate API billing. If image generation is unavailable, create a typography-led carousel from the visual plan and state that limitation.

## Inputs

Use these inputs when available:

* `Slides.md`: source content with one or more carousels and slides.
* Brand assets or visual reference: logo, palette, fonts, templates, or previous posts.
* Brand profile: supplied or created during onboarding.
* Output target: Instagram by default unless another channel is requested.

## Output hierarchy and revisions

Use one output root for the project. Its root contains `historico.md`; every carousel has its own `Carousel N` directory with `Description.md`, `slides/`, and `generated-images/`.

`historico.md` must record the carousel number, creation date, last update, theme, slide count, and status. The compositor maintains this file when a carousel is created or revised.

When the user asks to correct or alter a carousel, identify its existing number from `historico.md` or the project folders. Use `--mode revise --carousel N`. Update `Description.md`, final slides, generated source images, and the existing history entry inside that same `Carousel N` directory. Never create another carousel directory for a revision. If the specified carousel does not exist, stop and ask the user whether they want a new carousel.

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
  --output-json parsed-slides.json
```

Stop and fix parser errors before generation. Review warnings before continuing.

### 2. Plan and generate the source imagery

Create `visual-plan.json`, then generate image prompts:

```bash
python scripts/create_image_prompts.py \
  --parsed-json parsed-slides.json \
  --visual-plan visual-plan.json \
  --output image-prompts.md
```

Use ChatGPT Images to create the selected text-free images. Save them in `generated-images/` using the names in `image-prompts.md`. Do not generate images for every slide just to fill space: use typography-only slides where they communicate more clearly.

### 3. Compose the final assets

Use the selected format. Example:

```bash
python scripts/compose_theme_carousel.py \
  --parsed-json parsed-slides.json \
  --visual-plan visual-plan.json \
  --image-dir generated-images \
  --output-root "Social Media/Instagram/Carousel Series" \
  --mode create \
  --format vertical-principal \
  --output-json generation-report.json
```

The compositor creates PNG slides and `Description.md`. It can also generate a clean typography-led fallback when no source image is present.

Keep text within safe margins. Avoid tiny type, crowded blocks, clipped logos, and low contrast.

For a correction, pass `--mode revise --carousel N`. This replaces only the contents of the existing `Carousel N` folder and updates its row in `historico.md`; it never creates a new carousel for a revision.

### 4. Create Markdown descriptions

Use one `Description.md` per carousel as the sole canonical caption source. Include a suggested caption, five hashtags unless another count is requested, and an optional publishing note.

Do not create Word documents.

### 5. Validate

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
