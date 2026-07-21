"""
generate_terminal.py
─────────────────────
Generates `terminal-card.svg`:
  • Fetches GitHub avatar → converts to ASCII art via Pillow
  • macOS-style glassmorphic terminal window
  • Row-by-row ASCII reveal with SMIL clip-rect width animation
  • Sweeping cursor block per row
  • Footer typewriter: "$ whoami" → username

Run:  python generate_terminal.py
      python generate_terminal.py --no-fetch   (uses built-in silhouette)
"""

import argparse
import io
import os
import sys
import math
from textwrap import wrap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    PALETTE, OUT_TERMINAL, ANIM, USERNAME, DISPLAY_NAME
)

# ──────────────────────────────────────────────────────────────────────────────
# ASCII art constants
# ──────────────────────────────────────────────────────────────────────────────
ASCII_W = 52          # characters per row
ASCII_H = 26          # rows
# Density string — darkest → lightest (we invert for dark bg)
DENSITY = " .`-_':,;^=+/\"|)\\<>)(i!lI?/\\|)(}{][tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

# ──────────────────────────────────────────────────────────────────────────────
# Card dimensions
# ──────────────────────────────────────────────────────────────────────────────
CHAR_W     = 8.0      # monospace glyph advance width in px
CHAR_H     = 14.0     # line height in px
FONT_SIZE  = 11       # font-size for tspan elements

TITLE_BAR_H = 36
PADDING_X   = 18
PADDING_Y   = 16
FOOTER_H    = 50

CONTENT_W  = int(ASCII_W * CHAR_W) + 2 * PADDING_X    # ≈ 452
CONTENT_H  = int(ASCII_H * CHAR_H) + TITLE_BAR_H + PADDING_Y + FOOTER_H
SVG_W      = CONTENT_W + 4   # slight outer glow margin
SVG_H      = CONTENT_H + 4
INNER_X    = 2
INNER_Y    = 2


# ──────────────────────────────────────────────────────────────────────────────
# Avatar fetch & ASCII conversion
# ──────────────────────────────────────────────────────────────────────────────

def fetch_avatar(username: str) -> "Image":
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


def image_to_ascii(img: "Image | None") -> list[str]:
    """Convert a Pillow Image to a list of ASCII rows."""
    if img is None:
        return _silhouette_ascii()

    try:
        from PIL import Image, ImageFilter, ImageEnhance
    except ImportError:
        print("[warn] Pillow not installed, using fallback silhouette.")
        return _silhouette_ascii()

    # Resize with Lanczos filter; note 2:1 width:height ratio for terminal font
    img = img.resize((ASCII_W, ASCII_H), Image.LANCZOS)
    img = img.convert("L")  # grayscale

    # Slight contrast boost for better ASCII definition
    img = ImageEnhance.Contrast(img).enhance(1.4)

    rows = []
    pixels = list(img.getdata())
    for row_idx in range(ASCII_H):
        row_pixels = pixels[row_idx * ASCII_W: (row_idx + 1) * ASCII_W]
        row_chars = ""
        for px in row_pixels:
            # Invert: bright pixels → sparse chars, dark pixels → dense chars
            idx = int((255 - px) / 255 * (len(DENSITY) - 1))
            row_chars += DENSITY[idx]
        rows.append(row_chars)
    return rows


def _silhouette_ascii() -> list[str]:
    """Built-in 52×26 fallback ASCII silhouette (no network needed)."""
    # A simple geometric face silhouette
    template = [
        "                    ......::::::......                    ",
        "                ..:::::::::::::::::::::..                 ",
        "              .::::::::::::::::::::::::::::               ",
        "            .::::::::::::::::::::::::::::::.              ",
        "           .::::::::::::::::::::::::::::::::.             ",
        "          :::::::::::::::::::::::::::::::::::             ",
        "         ::::::::::::::::::::::::::::::::::::             ",
        "         ::::::::.          .::::::::.:::::::             ",
        "         ::::::::           ::::::::::::::::              ",
        "          :::::::.         .::::::::::::::::              ",
        "          :::::::::::::::::::::::::::::::::.              ",
        "           :::::::::::::::::::::::::::::::               ",
        "            .:::::::::::      ::::::::::::               ",
        "              ::::::::          ::::::::::               ",
        "               ::::::::::::::::::::::::::               ",
        "              :::::::::::::::::::::::::::.               ",
        "            .::::::::::::::::::::::::::::::              ",
        "          .:::::::::::::::::::::::::::::::::.            ",
        "        .::::::::::::::::::::::::::::::::::::::          ",
        "      .::::::::::::::::..      ..::::::::::::::::        ",
        "    .:::::::::::::::.              .::::::::::::::::     ",
        "  .::::::::::::::::                  .::::::::::::::.   ",
        " :::::::::::::::.                      .:::::::::::::.  ",
        ":::::::::::::::                          .:::::::::::::  ",
        "::::::::::::::                            .::::::::::::  ",
        "::::::::::::::                             ::::::::::::  ",
    ]
    # Trim/pad each row to ASCII_W
    rows = []
    for row in template[:ASCII_H]:
        if len(row) < ASCII_W:
            row = row + " " * (ASCII_W - len(row))
        rows.append(row[:ASCII_W])
    while len(rows) < ASCII_H:
        rows.append(" " * ASCII_W)
    return rows


