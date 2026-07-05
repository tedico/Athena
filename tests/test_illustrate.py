"""Tests for the illustration engine (no API calls — pure functions only)."""
import pytest
from PIL import Image

from src.illustrate import (
    INK_HEX,
    IllustrationError,
    build_prompt,
    make_transparent,
    transparent_from_file,
)


def test_prompt_swaps_subject_only():
    prompt = build_prompt("a moth drawn toward a candle flame")
    assert "a moth drawn toward a candle flame" in prompt
    assert prompt.startswith("Detailed black-and-white pen-and-ink illustration")
    assert "No signature" in prompt  # anti-"A. Moreau" clause must stay


def test_prompt_rejects_empty_subject():
    with pytest.raises(IllustrationError):
        build_prompt("   ")


def test_white_becomes_fully_transparent():
    white = Image.new("RGB", (4, 4), (255, 255, 255))
    out = make_transparent(white)
    assert out.mode == "RGBA"
    assert all(px[3] == 0 for px in out.getdata())


def test_black_ink_becomes_opaque_brand_ink():
    black = Image.new("RGB", (4, 4), (0, 0, 0))
    out = make_transparent(black)
    ink = tuple(int(INK_HEX.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
    assert all(px == ink + (255,) for px in out.getdata())


def test_midtone_maps_to_translucent_ink():
    gray = Image.new("RGB", (1, 1), (128, 128, 128))
    px = make_transparent(gray).getdata()[0]
    assert 100 < px[3] < 155  # roughly half-transparent


def test_paper_noise_clamps_to_zero_alpha():
    near_white = Image.new("RGB", (1, 1), (250, 250, 250))
    assert make_transparent(near_white).getdata()[0][3] == 0


def test_rerun_on_transparent_art_is_stable():
    art = Image.new("RGBA", (1, 1), (36, 32, 26, 200))
    px = make_transparent(art).getdata()[0]
    assert px[3] > 150  # ink survives a second pass instead of vanishing


def test_from_file_roundtrip(tmp_path):
    src = tmp_path / "raw.png"
    Image.new("RGB", (2, 2), (255, 255, 255)).save(src)
    out = transparent_from_file(src, tmp_path / "sub" / "clean.png")
    assert out.exists()
    assert Image.open(out).mode == "RGBA"
