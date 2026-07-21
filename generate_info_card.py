"""
generate_info_card.py
─────────────────────
Generates a redesigned, premium 2-column NeoFetch terminal SVG (`info-card.svg`):
  • 2-column layout matching the user's latest resume
  • Left column: Header (animated typing name), System Info, About & Focus, Highlights
  • Right column: Tech Stack (categorized with emojis), Featured Projects (clickable with hover glow), Certifications
  • Unified bottom footer: Currently Building and Always Learning banner
  • CSS-based interactive animations: Animated gradient border, pulsing status, name typing, section headers glow

Run:  python generate_info_card.py
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PALETTE, OUT_INFO, USERNAME, DISPLAY_NAME

SVG_W = 820
SVG_H = 610

def _escape_svg(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )

def generate(output_path: str = OUT_INFO) -> None:
    parts = []

    # SVG root
    parts.append(f"""<svg xmlns="http://www.w3.org/2000/svg"
     width="{SVG_W}" height="{SVG_H}"
     viewBox="0 0 {SVG_W} {SVG_H}"
     role="img" aria-label="NeoFetch Terminal Info Card — {DISPLAY_NAME}">""")

    # Defs: filters, gradients, scanline pattern
    parts.append(f"""  <defs>
    <!-- Card glass background gradient -->
    <linearGradient id="info-bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%"   stop-color="#121824" stop-opacity="0.97"/>
      <stop offset="100%" stop-color="#0a0d14" stop-opacity="0.98"/>
    </linearGradient>

    <!-- Animated neon border gradient -->
    <linearGradient id="border-glow-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{PALETTE['cyan']}">
        <animate attributeName="stop-color" values="{PALETTE['cyan']};{PALETTE['purple']};{PALETTE['green']};{PALETTE['orange']};{PALETTE['cyan']}" dur="8s" repeatCount="indefinite"/>
      </stop>
      <stop offset="50%" stop-color="{PALETTE['purple']}">
        <animate attributeName="stop-color" values="{PALETTE['purple']};{PALETTE['green']};{PALETTE['orange']};{PALETTE['cyan']};{PALETTE['purple']}" dur="8s" repeatCount="indefinite"/>
      </stop>
      <stop offset="100%" stop-color="{PALETTE['green']}">
        <animate attributeName="stop-color" values="{PALETTE['green']};{PALETTE['orange']};{PALETTE['cyan']};{PALETTE['purple']};{PALETTE['green']}" dur="8s" repeatCount="indefinite"/>
      </stop>
    </linearGradient>

    <!-- Title bar gradient -->
    <linearGradient id="info-titlebar-grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%"   stop-color="#22272e"/>
      <stop offset="100%" stop-color="#161b22"/>
    </linearGradient>

    <!-- Outer drop shadow glow -->
    <filter id="info-card-shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="10" result="blur"/>
      <feFlood flood-color="{PALETTE['purple']}" flood-opacity="0.25" result="color"/>
      <feComposite in="color" in2="blur" operator="in" result="glow"/>
      <feMerge>
        <feMergeNode in="glow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Scan-line texture -->
    <pattern id="info-scanlines" x="0" y="0" width="1" height="3" patternUnits="userSpaceOnUse">
      <rect width="1" height="1" fill="rgba(0,0,0,0.22)"/>
    </pattern>

    <!-- Text glow filter -->
    <filter id="text-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="1.5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Name typing animation clipPath -->
    <clipPath id="name-clip">
      <rect x="30" y="50" width="0" height="30">
        <animate attributeName="width" from="0" to="340" dur="1.8s" fill="freeze" begin="0.2s"
                 calcMode="spline" keySplines="0.25 0.1 0.25 1" keyTimes="0;1"/>
      </rect>
    </clipPath>
  </defs>""")

    # Stylesheet for transitions, fonts, and interactive states
    # We embed standard Google Font 'Fira Code' or fallback monospace
    parts.append(f"""  <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&amp;display=swap');
    
    .terminal-text {{
      font-family: 'Fira Code', 'SF Mono', 'Courier New', Courier, monospace;
      font-size: 11px;
      fill: {PALETTE['text']};
    }}
    .name-title {{
      font-family: 'Fira Code', 'SF Mono', 'Courier New', Courier, monospace;
      font-size: 18px;
      font-weight: 700;
      fill: {PALETTE['cyan']};
    }}
    .subtitle {{
      font-family: 'Fira Code', 'SF Mono', 'Courier New', Courier, monospace;
      font-size: 10px;
      fill: {PALETTE['muted']};
    }}
    .section-title {{
      font-family: 'Fira Code', 'SF Mono', 'Courier New', Courier, monospace;
      font-size: 12px;
      font-weight: 700;
      fill: {PALETTE['yellow']};
      filter: url(#text-glow);
    }}
    .label {{
      font-weight: 700;
      fill: {PALETTE['orange']};
    }}
    .project-link {{
      text-decoration: none;
    }}
    .project-title {{
      font-weight: 700;
      fill: {PALETTE['blue']};
      cursor: pointer;
      transition: fill 0.2s, filter 0.2s;
    }}
    .project-link:hover .project-title {{
      fill: {PALETTE['cyan']};
      filter: url(#text-glow);
    }}
    .banner-label {{
      font-weight: 700;
      fill: {PALETTE['purple']};
    }}
  </style>""")

    # Outer Glass Box and Title Bar
    parts.append(f"""  <!-- Outer background and glass blur -->
  <rect x="2" y="2" width="{SVG_W - 4}" height="{SVG_H - 4}" rx="12"
        fill="url(#info-bg-grad)" stroke="url(#border-glow-grad)" stroke-width="2.5"
        filter="url(#info-card-shadow)"/>

  <!-- Title bar chrome -->
  <rect x="3" y="3" width="{SVG_W - 6}" height="32" rx="9" fill="url(#info-titlebar-grad)"/>
  <rect x="3" y="25" width="{SVG_W - 6}" height="10" fill="#161b22"/>
  <line x1="3" y1="35" x2="{SVG_W - 3}" y2="35" stroke="{PALETTE['border']}" stroke-width="1" opacity="0.6"/>

  <!-- Window buttons -->
  <circle cx="20" cy="18" r="6" fill="{PALETTE['red']}"/>
  <circle cx="40" cy="18" r="6" fill="{PALETTE['yellow']}"/>
  <circle cx="60" cy="18" r="6" fill="{PALETTE['green']}"/>

  <!-- Title text -->
  <text x="{SVG_W // 2}" y="22" class="terminal-text" fill="{PALETTE['muted']}" text-anchor="middle" font-size="11">
    neofetch — {USERNAME}@github
  </text>""")

    # ============================================================================
    # LEFT COLUMN
    # ============================================================================
    left_x = 30
    
    parts.append(f"""  <!-- ================= LEFT COLUMN ================= -->
  <!-- Header identity -->
  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="0s" dur="0.4s" fill="freeze"/>
    <text x="{left_x}" y="70" class="name-title" clip-path="url(#name-clip)">{DISPLAY_NAME}</text>
    <text x="{left_x}" y="92" class="subtitle">{_escape_svg("Data Analytics • Business Intelligence • AI Developer")}</text>
    <text x="{left_x}" y="110" class="terminal-text" fill="{PALETTE['muted']}">
      📂 github.com/{USERNAME}
    </text>
    
    <!-- Typing cursor block -->
    <rect x="{left_x}" y="53" width="8" height="19" fill="{PALETTE['cyan']}" opacity="0">
      <animate attributeName="opacity" from="0" to="1" begin="0.2s" dur="0.01s" fill="freeze"/>
      <animate attributeName="x" from="{left_x}" to="{left_x + 230}" begin="0.2s" dur="1.8s" fill="freeze"
               calcMode="spline" keySplines="0.25 0.1 0.25 1" keyTimes="0;1"/>
      <animate attributeName="opacity" values="1;0;1" dur="0.8s" begin="2.0s" repeatCount="indefinite"/>
    </rect>
    
    <line x1="{left_x}" y1="125" x2="380" y2="125" stroke="{PALETTE['border']}" stroke-width="0.8" opacity="0.5"/>
  </g>""")

    # System Information Section
    parts.append(f"""  <!-- System Info -->
  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="0.3s" dur="0.4s" fill="freeze"/>
    <text x="{left_x}" y="150" class="section-title">╭─ 🖥️ System Information</text>
    
    <!-- OS -->
    <text x="{left_x + 10}" y="174" class="terminal-text"><tspan class="label">OS      </tspan> GitHub • Linux 6.x</text>
    <!-- Shell -->
    <text x="{left_x + 10}" y="194" class="terminal-text"><tspan class="label">Shell   </tspan> zsh + oh-my-zsh</text>
    <!-- Location -->
    <text x="{left_x + 10}" y="214" class="terminal-text"><tspan class="label">Location</tspan> Jodhpur, Rajasthan, India</text>
    <!-- Status -->
    <text x="{left_x + 10}" y="234" class="terminal-text"><tspan class="label">Status  </tspan>   Open to Data Analytics Opportunities</text>
    
    <!-- Pulsing Status Circle -->
    <g transform="translate({left_x + 72}, 230.5)">
      <circle cx="0" cy="0" r="4" fill="{PALETTE['green']}"/>
      <circle cx="0" cy="0" r="4" fill="none" stroke="{PALETTE['green']}" stroke-width="1.5">
        <animate attributeName="r" values="4;9;4" dur="2s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="1;0;1" dur="2s" repeatCount="indefinite"/>
      </circle>
    </g>
  </g>""")

    # About & Focus Section
    parts.append(f"""  <!-- About & Focus -->
  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="0.6s" dur="0.4s" fill="freeze"/>
    <text x="{left_x}" y="270" class="section-title">╭─ 🎓 About &amp; Focus</text>
    
    <text x="{left_x + 10}" y="294" class="terminal-text"><tspan class="label">Program </tspan> MCA @ JECRC University</text>
    <text x="{left_x + 10}" y="314" class="terminal-text"><tspan class="label">CGPA    </tspan> 8.65 / 10</text>
    <text x="{left_x + 10}" y="334" class="terminal-text"><tspan class="label">Focus On</tspan> • Data Analytics</text>
    <text x="{left_x + 68}" y="354" class="terminal-text">• Business Intelligence</text>
    <text x="{left_x + 68}" y="374" class="terminal-text">• SQL Development</text>
    <text x="{left_x + 68}" y="394" class="terminal-text">• Data Engineering &amp; AI Applications</text>
  </g>""")

    # Highlights Section
    parts.append(f"""  <!-- Highlights -->
  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="0.9s" dur="0.4s" fill="freeze"/>
    <text x="{left_x}" y="430" class="section-title">╭─ 🏆 Highlights</text>
    
    <text x="{left_x + 10}" y="454" class="terminal-text" fill="{PALETTE['cyan']}">★ CGPA 8.65 / 10</text>
    <text x="{left_x + 10}" y="474" class="terminal-text" fill="{PALETTE['cyan']}">★ 8+ Analytics &amp; AI Projects</text>
    <text x="{left_x + 10}" y="494" class="terminal-text" fill="{PALETTE['cyan']}">★ Microsoft Power BI Certified</text>
    <text x="{left_x + 10}" y="514" class="terminal-text" fill="{PALETTE['cyan']}">★ Microsoft Fabric Certified</text>
    <text x="{left_x + 10}" y="534" class="terminal-text" fill="{PALETTE['cyan']}">★ Cisco Data Analytics Certified</text>
  </g>""")

    # ============================================================================
    # RIGHT COLUMN
    # ============================================================================
    right_x = 425

    parts.append(f"""  <!-- ================= RIGHT COLUMN ================= -->
  <!-- Tech Stack -->
  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="0.5s" dur="0.4s" fill="freeze"/>
    <text x="{right_x}" y="70" class="section-title">╭─ 🛠️ Tech Stack</text>
    
    <!-- Languages -->
    <text x="{right_x + 10}" y="94" class="terminal-text">
      <tspan class="label">Languages: </tspan> 🐍 Python  🗄️ SQL  ⚛️ JS  ☕ Java  💻 C++
    </text>
    <!-- BI -->
    <text x="{right_x + 10}" y="114" class="terminal-text">
      <tspan class="label">BI Tools:  </tspan> 📊 Power BI  📈 DAX  🔄 Query M  📦 Fabric
    </text>
    <!-- Databases -->
    <text x="{right_x + 10}" y="134" class="terminal-text">
      <tspan class="label">Databases: </tspan> 🐘 PostgreSQL  🐬 MySQL  🍃 MongoDB
    </text>
    <!-- Analytics -->
    <text x="{right_x + 10}" y="154" class="terminal-text">
      <tspan class="label">Analytics: </tspan> 🐼 Pandas  🔢 NumPy  📉 Matplotlib / Seaborn
    </text>
    <!-- Web -->
    <text x="{right_x + 10}" y="174" class="terminal-text">
      <tspan class="label">Web:       </tspan> ⚛️ React  🟢 Node.js  ⚡ Express.js
    </text>
    <!-- Dev Tools -->
    <text x="{right_x + 10}" y="194" class="terminal-text">
      <tspan class="label">Dev Tools: </tspan> 🔧 Git/GitHub  📝 VS Code  🛠️ Vercel / Render
    </text>
    <!-- AI Tools -->
    <text x="{right_x + 10}" y="214" class="terminal-text">
      <tspan class="label">AI Tools:  </tspan> 🧠 Claude AI  ✨ Gemini Flash  🛸 Antigravity
    </text>
  </g>""")

    # Featured Projects Section (Clickable)
    parts.append(f"""  <!-- Featured Projects -->
  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="0.8s" dur="0.4s" fill="freeze"/>
    <text x="{right_x}" y="250" class="section-title">╭─ 📂 Featured Projects</text>
    
    <!-- Project 1 -->
    <a href="https://github.com/{USERNAME}/Velora-AI" target="_blank" class="project-link">
      <text x="{right_x + 10}" y="274" class="terminal-text project-title">🚀 Velora AI</text>
    </a>
    <text x="{right_x + 20}" y="290" class="terminal-text" fill="{PALETTE['muted']}">
      • MERN &amp; AI (Gemini/DeepSeek) Website Builder
    </text>

    <!-- Project 2 -->
    <a href="https://github.com/{USERNAME}/Samsung-Supply-Chain" target="_blank" class="project-link">
      <text x="{right_x + 10}" y="314" class="terminal-text project-title">📦 Samsung Supply Chain Dashboard</text>
    </a>
    <text x="{right_x + 20}" y="330" class="terminal-text" fill="{PALETTE['muted']}">
      • Power BI Dashboard with Star Schema &amp; KPI Analytics
    </text>

    <!-- Project 3 -->
    <a href="https://github.com/{USERNAME}/Spotify-Analytics" target="_blank" class="project-link">
      <text x="{right_x + 10}" y="354" class="terminal-text project-title">🎵 Spotify Analytics Dashboard</text>
    </a>
    <text x="{right_x + 20}" y="370" class="terminal-text" fill="{PALETTE['muted']}">
      • Music analytics using DAX &amp; Power Query M
    </text>

    <!-- Project 4 -->
    <a href="https://github.com/{USERNAME}/Swiggy-vs-Zomato-SQL" target="_blank" class="project-link">
      <text x="{right_x + 10}" y="394" class="terminal-text project-title">🍔 Swiggy vs Zomato SQL Analysis</text>
    </a>
    <text x="{right_x + 20}" y="410" class="terminal-text" fill="{PALETTE['muted']}">
      • Advanced PostgreSQL analytics with Power BI
    </text>
  </g>""")

    # Certifications Section
    parts.append(f"""  <!-- Certifications -->
  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="1.1s" dur="0.4s" fill="freeze"/>
    <text x="{right_x}" y="445" class="section-title">╭─ 🎓 Certifications</text>
    
    <text x="{right_x + 10}" y="469" class="terminal-text">✓ Microsoft Power BI Certified (Microsoft Learn)</text>
    <text x="{right_x + 10}" y="489" class="terminal-text">✓ Microsoft Fabric Environment (Microsoft Learn)</text>
    <text x="{right_x + 10}" y="509" class="terminal-text">✓ Cisco Data Analytics Essentials (Cisco NetAcad)</text>
  </g>""")

    # ============================================================================
    # BOTTOM FOOTER BANNER
    # ============================================================================
    parts.append(f"""  <!-- Bottom Banner / Footer -->
  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="1.4s" dur="0.4s" fill="freeze"/>
    
    <line x1="{left_x}" y1="550" x2="{SVG_W - left_x}" y2="550" stroke="{PALETTE['border']}" stroke-width="0.8" opacity="0.5"/>
    
    <!-- Currently Building -->
    <text x="{left_x}" y="572" class="terminal-text">
      <tspan class="banner-label">Currently Building: </tspan>
      AI Analytics Platform • Interactive BI Dashboards • Data Engineering &amp; Open Source
    </text>
    
    <!-- Always Learning -->
    <text x="{left_x}" y="590" class="terminal-text">
      <tspan class="banner-label">Always Learning:    </tspan>
      Data Analytics • Business Intelligence • Machine Learning • Cloud Data • AI Dev
    </text>
  </g>""")

    # Scanlines Overlay
    parts.append(f"""  <!-- Scanline texture overlay -->
  <rect x="3" y="3" width="{SVG_W - 6}" height="{SVG_H - 6}" rx="10" fill="url(#info-scanlines)" opacity="0.1" pointer-events="none"/>
</svg>""")

    svg_content = "\n".join(parts)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"[✓] Written: {output_path}  ({len(svg_content):,} bytes)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate info-card.svg")
    parser.add_argument("--output", default=OUT_INFO)
    args = parser.parse_args()
    generate(args.output)