# ──────────────────────────────────────────────────────────────────────────────
# SVG builders
# ──────────────────────────────────────────────────────────────────────────────

def _defs_block() -> str:
    return f"""  <defs>
    <!-- Terminal glass surface gradient -->
    <linearGradient id="term-bg-grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%"   stop-color="#1a2332" stop-opacity="0.98"/>
      <stop offset="100%" stop-color="#0d1117" stop-opacity="0.98"/>
    </linearGradient>

    <!-- Title bar gradient -->
    <linearGradient id="titlebar-grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%"   stop-color="#2d333b"/>
      <stop offset="100%" stop-color="#22272e"/>
    </linearGradient>

    <!-- Outer card glow -->
    <filter id="card-shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="8" result="blur"/>
      <feFlood flood-color="{PALETTE['cyan']}" flood-opacity="0.25" result="color"/>
      <feComposite in="color" in2="blur" operator="in" result="glow"/>
      <feMerge>
        <feMergeNode in="glow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Text glow for ASCII art -->
    <filter id="text-glow" x="-5%" y="-5%" width="110%" height="110%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="0.8" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Scan-line pattern -->
    <pattern id="scanlines" x="0" y="0" width="1" height="3" patternUnits="userSpaceOnUse">
      <rect width="1" height="1" fill="rgba(0,0,0,0.3)"/>
    </pattern>

    <!-- Cursor glow -->
    <filter id="cursor-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="1.5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>"""


def _window_chrome() -> str:
    """macOS-style title bar with traffic-light buttons and terminal path."""
    bx = INNER_X
    by = INNER_Y
    w  = CONTENT_W
    h  = CONTENT_H
    tbh = TITLE_BAR_H
    r   = 10   # corner radius

    btn_y  = by + tbh // 2
    btn_r  = 6
    btn_gap = 20
    btn1_x = bx + 22
    btn2_x = btn1_x + btn_gap
    btn3_x = btn2_x + btn_gap

    return f"""  <!-- Window frame -->
  <rect x="{bx}" y="{by}" width="{w}" height="{h}" rx="{r}" ry="{r}"
        fill="url(#term-bg-grad)" filter="url(#card-shadow)"/>

  <!-- Glass border -->
  <rect x="{bx}" y="{by}" width="{w}" height="{h}" rx="{r}" ry="{r}"
        fill="none" stroke="{PALETTE['border']}" stroke-width="1" opacity="0.9"/>

  <!-- Title bar -->
  <rect x="{bx}" y="{by}" width="{w}" height="{tbh}" rx="{r}" ry="{r}"
        fill="url(#titlebar-grad)"/>
  <rect x="{bx}" y="{by + tbh - r}" width="{w}" height="{r}" fill="#22272e"/>

  <!-- Title bar bottom border -->
  <line x1="{bx}" y1="{by + tbh}" x2="{bx + w}" y2="{by + tbh}"
        stroke="{PALETTE['border']}" stroke-width="1" opacity="0.6"/>

  <!-- Traffic light buttons -->
  <circle cx="{btn1_x}" cy="{btn_y}" r="{btn_r}" fill="{PALETTE['red']}">
    <animate attributeName="opacity" values="0.7;1;0.7" dur="4s" repeatCount="indefinite"/>
  </circle>
  <circle cx="{btn2_x}" cy="{btn_y}" r="{btn_r}" fill="{PALETTE['yellow']}">
    <animate attributeName="opacity" values="0.7;1;0.7" dur="4s" begin="0.5s" repeatCount="indefinite"/>
  </circle>
  <circle cx="{btn3_x}" cy="{btn_y}" r="{btn_r}" fill="{PALETTE['green']}">
    <animate attributeName="opacity" values="0.7;1;0.7" dur="4s" begin="1s" repeatCount="indefinite"/>
  </circle>

  <!-- Window title -->
  <text x="{bx + w // 2}" y="{by + tbh // 2 + 5}"
        font-family="'SF Mono', 'Courier New', Courier, monospace"
        font-size="11" fill="{PALETTE['muted']}" text-anchor="middle"
        letter-spacing="0.5">
    {USERNAME} — zsh — 80×26
  </text>"""


