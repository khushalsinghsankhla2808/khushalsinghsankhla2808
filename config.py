"""
config.py — Central configuration for the GitHub Profile README generator.
Edit this file to customize all three SVG cards without touching the generator scripts.
"""

# ──────────────────────────────────────────────────────────────────────────────
# GitHub Identity
# ──────────────────────────────────────────────────────────────────────────────
USERNAME     = "khushalsinghsankhla2808"
DISPLAY_NAME = "Khushal Singh Sankhla"

# ──────────────────────────────────────────────────────────────────────────────
# Info Card Content
# ──────────────────────────────────────────────────────────────────────────────
ABOUT_LINE   = "MCA @ JECRC | Data Analytics & AI Developer"
LOCATION     = "Jodhpur, Rajasthan, India"
STACK        = [
    "Power BI / DAX / Fabric",
    "Python / SQL / C++",
    "PostgreSQL / MongoDB",
    "React / Node.js / Express",
    "Pandas / NumPy / Seaborn",
    "AI (Claude / Gemini / DeepSeek)",
]
HIGHLIGHTS   = [
    "CGPA: 8.65/10 @ JECRC",
    "8+ Analytics & AI Projects",
    "Microsoft Certified Power BI",
    "Cisco Data Analytics Certified",
]

# ──────────────────────────────────────────────────────────────────────────────
# Color Palette (Cyberpunk / GitHub Dark)
# ──────────────────────────────────────────────────────────────────────────────
PALETTE = {
    "bg":           "#0d1117",
    "surface":      "#161b22",
    "border":       "#30363d",
    "text":         "#e6edf3",
    "muted":        "#8b949e",
    # Neon accents
    "cyan":         "#00ffff",
    "green":        "#39d353",
    "green_dim":    "#26a641",
    "green_mid":    "#006d32",
    "green_dark":   "#0e4429",
    "orange":       "#ff8c00",
    "blue":         "#58a6ff",
    "purple":       "#c084fc",
    "red":          "#ff4444",
    "yellow":       "#ffd700",
    "white":        "#ffffff",
    # Contribution levels
    "contrib_0":    "#161b22",
    "contrib_1":    "#0e4429",
    "contrib_2":    "#006d32",
    "contrib_3":    "#26a641",
    "contrib_4":    "#39d353",
}

# ──────────────────────────────────────────────────────────────────────────────
# Output Paths
# ──────────────────────────────────────────────────────────────────────────────
import os
ROOT = os.path.dirname(os.path.abspath(__file__))

OUT_CONTRIB  = os.path.join(ROOT, "github-contribution-animation.svg")
OUT_TERMINAL = os.path.join(ROOT, "terminal-card.svg")
OUT_INFO     = os.path.join(ROOT, "info-card.svg")
OUT_README   = os.path.join(ROOT, "README.md")

# ──────────────────────────────────────────────────────────────────────────────
# Animation Timing
# ──────────────────────────────────────────────────────────────────────────────
ANIM = {
    # Contribution graph
    "contrib_cell_stagger":  0.025,   # seconds between each diagonal band
    "contrib_reveal_dur":    0.3,     # duration of each cell's fade-in
    "contrib_glint_dur":     0.25,    # duration of the specular glint

    # Terminal card
    "terminal_row_stagger":  0.10,    # seconds between each ASCII row reveal
    "terminal_reveal_dur":   0.12,    # width-reveal animation duration per row
    "terminal_cursor_dur":   0.09,    # cursor travel duration per row

    # Info card
    "info_line_stagger":     0.06,    # seconds between each neofetch line
    "info_slide_dur":        0.35,    # slide-up duration per line
}
