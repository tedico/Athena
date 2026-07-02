"""7-card grammar + exact Notion property names (single source of truth).

Card 6 in the Notion schema is an intentionally unused spare (8 text slots,
7-card format). 'Content (2500 Chars Max)' is the title property = IG caption.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Card:
    number: int
    beat: str        # rhetorical job
    layout: str      # template CSS class
    payload_key: str # where its text lives in the carousel JSON payload


CARDS = (
    Card(1, "hook", "cover", "hook"),
    Card(2, "setup", "calm", "cards.0"),      # artwork layout deferred; calm fallback
    Card(3, "punchy", "punchy", "cards.1"),
    Card(4, "turn", "turn", "cards.2"),       # coral accent
    Card(5, "insight", "insight", "cards.3"), # columbia blue accent
    Card(6, "reframe", "calm-night", "cards.4"),
    Card(7, "cta", "cta", "cta"),
)

# --- Carousels DB property names (exact strings from the live schema) ---
PROP_TITLE = "Content (2500 Chars Max)"
PROP_HOOK = "Hook/Headline"
PROP_CARDS = ["Card 1", "Card 2", "Card 3", "Card 4", "Card 5"]
PROP_CTA = "CTA"
PROP_CHARCOUNT_HOOK = "CharCount_Headline (100 Max)"
PROP_CHARCOUNT_CARDS = [f"CharCount_Card{i}" for i in range(1, 6)]
PROP_CHARCOUNT_CTA = "CharCount_CTA"
PROP_CHARCOUNT_TITLE = "CharCount_Content"
PROP_INPUT_TYPE = "InputType"       # select → "Consensus"
PROP_VARIANT = "Variant"            # multi_select → ["Consensus_Psychology"]
PROP_STATUS = "Status"              # select (added in Task 1)
PROP_PAPER_RELATION = "Paper"       # relation (added in Task 1)

# --- Papers DB property names ---
PAPER_TITLE = "Title"
PAPER_AUTHORS = "Authors"
PAPER_YEAR = "Year"
PAPER_JOURNAL = "Journal"
PAPER_URL = "DOI/URL"
PAPER_FINDING = "Key Finding"
PAPER_WHY = "Why it matters"
PAPER_REASON = "Selection Reason"
PAPER_STATUS = "Status"
