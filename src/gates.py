"""Hard char-count gates. Code-enforced, never LLM-trusted (Useful Math lesson).

A payload that fails NEVER reaches Notion. All violations are reported in one
error so the copy can be fixed in a single pass.
"""

BANDS = {
    "hook": (10, 100),
    "card": (20, 280),
    "cta": (10, 200),
    "caption": (50, 2500),
}


class GateError(ValueError):
    pass


def _check(violations, field, text, band):
    lo, hi = BANDS[band]
    n = len(text)
    if not lo <= n <= hi:
        violations.append(f"{field}: {n} chars, band is {lo}-{hi}")


def validate_carousel(payload: dict) -> None:
    violations = []
    for field in ("paper_page_id", "caption", "hook", "cards", "cta"):
        if field not in payload:
            violations.append(f"{field}: missing")
    if violations:
        raise GateError("; ".join(violations))

    cards = payload["cards"]
    if not isinstance(cards, list) or len(cards) != 5:
        raise GateError(f"cards: exactly 5 required, got {len(cards)}")

    _check(violations, "hook", payload["hook"], "hook")
    _check(violations, "caption", payload["caption"], "caption")
    _check(violations, "cta", payload["cta"], "cta")
    for i, text in enumerate(cards):
        _check(violations, f"cards.{i}", text, "card")

    if violations:
        raise GateError("; ".join(violations))
