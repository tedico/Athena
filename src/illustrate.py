"""Athena's pen-and-ink illustration engine (Gemini image gen + transparency).

Athena-owned — independent of every other project's engine. Cloned from the
Useful Math generator on 2026-07-05 and adapted; the two must never share code
at runtime (per-project engines are always functionally separate).

Pipeline: brand prompt (subject swapped in) -> Gemini image -> white paper
converted to alpha, line work tinted brand Ink -> PNG that sits directly on
the Paper #F4EDDF card background.

Usage:
    python -m src.illustrate "a moth drawn toward a candle flame" -o moth.png
    python -m src.illustrate --from-png raw.png -o moth.png   # skip generation,
                                                              # only transparency
"""
import argparse
import io
import sys
from pathlib import Path

from PIL import Image

from src.config import require

# Brand template (brand book: pen-and-ink illustrations only). The trailing
# clause is load-bearing: Gemini likes to sign engraving-style images with a
# fake artist signature, which can never ship on a Post.
PROMPT_TEMPLATE = (
    "Detailed black-and-white pen-and-ink illustration of {subject}, "
    "fine cross-hatching, hand-drawn line art, vintage naturalist engraving "
    "style, single subject, plain white background, no colour. "
    "No signature, no watermark, no text, no lettering anywhere in the image."
)

INK_HEX = "#24201A"  # brand Ink; line work is tinted to this
MODEL = "gemini-2.5-flash-image"
ASPECT_RATIO = "1:1"  # cards are 1080x1350; the frame crops square art fine
NOISE_FLOOR = 242  # luminance above this is paper noise -> fully transparent;
# without it the near-white speckle leaves a ~2% haze that renders as a faint
# rectangle around the art on the card


class IllustrationError(RuntimeError):
    pass


def build_prompt(subject: str) -> str:
    subject = subject.strip()
    if not subject:
        raise IllustrationError("Subject must not be empty")
    return PROMPT_TEMPLATE.format(subject=subject)


def make_transparent(image: Image.Image, ink_hex: str = INK_HEX) -> Image.Image:
    """Map white paper to transparency and line work to the ink colour.

    Per pixel: alpha = 255 - luminance, colour = ink. Composited over any
    background this reproduces the drawing tonally — white vanishes, full
    ink stays opaque, cross-hatch midtones become translucent ink. Luminance
    above NOISE_FLOOR clamps to fully transparent (see comment at constant).
    """
    ink = tuple(int(ink_hex.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
    if image.mode == "RGBA":  # re-runs on already-transparent art: flatten first
        flat = Image.new("RGB", image.size, (255, 255, 255))
        flat.paste(image, mask=image.getchannel("A"))
        image = flat
    alpha = image.convert("L").point(
        lambda lum: 0 if lum > NOISE_FLOOR else 255 - lum
    )
    out = Image.new("RGBA", image.size, ink + (0,))
    out.putalpha(alpha)
    return out


def _generate_raw(prompt: str, api_key: str) -> Image.Image:
    """One Gemini call -> PIL image. Import deferred so tests need no SDK."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
            image_config=types.ImageConfig(aspect_ratio=ASPECT_RATIO),
        ),
    )
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.inline_data is not None:
                return Image.open(io.BytesIO(part.inline_data.data))
    raise IllustrationError("No image in Gemini response")


def generate_illustration(
    subject: str,
    output_path: Path,
    api_key: str | None = None,
    transparent: bool = True,
    ink_hex: str = INK_HEX,
) -> Path:
    """Generate one Athena illustration and save it as PNG."""
    api_key = api_key or require("GOOGLE_API_KEY")
    image = _generate_raw(build_prompt(subject), api_key)
    if transparent:
        image = make_transparent(image, ink_hex)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, "PNG")
    return output_path


def transparent_from_file(
    source: Path, output_path: Path, ink_hex: str = INK_HEX
) -> Path:
    """Apply the transparency pass to an already-generated illustration."""
    image = Image.open(source)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    make_transparent(image, ink_hex).save(output_path, "PNG")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("subject", nargs="?", help="[SUBJECT] for the brand prompt")
    parser.add_argument("--from-png", type=Path, help="skip generation; make this PNG transparent")
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--opaque", action="store_true", help="keep the white background")
    parser.add_argument("--ink", default=INK_HEX, help=f"line colour (default {INK_HEX})")
    args = parser.parse_args()

    try:
        if args.from_png:
            path = transparent_from_file(args.from_png, args.output, args.ink)
        elif args.subject:
            path = generate_illustration(
                args.subject, args.output, transparent=not args.opaque, ink_hex=args.ink
            )
        else:
            parser.error("give a subject or --from-png")
    except IllustrationError as e:
        sys.exit(f"Error: {e}")
    print(path)


if __name__ == "__main__":
    main()
