"""Ask the real bot every golden case and check the answer.

Slow: calls the LLM, needs Ollama running. Marked `llm`, so it runs
only with `-m llm` or `python scripts/run_llm_tests.py`.
"""

import pytest

from bot.bot import ask
from tests.golden import case_id, load_cases, normalize

CASES = load_cases()
SUBSTRING_CASES = [
    case for case in CASES if case.get("must_contain") or case.get("must_not_contain")
]


@pytest.mark.llm
@pytest.mark.parametrize("case", SUBSTRING_CASES, ids=case_id)
def test_bot_answer_matches_golden_case(case, bot_settings):
    answer = ask(case["question"], bot_settings).text
    normalized = normalize(answer)
    missing = [
        value for value in case.get("must_contain") or [] if normalize(value) not in normalized
    ]
    forbidden = [
        value for value in case.get("must_not_contain") or [] if normalize(value) in normalized
    ]

    # One assert at the end, so a single run reports ALL problems of the case,
    # and the bot answer is in the message, so you can triage without rerunning.
    assert not missing and not forbidden, (
        f"question ({case['language']}): {case['question']}\n"
        f"missing: {missing}\n"
        f"forbidden: {forbidden}\n"
        f"--- bot answer ---\n{answer}"
    )
