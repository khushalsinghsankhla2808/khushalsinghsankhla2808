"""
generate_info_card.py
─────────────────────
Generates `info-card.svg`:
  • Neofetch-style card with macOS window chrome (matching terminal-card)
  • Sections: OS, Shell, About, Stack, Highlights
  • Each line slides up + fades in with 0.06s staggered SMIL delay
  • Decorative rotating ASCII logo in top-right area
  • Breathing neon vertical accent bar on the left

Run:  python generate_info_card.py
"""

import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    PALETTE, OUT_INFO, ANIM, USERNAME, DISPLAY_NAME,
    ABOUT_LINE, LOCATION, STACK, HIGHLIGHTS
)

# ──────────────────────────────────────────────────────────────────────────────
# Card dimensions
# ──────────────────────────────────────────────────────────────────────────────
TITLE_BAR_H = 36
PADDING_X   = 22
PADDING_Y   = 18
SVG_W       = 390
FONT_SIZE   = 11
LINE_H      = 19     # pixels between lines
CHAR_W      = 7.2    # approximate monospace advance

# Compute SVG height from content
LOGO_LINES  = 8      # ASCII logo in header area (inside content)

# Build all content lines ahead of time so we know the height
def _build_lines() -> list[tuple[str, str, str]]:
    """
    Returns list of (prefix, key, value) tuples + colors.
    Each tuple is (label_color, value_color, full_text).
    """
    lines: list[tuple[str, str]] = []   # (color, text)

    # Identity block
    lines.append((PALETTE["cyan"],   f"╭── {DISPLAY_NAME}"))
    lines.append((PALETTE["muted"],  f"│   {USERNAME}@github"))
    lines.append((PALETTE["border"], "╰" + "─" * 30))
    lines.append(("",                ""))  # spacer

    # System info
    lines.append((PALETTE["orange"], "OS          " + "GitHub · Linux 6.x"))
    lines.append((PALETTE["green"],  "Shell       " + "zsh + oh-my-zsh"))
    lines.append((PALETTE["blue"],   "Location    " + LOCATION))
    lines.append((PALETTE["purple"], "Status      " + "🟢  Open to collaborate"))
    lines.append(("",                ""))  # spacer

    # About
    lines.append((PALETTE["yellow"], "About"))
    lines.append((PALETTE["text"],   "  " + ABOUT_LINE))
    lines.append(("",                ""))  # spacer

    # Stack
    lines.append((PALETTE["blue"],   "Stack"))
    for s in STACK:
        lines.append((PALETTE["text"], f"  ▸ {s}"))
    lines.append(("",                ""))  # spacer

    # Highlights
    lines.append((PALETTE["purple"], "Highlights"))
    for h in HIGHLIGHTS:
        lines.append((PALETTE["cyan"], f"  ★ {h}"))

    return lines


CONTENT_LINES = _build_lines()
CONTENT_H_INNER = len(CONTENT_LINES) * LINE_H + PADDING_Y * 2
SVG_H = TITLE_BAR_H + CONTENT_H_INNER + 4   # +4 for outer margin


# ──────────────────────────────────────────────────────────────────────────────
# SVG builders
# ──────────────────────────────────────────────────────────────────────────────

def _defs_block() -> str:
    return f"""  <defs>
    <!-- Card glass gradient -->
    <linearGradient id="info-bg-grad" x1="0%" y1="0%" x2="10%" y2="100%">
      <stop offset="0%"   stop-color="#1a2332" stop-opacity="0.98"/>
      <stop offset="100%" stop-color="#0d1117" stop-opacity="0.99"/>
    </linearGradient>

    <!-- Title bar gradient -->
    <linearGradient id="info-titlebar-grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%"   stop-color="#2d333b"/>
      <stop offset="100%" stop-color="#22272e"/>
    </linearGradient>

    <!-- Outer neon glow shadow -->
    <filter id="info-card-shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="7" result="blur"/>
      <feFlood flood-color="{PALETTE['purple']}" flood-opacity="0.22" result="color"/>
      <feComposite in="color" in2="blur" operator="in" result="glow"/>
      <feMerge>
        <feMergeNode in="glow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Accent bar gradient -->
    <linearGradient id="accent-bar-grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%"   stop-color="{PALETTE['cyan']}"/>
      <stop offset="50%"  stop-color="{PALETTE['purple']}"/>
      <stop offset="100%" stop-color="{PALETTE['green']}"/>
    </linearGradient>

    <!-- Clip path for text lines (slide-up) -->
    <clipPath id="line-clip">
      <rect x="0" y="0" width="{SVG_W}" height="{SVG_H}"/>
    </clipPath>

    <!-- Scan-line texture -->
    <pattern id="info-scanlines" x="0" y="0" width="1" height="3" patternUnits="userSpaceOnUse">
      <rect width="1" height="1" fill="rgba(0,0,0,0.28)"/>
    </pattern>

    <!-- Glow for accent elements -->
    <filter id="accent-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>"""


