import pytest
from PIL import Image

from src import render


@pytest.mark.browser
def test_renders_seven_pngs_at_exact_dims(tmp_path):
    copy = {
        "hook": "The pigeon in all of us",
        "cards": [
            "Fifty years ago, a psychologist put a pigeon in a box.",
            "The pigeon learned superstition in under a minute.",
            "Reward arrived at random. The pigeon invented rituals.",
            "We do the same thing with luck, streaks, and routines.",
            "Noticing the ritual is the first step out of it.",
        ],
        "cta": "Follow @athena for one useful idea a week.",
    }
    paths = render.render_carousel_copy(copy, tmp_path)
    assert [p.name for p in paths] == [f"card-0{i}.png" for i in range(1, 8)]
    for p in paths:
        assert Image.open(p).size == (1080, 1350)
