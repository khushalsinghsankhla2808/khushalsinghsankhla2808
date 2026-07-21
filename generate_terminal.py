"""
generate_terminal.py
─────────────────────
Generates a compact 250x400 terminal SVG card (`terminal-card.svg`) for 1:4 ratio layout:
  • Fetches GitHub avatar → converts to 28x21 ASCII art via Pillow
  • macOS-style glassmorphic terminal window
  • Row-by-row ASCII reveal animation
  • Sweeping cursor block per row
  • Footer typewriter: "$ whoami" → name
"""

import argparse
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PALETTE, OUT_TERMINAL, ANIM, USERNAME, DISPLAY_NAME

SVG_W = 250
SVG_H = 400

ASCII_W = 28          # characters per row
ASCII_H = 21          # rows
DENSITY = " .`-_':,;^=+/\"|)\\<>)(i!lI?/\\|)(}{][tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

CHAR_W = 7.0          # character advance width
CHAR_H = 12.0         # row line height
FONT_SIZE = 9.5

TITLE_BAR_H = 34
PADDING_X = 27
PADDING_Y = 14
INNER_X = 2
INNER_Y = 2
CONTENT_W = SVG_W - 4
CONTENT_H = SVG_H - 4


def fetch_avatar(username: str):
    """Download GitHub avatar. Returns a Pillow Image or None on failure."""
    try:
        import requests
        from PIL import Image
        url = f"https://github.com/{username}.png?size=200"
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        return Image.open(io.BytesIO(resp.content)).convert("RGB")
    except Exception as e:
        print(f"[warn] Avatar fetch failed ({e}), using fallback silhouette.")
        return None


def image_to_ascii(img) -> list[str]:
    """Convert a Pillow Image to a list of ASCII rows."""
    if img is None:
        return _silhouette_ascii()

    try:
        from PIL import Image, ImageEnhance
    except ImportError:
        print("[warn] Pillow not installed, using fallback silhouette.")
        return _silhouette_ascii()

    img = img.resize((ASCII_W, ASCII_H), Image.LANCZOS)
    img = img.convert("L")  # grayscale
    img = ImageEnhance.Contrast(img).enhance(1.4)

    rows = []
    pixels = list(img.getdata())
    for row_idx in range(ASCII_H):
        row_pixels = pixels[row_idx * ASCII_W: (row_idx + 1) * ASCII_W]
        row_chars = ""
        for px in row_pixels:
            idx = int((255 - px) / 255 * (len(DENSITY) - 1))
            row_chars += DENSITY[idx]
        rows.append(row_chars)
    return rows


def _silhouette_ascii() -> list[str]:
    """Built-in fallback ASCII silhouette."""
    template = [
        "       ......::::::......       ",
        "    ..:::::::::::::::::::::..   ",
        "  .:::::::::::::::::::::::::::: ",
        " .::::::::::::::::::::::::::::::.",
        ".::::::::::::::::::::::::::::::::.",
        ":::::::::::::::::::::::::::::::::",
        ":::::::::::::::::::::::::::::::::",
        "::::::::.          .::::::::.::::",
        "::::::::           ::::::::::::::",
        " :::::::.         .::::::::::::::",
        " :::::::::::::::::::::::::::::::.",
        "  :::::::::::::::::::::::::::::::",
        "   .:::::::::::      ::::::::::::",
        "     ::::::::          ::::::::::",
        "      :::::::::::::::::::::::::: ",
        "     :::::::::::::::::::::::::::.",
        "   .:::::::::::::::::::::::::::: ",
        " .::::::::::::::::::::::::::::::.",
        ":::::::::::::::::...  ...::::::::",
        ":::::::::::::.            .::::::",
        ":::::::::::.                .::::",
    ]
    rows = []
    for row in template[:ASCII_H]:
        if len(row) < ASCII_W:
            row = row + " " * (ASCII_W - len(row))
        rows.append(row[:ASCII_W])
    while len(rows) < ASCII_H:
        rows.append(" " * ASCII_W)
    return rows


def _escape_svg(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )


