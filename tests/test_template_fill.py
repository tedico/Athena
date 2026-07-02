import pytest

from src import render


COPY = {
    "hook": "The pigeon in all of us",
    "cards": ["two", "three", "four", "five", "six"],
    "cta": "Follow for more",
}


def test_all_placeholders_replaced():
    html = render.fill_template(render.TEMPLATE_PATH.read_text(), COPY)
    assert "{{" not in html and "}}" not in html
    assert "The pigeon in all of us" in html


def test_html_is_escaped():
    copy = dict(COPY, hook="<script>alert(1)</script>")
    html = render.fill_template(render.TEMPLATE_PATH.read_text(), copy)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_empty_slot_refuses():
    copy = dict(COPY, cta="")
    with pytest.raises(render.RenderError, match="cta"):
        render.fill_template(render.TEMPLATE_PATH.read_text(), copy)