def _window_chrome() -> str:
    bx = 2
    by = 2
    w  = SVG_W - 4
    h  = SVG_H - 4
    tbh = TITLE_BAR_H
    r   = 10

    btn_y  = by + tbh // 2
    btn_r  = 6
    btn_gap = 20
    btn1_x = bx + 22
    btn2_x = btn1_x + btn_gap
    btn3_x = btn2_x + btn_gap

    return f"""  <!-- Window frame -->
  <rect x="{bx}" y="{by}" width="{w}" height="{h}" rx="{r}" ry="{r}"
        fill="url(#info-bg-grad)" filter="url(#info-card-shadow)"/>
  <rect x="{bx}" y="{by}" width="{w}" height="{h}" rx="{r}" ry="{r}"
        fill="none" stroke="{PALETTE['border']}" stroke-width="1" opacity="0.9"/>

  <!-- Title bar -->
  <rect x="{bx}" y="{by}" width="{w}" height="{tbh}" rx="{r}" ry="{r}"
        fill="url(#info-titlebar-grad)"/>
  <rect x="{bx}" y="{by + tbh - r}" width="{w}" height="{r}" fill="#22272e"/>
  <line x1="{bx}" y1="{by + tbh}" x2="{bx + w}" y2="{by + tbh}"
        stroke="{PALETTE['border']}" stroke-width="1" opacity="0.6"/>

  <!-- Traffic lights -->
  <circle cx="{btn1_x}" cy="{btn_y}" r="{btn_r}" fill="{PALETTE['red']}">
    <animate attributeName="opacity" values="0.7;1;0.7" dur="4s" repeatCount="indefinite"/>
  </circle>
  <circle cx="{btn2_x}" cy="{btn_y}" r="{btn_r}" fill="{PALETTE['yellow']}">
    <animate attributeName="opacity" values="0.7;1;0.7" dur="4s" begin="0.5s" repeatCount="indefinite"/>
  </circle>
  <circle cx="{btn3_x}" cy="{btn_y}" r="{btn_r}" fill="{PALETTE['green']}">
    <animate attributeName="opacity" values="0.7;1;0.7" dur="4s" begin="1s" repeatCount="indefinite"/>
  </circle>

  <!-- Title -->
  <text x="{bx + w // 2}" y="{by + tbh // 2 + 5}"
        font-family="'SF Mono', 'Courier New', Courier, monospace"
        font-size="11" fill="{PALETTE['muted']}" text-anchor="middle">
    neofetch — {USERNAME}
  </text>"""


def _accent_bar() -> str:
    """Breathing neon vertical bar on the left edge."""
    bx = 2 + PADDING_X - 10
    by = 2 + TITLE_BAR_H + PADDING_Y
    bh = len(CONTENT_LINES) * LINE_H
    bw = 3
    r  = 2

    return f"""  <!-- Left accent bar -->
  <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="{r}"
        fill="url(#accent-bar-grad)" filter="url(#accent-glow)">
    <animate attributeName="opacity" values="0.5;1;0.5" dur="3s" repeatCount="indefinite"/>
    <!-- Subtle color-cycle via gradients – simulate by animating opacity -->
  </rect>"""


