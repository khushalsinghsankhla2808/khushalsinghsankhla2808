"""
generate_info_card.py
─────────────────────
Generates a native 440x440 side-by-side info card (`info-card.svg`):
  • 440x440 exact matching box dimensions to terminal-card.svg
  • Single-column layout with large, crisp, 100% visible 11px-14px typography
  • Sections: Header, ABOUT, STACK, HIGHLIGHTS, Footer
  • Pure SMIL staggered slide-up and fade-in animations

Run:  python generate_info_card.py
"""

import argparse
import os
import sys
import xml.sax.saxutils as saxutils

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PALETTE, OUT_INFO, USERNAME, DISPLAY_NAME

SVG_W = 440
SVG_H = 440

TITLE_BAR_H = 34
INNER_X = 2
INNER_Y = 2
CONTENT_W = SVG_W - 4
CONTENT_H = SVG_H - 4


def _escape_svg(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )


def generate(output_path: str = OUT_INFO) -> None:
    parts = []

    parts.append(f"""<svg xmlns="http://www.w3.org/2000/svg"
     width="{SVG_W}" height="{SVG_H}"
     viewBox="0 0 {SVG_W} {SVG_H}"
     role="img" aria-label="NeoFetch Terminal Info Card — {DISPLAY_NAME}">""")

    # Defs
    parts.append(f"""  <defs>
    <linearGradient id="info-bg-grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%"   stop-color="#161b22" stop-opacity="0.98"/>
      <stop offset="100%" stop-color="#0d1117" stop-opacity="0.98"/>
    </linearGradient>

    <linearGradient id="info-titlebar-grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%"   stop-color="#2d333b"/>
      <stop offset="100%" stop-color="#22272e"/>
    </linearGradient>

    <filter id="info-card-shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="6" result="blur"/>
      <feFlood flood-color="{PALETTE['purple']}" flood-opacity="0.15" result="color"/>
      <feComposite in="color" in2="blur" operator="in" result="glow"/>
      <feMerge>
        <feMergeNode in="glow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <pattern id="info-scanlines" x="0" y="0" width="1" height="3" patternUnits="userSpaceOnUse">
      <rect width="1" height="1" fill="rgba(0,0,0,0.18)"/>
    </pattern>
  </defs>""")

    # Outer Glass Box and Title Bar
    parts.append(f"""  <!-- Outer background and border -->
  <rect x="{INNER_X}" y="{INNER_Y}" width="{CONTENT_W}" height="{CONTENT_H}" rx="12"
        fill="url(#info-bg-grad)" stroke="{PALETTE['border']}" stroke-width="1.2"
        filter="url(#info-card-shadow)"/>

  <!-- Title bar -->
  <path d="M {INNER_X} {INNER_Y + 12} A 12 12 0 0 1 {INNER_X + 12} {INNER_Y} L {INNER_X + CONTENT_W - 12} {INNER_Y} A 12 12 0 0 1 {INNER_X + CONTENT_W} {INNER_Y + 12} L {INNER_X + CONTENT_W} {INNER_Y + TITLE_BAR_H} L {INNER_X} {INNER_Y + TITLE_BAR_H} Z" fill="url(#info-titlebar-grad)"/>
  <line x1="{INNER_X}" y1="{INNER_Y + TITLE_BAR_H}" x2="{INNER_X + CONTENT_W}" y2="{INNER_Y + TITLE_BAR_H}" stroke="{PALETTE['border']}" stroke-width="1" opacity="0.6"/>

  <!-- Window control buttons -->
  <circle cx="{INNER_X + 18}" cy="{INNER_Y + 17}" r="5.5" fill="{PALETTE['red']}"/>
  <circle cx="{INNER_X + 34}" cy="{INNER_Y + 17}" r="5.5" fill="{PALETTE['yellow']}"/>
  <circle cx="{INNER_X + 50}" cy="{INNER_Y + 17}" r="5.5" fill="{PALETTE['green']}"/>

  <!-- Title text -->
  <text x="{SVG_W // 2}" y="{INNER_Y + 21}" font-family="'Courier New', Courier, monospace" font-size="11" fill="{PALETTE['muted']}" text-anchor="middle">
    neofetch — {USERNAME}@github
  </text>""")

    # Structured Lines Specification for 440px Height Card
    lines_spec = [
        # Header (y=58)
        {"type": "header", "text": USERNAME, "color": PALETTE["purple"], "size": 13, "weight": "bold"},
        {"type": "sep", "text": "──────────────────────────────────", "color": PALETTE["border"], "size": 11},
        
        # ABOUT
        {"type": "pair", "label": "OS      :", "val": "MCA @ JECRC University", "color": PALETTE["orange"]},
        {"type": "pair", "label": "CGPA    :", "val": "8.65 / 10", "color": PALETTE["orange"]},
        {"type": "pair", "label": "Focus   :", "val": "Data Analytics & BI", "color": PALETTE["orange"]},
        {"type": "pair", "label": "City    :", "val": "Jodhpur, Rajasthan", "color": PALETTE["orange"]},
        
        # STACK
        {"type": "section", "text": "STACK", "color": PALETTE["cyan"], "size": 11},
        {"type": "pair", "label": "BI      :", "val": "Power BI · DAX · Fabric", "color": PALETTE["cyan"]},
        {"type": "pair", "label": "DB      :", "val": "PostgreSQL · MongoDB", "color": PALETTE["cyan"]},
        {"type": "pair", "label": "Lang    :", "val": "Python · SQL · JS", "color": PALETTE["cyan"]},
        {"type": "pair", "label": "AI      :", "val": "Gemini · Claude · MERN", "color": PALETTE["cyan"]},
        
        # HIGHLIGHTS
        {"type": "section", "text": "HIGHLIGHTS", "color": PALETTE["green"], "size": 11},
        {"type": "bullet", "text": "★ 8+ End-to-End Analytics Projects", "color": PALETTE["green"], "size": 11},
        {"type": "bullet", "text": "★ 4x Microsoft & Cisco Certifications", "color": PALETTE["green"], "size": 11},
        {"type": "bullet", "text": "★ Velora AI — MERN + DeepSeek Builder", "color": PALETTE["green"], "size": 11},
        {"type": "bullet", "text": "★ Samsung Supply Chain BI & Spotify Top 50", "color": PALETTE["green"], "size": 11},
        
        # Footer
        {"type": "footer", "text": f"github.com/{USERNAME}", "color": PALETTE["muted"], "size": 10}
    ]

    curr_y = 58.0
    line_h = 19.5
    font_family = "'Courier New', Courier, monospace"

    for i, item in enumerate(lines_spec):
        actual_begin = 0.3 + i * 0.05

        if item["type"] == "section":
            curr_y += 3.0

        y_pos = curr_y

        parts.append(f'  <g opacity="0">')
        parts.append(f'    <animate attributeName="opacity" from="0" to="1" begin="{actual_begin:.2f}s" dur="0.35s" fill="freeze"/>')
        parts.append(f'    <animateTransform attributeName="transform" type="translate" from="0 10" to="0 0" begin="{actual_begin:.2f}s" dur="0.35s" fill="freeze"/>')

        if item["type"] == "header":
            txt = _escape_svg(item["text"])
            parts.append(f'    <text x="20" y="{y_pos:.1f}" fill="{item["color"]}" font-size="{item["size"]}" font-weight="bold" font-family="{font_family}">{txt}</text>')
        elif item["type"] in ("sep", "section", "bullet"):
            txt = _escape_svg(item["text"])
            weight_attr = ' font-weight="bold"' if item["type"] == "section" else ''
            parts.append(f'    <text x="20" y="{y_pos:.1f}" fill="{item["color"]}" font-size="{item["size"]}"{weight_attr} font-family="{font_family}">{txt}</text>')
        elif item["type"] == "pair":
            lbl = _escape_svg(item["label"])
            val = _escape_svg(item["val"])
            parts.append(f'    <text x="20" y="{y_pos:.1f}" fill="{item["color"]}" font-size="11" font-weight="bold" font-family="{font_family}">{lbl}</text>')
            parts.append(f'    <text x="110" y="{y_pos:.1f}" fill="{PALETTE["white"]}" font-size="11" font-family="{font_family}">{val}</text>')
        elif item["type"] == "footer":
            txt = _escape_svg(item["text"])
            parts.append(f'    <text x="{SVG_W // 2}" y="420" fill="{item["color"]}" font-size="{item["size"]}" font-family="{font_family}" text-anchor="middle">{txt}</text>')

        parts.append("  </g>")

        if item["type"] != "footer":
            curr_y += line_h

    # Scanline texture overlay
    parts.append(f'  <rect x="{INNER_X}" y="{INNER_Y + TITLE_BAR_H}" width="{CONTENT_W}" height="{CONTENT_H - TITLE_BAR_H}" fill="url(#info-scanlines)" opacity="0.1" pointer-events="none" rx="6"/>')
    parts.append("</svg>")

    svg_content = "\n".join(parts)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"[✓] Written: {output_path}  ({len(svg_content):,} bytes)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate info-card.svg")
    parser.add_argument("--output", default=OUT_INFO)
    args = parser.parse_args()
    generate(args.output)
