"""
generate_contributions.py
─────────────────────────
Generates `github-contribution-animation.svg`:
  • 53-week × 7-day contribution calendar
  • Diagonal slant-reveal (bottom-left → top-right) via SMIL
  • Per-cell specular glint that flashes then settles into contribution color
  • Outer neon glow filter on Level 3/4 cells
  • Breathing neon scan-line header

Run:  python generate_contributions.py
      python generate_contributions.py --token ghp_xxxx
"""

import argparse
import math
import os
import random
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PALETTE, OUT_CONTRIB, ANIM, USERNAME

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────
WEEKS        = 53
DAYS         = 7
CELL_SIZE    = 11
CELL_GAP     = 3
CELL_STEP    = CELL_SIZE + CELL_GAP   # 14px
CELL_RADIUS  = 2

MARGIN_LEFT  = 28    # room for day labels
MARGIN_TOP   = 52    # room for header + month labels
MARGIN_BOT   = 20
MARGIN_RIGHT = 20

GRID_W  = WEEKS * CELL_STEP - CELL_GAP
GRID_H  = DAYS  * CELL_STEP - CELL_GAP
SVG_W   = MARGIN_LEFT + GRID_W + MARGIN_RIGHT   # ≈ 786
SVG_H   = MARGIN_TOP  + GRID_H + MARGIN_BOT     # ≈ 170

CONTRIB_COLORS = [
    PALETTE["contrib_0"],
    PALETTE["contrib_1"],
    PALETTE["contrib_2"],
    PALETTE["contrib_3"],
    PALETTE["contrib_4"],
]

DAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]


# ──────────────────────────────────────────────────────────────────────────────
# Data fetching / mock generation
# ──────────────────────────────────────────────────────────────────────────────

def fetch_contributions(username: str, token: str | None) -> list[list[int]]:
    """Returns a 53×7 grid (weeks × days) of contribution levels 0-4."""
    if token:
        try:
            return _fetch_github_graphql(username, token)
        except Exception as e:
            print(f"[warn] GraphQL fetch failed ({e}), trying public HTML fetch.")
    try:
        return _fetch_github_html(username)
    except Exception as e:
        print(f"[warn] HTML fetch failed ({e}), using mock data.")
    return _mock_contributions(username)


def _fetch_github_html(username: str) -> list[list[int]]:
    """Fetch real public contribution levels by parsing GitHub's public contribution calendar page."""
    import re
    import requests
    url = f"https://github.com/users/{username}/contributions"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()

    # Extract id="contribution-day-component-ROW-COL" and data-level="LEVEL"
    matches = re.findall(
        r'id=["\']contribution-day-component-(\d+)-(\d+)["\'][^>]*data-level=["\']([0-4])["\']',
        resp.text
    )

    if not matches:
        # Fallback attribute ordering search
        matches = re.findall(
            r'data-level=["\']([0-4])["\'][^>]*id=["\']contribution-day-component-(\d+)-(\d+)["\']',
            resp.text
        )
        if matches:
            matches = [(m[1], m[2], m[0]) for m in matches]

    if not matches:
        raise ValueError("Could not parse contribution day components from GitHub HTML")

    max_col = max(int(m[1]) for m in matches)
    num_cols = max(WEEKS, max_col + 1)
    grid = [[0] * DAYS for _ in range(num_cols)]

    for row_str, col_str, lvl_str in matches:
        r = int(row_str)
        c = int(col_str)
        lvl = int(lvl_str)
        if r < DAYS and c < num_cols:
            grid[c][r] = lvl

    return grid[-WEEKS:]



