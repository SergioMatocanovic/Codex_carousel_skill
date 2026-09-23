# AIA Design System Builder

> Skill para criar e validar carrosseis da Plataforma AIA com uma identidade visual consistente.

O primeiro modulo disponivel e o **Instagram Carousel Builder**. Ele transforma um arquivo `Slides.md` em imagens PNG quadradas, descricoes editaveis e relatorios de validacao.

## O que esta incluido

* `SKILL.md`: instrucoes da skill.
* `assets/`: logo, painel visual e os sete slides de referencia.
* `references/`: especificacao do sistema visual.
* `scripts/`: parser, geracao de PNGs, descricoes, documento DOCX e validacao.

## Requisitos

Use Python 3.10 ou posterior e instale as dependencias:

```bash
python -m pip install -r requirements.txt
```

Para a geracao alternativa em HTML, instale Node.js e as dependencias que o ambiente da sua automacao solicitar.

## Uso basico

Crie um `Slides.md` e execute:

```bash
python scripts/parse_slides.py Slides.md --output-json parsed-slides.json --scaffold "Redes Sociais/Instagram/Serie ChatGPT Work" --create-descriptions
python scripts/generate_carousel_pngs.py --parsed-json parsed-slides.json --output-root "Redes Sociais/Instagram/Serie ChatGPT Work" --output-json generation-report.json
python scripts/validate_carousel_output.py "Redes Sociais/Instagram/Serie ChatGPT Work" --parsed-json parsed-slides.json --output-json validation-report.json
```

Leia `SKILL.md` antes de gerar um carrossel. Ele define o fluxo, os requisitos de qualidade e a estrutura de saida.