def _ascii_logo_corner() -> str:
    """Small rotating neon logo in top-right of content area."""
    # A tiny lambda / code symbol made from ASCII
    logo_chars = [
        "  /\\  ",
        " /  \\ ",
        "/ λ  \\",
        "‾‾‾‾‾‾",
    ]
    logo_x = SVG_W - 2 - PADDING_X - 50
    logo_y = 2 + TITLE_BAR_H + PADDING_Y + 4
    lh = 13
    lfs = 9

    parts = [f"""  <!-- ASCII logo corner -->
  <g transform-origin="{logo_x + 25} {logo_y + 25}">
    <animateTransform attributeName="transform" type="rotate"
                      from="0 {logo_x + 25} {logo_y + 26}"
                      to="360 {logo_x + 25} {logo_y + 26}"
                      dur="12s" repeatCount="indefinite"/>"""]

    for i, row in enumerate(logo_chars):
        cy = logo_y + i * lh + lh
        color = [PALETTE["cyan"], PALETTE["purple"], PALETTE["green"], PALETTE["blue"]][i % 4]
        parts.append(
            f'    <text x="{logo_x}" y="{cy}" '
            f'font-family="\'SF Mono\', \'Courier New\', Courier, monospace" '
            f'font-size="{lfs}" fill="{color}" opacity="0.7" xml:space="preserve">'
            f'{_escape_svg(row)}</text>'
        )
    parts.append("  </g>")
    return "\n".join(parts)


def _content_lines_svg() -> str:
    """Staggered slide-up + fade-in for each neofetch line."""
    base_x = 2 + PADDING_X
    base_y = 2 + TITLE_BAR_H + PADDING_Y

    parts = []
    for i, (color, text) in enumerate(CONTENT_LINES):
        if not text:
            continue  # pure spacer — no element needed

        line_y = base_y + i * LINE_H + LINE_H
        t_start = i * ANIM["info_line_stagger"]
        dur = ANIM["info_slide_dur"]

        def ft(t: float) -> str:
            return f"{t:.3f}s"

        # Wrapper group with slide-up transform + fade
        parts.append(f"""  <!-- Line {i} -->
  <g opacity="0">
    <animate attributeName="opacity"
             from="0" to="1"
             begin="{ft(t_start)}" dur="{ft(dur)}"
             fill="freeze" calcMode="spline"
             keySplines="0.25 0.1 0.25 1" keyTimes="0;1"/>
    <animateTransform attributeName="transform"
                      type="translate"
                      from="0,12" to="0,0"
                      begin="{ft(t_start)}" dur="{ft(dur)}"
                      fill="freeze" calcMode="spline"
                      keySplines="0.34 1.56 0.64 1" keyTimes="0;1"/>
    <text x="{base_x}" y="{line_y}"
          font-family="'SF Mono', 'Courier New', Courier, monospace"
          font-size="{FONT_SIZE}" fill="{color if color else PALETTE['text']}"
          xml:space="preserve">{_escape_svg(text)}</text>
  </g>""")

    return "\n".join(parts)


def _scanline_overlay() -> str:
    return (
        f'  <rect x="2" y="{2 + TITLE_BAR_H}" '
        f'width="{SVG_W - 4}" height="{SVG_H - 2 - TITLE_BAR_H}" '
        f'fill="url(#info-scanlines)" opacity="0.12" pointer-events="none" rx="4"/>'
    )


def _escape_svg(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )


# ──────────────────────────────────────────────────────────────────────────────
# Main generator
# ──────────────────────────────────────────────────────────────────────────────

def generate(output_path: str = OUT_INFO) -> None:
    parts: list[str] = []

    parts.append(f"""<svg xmlns="http://www.w3.org/2000/svg"
     width="{SVG_W}" height="{SVG_H}"
     viewBox="0 0 {SVG_W} {SVG_H}"
     role="img" aria-label="Neofetch Info Card — {USERNAME}">""")

    parts.append(_defs_block())

    # Outer background
    parts.append(
        f'  <rect width="{SVG_W}" height="{SVG_H}" '
        f'fill="{PALETTE["bg"]}" rx="12"/>'
    )

    # Window chrome
    parts.append(_window_chrome())

    # Left accent bar
    parts.append(_accent_bar())

    # Rotating logo
    parts.append(_ascii_logo_corner())

    # Content lines
    parts.append(_content_lines_svg())

    # Scan-line texture
    parts.append(_scanline_overlay())

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
        description="Generate info-card.svg"
    )
    parser.add_argument("--output", default=OUT_INFO)
    args = parser.parse_args()
    generate(args.output)
