"""
generate_readme_assets.py
Generates three premium, self-contained, animated SVG files and auto-injects them into GitHub README.md.
"""

import io
import os
import random
import sys
import xml.sax.saxutils as saxutils
from PIL import Image
import requests

# CONFIG dict (all usernames, colors, sizes in one place)
CONFIG = {
    "username": "khushalsinghsankhla2808",
    "name": "Khushal Singh Sankhla",
    "role": "Data Analyst | BI Developer | MCA '27",
    "university": "JECRC University, Jodhpur",
    "cgpa": "8.65 / 10",
    "avatar_url": "https://github.com/khushalsinghsankhla2808.png",
    "colors": {
        "bg": "#0d1117",
        "glass_fill": "rgba(255,255,255,0.03)",
        "glass_stroke": "rgba(255,255,255,0.08)",
        "cyan": "#00d4ff",
        "green": "#39d353",
        "orange": "#f78166",
        "purple": "#a855f7",
        "gray": "#8b949e",
        "dark_gray": "#30363d",
        "white": "#ffffff",
        "contrib_levels": ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"],
    },
    "font_family": "'Courier New', Courier, monospace",
}


def generate_contribution_svg(filename="github-contribution-animation.svg") -> bool:
    """Generates a 900x160 contribution graph with SMIL diagonal slant reveal, white glint, and glows."""
    try:
        random.seed(42)
        width, height = 900, 160
        cols, rows = 53, 7
        sq_size, gap = 11, 3
        grid_w = cols * sq_size + (cols - 1) * gap  # 739
        grid_h = rows * sq_size + (rows - 1) * gap  # 95
        grid_x0 = (width - grid_w) / 2.0  # 80.5
        grid_y0 = 46.0

        month_cols = [0, 4, 8, 13, 17, 22, 26, 31, 35, 40, 44, 48]
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        svg = []
        svg.append('<?xml version="1.0" encoding="UTF-8"?>')
        svg.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">'
        )
        svg.append('  <defs>')
        svg.append('    <filter id="glow-level3" x="-50%" y="-50%" width="200%" height="200%">')
        svg.append('      <feGaussianBlur stdDeviation="2.5" result="blur"/>')
        svg.append('      <feMerge>')
        svg.append('        <feMergeNode in="blur"/>')
        svg.append('        <feMergeNode in="SourceGraphic"/>')
        svg.append('      </feMerge>')
        svg.append('    </filter>')
        svg.append('    <filter id="glow-level4" x="-50%" y="-50%" width="200%" height="200%">')
        svg.append('      <feGaussianBlur stdDeviation="2.5" result="blur"/>')
        svg.append('      <feMerge>')
        svg.append('        <feMergeNode in="blur"/>')
        svg.append('        <feMergeNode in="SourceGraphic"/>')
        svg.append('      </feMerge>')
        svg.append('    </filter>')
        svg.append('  </defs>')

        # Background card
        svg.append(
            f'  <rect width="{width}" height="{height}" fill="{CONFIG["colors"]["bg"]}" stroke="{CONFIG["colors"]["glass_stroke"]}" stroke-width="1" rx="12"/>'
        )

        # Title
        svg.append(
            f'  <text x="20" y="24" fill="{CONFIG["colors"]["gray"]}" font-size="11" font-family="{CONFIG["font_family"]}"><tspan fill="{CONFIG["colors"]["green"]}">● </tspan>Contribution Graph</text>'
        )

        # Month labels
        for col_idx, m_name in zip(month_cols, month_names):
            mx = grid_x0 + col_idx * (sq_size + gap)
            svg.append(
                f'  <text x="{mx:.1f}" y="36" fill="{CONFIG["colors"]["gray"]}" font-size="9" font-family="{CONFIG["font_family"]}">{m_name}</text>'
            )

        # Day labels (Mon, Wed, Fri)
        day_rows = [(1, "Mon"), (3, "Wed"), (5, "Fri")]
        for r_idx, d_name in day_rows:
            dy = grid_y0 + r_idx * (sq_size + gap) + 9
            svg.append(
                f'  <text x="{grid_x0 - 28:.1f}" y="{dy:.1f}" fill="{CONFIG["colors"]["gray"]}" font-size="9" font-family="{CONFIG["font_family"]}">{d_name}</text>'
            )

        # Contribution Data weights
        normal_choices = [0] * 40 + [1] * 25 + [2] * 20 + [3] * 10 + [4] * 5
        burst_choices = [0] * 10 + [1] * 15 + [2] * 25 + [3] * 30 + [4] * 20

        for col in range(cols):
            is_burst = 44 <= col <= 52
            for row in range(rows):
                level = random.choice(burst_choices if is_burst else normal_choices)
                color = CONFIG["colors"]["contrib_levels"][level]

                cx = grid_x0 + col * (sq_size + gap) + sq_size / 2.0
                cy = grid_y0 + row * (sq_size + gap) + sq_size / 2.0
                diag = col + row
                begin_s = diag * 0.015

                filter_attr = ""
                if level == 3:
                    filter_attr = ' filter="url(#glow-level3)"'
                elif level == 4:
                    filter_attr = ' filter="url(#glow-level4)"'

                svg.append(f'  <g transform="translate({cx:.1f}, {cy:.1f})">')
                svg.append(
                    f'    <rect x="-5.5" y="-5.5" width="11" height="11" rx="2" fill="{color}" opacity="0"{filter_attr}>'
                )
                svg.append(
                    f'      <animate attributeName="opacity" from="0" to="1" begin="{begin_s:.3f}s" dur="0.3s" fill="freeze"/>'
                )
                svg.append(
                    f'      <animateTransform attributeName="transform" type="scale" from="0.4" to="1" begin="{begin_s:.3f}s" dur="0.3s" fill="freeze"/>'
                )
                svg.append("    </rect>")
                # Glint Effect
                svg.append('    <rect x="-5.5" y="-5.5" width="11" height="11" rx="2" fill="#ffffff" opacity="0">')
                svg.append(
                    f'      <animate attributeName="opacity" values="0;0.85;0" keyTimes="0;0.5;1" begin="{begin_s:.3f}s" dur="0.4s" fill="freeze"/>'
                )
                svg.append("    </rect>")
                svg.append("  </g>")

        svg.append("</svg>")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(svg))
        return True
    except Exception as e:
        print(f"Error generating contribution SVG: {e}")
        return False


