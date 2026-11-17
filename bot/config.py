"""Bot configuration loaded from environment variables.

Priority: real environment variable > value in .env file > default below.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Immutable settings for one bot run."""

    ollama_url: str
    model: str
    temperature: float
    num_predict: int
    prompt_version: str
    request_timeout: int


def _get_number(name: str, default: str, cast: type[int] | type[float]) -> int | float:
    """Read an env variable and convert it to a number, failing with a clear message."""
    raw = os.getenv(name, default)
    try:
        return cast(raw)
    except ValueError:
        raise ValueError(f"{name} must be a {cast.__name__}, got {raw!r}") from None


def load_settings() -> Settings:
    """Build Settings from environment variables, falling back to defaults."""
    return Settings(
        ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
        model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
        temperature=_get_number("TEMPERATURE", "0", float),
        num_predict=_get_number("NUM_PREDICT", "400", int),
        prompt_version=os.getenv("PROMPT_VERSION", "v1"),
        request_timeout=_get_number("REQUEST_TIMEOUT", "120", int),
    )
