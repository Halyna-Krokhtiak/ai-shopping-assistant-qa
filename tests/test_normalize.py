"""Unit tests for the normalize() helper. No LLM, run on every PR.

The helper decides whether a bot test is red or green, so it must be tested too:
a bug here would make every price check lie.
"""

import pytest

from tests.golden import normalize


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("$12,999.99", "$12999.99"),
        ("13 999.99", "13999.99"),
        ("1399999", "1399999"),
        ("OUT OF STOCK", "out of stock"),
        ("out of stock", "out of stock"),
        ("out of stock", "out of stock"),
        ("1,2,3", "1,2,3"),
        ("Rolex, Longines", "rolex, longines"),
        ("rolex$%^&*!@", "rolex$%^&*!@"),
    ],
)
def test_normalize(raw, expected):
    assert normalize(raw) == expected
