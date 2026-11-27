"""Shared pytest fixtures.

pytest loads conftest.py automatically; fixtures defined here are available
in every test file without an import.
"""

import pytest
import requests

from bot.config import Settings, load_settings


@pytest.fixture(scope="session")
def bot_settings() -> Settings:
    """Settings for the bot under test. Skips LLM tests if Ollama is not running.

    scope="session": the check runs once per pytest run, not once per test.
    """
    settings = load_settings()
    try:
        response = requests.get(f"{settings.ollama_url}/api/tags", timeout=3)
        response.raise_for_status()
    except requests.RequestException as e:
        pytest.skip(f"Ollama is not reachable at {settings.ollama_url}: {e}")
    return settings
