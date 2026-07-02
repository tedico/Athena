# tests/test_slots.py
from src import slots


def test_seven_cards_in_order():
    assert [c.number for c in slots.CARDS] == [1, 2, 3, 4, 5, 6, 7]


def test_beat_grammar_matches_spec():
    assert [c.beat for c in slots.CARDS] == [
        "hook", "setup", "punchy", "turn", "insight", "reframe", "cta",
    ]


def test_payload_keys_cover_all_cards():
    # card 1 ← hook, cards 2-6 ← cards[0..4], card 7 ← cta
    assert slots.CARDS[0].payload_key == "hook"
    assert [c.payload_key for c in slots.CARDS[1:6]] == [
        "cards.0", "cards.1", "cards.2", "cards.3", "cards.4",
    ]
    assert slots.CARDS[6].payload_key == "cta"


def test_notion_property_names_exact():
    # exact strings from Ted's existing schema — typos here corrupt real data
    assert slots.PROP_TITLE == "Content (2500 Chars Max)"
    assert slots.PROP_HOOK == "Hook/Headline"
    assert slots.PROP_CARDS == ["Card 1", "Card 2", "Card 3", "Card 4", "Card 5"]
    assert slots.PROP_CTA == "CTA"
    assert slots.PROP_CHARCOUNT_HOOK == "CharCount_Headline (100 Max)"