def _fetch_github_graphql(username: str, token: str) -> list[list[int]]:
    """Fetch real contribution data from GitHub GraphQL API."""
    import requests
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays {
                contributionLevel
              }
            }
          }
        }
      }
    }
    """
    resp = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": {"login": username}},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    weeks_raw = (
        data["data"]["user"]["contributionsCollection"]
            ["contributionCalendar"]["weeks"]
    )
    level_map = {
        "NONE":           0,
        "FIRST_QUARTILE": 1,
        "SECOND_QUARTILE":2,
        "THIRD_QUARTILE": 3,
        "FOURTH_QUARTILE":4,
    }
    grid = []
    for week in weeks_raw[-WEEKS:]:
        col = []
        for day in week["contributionDays"]:
            col.append(level_map.get(day["contributionLevel"], 0))
        # pad to 7 days if week is short
        while len(col) < DAYS:
            col.insert(0, 0)
        grid.append(col)
    # pad to 53 weeks
    while len(grid) < WEEKS:
        grid.append([0] * DAYS)
    return grid


def _mock_contributions(username: str) -> list[list[int]]:
    """Generate plausible-looking seeded mock contribution data."""
    rng = random.Random(hash(username) & 0xFFFF_FFFF)
    grid = []
    for w in range(WEEKS):
        col = []
        for d in range(DAYS):
            # Weekends less likely, random bursts
            skip = d in (0, 6) and rng.random() < 0.55
            if skip:
                col.append(0)
                continue
            r = rng.random()
            if r < 0.18:
                col.append(0)
            elif r < 0.42:
                col.append(1)
            elif r < 0.65:
                col.append(2)
            elif r < 0.82:
                col.append(3)
            else:
                col.append(4)
        grid.append(col)
    return grid


# ──────────────────────────────────────────────────────────────────────────────
# Month label positions
# ──────────────────────────────────────────────────────────────────────────────

def _month_labels(start_date: date | None = None) -> list[tuple[int, str]]:
    """Returns list of (x_pixel, month_name) for labeling columns."""
    if start_date is None:
        # figure out the Sunday 52 weeks ago
        today = date.today()
        start_date = today - timedelta(weeks=52, days=today.weekday() + 1)
        start_date -= timedelta(days=start_date.weekday())  # go to Sunday

    labels = []
    seen = set()
    for w in range(WEEKS):
        d = start_date + timedelta(weeks=w)
        if d.month not in seen:
            seen.add(d.month)
            x = MARGIN_LEFT + w * CELL_STEP
            labels.append((x, MONTH_NAMES[d.month - 1]))
    return labels


# ──────────────────────────────────────────────────────────────────────────────
# SVG builders
# ──────────────────────────────────────────────────────────────────────────────

def _defs_block() -> str:
    """SVG <defs>: glow filters, glint gradient, scan-line pattern."""
    return f"""  <defs>
    <!-- Neon glow filter for level 3-4 cells -->
    <filter id="glow-green" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="2.5" result="blur"/>
      <feColorMatrix in="blur" type="matrix"
        values="0 0 0 0 0   0 1 0 0 0.85   0 0 0 0 0.32   0 0 0 18 -7"
        result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="glow-bright" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="3.5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Glint gradient: white flash overlay -->
    <linearGradient id="glint-grad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%"   stop-color="#ffffff" stop-opacity="0.9"/>
      <stop offset="60%"  stop-color="#aaffcc" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>

    <!-- Scan-line overlay texture -->
    <pattern id="scanlines" x="0" y="0" width="1" height="3" patternUnits="userSpaceOnUse">
      <rect width="1" height="1" fill="rgba(0,0,0,0.25)"/>
    </pattern>

    <!-- Header neon gradient -->
    <linearGradient id="header-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%"   stop-color="{PALETTE['green']}"/>
      <stop offset="50%"  stop-color="{PALETTE['cyan']}"/>
      <stop offset="100%" stop-color="{PALETTE['green']}"/>
    </linearGradient>

    <!-- Outer card glow -->
    <filter id="card-glow" x="-5%" y="-5%" width="110%" height="110%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>"""


