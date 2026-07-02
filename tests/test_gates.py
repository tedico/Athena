import pytest

from src import gates


def good_payload():
    return {
        "paper_page_id": "abc123",
        "caption": "A caption that is comfortably over the fifty character minimum for captions.",
        "hook": "The pigeon in all of us",
        "cards": [
            "Card two text that is long enough to pass the gate.",
            "Card three text that is long enough to pass the gate.",
            "Card four text that is long enough to pass the gate.",
            "Card five text that is long enough to pass the gate.",
            "Card six text that is long enough to pass the gate.",
        ],
        "cta": "Follow @athena for one useful idea a week.",
    }


def test_good_payload_passes():
    gates.validate_carousel(good_payload())  # no raise


def test_hook_over_100_fails():
    p = good_payload()
    p["hook"] = "x" * 101
    with pytest.raises(gates.GateError, match="hook"):
        gates.validate_carousel(p)


def test_card_over_280_fails():
    p = good_payload()
    p["cards"][2] = "x" * 281
    with pytest.raises(gates.GateError, match="cards.2"):
        gates.validate_carousel(p)


def test_short_card_fails():
    p = good_payload()
    p["cards"][0] = "too short"
    with pytest.raises(gates.GateError, match="cards.0"):
        gates.validate_carousel(p)


def test_must_have_exactly_five_cards():
    p = good_payload()
    p["cards"] = p["cards"][:4]
    with pytest.raises(gates.GateError, match="exactly 5"):
        gates.validate_carousel(p)


def test_missing_field_fails():
    p = good_payload()
    del p["cta"]
    with pytest.raises(gates.GateError, match="cta"):
        gates.validate_carousel(p)


def test_all_violations_reported_at_once():
    p = good_payload()
    p["hook"] = ""
    p["cta"] = "x" * 999
    with pytest.raises(gates.GateError) as e:
        gates.validate_carousel(p)
    assert "hook" in str(e.value) and "cta" in str(e.value)
