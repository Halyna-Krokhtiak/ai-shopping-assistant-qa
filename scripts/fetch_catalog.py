"""Fetch products from DummyJSON and save a trimmed catalog snapshot to data/catalog.json.

Run from the repo root:
    python scripts/fetch_catalog.py
"""

import json
from pathlib import Path

import requests

BASE_URL = "https://dummyjson.com/products/category"
CATEGORIES = ["mens-watches", "sports-accessories"]
FIELDS = [
    "id",
    "title",
    "brand",
    "category",
    "price",
    "stock",
    "availabilityStatus",
    "description",
    "shippingInformation",
]
OUTPUT_PATH = Path("data") / "catalog.json"
TIMEOUT_SECONDS = 10


def fetch_category(category: str) -> list[dict]:
    """Return all products of one category from the API."""
    url = f"{BASE_URL}/{category}"
    response = requests.get(url, params={"limit": 0}, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    data = response.json()
    products = data["products"]
    total = data["total"]
    if len(products) != total:
        raise RuntimeError(f"{category}: got {len(products)} of {total} products")
    return products


def trim_product(product: dict) -> dict:
    """Keep only the fields listed in FIELDS."""
    return {key: product.get(key) for key in FIELDS}


def main() -> None:
    products = []
    for category in CATEGORIES:
        raw_products = fetch_category(category)
        products.extend(trim_product(p) for p in raw_products)

    products = sorted(products, key=lambda p: p["id"])

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Saved {len(products)} products to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