def fetch_avatar_ascii() -> list[str]:
    """Fetches GitHub avatar and converts to 62x31 ASCII art. Falls back on network failure."""
    chars = ["@", "#", "S", "%", "?", "*", "+", ";", ":", "."]
    try:
        resp = requests.get(CONFIG["avatar_url"], timeout=5)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("L")
        img = img.resize((62, 31), Image.Resampling.LANCZOS)

        lines = []
        for y in range(31):
            row = ""
            for x in range(62):
                p = img.getpixel((x, y))
                idx = int(p / 255.0 * (len(chars) - 1))
                row += chars[idx]
            lines.append(row)
        return lines
    except Exception as e:
        print(f"[WARNING] Avatar fetch failed ({e}). Using fallback ASCII pattern.")
        # Fallback 31x62 geometric portrait pattern
        fallback = []
        for y in range(31):
            row = ""
            for x in range(62):
                dx = (x - 31) / 15.0
                dy = (y - 15) / 8.0
                dist = int((dx * dx + dy * dy) * 3)
                idx = min(len(chars) - 1, max(0, dist))
                row += chars[idx]
            fallback.append(row)
        return fallback


def generate_terminal_card_svg(filename="terminal-card.svg") -> bool:
    """Generates a 520x380 terminal window with animated row reveal ASCII portrait and typewriter footer."""
    try:
        width, height = 520, 380
        ascii_rows = fetch_avatar_ascii()

        svg = []
        svg.append('<?xml version="1.0" encoding="UTF-8"?>')
        svg.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">'
        )

        # Outer terminal window
        svg.append(
            f'  <rect width="{width}" height="{height}" fill="{CONFIG["colors"]["bg"]}" stroke="{CONFIG["colors"]["glass_stroke"]}" stroke-width="1" rx="12"/>'
        )

        # Title bar rect with rounded top corners
        svg.append(
            '  <path d="M 0 12 A 12 12 0 0 1 12 0 L 508 0 A 12 12 0 0 1 520 12 L 520 36 L 0 36 Z" fill="rgba(255,255,255,0.04)"/>'
        )

        # macOS dots
        svg.append('  <circle cx="20" cy="18" r="6" fill="#ff5f56"/>')
        svg.append('  <circle cx="40" cy="18" r="6" fill="#ffbd2e"/>')
        svg.append('  <circle cx="60" cy="18" r="6" fill="#27c93f"/>')

        # Title text
        title_text = saxutils.escape(f"terminal — {CONFIG['username']}")
        svg.append(
            f'  <text x="260" y="22" fill="{CONFIG["colors"]["gray"]}" font-size="12" font-family="{CONFIG["font_family"]}" text-anchor="middle">{title_text}</text>'
        )

        # ASCII Art Rows Display & Row-by-Row Reveal Animation
        start_y = 52
        row_h = 9.2

        for i, row in enumerate(ascii_rows):
            ry = start_y + i * row_h + 7.5
            escaped_row = saxutils.escape(row)
            begin_t = 0.5 + i * 0.06

            # Row text element
            svg.append(
                f'  <text x="16" y="{ry:.1f}" font-size="9.5" font-family="{CONFIG["font_family"]}" fill="{CONFIG["colors"]["green"]}" xml:space="preserve" visibility="hidden">'
            )
            svg.append(
                f'    <set attributeName="visibility" to="visible" begin="{begin_t:.2f}s" fill="freeze"/>'
            )
            svg.append(f"    {escaped_row}")
            svg.append("  </text>")

            # Cursor block for this row
            cur_y = start_y + i * row_h
            svg.append(
                f'  <rect x="16" y="{cur_y:.1f}" width="6" height="9" fill="#ffffff" visibility="hidden">'
            )
            svg.append(
                f'    <set attributeName="visibility" to="visible" begin="{begin_t:.2f}s" dur="0.06s"/>'
            )
            svg.append(
                f'    <animate attributeName="x" from="16" to="369" begin="{begin_t:.2f}s" dur="0.06s" fill="freeze"/>'
            )
            svg.append("  </rect>")

        # Footer Typewriter lines (below ASCII art)
        line1_begin = 2.5
        line1_dur = 8 * 0.07  # 0.56s
        line2_begin = 3.1
        line2_dur = 21 * 0.07  # 1.47s
        end_time = line2_begin + line2_dur  # 4.57s

        # Footer Line 1: "$ whoami"
        svg.append("  <g>")
        svg.append('    <clipPath id="clip-footer-1">')
        svg.append('      <rect x="16" y="338" width="0" height="15">')
        svg.append(
            f'        <animate attributeName="width" from="0" to="80" begin="{line1_begin:.2f}s" dur="{line1_dur:.2f}s" fill="freeze"/>'
        )
        svg.append("      </rect>")
        svg.append("    </clipPath>")
        svg.append(
            f'    <text x="16" y="350" font-family="{CONFIG["font_family"]}" font-size="11" clip-path="url(#clip-footer-1)">'
        )
        svg.append(
            f'      <tspan fill="{CONFIG["colors"]["cyan"]}">$ </tspan><tspan fill="{CONFIG["colors"]["white"]}">whoami</tspan>'
        )
        svg.append("    </text>")
        svg.append(
            '    <rect x="16" y="340" width="6" height="11" fill="#ffffff" visibility="hidden">'
        )
        svg.append(
            f'      <set attributeName="visibility" to="visible" begin="{line1_begin:.2f}s" dur="{line1_dur:.2f}s"/>'
        )
        svg.append(
            f'      <animate attributeName="x" from="16" to="72" begin="{line1_begin:.2f}s" dur="{line1_dur:.2f}s" fill="freeze"/>'
        )
        svg.append("    </rect>")
        svg.append("  </g>")

        # Footer Line 2: "Khushal Singh Sankhla"
        svg.append("  <g>")
        svg.append('    <clipPath id="clip-footer-2">')
        svg.append('      <rect x="16" y="353" width="0" height="15">')
        svg.append(
            f'        <animate attributeName="width" from="0" to="180" begin="{line2_begin:.2f}s" dur="{line2_dur:.2f}s" fill="freeze"/>'
        )
        svg.append("      </rect>")
        svg.append("    </clipPath>")
        escaped_name = saxutils.escape(CONFIG["name"])
        svg.append(
            f'    <text x="16" y="365" font-family="{CONFIG["font_family"]}" font-size="11" fill="{CONFIG["colors"]["white"]}" clip-path="url(#clip-footer-2)">{escaped_name}</text>'
        )
        # Cursor for Line 2 and blinking final cursor
        svg.append(
            '    <rect x="16" y="355" width="6" height="11" fill="#ffffff" opacity="0">'
        )
        svg.append(
            f'      <set attributeName="opacity" to="1" begin="{line2_begin:.2f}s" dur="{line2_dur:.2f}s"/>'
        )
        svg.append(
            f'      <animate attributeName="x" from="16" to="165" begin="{line2_begin:.2f}s" dur="{line2_dur:.2f}s" fill="freeze"/>'
        )
        svg.append(
            f'      <animate attributeName="opacity" values="1;0;1" keyTimes="0;0.5;1" begin="{end_time:.2f}s" dur="0.8s" repeatCount="indefinite"/>'
        )
        svg.append("    </rect>")
        svg.append("  </g>")

        svg.append("</svg>")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(svg))
        return True
    except Exception as e:
        print(f"Error generating terminal card SVG: {e}")
        return False


