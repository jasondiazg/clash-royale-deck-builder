# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Generate best decks HTML — thin wrapper around generate_decks_html.py (mode=best).

Kept for backward compatibility. Prefer: generate_decks_html.py --mode best
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv = [a if a != sys.argv[0] else "generate_decks_html.py" for a in sys.argv] + ["--mode", "best"]

from generate_decks_html import main
main()
