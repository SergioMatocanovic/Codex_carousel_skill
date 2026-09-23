# Optional AIA ChatGPT Work Example

Use this reference only when the user explicitly requests the **AIA ChatGPT Work Series** style or provides its related assets. It is an example, not the default identity for Carousel Builder.

## Source assets

Official reference carousel:

`assets/instagram/serie-chatgpt-work/reference-carousel-1/`

Logo asset:

`assets/instagram/serie-chatgpt-work/logo/aia-platform-logo.png`

Extracted right-side symbol panel:

`assets/instagram/serie-chatgpt-work/extracted/right-symbol-panel.png`

Use the seven reference slides as the visual source of truth. Do not reinterpret the style unless the user explicitly asks to evolve the design system.

## Output convention

```text
Social Media/
  Instagram/
    ChatGPT Work Series/
      Carousel 1/
        slides/
          slide-01.png
          slide-02.png
        Description.md
      Carousel 2/
        slides/
          slide-01.png
          slide-02.png
        Description.md
```

Use `Carousel 1`, `Carousel 2`, `Carousel 3`, and so on. `Description.md` is the only editable caption source. Do not create Word documents.

## Canvas formats

Ask the user to choose one format before creating output. Use that format consistently for generation and validation.

| Command value | Format | Size | Ratio |
| --- | --- | --- | --- |
| `vertical-principal` | Vertical Principal | 1080 x 1440 px | 3:4 |
| `vertical-classic` | Vertical Classic | 1080 x 1350 px | 4:5 |
| `square` | Square | 1080 x 1080 px | 1:1 |

Vertical Principal is the recommended choice because it gives the content more screen coverage.

## Brand elements

* Series label: `SERIES` or `SÉRIE` in white and `CHATGPT WORK` in cyan or green.
* Part label: top-right, such as `Part 1/4`.
* Progress indicator: four rounded rectangles centered near the top.
* Footer: Plataforma AIA logo at the lower left on internal slides.
* Handle: `@sergiomatocanovic` in muted gray near the footer.
* Navigation arrow: cyan arrow inside a cyan outlined circle at the lower right.

## Visual style

* Use a dark navy or black background with a subtle vignette, cyan glow, and faint tech texture.
* Use high contrast white body text with cyan or aqua for emphasis.
* Use magenta or pink only as a secondary accent.
* Keep the large cyan AI symbol on the right when it supports the slide.
* Keep all text inside safe margins and avoid tiny explanatory paragraphs.

## Slide roles

**Slide 1:** strong headline and a CTA hint.

**Slides 2, 3, 5, and 6:** headline or subheadline with checklists, icon rows, quote boxes, or short contrast blocks.

**Slide 4:** engagement CTA using like, share, and save actions.

**Slide 7:** next-part CTA and follow prompt.

## Description file

`Description.md` should use this structure:

```markdown
# Carousel X - Title

## Caption

caption text

## Hashtags

#hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5

## Notes

optional publishing note
```

Generate the first caption with `scripts/description_generator.py`. Keep it direct, practical, and easy to revise before publishing.

## Validation

Confirm that all expected slide PNGs exist, match the selected dimensions, sort in reading order, and have a matching `Description.md`. Review the contact sheet for visual identity, logo placement, progress indicators, and text clipping.
