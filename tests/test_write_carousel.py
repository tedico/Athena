from unittest.mock import MagicMock

import pytest

from src import gates, write_carousel


def good_payload():
    return {
        "paper_page_id": "paper1",
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


def test_gate_failure_writes_nothing(monkeypatch):
    client = MagicMock()
    bad = good_payload()
    bad["hook"] = "x" * 500
    with pytest.raises(gates.GateError):
        write_carousel.run(client, "db2", bad)
    client.pages.create.assert_not_called()
    client.pages.update.assert_not_called()


def test_success_inserts_and_flips_paper_status(monkeypatch):
    client = MagicMock()
    client.pages.create.return_value = {"id": "car1", "url": "https://notion.so/car1"}
    result = write_carousel.run(client, "db2", good_payload())
    assert result["url"] == "https://notion.so/car1"
    client.pages.update.assert_called_once_with(
        page_id="paper1",
        properties={"Status": {"select": {"name": "Written"}}},
    )
