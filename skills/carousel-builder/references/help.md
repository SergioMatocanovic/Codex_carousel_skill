# Carousel Builder Help

## Installation

### Codex

Install the skill from this repository using the path `skills/carousel-builder`. Start a new Codex task after installation so the skill is available.

### ChatGPT Work

Create a ZIP whose root contains `SKILL.md`, `assets`, `references`, `scripts`, and `requirements.txt`. In ChatGPT Work, open **Plugins → Skills → Create → Upload** and upload the ZIP. Install the scanned skill from the Skills page.

## Usage

Provide a `Slides.md` file with headings such as `# Carousel 1` and `## Slide 1`.

Choose a brand mode first: provide an existing visual reference, describe a brand brief, or ask the skill to create a starter profile and confirm it before final generation.

Choose one canvas format before generation:

1. Vertical Principal: `1080 x 1440 px`, `3:4`.
2. Vertical Classic: `1080 x 1350 px`, `4:5`.
3. Square: `1080 x 1080 px`, `1:1`.

The output includes sortable PNG slides and a `Description.md` caption file for each carousel. The workflow does not create Word documents.

## Example request

```text
Create a starter brand profile for my financial education audience, then use this Slides.md to generate an Instagram carousel in Vertical Principal format.
```