def generate_info_card_svg(filename="info-card.svg") -> bool:
    """Generates a 340x380 info card with staggered slide-up and fade-in animation per line."""
    try:
        width, height = 340, 380

        lines_spec = [
            # Header
            {
                "type": "header",
                "text": CONFIG["username"],
                "color": CONFIG["colors"]["purple"],
                "size": 13,
            },
            {
                "type": "sep",
                "text": "─────────────────────",
                "color": CONFIG["colors"]["dark_gray"],
                "size": 11,
            },
            # About
            {
                "type": "pair",
                "label": "OS      :",
                "val": "MCA @ JECRC University",
                "color": CONFIG["colors"]["orange"],
            },
            {"type": "pair", "label": "CGPA    :", "val": CONFIG["cgpa"], "color": CONFIG["colors"]["orange"]},
            {
                "type": "pair",
                "label": "Focus   :",
                "val": "Data Analytics & BI",
                "color": CONFIG["colors"]["orange"],
            },
            {
                "type": "pair",
                "label": "City    :",
                "val": "Jodhpur, Rajasthan",
                "color": CONFIG["colors"]["orange"],
            },
            # Stack
            {"type": "section", "text": "STACK", "color": CONFIG["colors"]["cyan"], "size": 11},
            {
                "type": "pair",
                "label": "BI      :",
                "val": "Power BI · DAX · Fabric",
                "color": CONFIG["colors"]["cyan"],
            },
            {
                "type": "pair",
                "label": "DB      :",
                "val": "PostgreSQL · MongoDB",
                "color": CONFIG["colors"]["cyan"],
            },
            {
                "type": "pair",
                "label": "Lang    :",
                "val": "Python · SQL · JS",
                "color": CONFIG["colors"]["cyan"],
            },
            {
                "type": "pair",
                "label": "AI      :",
                "val": "Gemini · Claude · MERN",
                "color": CONFIG["colors"]["cyan"],
            },
            # Highlights
            {"type": "section", "text": "HIGHLIGHTS", "color": CONFIG["colors"]["green"], "size": 11},
            {"type": "bullet", "text": "★ 8+ End-to-End Projects", "color": CONFIG["colors"]["green"], "size": 11},
            {
                "type": "bullet",
                "text": "★ 4x Microsoft Certifications",
                "color": CONFIG["colors"]["green"],
                "size": 11,
            },
            {
                "type": "bullet",
                "text": "★ Velora AI — MERN + DeepSeek",
                "color": CONFIG["colors"]["green"],
                "size": 11,
            },
            {
                "type": "bullet",
                "text": "★ Samsung Supply Chain BI",
                "color": CONFIG["colors"]["green"],
                "size": 11,
            },
            {
                "type": "bullet",
                "text": "★ Spotify Top 50 Analytics",
                "color": CONFIG["colors"]["green"],
                "size": 11,
            },
            # Footer
            {
                "type": "footer",
                "text": f"github.com/{CONFIG['username']}",
                "color": CONFIG["colors"]["gray"],
                "size": 9,
            },
        ]

        svg = []
        svg.append('<?xml version="1.0" encoding="UTF-8"?>')
        svg.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">'
        )

        # Background card
        svg.append(
            f'  <rect width="{width}" height="{height}" fill="{CONFIG["colors"]["bg"]}" stroke="{CONFIG["colors"]["glass_stroke"]}" stroke-width="1" rx="12"/>'
        )
        # Inner glass panel
        svg.append(
            f'  <rect x="1" y="1" width="{width-2}" height="{height-2}" fill="{CONFIG["colors"]["glass_fill"]}" rx="12"/>'
        )

        curr_y = 26.0
        line_h = 17.0

        for i, item in enumerate(lines_spec):
            actual_begin = 0.3 + i * 0.06

            if item["type"] == "section":
                curr_y += 4.0

            y_pos = curr_y

            svg.append('  <g opacity="0">')
            svg.append(
                f'    <animate attributeName="opacity" from="0" to="1" begin="{actual_begin:.2f}s" dur="0.4s" fill="freeze"/>'
            )
            svg.append(
                f'    <animateTransform attributeName="transform" type="translate" from="0 12" to="0 0" begin="{actual_begin:.2f}s" dur="0.4s" fill="freeze"/>'
            )

            if item["type"] == "header":
                txt = saxutils.escape(item["text"])
                svg.append(
                    f'    <text x="16" y="{y_pos:.1f}" fill="{item["color"]}" font-size="{item["size"]}" font-weight="bold" font-family="{CONFIG["font_family"]}">{txt}</text>'
                )
            elif item["type"] in ("sep", "section", "bullet"):
                txt = saxutils.escape(item["text"])
                svg.append(
                    f'    <text x="16" y="{y_pos:.1f}" fill="{item["color"]}" font-size="{item["size"]}" font-family="{CONFIG["font_family"]}">{txt}</text>'
                )
            elif item["type"] == "pair":
                lbl = saxutils.escape(item["label"])
                val = saxutils.escape(item["val"])
                svg.append(
                    f'    <text x="16" y="{y_pos:.1f}" fill="{item["color"]}" font-size="11" font-family="{CONFIG["font_family"]}">{lbl}</text>'
                )
                svg.append(
                    f'    <text x="100" y="{y_pos:.1f}" fill="{CONFIG["colors"]["white"]}" font-size="11" font-family="{CONFIG["font_family"]}">{val}</text>'
                )
            elif item["type"] == "footer":
                txt = saxutils.escape(item["text"])
                svg.append(
                    f'    <text x="170" y="356" fill="{item["color"]}" font-size="{item["size"]}" font-family="{CONFIG["font_family"]}" text-anchor="middle">{txt}</text>'
                )

            svg.append("  </g>")

            if item["type"] != "footer":
                curr_y += line_h

        svg.append("</svg>")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(svg))
        return True
    except Exception as e:
        print(f"Error generating info card SVG: {e}")
        return False


