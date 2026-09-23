#!/usr/bin/env node
/* Generate Instagram carousel HTML and PNG assets from parsed-slides.json. */

const fs = require("fs");
const path = require("path");

const SIZE = 1254;
const DEFAULT_HASHTAGS =
  "#chatgpt #inteligenciaartificial #chatgptwork #plataformaaia #produtividade";

function parseArgs(argv) {
  const args = {
    parsedJson: null,
    outputRoot: null,
    htmlOnly: false,
    limitCarousel: null,
  };

  for (let index = 2; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--parsed-json") {
      args.parsedJson = argv[++index];
    } else if (arg === "--output-root") {
      args.outputRoot = argv[++index];
    } else if (arg === "--html-only") {
      args.htmlOnly = true;
    } else if (arg === "--carousel") {
      args.limitCarousel = Number(argv[++index]);
    } else if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }

  if (!args.parsedJson) {
    throw new Error("Missing required --parsed-json argument");
  }
  if (!args.outputRoot) {
    throw new Error("Missing required --output-root argument");
  }
  return args;
}

function printHelp() {
  console.log(`Usage:
node scripts/generate_carousel_assets.js \\
  --parsed-json parsed-slides.json \\
  --output-root "Redes Sociais/Instagram/Serie ChatGPT Work"

Options:
  --html-only       Generate slide HTML without rendering PNG screenshots.
  --carousel N      Generate only one carousel number.
`);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function assetDataUrl(relativePath) {
  const assetPath = path.resolve(__dirname, "..", relativePath);
  const bytes = fs.readFileSync(assetPath);
  const ext = path.extname(assetPath).slice(1).toLowerCase() || "png";
  return `data:image/${ext};base64,${bytes.toString("base64")}`;
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function firstContentLine(slide) {
  return slide.content_lines?.[0] || "";
}

function contentWithoutSeriesLine(slide) {
  const lines = slide.content_lines || [];
  if (lines[0] && /^S[eé]rie\s+ChatGPT Work/i.test(lines[0])) {
    return lines.slice(1);
  }
  return lines;
}

function highlightText(text) {
  const escaped = escapeHtml(text);
  return escaped.replace(
    /(ChatGPT Work|ChatGPT|Claude Cowork|Claude|AIA|funcion[aá]rio|delegar|trabalho|mudou|chatbot|sair na frente|respostas?|pergunta|Google|Docker|VS|5 tipos)/gi,
    '<span class="accent">$1</span>',
  );
}

function iconForLine(line, fallbackIndex = 0) {
  const trimmed = line.trim();
  if (trimmed.startsWith("❤️")) return "♡";
  if (trimmed.startsWith("📤")) return "↗";
  if (trimmed.startsWith("📌")) return "⌑";
  if (trimmed.startsWith("📄")) return "▤";
  if (trimmed.startsWith("💻")) return "</>";
  if (trimmed.startsWith("📊")) return "▦";
  if (trimmed.startsWith("✍️")) return "✎";
  if (trimmed.startsWith("❌")) return "×";
  if (trimmed.startsWith("✅")) return "✓";
  if (trimmed.startsWith("👉") || trimmed.startsWith("👇")) return "→";
  return ["?", "☰", "</>", "✎", "⚙", "✓"][fallbackIndex % 6];
}

function cleanLine(line) {
  return line
    .replace(/^[✅✔]\s*/u, "")
    .replace(/^[❤️📤📌📄💻📊]\s*/u, "")
    .replace(/^✍️\s*/u, "")
    .replace(/^[❌👉👇]\s*/u, "")
    .trim();
}

function header(carouselNumber) {
  const bars = [1, 2, 3, 4]
    .map((part) => `<span class="bar ${part === carouselNumber ? "active" : ""}"></span>`)
    .join("");
  return `
    <div class="header">
      <div class="series"><span>SÉRIE</span> <strong>CHATGPT WORK</strong></div>
      <div class="progress">${bars}</div>
      <div class="part">Parte ${carouselNumber}/4</div>
    </div>
  `;
}

function footer(logoDataUrl, withLogo = true) {
  return `
    <div class="footer">
      <div class="footer-left">
        ${withLogo ? `<img class="aia-logo" src="${logoDataUrl}" alt="Plataforma AIA" />` : ""}
        <span class="divider"></span>
        <span class="handle">@sergiomatocanovic</span>
      </div>
      <div class="next-arrow">→</div>
    </div>
  `;
}

function aiMark() {
  return `
    <div class="ai-mark" aria-hidden="true">
      <div class="loop loop-a"></div>
      <div class="loop loop-b"></div>
      <div class="loop loop-c"></div>
      <div class="core"></div>
    </div>
  `;
}

function renderCover(lines) {
  const body = lines.filter((line) => line.trim());
  const headline = body.slice(0, -1);
  const finalLine = body.at(-1) || "";
  return `
    <main class="cover-main">
      <div class="cover-title">
        ${headline.map((line) => `<div>${highlightText(line)}</div>`).join("")}
      </div>
      <div class="cyan-rule"></div>
      <div class="cover-final">${highlightText(finalLine)}</div>
      <div class="cover-cta"><span class="circle">→</span><span>Descubra por quê</span><span>→</span></div>
    </main>
  `;
}

function renderCta(lines) {
  const items = lines.filter((line) => /^[❤️📤📌]/u.test(line.trim()));
  return `
    <main class="cta-main">
      ${items
        .map(
          (line, index) => `
          <div class="cta-row">
            <div class="icon neon-${index}">${iconForLine(line, index)}</div>
            <div class="vertical-line"></div>
            <div class="cta-text">${highlightText(cleanLine(line))}</div>
          </div>
        `,
        )
        .join("")}
    </main>
  `;
}

function renderQuoteSlide(lines) {
  const blocks = [];
  let currentLabel = "";
  for (const line of lines) {
    if (!line.trim()) continue;
    if (/^(Agora|Antes|✅ Agora|❌ Antes|A pergunta deixou|Qual|")/i.test(line.trim())) {
      blocks.push(line);
    } else {
      blocks.push(line);
    }
  }
  return `
    <main class="quote-main">
      ${blocks
        .map((line) => {
          const clean = cleanLine(line);
          const isQuote = clean.includes('"');
          const isBad = line.includes("❌") || clean.includes("prompt") || clean.includes("Explique") || clean.includes("resumo");
          const cls = isQuote ? `quote-box ${isBad ? "bad" : "good"}` : "quote-label";
          return `<div class="${cls}">${highlightText(clean)}</div>`;
        })
        .join("")}
    </main>
  `;
}

function renderListSlide(lines) {
  const titleLines = [];
  const items = [];
  for (const line of lines) {
    if (/^[✅✔]/u.test(line.trim())) {
      items.push(cleanLine(line));
    } else if (line.trim()) {
      titleLines.push(line.trim());
    }
  }

  return `
    <main class="content-main">
      <section class="left-copy">
        <div class="content-title">
          ${titleLines.slice(0, 4).map((line) => `<div>${highlightText(cleanLine(line))}</div>`).join("")}
        </div>
        <div class="cyan-rule"></div>
        <div class="check-list">
          ${items
            .map(
              (item, index) => `
                <div class="check-row">
                  <span class="round-icon">${iconForLine(item, index)}</span>
                  <span class="check-dot">✓</span>
                  <span>${highlightText(item)}</span>
                </div>
              `,
            )
            .join("")}
        </div>
      </section>
    </main>
  `;
}

function renderTextSlide(lines, slideNumber) {
  const body = lines.filter((line) => line.trim());
  if (body.some((line) => line.includes('"'))) {
    return renderQuoteSlide(body);
  }
  if (body.some((line) => /^[✅✔]/u.test(line.trim()))) {
    return renderListSlide(body);
  }
  const big = slideNumber === 7 ? " next-title" : "";
  return `
    <main class="text-main${big}">
      ${body
        .map((line, index) => {
          const cls = index === 0 ? "lead-line" : "body-line";
          return `<div class="${cls}">${highlightText(cleanLine(line))}</div>`;
        })
        .join("")}
    </main>
  `;
}

function renderSlide(carousel, slide, logoDataUrl) {
  const lines = contentWithoutSeriesLine(slide);
  const slideNumber = slide.number;
  const isCover = slideNumber === 1;
  const isCta = slideNumber === 4 && lines.some((line) => /^[❤️📤📌]/u.test(line.trim()));
  const content = isCover
    ? renderCover(lines)
    : isCta
      ? renderCta(lines)
      : renderTextSlide(lines, slideNumber);

  return `<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=${SIZE}, initial-scale=1" />
  <title>Carrossel ${carousel.number} - Slide ${slide.number}</title>
  <style>${css()}</style>
</head>
<body>
  <section class="slide">
    <div class="dot-grid"></div>
    ${header(carousel.number)}
    ${aiMark()}
    ${content}
    ${footer(logoDataUrl, !isCover)}
  </section>
</body>
</html>`;
}

function css() {
  return `
    * { box-sizing: border-box; }
    body {
      margin: 0;
      width: ${SIZE}px;
      height: ${SIZE}px;
      overflow: hidden;
      font-family: Inter, Arial, Helvetica, sans-serif;
      background: #020713;
    }
    .slide {
      position: relative;
      width: ${SIZE}px;
      height: ${SIZE}px;
      overflow: hidden;
      color: #f7f9ff;
      background:
        radial-gradient(circle at 78% 73%, rgba(0, 217, 255, 0.32), transparent 26%),
        radial-gradient(circle at 20% 20%, rgba(0, 255, 204, 0.12), transparent 30%),
        linear-gradient(135deg, #020714 0%, #031224 52%, #06101d 100%);
    }
    .slide::before {
      content: "";
      position: absolute;
      inset: 0;
      box-shadow: inset 0 0 120px rgba(0,0,0,.85);
      pointer-events: none;
      z-index: 2;
    }
    .dot-grid {
      position: absolute;
      top: 110px;
      right: 48px;
      width: 530px;
      height: 600px;
      opacity: .42;
      background-image: radial-gradient(circle, rgba(0, 239, 255, .9) 1.2px, transparent 1.4px);
      background-size: 22px 22px;
      mask-image: linear-gradient(to left, black, transparent);
    }
    .header {
      position: absolute;
      z-index: 5;
      top: 38px;
      left: 43px;
      right: 66px;
      display: grid;
      grid-template-columns: 1fr auto 1fr;
      align-items: center;
      font-size: 30px;
      font-weight: 800;
      letter-spacing: .3px;
    }
    .series span { color: #fff; }
    .series strong { color: #00f4ee; margin-left: 12px; }
    .progress { display: flex; gap: 17px; }
    .bar {
      width: 58px;
      height: 30px;
      border-radius: 5px;
      background: linear-gradient(180deg, #313948, #202636);
      box-shadow: inset 0 1px 3px rgba(255,255,255,.12);
    }
    .bar.active {
      background: linear-gradient(90deg, #00efff, #00f2d7);
      box-shadow: 0 0 18px rgba(0,239,255,.3);
    }
    .part {
      justify-self: end;
      color: #fff;
      font-weight: 700;
    }
    .footer {
      position: absolute;
      z-index: 5;
      left: 49px;
      right: 60px;
      bottom: 34px;
      height: 98px;
      border-top: 1px solid rgba(0, 240, 240, .45);
      display: flex;
      align-items: end;
      justify-content: space-between;
      padding-top: 20px;
    }
    .footer-left {
      display: flex;
      align-items: center;
      gap: 36px;
      height: 82px;
    }
    .aia-logo {
      width: 172px;
      max-height: 74px;
      object-fit: contain;
      object-position: left center;
    }
    .divider {
      display: inline-block;
      width: 1px;
      height: 78px;
      background: rgba(0, 239, 255, .42);
    }
    .handle {
      color: rgba(230,235,245,.62);
      font-size: 29px;
      font-weight: 500;
    }
    .next-arrow, .circle {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border: 2px solid #00f4ee;
      color: #00f4ee;
      border-radius: 999px;
      font-size: 54px;
      line-height: 1;
      box-shadow: 0 0 18px rgba(0, 239, 255, .1);
    }
    .next-arrow { width: 78px; height: 78px; }
    .circle { width: 102px; height: 102px; font-size: 58px; }
    .ai-mark {
      position: absolute;
      z-index: 1;
      right: -75px;
      top: 310px;
      width: 555px;
      height: 555px;
      filter: drop-shadow(0 35px 24px rgba(0,0,0,.55));
      opacity: .95;
    }
    .loop {
      position: absolute;
      border: 42px solid #08e8df;
      border-radius: 150px;
      box-shadow:
        inset 0 0 18px rgba(255,255,255,.35),
        0 0 28px rgba(0, 240, 240, .34);
    }
    .loop-a { width: 320px; height: 420px; left: 110px; top: 20px; transform: rotate(45deg); }
    .loop-b { width: 320px; height: 420px; left: 70px; top: 120px; transform: rotate(-15deg); }
    .loop-c { width: 320px; height: 420px; left: 205px; top: 120px; transform: rotate(105deg); }
    .core {
      position: absolute;
      width: 190px;
      height: 190px;
      left: 190px;
      top: 190px;
      border: 30px solid #08e8df;
      border-radius: 36px;
      transform: rotate(45deg);
      box-shadow: inset 0 0 20px rgba(255,255,255,.28), 0 0 28px rgba(0,240,240,.3);
    }
    .accent {
      color: #00f4ee;
      text-shadow: 0 0 14px rgba(0, 240, 240, .18);
    }
    .cyan-rule {
      width: 170px;
      height: 6px;
      background: #00f4ee;
      margin: 34px 0 54px;
      box-shadow: 0 0 14px rgba(0, 240, 240, .35);
    }
    .cover-main {
      position: absolute;
      z-index: 4;
      left: 62px;
      top: 185px;
      width: 760px;
    }
    .cover-title {
      font-size: 102px;
      line-height: 1.04;
      font-weight: 900;
      letter-spacing: -1px;
    }
    .cover-final {
      font-size: 134px;
      line-height: .92;
      font-weight: 950;
      color: #00eefe;
      text-transform: uppercase;
      letter-spacing: -2px;
    }
    .cover-cta {
      display: flex;
      align-items: center;
      gap: 34px;
      margin-top: 35px;
      font-size: 38px;
      font-weight: 800;
    }
    .content-main, .text-main, .quote-main, .cta-main {
      position: absolute;
      z-index: 4;
      left: 74px;
      top: 140px;
      width: 650px;
      min-height: 850px;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }
    .content-title {
      font-size: 60px;
      line-height: 1.12;
      font-weight: 900;
    }
    .check-list {
      display: flex;
      flex-direction: column;
      gap: 18px;
      margin-top: 12px;
      font-size: 32px;
      font-weight: 850;
    }
    .check-row {
      display: grid;
      grid-template-columns: 86px 50px 1fr;
      align-items: center;
      gap: 18px;
      min-height: 74px;
      border-bottom: 1px solid rgba(0, 240, 240, .28);
      padding-bottom: 10px;
    }
    .round-icon {
      width: 68px;
      height: 68px;
      border: 2px solid #00f4ee;
      border-radius: 999px;
      color: #00f4ee;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 29px;
      font-weight: 800;
      text-shadow: 0 0 14px rgba(0, 240, 240, .6);
    }
    .check-dot {
      width: 40px;
      height: 40px;
      border-radius: 999px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: #00f4ee;
      color: #02101b;
      font-size: 27px;
      font-weight: 950;
    }
    .text-main {
      width: 640px;
      top: 170px;
      gap: 28px;
    }
    .text-main.next-title {
      width: 720px;
      justify-content: center;
    }
    .lead-line {
      font-size: 62px;
      line-height: 1.05;
      font-weight: 950;
    }
    .body-line {
      font-size: 56px;
      line-height: 1.13;
      font-weight: 850;
    }
    .quote-main {
      top: 170px;
      gap: 34px;
      justify-content: center;
    }
    .quote-label {
      font-size: 54px;
      line-height: 1.05;
      font-weight: 950;
    }
    .quote-box {
      border: 2px solid #00f4ee;
      border-radius: 18px;
      padding: 32px 38px;
      font-size: 54px;
      line-height: 1.15;
      font-weight: 900;
      box-shadow: 0 0 24px rgba(0, 240, 240, .22);
      background: rgba(2, 8, 22, .56);
    }
    .quote-box.bad {
      border-color: #ff4f7a;
      box-shadow: 0 0 24px rgba(255, 79, 122, .25);
    }
    .cta-main {
      top: 200px;
      width: 700px;
      gap: 92px;
    }
    .cta-row {
      display: grid;
      grid-template-columns: 150px 38px 1fr;
      align-items: center;
      gap: 34px;
    }
    .icon {
      width: 146px;
      height: 146px;
      border: 2px solid #00f4ee;
      border-radius: 999px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-size: 74px;
      text-shadow: 0 0 18px rgba(0, 240, 240, .9);
    }
    .neon-0 { color: #ff4f7a; text-shadow: 0 0 16px rgba(255,79,122,.9); }
    .neon-1 { color: #42ddff; }
    .neon-2 { color: #e852ff; text-shadow: 0 0 16px rgba(232,82,255,.9); }
    .vertical-line {
      width: 3px;
      height: 105px;
      background: #00f4ee;
    }
    .cta-text {
      font-size: 52px;
      line-height: 1.08;
      font-weight: 950;
    }
  `;
}

function descriptionMarkdown(carousel) {
  const cleanLine = (line) => String(line || "")
    .replace(/[✅✔❤️📤📌📄💻📊❌👉👇]/g, "")
    .replace(/✍️/g, "")
    .replace(/—/g, " ")
    .trim();
  const normalizeSentence = (text) => {
    const value = cleanLine(text).replace(/\s+/g, " ").trim();
    if (!value) return value;
    return /[.?!:]$/.test(value) ? value : `${value}.`;
  };
  const contentWithoutSeries = (slide) => {
    const lines = slide.content_lines || [];
    if (lines[0] && /^S[eé]rie\s+ChatGPT Work/i.test(lines[0])) return lines.slice(1);
    return lines;
  };
  const title = normalizeSentence(carousel.title || `Carrossel ${carousel.number}`);
  const firstSlide = (carousel.slides || []).find((slide) => slide.number === 1) || (carousel.slides || [])[0] || {};
  const firstLines = contentWithoutSeries(firstSlide).map(cleanLine).filter(Boolean);
  let ideaText = firstLines.slice(0, 6).join(" ");
  if (ideaText.length > 180) ideaText = firstLines.slice(0, 3).join(" ");
  const idea = normalizeSentence(ideaText || title);
  const pointForSlide = (slide) => {
    const lines = contentWithoutSeries(slide).filter((line) => cleanLine(line));
    if (!lines.length) return "";
    const first = cleanLine(lines[0]);
    const label = first.replace(/[.:]+$/g, "");
    const quote = lines.slice(1).map(cleanLine).find((line) => line.includes('"'));
    const checked = lines.filter((line) => /^[✅✔]/.test(line.trim())).map(cleanLine);
    if (/^(Antes|Agora)$/i.test(first) && quote) return normalizeSentence(`${first}: ${quote.replace(/"/g, "")}`);
    if (checked.length) return normalizeSentence(label ? `${label}: ${checked.slice(0, 3).join(", ")}` : checked.slice(0, 3).join(", "));
    const second = cleanLine(lines[1]);
    if (second.toLowerCase().startsWith("parece") && label) return normalizeSentence(`${label}: ${second}`);
    if (second && first.length < 36) return normalizeSentence(`${first} ${second}`);
    return normalizeSentence(first);
  };
  const points = [];
  for (const slide of carousel.slides || []) {
    if ([1, 4, 7].includes(slide.number)) continue;
    const point = pointForSlide(slide);
    if (point && !points.includes(point)) points.push(point);
    if (points.length >= 4) break;
  }
  const lowerTitle = title.toLowerCase();
  let closing = "Salve para consultar depois e me conta: qual trabalho você já delegaria hoje?";
  if (lowerTitle.includes("vs") || lowerTitle.includes("claude") || lowerTitle.includes("cowork")) {
    closing = "E você: qual dessas ferramentas faz mais sentido para o seu dia a dia?";
  } else if (lowerTitle.includes("tipos de trabalho")) {
    closing = "Salve para consultar depois e escolha um trabalho para delegar ainda esta semana.";
  } else if (lowerTitle.includes("respostas")) {
    closing = "Na próxima vez que abrir o ChatGPT, teste trocar pedido por delegação.";
  }
  const caption = [
    title,
    "",
    `A ideia aqui é simples: ${idea}`,
    "",
    ...(points.length ? ["Neste carrossel:", ...points.map((point) => `- ${point}`), ""] : []),
    closing,
  ];
  return [
    `# Carrossel ${carousel.number} - ${cleanLine(carousel.title)}`,
    "",
    "## Legenda",
    "",
    ...caption,
    "",
    "## Hashtags",
    "",
    DEFAULT_HASHTAGS,
    "",
    "## Observacao",
    "",
    "Legenda gerada automaticamente a partir do Slides.md. Revisar antes de postar se quiser ajustar a voz final.",
    "",
  ].join("\n");
}

async function renderPng(html, outputPath) {
  const { chromium } = require("playwright");
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: SIZE, height: SIZE }, deviceScaleFactor: 1 });
  await page.setContent(html, { waitUntil: "networkidle" });
  await page.screenshot({ path: outputPath, clip: { x: 0, y: 0, width: SIZE, height: SIZE } });
  await browser.close();
}

