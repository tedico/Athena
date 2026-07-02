"""CLI: render a Carousel row to seven verified 1080x1350 PNGs.

Usage: python -m src.render <carousel_page_id> [--slug my-carousel]
Gates: all 7 slots non-empty; fonts loaded (15s budget); every screenshot
exactly 1080x1350 — anything else aborts with statuses untouched.
"""
import argparse
import html as html_lib
import re
import tempfile
from pathlib import Path

from PIL import Image

from src import notion_io, slots

TEMPLATE_PATH = Path(__file__).parent.parent / "template" / "athena_cards.html"
CARD_SIZE = (1080, 1350)


class RenderError(RuntimeError):
    pass


def fill_template(template_text: str, copy: dict) -> str:
    values = {
        "HOOK": copy["hook"],
        "CARD2": copy["cards"][0],
        "CARD3": copy["cards"][1],
        "CARD4": copy["cards"][2],
        "CARD5": copy["cards"][3],
        "CARD6": copy["cards"][4],
        "CTA": copy["cta"],
    }
    empties = [
        k for k, v in copy.items()
        if k != "cards" and isinstance(v, str) and not v.strip()
    ]
    empties += [f"cards.{i}" for i, v in enumerate(copy["cards"]) if not v.strip()]
    if empties:
        raise RenderError(f"empty slots: {', '.join(empties)}")

    filled = template_text
    for key, value in values.items():
        filled = filled.replace("{{" + key + "}}", html_lib.escape(value))
    leftover = re.findall(r"\{\{[A-Z0-9]+\}\}", filled)
    if leftover:
        raise RenderError(f"unfilled placeholders: {leftover}")
    return filled


def render_carousel_copy(copy: dict, out_dir: Path) -> list:
    """Pure copy → PNGs (no Notion). Used by main() and by tests."""
    from playwright.sync_api import sync_playwright

    filled = fill_template(TEMPLATE_PATH.read_text(), copy)
    out_dir.mkdir(parents=True, exist_ok=True)
    # write next to the template so relative assets/ URLs resolve
    with tempfile.NamedTemporaryFile(
        "w", suffix=".html", dir=TEMPLATE_PATH.parent, delete=False
    ) as f:
        f.write(filled)
        page_path = Path(f.name)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(
                viewport={"width": 1200, "height": 1500}, device_scale_factor=1
            )
            page.goto(page_path.as_uri())
            page.wait_for_function(
                "document.fonts.status === 'loaded'", timeout=15000
            )
            cards = page.locator(".card")
            if cards.count() != 7:
                raise RenderError(f"expected 7 cards, found {cards.count()}")
            paths = []
            for i in range(7):
                out = out_dir / f"card-0{i + 1}.png"
                cards.nth(i).screenshot(path=str(out))
                paths.append(out)
            browser.close()
    finally:
        page_path.unlink(missing_ok=True)

    for path in paths:
        size = Image.open(path).size
        if size != CARD_SIZE:
            raise RenderError(f"{path.name} is {size}, must be {CARD_SIZE}")
    return paths


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("carousel_page_id")
    parser.add_argument("--slug", default=None)
    args = parser.parse_args()

    client = notion_io.client()
    copy = notion_io.fetch_carousel(client, args.carousel_page_id)
    slug = args.slug or re.sub(r"[^a-z0-9]+", "-", copy["hook"].lower()).strip("-")
    out_dir = Path("output") / slug

    paths = render_carousel_copy(copy, out_dir)

    notion_io.update_status(
        client, args.carousel_page_id, slots.PROP_STATUS, "Rendered"
    )
    if copy["paper_page_id"]:
        notion_io.update_status(
            client, copy["paper_page_id"], slots.PAPER_STATUS, "Rendered"
        )
    print(f"rendered {len(paths)} cards → {out_dir}/")


if __name__ == "__main__":
    main()