def generate(rows: list[str], output_path: str = OUT_TERMINAL) -> None:
    parts = []

    parts.append(f"""<svg xmlns="http://www.w3.org/2000/svg"
     width="{SVG_W}" height="{SVG_H}"
     viewBox="0 0 {SVG_W} {SVG_H}"
     role="img" aria-label="Terminal ASCII Portrait — {USERNAME}">""")

    # Defs
    parts.append(f"""  <defs>
    <linearGradient id="term-bg-grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%"   stop-color="#161b22" stop-opacity="0.98"/>
      <stop offset="100%" stop-color="#0d1117" stop-opacity="0.98"/>
    </linearGradient>

    <linearGradient id="titlebar-grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%"   stop-color="#2d333b"/>
      <stop offset="100%" stop-color="#22272e"/>
    </linearGradient>

    <filter id="card-shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="6" result="blur"/>
      <feFlood flood-color="{PALETTE['green']}" flood-opacity="0.15" result="color"/>
      <feComposite in="color" in2="blur" operator="in" result="glow"/>
      <feMerge>
        <feMergeNode in="glow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <pattern id="scanlines" x="0" y="0" width="1" height="3" patternUnits="userSpaceOnUse">
      <rect width="1" height="1" fill="rgba(0,0,0,0.2)"/>
    </pattern>
  </defs>""")

    # Background card frame
    parts.append(f"""  <!-- Outer background and glass border -->
  <rect x="{INNER_X}" y="{INNER_Y}" width="{CONTENT_W}" height="{CONTENT_H}" rx="12"
        fill="url(#term-bg-grad)" stroke="{PALETTE['border']}" stroke-width="1.2"
        filter="url(#card-shadow)"/>

  <!-- Title bar -->
  <path d="M {INNER_X} {INNER_Y + 12} A 12 12 0 0 1 {INNER_X + 12} {INNER_Y} L {INNER_X + CONTENT_W - 12} {INNER_Y} A 12 12 0 0 1 {INNER_X + CONTENT_W} {INNER_Y + 12} L {INNER_X + CONTENT_W} {INNER_Y + TITLE_BAR_H} L {INNER_X} {INNER_Y + TITLE_BAR_H} Z" fill="url(#titlebar-grad)"/>
  <line x1="{INNER_X}" y1="{INNER_Y + TITLE_BAR_H}" x2="{INNER_X + CONTENT_W}" y2="{INNER_Y + TITLE_BAR_H}" stroke="{PALETTE['border']}" stroke-width="1" opacity="0.6"/>

  <!-- Traffic lights -->
  <circle cx="{INNER_X + 16}" cy="{INNER_Y + 17}" r="5" fill="{PALETTE['red']}"/>
  <circle cx="{INNER_X + 30}" cy="{INNER_Y + 17}" r="5" fill="{PALETTE['yellow']}"/>
  <circle cx="{INNER_X + 44}" cy="{INNER_Y + 17}" r="5" fill="{PALETTE['green']}"/>

  <!-- Title -->
  <text x="{SVG_W // 2}" y="{INNER_Y + 21}" font-family="'Courier New', Courier, monospace" font-size="10" fill="{PALETTE['muted']}" text-anchor="middle">
    terminal — {USERNAME[:12]}
  </text>""")

    # ASCII Rows
    text_x = INNER_X + PADDING_X
    first_row_y = INNER_Y + TITLE_BAR_H + PADDING_Y
    row_w = ASCII_W * CHAR_W
    ascii_color = PALETTE["green"]

    for i, row_text in enumerate(rows):
        row_y = first_row_y + i * CHAR_H
        baseline = row_y + CHAR_H - 2.5
        clip_id = f"clip-row-{i}"
        row_start = 0.4 + i * 0.07
        dur_s = 0.08

        escaped = _escape_svg(row_text)

        parts.append(f"""  <g>
    <clipPath id="{clip_id}">
      <rect x="{text_x}" y="{row_y}" width="0" height="{CHAR_H + 1}">
        <animate attributeName="width" from="0" to="{row_w}" begin="{row_start:.2f}s" dur="{dur_s:.2f}s" fill="freeze"/>
      </rect>
    </clipPath>
    <text x="{text_x}" y="{baseline:.1f}" font-family="'Courier New', Courier, monospace" font-size="{FONT_SIZE}" fill="{ascii_color}" clip-path="url(#{clip_id})" xml:space="preserve">{escaped}</text>
    <!-- Cursor block -->
    <rect x="{text_x}" y="{row_y:.1f}" width="5" height="9" fill="{PALETTE['white']}" visibility="hidden">
      <set attributeName="visibility" to="visible" begin="{row_start:.2f}s" dur="{dur_s:.2f}s"/>
      <animate attributeName="x" from="{text_x}" to="{text_x + row_w - 5:.1f}" begin="{row_start:.2f}s" dur="{dur_s:.2f}s" fill="freeze"/>
    </rect>
  </g>""")

    # Footer Typewriter lines (below ASCII art)
    footer_y1 = 330.0
    footer_y2 = 348.0

    # Line 1: "$ whoami"
    parts.append(f"""  <!-- Footer Typewriter -->
  <line x1="16" y1="316" x2="{SVG_W - 16}" y2="316" stroke="{PALETTE['border']}" stroke-width="0.8" opacity="0.6"/>
  <g>
    <clipPath id="clip-footer-1">
      <rect x="16" y="320" width="0" height="14">
        <animate attributeName="width" from="0" to="80" begin="2.0s" dur="0.5s" fill="freeze"/>
      </rect>
    </clipPath>
    <text x="16" y="{footer_y1}" font-family="'Courier New', Courier, monospace" font-size="10.5" clip-path="url(#clip-footer-1)">
      <tspan fill="{PALETTE['cyan']}">$ </tspan><tspan fill="{PALETTE['white']}">whoami</tspan>
    </text>
    <rect x="16" y="321" width="5" height="10" fill="#ffffff" visibility="hidden">
      <set attributeName="visibility" to="visible" begin="2.0s" dur="0.5s"/>
      <animate attributeName="x" from="16" to="78" begin="2.0s" dur="0.5s" fill="freeze"/>
    </rect>
  </g>""")

    # Line 2: Display Name
    escaped_name = _escape_svg(DISPLAY_NAME)
    parts.append(f"""  <g>
    <clipPath id="clip-footer-2">
      <rect x="16" y="336" width="0" height="16">
        <animate attributeName="width" from="0" to="210" begin="2.6s" dur="1.2s" fill="freeze"/>
      </rect>
    </clipPath>
    <text x="16" y="{footer_y2}" font-family="'Courier New', Courier, monospace" font-size="10.5" fill="{PALETTE['cyan']}" font-weight="bold" clip-path="url(#clip-footer-2)">{escaped_name}</text>
    <!-- Blinking final cursor -->
    <rect x="16" y="338" width="5" height="10" fill="#ffffff" opacity="0">
      <set attributeName="opacity" to="1" begin="2.6s" dur="1.2s"/>
      <animate attributeName="x" from="16" to="160" begin="2.6s" dur="1.2s" fill="freeze"/>
      <animate attributeName="opacity" values="1;0;1" keyTimes="0;0.5;1" begin="3.8s" dur="0.8s" repeatCount="indefinite"/>
    </rect>
  </g>""")

    # Scanline overlay
    parts.append(f'  <rect x="{INNER_X}" y="{INNER_Y + TITLE_BAR_H}" width="{CONTENT_W}" height="{CONTENT_H - TITLE_BAR_H}" fill="url(#scanlines)" opacity="0.12" pointer-events="none" rx="6"/>')

    parts.append("</svg>")

    svg_content = "\n".join(parts)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"[✓] Written: {output_path}  ({len(svg_content):,} bytes)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate terminal-card.svg")
    parser.add_argument("--username", default=USERNAME)
    parser.add_argument("--output", default=OUT_TERMINAL)
    parser.add_argument("--no-fetch", action="store_true")
    args = parser.parse_args()

    img = None if args.no_fetch else fetch_avatar(args.username)
    rows = image_to_ascii(img)
    generate(rows, args.output)