def _cell_element(col: int, row: int, level: int, cell_id: str) -> str:
    """Return SVG elements for a single contribution cell with SMIL animations."""
    x = MARGIN_LEFT + col * CELL_STEP
    y = MARGIN_TOP  + row * CELL_STEP
    color = CONTRIB_COLORS[level]

    # Diagonal band index: 0 at bottom-left, increases to top-right
    band = col + (DAYS - 1 - row)
    reveal_start  = band * ANIM["contrib_cell_stagger"]
    reveal_end    = reveal_start + ANIM["contrib_reveal_dur"]
    glint_start   = reveal_end
    glint_end     = glint_start + ANIM["contrib_glint_dur"]

    use_glow = level >= 3
    filter_attr = f' filter="url(#glow-green)"' if use_glow else ""

    # Format times
    def ft(t: float) -> str:
        return f"{t:.3f}s"

    # Main cell rect (starts invisible, fades + scales in)
    cell_svg = f"""    <g id="{cell_id}">
      <!-- base rect -->
      <rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" rx="{CELL_RADIUS}" ry="{CELL_RADIUS}"
            fill="{color}"{filter_attr} opacity="0">
        <!-- reveal: fade in -->
        <animate attributeName="opacity"
                 from="0" to="1"
                 begin="{ft(reveal_start)}" dur="{ft(ANIM['contrib_reveal_dur'])}"
                 fill="freeze" calcMode="spline"
                 keySplines="0.25 0 0.25 1" keyTimes="0;1"/>
        <!-- subtle scale-in via y squeeze illusion using height -->
        <animate attributeName="height"
                 from="0" to="{CELL_SIZE}"
                 begin="{ft(reveal_start)}" dur="{ft(ANIM['contrib_reveal_dur'] * 0.7)}"
                 fill="freeze" calcMode="spline"
                 keySplines="0.34 1.56 0.64 1" keyTimes="0;1"/>
        <animate attributeName="y"
                 from="{y + CELL_SIZE // 2}" to="{y}"
                 begin="{ft(reveal_start)}" dur="{ft(ANIM['contrib_reveal_dur'] * 0.7)}"
                 fill="freeze" calcMode="spline"
                 keySplines="0.34 1.56 0.64 1" keyTimes="0;1"/>
      </rect>"""

    # Glint overlay rect (only on non-zero cells)
    if level > 0:
        cell_svg += f"""
      <!-- glint overlay -->
      <rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" rx="{CELL_RADIUS}" ry="{CELL_RADIUS}"
            fill="url(#glint-grad)" opacity="0" pointer-events="none">
        <animate attributeName="opacity"
                 values="0;0.95;0"
                 keyTimes="0;0.4;1"
                 begin="{ft(glint_start)}" dur="{ft(ANIM['contrib_glint_dur'])}"
                 fill="freeze" calcMode="spline"
                 keySplines="0.25 0 0.25 1;0.25 0 0.25 1"/>
      </rect>"""

    cell_svg += "\n    </g>"
    return cell_svg


def _header_block() -> str:
    """Animated header with title and breathing neon underline."""
    title_y = 22
    underline_y = title_y + 8
    return f"""  <!-- Header -->
  <text x="{SVG_W // 2}" y="{title_y}"
        font-family="'Courier New', Courier, monospace"
        font-size="13" font-weight="700" fill="url(#header-grad)"
        text-anchor="middle" letter-spacing="3">
    CONTRIBUTION GRAPH
    <animate attributeName="opacity" values="0.7;1;0.7" dur="3s" repeatCount="indefinite"/>
  </text>
  <!-- Neon underline -->
  <line x1="{SVG_W//2 - 120}" y1="{underline_y}" x2="{SVG_W//2 + 120}" y2="{underline_y}"
        stroke="url(#header-grad)" stroke-width="1" opacity="0.6">
    <animate attributeName="opacity" values="0.3;0.8;0.3" dur="2.5s" repeatCount="indefinite"/>
  </line>"""


def _day_labels() -> str:
    """Mon/Wed/Fri day-of-week labels on left edge."""
    parts = []
    for i, label in enumerate(DAY_LABELS):
        if i % 2 == 1:   # Mon, Wed, Fri (indices 1,3,5 in Sun-based)
            y = MARGIN_TOP + i * CELL_STEP + CELL_SIZE - 1
            parts.append(
                f'  <text x="{MARGIN_LEFT - 4}" y="{y}" '
                f'font-family="\'Courier New\', Courier, monospace" '
                f'font-size="7" fill="{PALETTE["muted"]}" text-anchor="end">{label}</text>'
            )
    return "\n".join(parts)


def _month_labels_svg(month_labels: list[tuple[int, str]]) -> str:
    y = MARGIN_TOP - 5
    parts = []
    for x, name in month_labels:
        parts.append(
            f'  <text x="{x}" y="{y}" '
            f'font-family="\'Courier New\', Courier, monospace" '
            f'font-size="8" fill="{PALETTE["muted"]}">{name}</text>'
        )
    return "\n".join(parts)


