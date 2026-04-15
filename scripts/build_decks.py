# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Build 4 optimized decks from Clash Royale player data.

Modes:
  war  — No card overlap across decks (for Clan War).
  best — Cards CAN repeat across decks (strongest possible per archetype).

Priority: 1) Synergy 2) Card Level 3) Heroes 4) Evos
Each deck has 3 evo/hero slots: 1 Hero + 1 Evo + 1 Flex (Hero or Evo).
"""

import argparse
import json
import os
import sys
import tempfile

try:
    from cr_styles import build_top_cards_text
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from cr_styles import build_top_cards_text


def main():
    parser = argparse.ArgumentParser(description="Build CR decks (war or best)")
    parser.add_argument("--input", default="cr_player_data.json", help="Input JSON path")
    parser.add_argument("--output", default=None, help="Output txt path")
    parser.add_argument("--mode", choices=["war", "best"], default="war",
                        help="war = no card overlap, best = cards can repeat")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        print("Run fetch_player.py first to get player data.", file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r") as f:
        data = json.load(f)

    tag = data.get("tag", "#UNKNOWN").lstrip("#")
    suffix = "war-decks" if args.mode == "war" else "best-decks"
    output = args.output or f"clash-royale-{suffix}-{tag}.txt"

    report = build_top_cards_text(data, mode=args.mode)

    output_path = os.path.realpath(output)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False,
                                     dir=os.path.dirname(output_path) or ".") as tmp:
        tmp.write(report)
        tmp_path = tmp.name

    os.replace(tmp_path, output_path)
    print(f"Decks ({args.mode}) saved to {output_path}")


if __name__ == "__main__":
    main()
