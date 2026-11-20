"""Shopping assistant bot: answers customer questions using the product catalog."""

import json
import time
from dataclasses import dataclass
from pathlib import Path

import requests

from bot.config import Settings, load_settings

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = PROJECT_ROOT / "data" / "catalog.json"
PROMPTS_DIR = PROJECT_ROOT / "bot" / "prompts"
CATALOG_PLACEHOLDER = "{{CATALOG}}"


@dataclass(frozen=True)
class BotResponse:
    """Bot answer plus metadata used by latency, cost and stability tests."""

    text: str
    model: str
    prompt_version: str
    latency_s: float
    prompt_tokens: int
    completion_tokens: int
    done_reason: str


def load_catalog() -> list[dict]:
    """Read the product catalog from data/catalog.json."""
    with open(CATALOG_PATH, encoding="utf-8") as f:
        return json.load(f)


def build_system_prompt(prompt_version: str) -> str:
    """Load the prompt template for the given version and insert the catalog."""
    path = PROMPTS_DIR / f"{prompt_version}.md"
    template = path.read_text(encoding="utf-8")
    catalog_json = json.dumps(load_catalog(), ensure_ascii=False)
    return template.replace(CATALOG_PLACEHOLDER, catalog_json)


def ask(question: str, settings: Settings | None = None) -> BotResponse:
    """Send one customer question to the model and return the answer with metadata."""
    settings = settings or load_settings()

    payload = {
        "model": settings.model,
        "messages": [
            {"role": "system", "content": build_system_prompt(settings.prompt_version)},
            {"role": "user", "content": question},
        ],
        "stream": False,
        "options": {
            "temperature": settings.temperature,
            "num_predict": settings.num_predict,
        },
    }

    start = time.perf_counter()
    response = requests.post(
        f"{settings.ollama_url}/api/chat",
        json=payload,
        timeout=settings.request_timeout,
    )
    response.raise_for_status()
    latency = time.perf_counter() - start
    data = response.json()

    return BotResponse(
        text=data["message"]["content"],
        model=settings.model,
        prompt_version=settings.prompt_version,
        latency_s=latency,
        prompt_tokens=data.get("prompt_eval_count", 0),
        completion_tokens=data.get("eval_count", 0),
        done_reason=data.get("done_reason", ""),
    )


def main() -> None:
    """Tiny manual chat loop for exploratory testing. Type 'exit' to quit."""
    settings = load_settings()
    print(f"Model: {settings.model} | prompt: {settings.prompt_version}")
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue
        resp = ask(question, settings)
        print(f"\nBot: {resp.text}")
        print(
            f"[latency: {resp.latency_s:.2f}s | "
            f"tokens: {resp.prompt_tokens} prompt + {resp.completion_tokens} completion | "
            f"done_reason: {resp.done_reason}]"
        )


if __name__ == "__main__":
    main()