def _legend_block() -> str:
    """Color legend at bottom-right."""
    bx = SVG_W - MARGIN_RIGHT - 5 * (CELL_SIZE + 4) - 40
    by = SVG_H - MARGIN_BOT + 5
    parts = [
        f'  <text x="{bx - 4}" y="{by + 9}" '
        f'font-family="\'Courier New\', Courier, monospace" '
        f'font-size="7" fill="{PALETTE["muted"]}" text-anchor="end">Less</text>'
    ]
    for i in range(5):
        lx = bx + i * (CELL_SIZE + 4)
        parts.append(
            f'  <rect x="{lx}" y="{by}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
            f'rx="{CELL_RADIUS}" fill="{CONTRIB_COLORS[i]}"/>'
        )
    ex = bx + 5 * (CELL_SIZE + 4)
    parts.append(
        f'  <text x="{ex}" y="{by + 9}" '
        f'font-family="\'Courier New\', Courier, monospace" '
        f'font-size="7" fill="{PALETTE["muted"]}">More</text>'
    )
    return "\n".join(parts)


def _scanline_overlay() -> str:
    return (
        f'  <rect x="0" y="0" width="{SVG_W}" height="{SVG_H}" '
        f'fill="url(#scanlines)" opacity="0.18" pointer-events="none"/>'
    )


# ──────────────────────────────────────────────────────────────────────────────
# Main generator
# ──────────────────────────────────────────────────────────────────────────────

def generate(grid: list[list[int]], output_path: str = OUT_CONTRIB) -> None:
    month_labels = _month_labels()
    parts: list[str] = []

    # SVG root
    parts.append(f"""<svg xmlns="http://www.w3.org/2000/svg"
     width="{SVG_W}" height="{SVG_H}"
     viewBox="0 0 {SVG_W} {SVG_H}"
     role="img" aria-label="GitHub Contribution Graph — {USERNAME}">""")

    parts.append(_defs_block())

    parts.append(f"""  <a href="https://github.com/{USERNAME}" target="_blank">""")

    # Background
    parts.append(f"""  <!-- Background -->
  <rect width="{SVG_W}" height="{SVG_H}" fill="{PALETTE['bg']}" rx="8"/>
  <!-- Subtle inner border glow -->
  <rect x="1" y="1" width="{SVG_W-2}" height="{SVG_H-2}"
        fill="none" stroke="{PALETTE['green']}" stroke-width="0.5" rx="8" opacity="0.3"/>""")

    # Header
    parts.append(_header_block())

    # Month labels
    parts.append(_month_labels_svg(month_labels))

    # Day labels
    parts.append(_day_labels())

    # Grid cells
    parts.append("  <!-- Contribution cells -->")
    for col, week in enumerate(grid):
        for row, level in enumerate(week):
            cell_id = f"c{col:02d}r{row}"
            parts.append(_cell_element(col, row, level, cell_id))

    # Legend
    parts.append(_legend_block())

    # Scan-line texture
    parts.append(_scanline_overlay())

    # Corner decorations
    parts.append(f"""  <!-- Corner accent -->
  <circle cx="{SVG_W - 10}" cy="10" r="3" fill="{PALETTE['cyan']}" opacity="0.5">
    <animate attributeName="opacity" values="0.2;0.8;0.2" dur="2.1s" repeatCount="indefinite"/>
  </circle>
  <circle cx="10" cy="{SVG_H - 10}" r="2" fill="{PALETTE['green']}" opacity="0.4">
    <animate attributeName="opacity" values="0.2;0.7;0.2" dur="1.7s" repeatCount="indefinite"/>
  </circle>""")

    parts.append("  </a>")
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
        description="Generate github-contribution-animation.svg"
    )
    parser.add_argument("--username", default=USERNAME, help="GitHub username")
    parser.add_argument("--token",    default=None,     help="GitHub PAT (optional)")
    parser.add_argument("--output",   default=OUT_CONTRIB)
    parser.add_argument("--no-fetch", action="store_true",
                        help="Skip network calls, use mock data")
    args = parser.parse_args()

    token = None if args.no_fetch else args.token
    grid = fetch_contributions(args.username, token)
    generate(grid, args.output)
