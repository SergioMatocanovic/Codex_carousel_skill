# Carousel Builder Help

## Installation

### Codex

Install the skill from this repository using the path `skills/carousel-builder`. Start a new Codex task after installation so the skill is available.

### ChatGPT Work

Create a ZIP whose root contains `SKILL.md`, `references`, `scripts`, and `requirements.txt`. In ChatGPT Work, open **Plugins → Skills → Create → Upload** and upload the ZIP. Install the scanned skill from the Skills page.

## Usage

Start with either a theme in the conversation or your own `Slides.md` file.

If you provide only a theme, the skill proposes the slide sequence and creates a `Slides.md` working file after you approve the content direction. You do not need to know Markdown to start.

`Slides.md` is optional. It is simply a Markdown screenplay for people who want to control the exact slide order and copy. It uses headings such as `# Carousel 1` and `## Slide 1`. See [examples/Slides.example.md](../examples/Slides.example.md) for a complete seven-slide example.

Choose a brand mode first: provide an existing visual reference, describe a brand brief, or ask the skill to create a starter profile and confirm it before final generation.

The skill creates a unique visual plan for the subject rather than reusing a fixed template. When available, use ChatGPT Images to make text-free source imagery from that plan. The final carousel text is composed separately for accuracy.

Choose one canvas format before generation:

1. Vertical Principal: `1080 x 1440 px`, `3:4`.
2. Vertical Classic: `1080 x 1350 px`, `4:5`.
3. Square: `1080 x 1080 px`, `1:1`.

The output includes sortable PNG slides and a `Description.md` caption file for each carousel. The workflow does not create Word documents.

The project root also contains `historico.md`, which records each carousel's date, theme, slide count, and status. Corrections always update the existing carousel folder and its history entry.

## Example request

```text
Create a starter brand profile for my financial education audience and make a seven-slide Instagram carousel about building an emergency fund, in Vertical Principal format.
```
