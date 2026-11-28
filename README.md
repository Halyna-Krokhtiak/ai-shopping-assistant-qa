# ai-shopping-assistant-qa
Automated testing of an LLM chatbot for e-commerce: accuracy, hallucinations, security, regression. Python + pytest + Ollama.

[![CI](https://github.com/Halyna-Krokhtiak/ai-shopping-assistant-qa/actions/workflows/ci.yml/badge.svg)](https://github.com/Halyna-Krokhtiak/ai-shopping-assistant-qa/actions/workflows/ci.yml)

## How to run LLM tests

The tests are split by cost:

| Command | What it checks | Needs Ollama | Time |
|---|---|---|---|
| `pytest -m "not llm"` | golden dataset and helper code | no | < 1 s |
| `python scripts/run_llm_tests.py` | real bot answers against the golden dataset | yes | ~10 min |

### 1. Prepare

```bash
pip install -e ".[dev]"
ollama pull qwen2.5:7b
ollama serve            # skip if Ollama already runs in the background
```

The model, prompt version and Ollama URL come from environment variables or a `.env` file
(`OLLAMA_MODEL`, `PROMPT_VERSION`, `OLLAMA_URL`). Defaults: `qwen2.5:7b`, `v1`, `http://localhost:11434`.

### 2. Run

```bash
python scripts/run_llm_tests.py                 # all LLM cases
python scripts/run_llm_tests.py --lf            # only the cases that failed last time
python scripts/run_llm_tests.py -k comparison   # only cases whose id contains "comparison"
```

Any extra argument is passed to pytest as is.
If Ollama is not reachable, the LLM tests are **skipped** (not failed), and the reason is shown in the report.

### 3. Read the results

Every run saves two files to `reports/`, named by date, time, model and prompt version:

```
reports/2026-11-27_1205_qwen2.5-7b_v1.txt   # console output (UTF-8), for people
reports/2026-11-27_1205_qwen2.5-7b_v1.xml   # JUnit XML, for CI tools
```

Each failure shows the question, the expected values that are missing, the forbidden values that were found, and the full bot answer, so a failure can be triaged without rerunning it.

The exit code is the same as pytest's: `0` means all passed, `1` means at least one case failed.

> A red LLM test is a question, not a verdict. Before filing a bug, check the answer against
> `data/catalog.json` (facts) and `bot/prompts/v1.md` (expected behaviour). Confirmed bugs go to the bug register.

