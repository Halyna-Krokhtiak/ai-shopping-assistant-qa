# Progress Log

A running log of what has been done on this project and what comes next.
Newest entries go on top.

---

## 2026-11-16

### Done

- **Environment:** set up the local environment for running and testing LLMs locally.
- **Ollama and models:** installed Ollama and pulled `qwen2.5:7b` and `llama3.2:3b`; both are queried through the CLI and the HTTP API.
- **Research session:** ran a baseline session with shopping queries ("Порадь недорогий смартфон", "Який смартфон із гарною камерою ти порадиш до 10 тисяч гривень?", "can you advise the cheapest smartphone with storage 500gb", "¿Podrías recomendarme el smartphone más barato con 500 GB de almacenamiento?") in Ukrainian, English and Spanish: 6 baseline runs + 3 follow-ups (2 models × 3 languages), 6 of 6 answers with at least one defect. Key findings:
  - **Language:** `qwen2.5:7b` answered a Ukrainian question in Russian; after "answer in Ukrainian" it switched, but with Russianisms. `llama3.2:3b` Ukrainian is low quality (malformed words, mixed scripts).
  - **Knowledge cutoff:** 2021 models suggested.
  - **Hallucinated specs:** both models invent 512 GB variants for phones that max out at 256 GB; `llama3.2:3b` claims all 5 phones have 512 GB (EN) or exactly "500 GB" (ES), names a non-existent model ("Redmi Note 11 Pro Max") and wrong processors.
  - **Ignored constraints:** prices missing or invented, budget ignored; `qwen2.5:7b` (ES) drifts to 128 GB phones.
  - **Reasoning:** `qwen2.5:7b` (EN) calls 512 GB "the closest without exceeding 500".
  - **Stability:** `llama3.2:3b` loops endlessly in the CLI (UA) and gives different answers on two API runs at `temperature=0`.
  - **Formatting:** broken markdown (`** X**`) in `qwen2.5:7b` output.
  - **Speed:** `qwen2.5:7b` 41–59 s per answer (~7–8 tok/s); `llama3.2:3b` 21–34 s, roughly 2× faster (up to 16 tok/s).
- **Repository skeleton:** created the initial structure:

  ```
  ai-shopping-assistant-qa/
  ├── bot/
  ├── data/golden/
  ├── scripts/
  ├── tests/
  ├── reports/
  └── .github/workflows/
  ```

### Next

- [ ] Write up the exploratory session in `docs/exploratory/2026-11-16-baseline-session.md` (queries, findings, evidence).
- [ ] Add `pyproject.toml` with dependencies and ruff config; add `bot/config.py` (model, prompt version, Ollama URL via env variables).
- [ ] Add `scripts/fetch_catalog.py` to save 20–30 products from DummyJSON to `data/catalog.json`.
- [ ] Build `bot/bot.py` with system prompt `bot/prompts/v1.md`: answers only from the catalog, in the user's language.
- [ ] Create the golden dataset in `data/golden/` (30+ cases: question, language, constraints, expected facts), based on today's findings.
- [ ] Write the first tests for accuracy and hallucinations against the bot.
- [ ] Add a GitHub Actions workflow that runs ruff on every PR.