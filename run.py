"""
run.py — Master orchestrator for the GitHub Profile README generator.

Usage:
    python run.py                          # full run (fetches avatar + mock contributions)
    python run.py --token ghp_xxxxx        # use real GitHub PAT for contribution data
    python run.py --no-fetch               # skip all network calls (offline mode)
    python run.py --username someone_else  # override username from config

What it does:
  1. Generates github-contribution-animation.svg
  2. Generates terminal-card.svg
  3. Generates info-card.svg
  4. Injects all three into README.md
"""

import argparse
import os
import sys
import time
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Patch config before importing sub-modules (if --username supplied)
import config as _cfg

# Force UTF-8 output so Unicode prints work on Windows consoles
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def _validate_svg(path: str) -> bool:
    """Attempt to parse the SVG as XML to catch malformed output."""
    try:
        ET.parse(path)
        return True
    except ET.ParseError as e:
        print(f"[✗] Invalid XML in {path}: {e}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate premium GitHub Profile README SVGs"
    )
    parser.add_argument("--username", default=None,
                        help=f"GitHub username (default: {_cfg.USERNAME})")
    parser.add_argument("--token",    default=None,
                        help="GitHub PAT for real contribution data (optional)")
    parser.add_argument("--no-fetch", action="store_true",
                        help="Skip all network calls (offline mode)")
    parser.add_argument("--skip-readme", action="store_true",
                        help="Don't update README.md")
    args = parser.parse_args()

    # Override username in config at runtime
    if args.username:
        _cfg.USERNAME = args.username
        print(f"[i] Using username: {_cfg.USERNAME}")

    print("\n+======================================================+")
    print("|  GitHub Profile README -- Premium SVG Generator      |")
    print("+======================================================+\n")

    # ── Step 1: Contribution Graph ──────────────────────────────────────────
    print("▶ [1/4] Generating contribution graph…")
    t0 = time.time()
    from generate_contributions import fetch_contributions, generate as gen_contrib
    token = None if args.no_fetch else args.token
    grid = fetch_contributions(_cfg.USERNAME, token)
    gen_contrib(grid, _cfg.OUT_CONTRIB)
    print(f"    Done in {time.time() - t0:.2f}s")

    # ── Step 2: Terminal ASCII Card ──────────────────────────────────────────
    print("▶ [2/4] Generating terminal ASCII card…")
    t0 = time.time()
    from generate_terminal import fetch_avatar, image_to_ascii, generate as gen_terminal
    img  = None if args.no_fetch else fetch_avatar(_cfg.USERNAME)
    rows = image_to_ascii(img)
    gen_terminal(rows, _cfg.OUT_TERMINAL)
    print(f"    Done in {time.time() - t0:.2f}s")

    # ── Step 3: Neofetch Info Card ───────────────────────────────────────────
    print("▶ [3/4] Generating neofetch info card…")
    t0 = time.time()
    from generate_info_card import generate as gen_info
    gen_info(_cfg.OUT_INFO)
    print(f"    Done in {time.time() - t0:.2f}s")

    # ── Step 4: README Injection ─────────────────────────────────────────────
    if not args.skip_readme:
        print("▶ [4/4] Injecting SVGs into README.md…")
        t0 = time.time()
        from generate_readme import inject
        inject(
            readme_path=_cfg.OUT_README,
            terminal_path=_cfg.OUT_TERMINAL,
            info_path=_cfg.OUT_INFO,
            contrib_path=_cfg.OUT_CONTRIB,
        )
        print(f"    Done in {time.time() - t0:.2f}s")
    else:
        print("▶ [4/4] Skipping README injection (--skip-readme)")

    # ── Validation ───────────────────────────────────────────────────────────
    print("\n▶ Validating SVG XML…")
    all_ok = True
    for path in [_cfg.OUT_CONTRIB, _cfg.OUT_TERMINAL, _cfg.OUT_INFO]:
        ok = _validate_svg(path)
        icon = "✓" if ok else "✗"
        name = os.path.basename(path)
        size = os.path.getsize(path) / 1024
        print(f"    [{icon}] {name:<45}  {size:6.1f} KB")
        if not ok:
            all_ok = False

    print("\n" + ("=" * 56))
    if all_ok:
        print("  [OK] All files generated and validated successfully!")
    else:
        print("  [!!] Some files had XML errors -- check output above.")
    print("=" * 56)
    print()
    print("  Files written:")
    print(f"    • {_cfg.OUT_CONTRIB}")
    print(f"    • {_cfg.OUT_TERMINAL}")
    print(f"    • {_cfg.OUT_INFO}")
    if not args.skip_readme:
        print(f"    • {_cfg.OUT_README}")
    print()
    print("  Next steps:")
    print("    1. Open the .svg files in your browser to preview animations.")
    print("    2. git add . && git commit -m 'feat: premium profile SVGs'")
    print("    3. git push → view at github.com/{}\n".format(_cfg.USERNAME))


if __name__ == "__main__":
    main()