def _ascii_rows_svg(rows: list[str]) -> str:
    """Render ASCII rows with clip-rect reveal + cursor sweep per row."""
    text_x = INNER_X + PADDING_X
    first_row_y = INNER_Y + TITLE_BAR_H + PADDING_Y
    row_w = ASCII_W * CHAR_W
    parts = []

    # Total duration of all row reveals (needed to know when footer starts)
    total_reveal_time = ASCII_H * ANIM["terminal_row_stagger"] + ANIM["terminal_reveal_dur"]

    # Neon prompt color: green ASCII art
    ascii_color = PALETTE["green"]

    for i, row_text in enumerate(rows):
        row_y   = first_row_y + i * CHAR_H
        baseline = row_y + CHAR_H - 3
        clip_id  = f"clip-row-{i}"
        row_start = i * ANIM["terminal_row_stagger"]
        row_end   = row_start + ANIM["terminal_reveal_dur"]

        def ft(t: float) -> str:
            return f"{t:.3f}s"

        # clipPath for this row
        parts.append(f"""    <!-- Row {i} clip + text -->
    <defs>
      <clipPath id="{clip_id}">
        <rect id="cr{i}" x="{text_x}" y="{row_y}" width="0" height="{CHAR_H + 1}">
          <animate attributeName="width"
                   from="0" to="{row_w}"
                   begin="{ft(row_start)}" dur="{ft(ANIM['terminal_reveal_dur'])}"
                   fill="freeze" calcMode="spline"
                   keySplines="0.25 0.1 0.25 1" keyTimes="0;1"/>
        </rect>
      </clipPath>
    </defs>
    <text x="{text_x}" y="{baseline}"
          font-family="'SF Mono', 'Courier New', Courier, monospace"
          font-size="{FONT_SIZE}" fill="{ascii_color}"
          clip-path="url(#{clip_id})"
          filter="url(#text-glow)"
          xml:space="preserve">{_escape_svg(row_text)}</text>""")

        # Cursor block for this row
        cursor_w  = CHAR_W
        cursor_h  = CHAR_H
        cursor_y  = row_y + 1
        cursor_id = f"cur-{i}"

        # Cursor appears at row start, sweeps to end, disappears
        parts.append(f"""    <rect id="{cursor_id}" x="{text_x}" y="{cursor_y}"
          width="{cursor_w}" height="{cursor_h}"
          fill="{PALETTE['white']}" opacity="0" filter="url(#cursor-glow)">
      <!-- appear -->
      <animate attributeName="opacity" from="0" to="0.85"
               begin="{ft(row_start)}" dur="0.02s" fill="freeze"/>
      <!-- sweep x -->
      <animate attributeName="x"
               from="{text_x}" to="{text_x + row_w - cursor_w}"
               begin="{ft(row_start)}" dur="{ft(ANIM['terminal_cursor_dur'] * ASCII_W)}"
               fill="freeze" calcMode="linear"/>
      <!-- disappear when row done -->
      <animate attributeName="opacity" from="0.85" to="0"
               begin="{ft(row_end - 0.05)}" dur="0.05s" fill="freeze"/>
    </rect>""")

    return "\n".join(parts), total_reveal_time


