# Instagram Carousel Design System

Use this reference for the **Serie ChatGPT Work** Instagram carousel module.

## Source Assets

Official reference carousel:

`assets/instagram/serie-chatgpt-work/reference-carousel-1/`

Logo asset:

`assets/instagram/serie-chatgpt-work/logo/aia-platform-logo.png`

Extracted right-side symbol panel:

`assets/instagram/serie-chatgpt-work/extracted/right-symbol-panel.png`

Use the 7 reference slides as the visual source of truth. Do not reinterpret the style unless Sergio explicitly asks to evolve the design system.

## Output Folder Convention

Use this folder structure by default:

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

Use `Carrossel 1`, `Carrossel 2`, `Carrossel 3`, and so on. Keep the folder name in Portuguese for this series. Avoid leading spaces before folder names.

## Canvas

- Size: `1254x1254`.
- Format: PNG.
- Background: dark navy/black, subtle vignette, cyan glow, faint tech texture.
- Main visual anchor: large cyan 3D ChatGPT/OpenAI-like symbol on the right for most slides. Prefer the extracted `right-symbol-panel.png` asset instead of redrawing the symbol.
- Content zone: left side and upper-left/mid-left.
- Footer zone: logo left, handle near bottom center-left, arrow button bottom-right.

## Brand Elements

- Series label: `SERIE` or `SÉRIE` in white, `CHATGPT WORK` in cyan/green.
- Part label: top-right, such as `Parte 1/4`.
- Progress indicator: four rounded rectangles centered near the top; active part in bright cyan, inactive parts in dark gray.
- Footer: Plataforma AIA logo at bottom-left on internal slides.
- Handle: `@sergiomatocanovic` in muted gray near the footer.
- Navigation arrow: cyan arrow inside a cyan outlined circle at bottom-right.

## Visual Style

- Use high contrast: white body text over dark background.
- Use cyan/aqua for key words, section emphasis, progress, arrows, check marks, and dividers.
- Use magenta/pink only as secondary accent for CTA/icons or contrast boxes.
- Use bold, large typography with strong hierarchy.
- Use short text blocks. If the source text is long, preserve meaning but reduce line length.
- Keep safe margins around every edge. Never let text or logo touch the borders.

## Slide Roles

### Slide 1: Cover

- Strong headline.
- Larger typography than internal slides.
- Usually no footer logo block.
- Use a CTA hint at the bottom, such as `Descubra por que`, with arrow styling when appropriate.

### Slides 2, 3, 5, 6: Content

- Use headline/subheadline on the left.
- Use checklists, icon rows, quote boxes, or short contrast blocks depending on content.
- Keep the large cyan symbol on the right when it helps maintain series identity.
- Highlight key phrases in cyan.

### Slide 4: Engagement CTA

Use the series CTA pattern:

- `Curta este post`
- `Compartilhe com um amigo`
- `Salve para consultar depois`

Use large icons on the left and text on the right. Keep the footer and right-side symbol.

### Slide 7: Next-Part CTA

- Announce the next part.
- Use very large typography for the key promise.
- Include a follow CTA, such as `Segue o perfil para nao perder.`

## Text Rules

- Keep Portuguese copy natural and direct.
- Preserve Sergio's tone: technical, clear, practical, warm, and lightly humorous.
- Prefer short statements that fit the visual hierarchy.
- Avoid generic AI hype.
- Avoid tiny explanatory paragraphs.

## Description Files

Create `Descricao.md` as the canonical editable caption file. Generate an initial caption from the carousel title and slide content; do not leave `TODO` placeholders. Use this structure:

```markdown
# Carrossel X - Title

## Legenda

caption text

## Hashtags

#hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5

## Observacao

optional posting note
```

Use `scripts/description_generator.py` for the shared caption-generation logic used by the parser and PNG generator. Keep the generated text direct, practical, and easy to revise before posting.

Create `Descricao.docx` only when the workflow or user requests a document export. Generate it from the Markdown source with:

```bash
python3 scripts/create_description_docx.py \
  "Redes Sociais/Instagram/Serie ChatGPT Work" \
  --parsed-json parsed-slides.json \
  --output-json description-docx-report.json
```

Keep `Descricao.md` as the source of truth. Regenerate `Descricao.docx` after editing the Markdown.

## Validation

Validate every generated carousel:

- all slide PNGs exist;
- every PNG is exactly `1254x1254`;
- filenames are sortable as `slide-01.png`, `slide-02.png`, etc.;
- output folder follows the default convention unless the user provides another target;
- `Descricao.md` exists;
- `Descricao.docx` exists and is a valid DOCX package when requested;
- slide visual style matches the 7 reference slides;
- progress indicator and part label match the carousel number;
- footer, handle, logo, and arrow appear where the reference pattern requires them;
- text is legible, unclipped, and inside safe margins.
