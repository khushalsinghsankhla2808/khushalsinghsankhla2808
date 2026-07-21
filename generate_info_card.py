"""
generate_info_card.py
─────────────────────
Generates a wide 650x400 2-column NeoFetch SVG card (`info-card.svg`) for 1:4 ratio layout:
  • 650x400 matching height card to terminal-card.svg
  • 2-column layout with 100% large, crisp, visible 11px-16px text
  • Left column: Identity, System Info, About & Focus, Highlights
  • Right column: Tech Stack, Featured Projects, Certifications
  • Bottom banner: Currently Building & Always Learning
  • Pure SMIL staggered slide-up and fade-in animations

Run:  python generate_info_card.py
"""

import argparse
import os
import sys
import xml.sax.saxutils as saxutils

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PALETTE, OUT_INFO, USERNAME, DISPLAY_NAME

SVG_W = 650
SVG_H = 400

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
  <circle cx="{INNER_X + 16}" cy="{INNER_Y + 17}" r="5" fill="{PALETTE['red']}"/>
  <circle cx="{INNER_X + 30}" cy="{INNER_Y + 17}" r="5" fill="{PALETTE['yellow']}"/>
  <circle cx="{INNER_X + 44}" cy="{INNER_Y + 17}" r="5" fill="{PALETTE['green']}"/>

  <!-- Title text -->
  <text x="{SVG_W // 2}" y="{INNER_Y + 21}" font-family="'Courier New', Courier, monospace" font-size="11" fill="{PALETTE['muted']}" text-anchor="middle">
    neofetch — {USERNAME}@github
  </text>""")

    font_family = "'Courier New', Courier, monospace"

    # ============================================================================
    # LEFT COLUMN (x=20 to 310)
    # ============================================================================
    lx = 20

    # Header Identity
    parts.append(f"""  <!-- LEFT COLUMN -->
  <g>
    <animate attributeName="opacity" from="0" to="1" begin="0.2s" dur="0.35s" fill="freeze"/>
    <text x="{lx}" y="58" font-family="{font_family}" font-size="16" font-weight="bold" fill="{PALETTE['purple']}">{_escape_svg(DISPLAY_NAME)}</text>
    <text x="{lx}" y="74" font-family="{font_family}" font-size="10" fill="{PALETTE['muted']}">Data Analytics • BI • AI Developer</text>
    <line x1="{lx}" y1="83" x2="310" y2="83" stroke="{PALETTE['border']}" stroke-width="0.8" opacity="0.6"/>
  </g>""")

    # System Info & About
    parts.append(f"""  <g>
    <animate attributeName="opacity" from="0" to="1" begin="0.4s" dur="0.35s" fill="freeze"/>
    <text x="{lx}" y="103" font-family="{font_family}" font-size="11.5" font-weight="bold" fill="{PALETTE['yellow']}">╭─ 🖥️ System &amp; Education</text>
    
    <text x="{lx + 8}" y="122" font-family="{font_family}" font-size="11"><tspan font-weight="bold" fill="{PALETTE['orange']}">Program : </tspan><tspan fill="{PALETTE['white']}">MCA @ JECRC University</tspan></text>
    <text x="{lx + 8}" y="139" font-family="{font_family}" font-size="11"><tspan font-weight="bold" fill="{PALETTE['orange']}">CGPA    : </tspan><tspan fill="{PALETTE['white']}">8.65 / 10</tspan></text>
    <text x="{lx + 8}" y="156" font-family="{font_family}" font-size="11"><tspan font-weight="bold" fill="{PALETTE['orange']}">Focus   : </tspan><tspan fill="{PALETTE['white']}">Data Analytics &amp; BI</tspan></text>
    <text x="{lx + 8}" y="173" font-family="{font_family}" font-size="11"><tspan font-weight="bold" fill="{PALETTE['orange']}">Location: </tspan><tspan fill="{PALETTE['white']}">Jodhpur, Rajasthan</tspan></text>
    <text x="{lx + 8}" y="190" font-family="{font_family}" font-size="11"><tspan font-weight="bold" fill="{PALETTE['orange']}">Status  : </tspan><tspan fill="{PALETTE['white']}">  Open for Roles</tspan></text>

    <!-- Status indicator circle -->
    <circle cx="{lx + 68}" cy="186.5" r="3.5" fill="{PALETTE['green']}"/>
  </g>""")

    # Highlights
    parts.append(f"""  <g>
    <animate attributeName="opacity" from="0" to="1" begin="0.6s" dur="0.35s" fill="freeze"/>
    <text x="{lx}" y="215" font-family="{font_family}" font-size="11.5" font-weight="bold" fill="{PALETTE['green']}">╭─ 🏆 Key Highlights</text>
    
    <text x="{lx + 8}" y="234" font-family="{font_family}" font-size="11" fill="{PALETTE['green']}">★ 8+ Analytics &amp; AI Projects</text>
    <text x="{lx + 8}" y="251" font-family="{font_family}" font-size="11" fill="{PALETTE['green']}">★ Microsoft Power BI Certified</text>
    <text x="{lx + 8}" y="268" font-family="{font_family}" font-size="11" fill="{PALETTE['green']}">★ Microsoft Fabric Certified</text>
    <text x="{lx + 8}" y="285" font-family="{font_family}" font-size="11" fill="{PALETTE['green']}">★ Cisco Data Analytics Certified</text>
  </g>""")

    # Vertical Separator between columns
    parts.append(f'<line x1="325" y1="50" x2="325" y2="350" stroke="{PALETTE["border"]}" stroke-width="0.8" opacity="0.6"/>')

    # ============================================================================
    # RIGHT COLUMN (x=340 to 630)
    # ============================================================================
    rx = 340

    # Tech Stack
    parts.append(f"""  <!-- RIGHT COLUMN -->
  <g>
    <animate attributeName="opacity" from="0" to="1" begin="0.5s" dur="0.35s" fill="freeze"/>
    <text x="{rx}" y="58" font-family="{font_family}" font-size="11.5" font-weight="bold" fill="{PALETTE['cyan']}">╭─ 🛠️ Tech Stack</text>
    
    <text x="{rx + 8}" y="77" font-family="{font_family}" font-size="10.5"><tspan font-weight="bold" fill="{PALETTE['cyan']}">BI    : </tspan><tspan fill="{PALETTE['white']}">Power BI · DAX · Fabric</tspan></text>
    <text x="{rx + 8}" y="94" font-family="{font_family}" font-size="10.5"><tspan font-weight="bold" fill="{PALETTE['cyan']}">DB    : </tspan><tspan fill="{PALETTE['white']}">PostgreSQL · MongoDB</tspan></text>
    <text x="{rx + 8}" y="111" font-family="{font_family}" font-size="10.5"><tspan font-weight="bold" fill="{PALETTE['cyan']}">Lang  : </tspan><tspan fill="{PALETTE['white']}">Python · SQL · JS · C++</tspan></text>
    <text x="{rx + 8}" y="128" font-family="{font_family}" font-size="10.5"><tspan font-weight="bold" fill="{PALETTE['cyan']}">AI    : </tspan><tspan fill="{PALETTE['white']}">Gemini · Claude · DeepSeek</tspan></text>
  </g>""")

    # Featured Projects
    parts.append(f"""  <g>
    <animate attributeName="opacity" from="0" to="1" begin="0.7s" dur="0.35s" fill="freeze"/>
    <text x="{rx}" y="153" font-family="{font_family}" font-size="11.5" font-weight="bold" fill="{PALETTE['blue']}">╭─ 📂 Featured Projects</text>
    
    <text x="{rx + 8}" y="172" font-family="{font_family}" font-size="11" font-weight="bold" fill="{PALETTE['cyan']}">🚀 Velora AI <tspan font-weight="normal" fill="{PALETTE['muted']}">— MERN + AI Builder</tspan></text>
    <text x="{rx + 8}" y="189" font-family="{font_family}" font-size="11" font-weight="bold" fill="{PALETTE['cyan']}">📦 Samsung Supply Chain <tspan font-weight="normal" fill="{PALETTE['muted']}">— Power BI</tspan></text>
    <text x="{rx + 8}" y="206" font-family="{font_family}" font-size="11" font-weight="bold" fill="{PALETTE['cyan']}">🎵 Spotify Top 50 <tspan font-weight="normal" fill="{PALETTE['muted']}">— DAX Analytics</tspan></text>
    <text x="{rx + 8}" y="223" font-family="{font_family}" font-size="11" font-weight="bold" fill="{PALETTE['cyan']}">🍔 Swiggy vs Zomato <tspan font-weight="normal" fill="{PALETTE['muted']}">— PostgreSQL BI</tspan></text>
  </g>""")

    # Certifications
    parts.append(f"""  <g>
    <animate attributeName="opacity" from="0" to="1" begin="0.9s" dur="0.35s" fill="freeze"/>
    <text x="{rx}" y="248" font-family="{font_family}" font-size="11.5" font-weight="bold" fill="{PALETTE['yellow']}">╭─ 📜 Certifications</text>
    
    <text x="{rx + 8}" y="267" font-family="{font_family}" font-size="10.5" fill="{PALETTE['white']}">✓ Power BI &amp; Fabric (Microsoft)</text>
    <text x="{rx + 8}" y="284" font-family="{font_family}" font-size="10.5" fill="{PALETTE['white']}">✓ Data Analytics Essentials (Cisco)</text>
  </g>""")

    # Bottom Banner Footer (across full 650px width)
    parts.append(f"""  <g>
    <animate attributeName="opacity" from="0" to="1" begin="1.1s" dur="0.35s" fill="freeze"/>
    <line x1="20" y1="316" x2="{SVG_W - 20}" y2="316" stroke="{PALETTE['border']}" stroke-width="0.8" opacity="0.6"/>
    
    <text x="20" y="336" font-family="{font_family}" font-size="10.5">
      <tspan font-weight="bold" fill="{PALETTE['purple']}">Building: </tspan>
      <tspan fill="{PALETTE['white']}">AI Analytics Platform • Interactive BI Dashboards • MERN AI</tspan>
    </text>
    
    <text x="20" y="353" font-family="{font_family}" font-size="10.5">
      <tspan font-weight="bold" fill="{PALETTE['purple']}">Learning: </tspan>
      <tspan fill="{PALETTE['white']}">Data Engineering • Real-Time Analytics • DeepSeek Pipelines</tspan>
    </text>
    
    <text x="{SVG_W // 2}" y="382" font-family="{font_family}" font-size="10" fill="{PALETTE['muted']}" text-anchor="middle">github.com/{USERNAME}</text>
  </g>""")

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
