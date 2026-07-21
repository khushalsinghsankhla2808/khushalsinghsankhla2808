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

# Force UTF-8 output so Unicode prints work cleanly on Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Import master config and modular generators to ensure 100% synchronization
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from generate_contributions import fetch_contributions, generate as gen_contrib
from generate_terminal import fetch_avatar, image_to_ascii, generate as gen_terminal
from generate_info_card import generate as gen_info
from generate_readme import inject as inject_readme


def main():
    print("Generating GitHub Profile README Animated SVG Assets...")

    print("▶ [1/4] Generating contribution graph…")
    grid = fetch_contributions(config.USERNAME, token=None)
    gen_contrib(grid, config.OUT_CONTRIB)
    print("[SUCCESS] Generated github-contribution-animation.svg")

    print("▶ [2/4] Generating terminal ASCII card…")
    img = fetch_avatar(config.USERNAME)
    rows = image_to_ascii(img)
    gen_terminal(rows, config.OUT_TERMINAL)
    print("[SUCCESS] Generated terminal-card.svg")

    print("▶ [3/4] Generating neofetch info card…")
    gen_info(config.OUT_INFO)
    print("[SUCCESS] Generated info-card.svg")

    print("▶ [4/4] Injecting SVGs into README.md…")
    inject_readme(
        readme_path=config.OUT_README,
        terminal_path=config.OUT_TERMINAL,
        info_path=config.OUT_INFO,
        contrib_path=config.OUT_CONTRIB,
    )
    print("[SUCCESS] Updated README.md with SVG assets")

    print("\nAll assets generated and README updated successfully!")


if __name__ == "__main__":
    main()
