"""Sanity checks for the golden dataset itself.

No LLM calls: these tests read two files and finish in well under a second,
so they run on every PR in CI.
"""

import json
from collections import Counter
from pathlib import Path

import pytest
import yaml

# Path(__file__) is this test file; .parent.parent is the repo root.
# Building paths from the file location (not from the current directory)
# makes the tests work no matter where pytest is started from.
ROOT = Path(__file__).resolve().parent.parent
CASES_PATH = ROOT / "data" / "golden" / "cases.yaml"
CATALOG_PATH = ROOT / "data" / "catalog.json"

MIN_CASES = 30
REQUIRED_FIELDS = {"id", "category", "language", "question"}
ALLOWED_CATEGORIES = {
    "price",
    "availability",
    "brand",
    "not_in_catalog",
    "language",
    "discount",
    "shipping",
    "comparison",
    "out_of_scope",
    "unclear_input",
    "hallucination",
    "store_policy",
}
# None means "language does not matter for this case" (language: null in YAML).
ALLOWED_LANGUAGES = {"en", "uk", "es", "zh", None}
CHECK_FIELDS = ("must_contain", "must_not_contain", "expected_behavior")


def load_cases() -> list[dict]:
    """Read cases.yaml and return the list of cases."""
    with open(CASES_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def load_catalog_by_id() -> dict[int, dict]:
    """Read catalog.json and return {product_id: product}."""
    with open(CATALOG_PATH, encoding="utf-8") as f:
        products = json.load(f)
    return {product["id"]: product for product in products}


# Loaded once at import time, because @pytest.mark.parametrize needs the data
# while pytest is *collecting* tests, before any fixture can run.
CASES = load_cases()
CATALOG = load_catalog_by_id()
PRICE_CASES = [c for c in CASES if c.get("category") == "price"]


def case_id(case: dict) -> str:
    """Readable test name in pytest output, e.g. test_x[price-001]."""
    return case.get("id", "<missing id>")


def price_strings(price: float) -> set[str]:
    """The ways a catalog price may reasonably be written in must_contain.

    str() alone is not enough: str(10.0) == "10.0", but a person (and the bot)
    writes "10" or "10.00". So 10.0 gives {"10.0", "10.00", "10"}.
    """
    variants = {str(price), f"{price:.2f}"}
    if float(price).is_integer():
        variants.add(str(int(price)))
    return variants


# ---------- Dataset-level checks (run once) ----------


def test_dataset_has_enough_cases():
    assert len(CASES) >= MIN_CASES, f"expected at least {MIN_CASES} cases, found {len(CASES)}"


def test_case_ids_are_unique():
    counts = Counter(case.get("id") for case in CASES)
    duplicates = sorted(str(i) for i, n in counts.items() if n > 1)
    assert not duplicates, f"duplicated case ids: {duplicates}"


# ---------- Per-case checks (one test per case) ----------


@pytest.mark.parametrize("case", CASES, ids=case_id)
def test_case_has_required_fields(case):
    missing = REQUIRED_FIELDS - case.keys()
    assert not missing, f"missing required fields: {sorted(missing)}"


@pytest.mark.parametrize("case", CASES, ids=case_id)
def test_case_category_is_allowed(case):
    category = case.get("category")
    assert category in ALLOWED_CATEGORIES, (
        f"unknown category {category!r}; allowed: {sorted(ALLOWED_CATEGORIES)}"
    )


@pytest.mark.parametrize("case", CASES, ids=case_id)
def test_case_id_starts_with_category(case):
    case_id_value = str(case.get("id", ""))
    category = case.get("category")
    assert case_id_value.startswith(f"{category}-"), (
        f"id {case_id_value!r} must start with '{category}-'"
    )


@pytest.mark.parametrize("case", CASES, ids=case_id)
def test_case_language_is_allowed(case):
    language = case.get("language")
    allowed = sorted(str(lang) for lang in ALLOWED_LANGUAGES)
    assert language in ALLOWED_LANGUAGES, f"unknown language {language!r}; allowed: {allowed}"


@pytest.mark.parametrize("case", CASES, ids=case_id)
def test_case_product_ids_exist_in_catalog(case):
    product_ids = case.get("product_ids") or []
    bad = [
        pid
        for pid in product_ids
        if isinstance(pid, bool) or not isinstance(pid, int) or pid not in CATALOG
    ]
    assert not bad, f"product_ids not found in catalog (or not ints): {bad}"


@pytest.mark.parametrize("case", CASES, ids=case_id)
def test_case_has_at_least_one_check(case):
    assert any(case.get(field) for field in CHECK_FIELDS), (
        f"case has no checks; fill at least one of {list(CHECK_FIELDS)}"
    )


@pytest.mark.parametrize("case", PRICE_CASES, ids=case_id)
def test_price_case_matches_catalog(case):
    product_ids = case.get("product_ids") or []
    assert product_ids, "price case must list product_ids"

    catalog_prices = set()
    for pid in product_ids:
        if pid in CATALOG:  # unknown ids are reported by the catalog test above
            catalog_prices |= price_strings(CATALOG[pid]["price"])

    must_contain = [str(v) for v in case.get("must_contain") or []]
    assert catalog_prices & set(must_contain), (
        f"must_contain {must_contain} has no catalog price; "
        f"expected one of {sorted(catalog_prices)}"
    )


@pytest.mark.parametrize("case", CASES, ids=case_id)
def test_golden_case_substring_values_are_strings(case):
    problems = []
    for field in ("must_contain", "must_not_contain"):
        values = case.get(field) or []
        if not isinstance(values, list):
            problems.append(f"{field} must be a list, got {type(values).__name__}: {values!r}")
            continue
        problems += [
            f"{field}[{i}] must be a string, got {type(v).__name__}: {v!r} (quote it in YAML)"
            for i, v in enumerate(values)
            if not isinstance(v, str)
        ]
    assert not problems, "\n".join(problems)