def _footer_typewriter(total_reveal_time: float) -> str:
    """Typewriter animation: $ whoami -> DISPLAY_NAME."""
    text_x = INNER_X + PADDING_X
    footer_y = INNER_Y + TITLE_BAR_H + PADDING_Y + ASCII_H * CHAR_H + 14

    # Give 0.3s buffer after last row finishes
    t_start = total_reveal_time + 0.3

    prompt = "$ whoami"
    result = DISPLAY_NAME

    parts = []

    # Pre-extract colors (avoid backslashes inside f-string expressions on Py<3.12)
    color_green  = PALETTE["green"]
    color_cyan   = PALETTE["cyan"]
    color_border = PALETTE["border"]

    prompt_chars = list(prompt)
    char_delay = 0.1   # 100ms per character

    def ft(t: float) -> str:
        return f"{t:.3f}s"

    # Line 1: "$ whoami" — typed char by char
    for k, ch in enumerate(prompt_chars):
        appear_t = t_start + k * char_delay
        cx = text_x + k * CHAR_W
        ch_escaped = _escape_svg(ch)
        parts.append(
            f'  <text x="{cx}" y="{footer_y}" '
            "font-family=\"'SF Mono', 'Courier New', Courier, monospace\" "
            f'font-size="{FONT_SIZE}" fill="{color_green}" '
            f'opacity="0" xml:space="preserve">'
            f'{ch_escaped}'
            f'<animate attributeName="opacity" from="0" to="1" '
            f'begin="{ft(appear_t)}" dur="0.05s" fill="freeze"/>'
            f'</text>'
        )

    # Blinking cursor after prompt
    prompt_end_t   = t_start + len(prompt_chars) * char_delay
    result_start_t = prompt_end_t + 0.6
    blink_x  = text_x + len(prompt_chars) * CHAR_W
    blink_y  = footer_y - CHAR_H + 3
    blink_rc = int(0.6 / 0.6) + 2

    parts.append(
        f'  <rect x="{blink_x}" y="{blink_y}" '
        f'width="{CHAR_W}" height="{CHAR_H}" '
        f'fill="{color_green}" opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" '
        f'begin="{ft(prompt_end_t)}" dur="0.05s" fill="freeze"/>'
        f'<animate attributeName="opacity" values="1;0;1" dur="0.6s" '
        f'begin="{ft(prompt_end_t)}" repeatCount="{blink_rc}"/>'
        f'<animate attributeName="opacity" from="1" to="0" '
        f'begin="{ft(result_start_t)}" dur="0.05s" fill="freeze"/>'
        f'</rect>'
    )

    # Line 2: result (display name) — typed char by char
    result_y = footer_y + CHAR_H + 4
    for k, ch in enumerate(result):
        appear_t = result_start_t + k * char_delay * 0.7
        cx = text_x + k * CHAR_W
        ch_escaped = _escape_svg(ch)
        parts.append(
            f'  <text x="{cx}" y="{result_y}" '
            "font-family=\"'SF Mono', 'Courier New', Courier, monospace\" "
            f'font-size="{FONT_SIZE}" fill="{color_cyan}" font-weight="bold" '
            f'opacity="0">'
            f'{ch_escaped}'
            f'<animate attributeName="opacity" from="0" to="1" '
            f'begin="{appear_t:.3f}s" dur="0.05s" fill="freeze"/>'
            f'</text>'
        )


    # Footer separator line
    sep_y = footer_y - 10
    parts.insert(0,
        f'  <line x1="{text_x}" y1="{sep_y}" '
        f'x2="{INNER_X + CONTENT_W - PADDING_X}" y2="{sep_y}" '
        f'stroke="{PALETTE["border"]}" stroke-width="0.5" opacity="0.6"/>'
    )

    return "\n".join(parts)


def _escape_svg(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )


def _scanline_overlay() -> str:
    return (
        f'  <rect x="{INNER_X}" y="{INNER_Y + TITLE_BAR_H}" '
        f'width="{CONTENT_W}" height="{CONTENT_H - TITLE_BAR_H}" '
        f'fill="url(#scanlines)" opacity="0.15" pointer-events="none" rx="4"/>'
    )


# ──────────────────────────────────────────────────────────────────────────────
# Main generator
# ──────────────────────────────────────────────────────────────────────────────

def generate(rows: list[str], output_path: str = OUT_TERMINAL) -> None:
    parts: list[str] = []

    parts.append(f"""<svg xmlns="http://www.w3.org/2000/svg"
     width="{SVG_W}" height="{SVG_H}"
     viewBox="0 0 {SVG_W} {SVG_H}"
     role="img" aria-label="Terminal ASCII Portrait — {USERNAME}">""")

    parts.append(_defs_block())

    # Outer background
    parts.append(
        f'  <rect width="{SVG_W}" height="{SVG_H}" '
        f'fill="{PALETTE["bg"]}" rx="12"/>'
    )

    # Window chrome (title bar + frame)
    parts.append(_window_chrome())

    # ASCII art rows + cursors
    ascii_svg, total_reveal_time = _ascii_rows_svg(rows)
    parts.append(ascii_svg)

    # Scan-line texture
    parts.append(_scanline_overlay())

    # Footer typewriter
    parts.append(_footer_typewriter(total_reveal_time))

    parts.append("</svg>")

    svg_content = "\n".join(parts)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"[✓] Written: {output_path}  ({len(svg_content):,} bytes)")


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate terminal-card.svg"
    )
    parser.add_argument("--username", default=USERNAME)
    parser.add_argument("--output",   default=OUT_TERMINAL)
    parser.add_argument("--no-fetch", action="store_true",
                        help="Skip avatar download, use built-in silhouette")
    args = parser.parse_args()

    img  = None if args.no_fetch else fetch_avatar(args.username)
    rows = image_to_ascii(img)
    generate(rows, args.output)
