"""Shared helpers for tests that use the golden dataset.

Imported by test_golden_dataset.py and test_bot_golden.py, so the loading
logic lives in one place.
"""

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CASES_PATH = ROOT / "data" / "golden" / "cases.yaml"
CATALOG_PATH = ROOT / "data" / "catalog.json"


def load_cases() -> list[dict]:
    """Read cases.yaml and return the list of cases."""
    with open(CASES_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def load_catalog_by_id() -> dict[int, dict]:
    """Read catalog.json and return {product_id: product}."""
    with open(CATALOG_PATH, encoding="utf-8") as f:
        products = json.load(f)
    return {product["id"]: product for product in products}


def case_id(case: dict) -> str:
    """Readable test name in pytest output, e.g. test_x[price-001]."""
    return case.get("id", "<missing id>")


# A comma or space between digits, followed by exactly 3 digits: a thousands separator.
# "12,999.99" -> "12999.99", "13 999.99" -> "13999.99", but "1,5" and "3, 4" stay as they are.
THOUSANDS_SEPARATOR = re.compile(r"(?<=\d)[,\s](?=\d{3}(?!\d))")


def normalize(text: str) -> str:
    """Prepare text for substring checks: lowercase and no thousands separators."""
    return THOUSANDS_SEPARATOR.sub("", text).lower()