def inject_into_readme(filename="README.md") -> bool:
    """Auto-injects the generated SVG assets into README.md between marker tags."""
    try:
        start_marker = "<!-- GITHUB-ASSETS-START -->"
        end_marker = "<!-- GITHUB-ASSETS-END -->"

        replacement_block = (
            f"{start_marker}\n"
            '<p align="center">\n'
            "<table>\n"
            "<tr>\n"
            '<td><img src="terminal-card.svg" width="520"/></td>\n'
            '<td><img src="info-card.svg" width="340"/></td>\n'
            "</tr>\n"
            "</table>\n"
            "</p>\n\n"
            '<p align="center">\n'
            '  <img src="github-contribution-animation.svg" width="900"/>\n'
            "</p>\n"
            f"{end_marker}"
        )

        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# {CONFIG['name']}\n\n{replacement_block}\n")
            return True

        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        if start_marker in content and end_marker in content:
            pre = content.split(start_marker)[0]
            post = content.split(end_marker)[1]
            new_content = pre + replacement_block + post
        elif "<!-- PROFILE-START -->" in content and "<!-- PROFILE-END -->" in content:
            pre = content.split("<!-- PROFILE-START -->")[0]
            post = content.split("<!-- PROFILE-END -->")[1]
            new_content = pre + replacement_block + post
        else:
            lines = content.splitlines()
            header_idx = -1
            for idx, line in enumerate(lines):
                if line.startswith("#"):
                    header_idx = idx
                    break
            if header_idx != -1:
                lines.insert(header_idx + 1, "\n" + replacement_block + "\n")
                new_content = "\n".join(lines)
            else:
                new_content = replacement_block + "\n\n" + content

        with open(filename, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"Error injecting into README.md: {e}")
        return False


def main():
    print("Generating GitHub Profile README Animated SVG Assets...")

    success_contrib = generate_contribution_svg()
    if success_contrib:
        print("[SUCCESS] Generated github-contribution-animation.svg")
    else:
        print("[FAILURE] Failed to generate github-contribution-animation.svg")

    success_terminal = generate_terminal_card_svg()
    if success_terminal:
        print("[SUCCESS] Generated terminal-card.svg")
    else:
        print("[FAILURE] Failed to generate terminal-card.svg")

    success_info = generate_info_card_svg()
    if success_info:
        print("[SUCCESS] Generated info-card.svg")
    else:
        print("[FAILURE] Failed to generate info-card.svg")

    success_readme = inject_into_readme()
    if success_readme:
        print("[SUCCESS] Updated README.md with SVG assets")
    else:
        print("[FAILURE] Failed to update README.md")

    if success_contrib and success_terminal and success_info and success_readme:
        print("\nAll assets generated and README updated successfully!")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