async function main() {
  const args = parseArgs(process.argv);
  const parsed = JSON.parse(fs.readFileSync(args.parsedJson, "utf8"));
  const logoDataUrl = assetDataUrl("assets/instagram/serie-chatgpt-work/logo/aia-platform-logo.png");
  const report = {
    outputRoot: args.outputRoot,
    htmlOnly: args.htmlOnly,
    generated: [],
  };

  for (const carousel of parsed.carousels || []) {
    if (args.limitCarousel && carousel.number !== args.limitCarousel) {
      continue;
    }
    const carouselDir = path.join(args.outputRoot, `Carrossel ${carousel.number}`);
    const slidesDir = path.join(carouselDir, "slides");
    ensureDir(slidesDir);

    const descriptionPath = path.join(carouselDir, "Descricao.md");
    if (!fs.existsSync(descriptionPath)) {
      fs.writeFileSync(descriptionPath, descriptionMarkdown(carousel), "utf8");
    }

    for (const slide of carousel.slides || []) {
      const html = renderSlide(carousel, slide, logoDataUrl);
      const htmlPath = path.join(slidesDir, `slide-${String(slide.number).padStart(2, "0")}.html`);
      const pngPath = path.join(slidesDir, `slide-${String(slide.number).padStart(2, "0")}.png`);
      fs.writeFileSync(htmlPath, html, "utf8");
      if (!args.htmlOnly) {
        await renderPng(html, pngPath);
      }
      report.generated.push({
        carousel: carousel.number,
        slide: slide.number,
        html: htmlPath,
        png: args.htmlOnly ? null : pngPath,
      });
    }
  }

  console.log(JSON.stringify(report, null, 2));
}

main().catch((error) => {
  console.error(error.stack || error.message || String(error));
  process.exit(1);
});
