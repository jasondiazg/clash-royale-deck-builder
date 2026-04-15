# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Generate war decks HTML — thin wrapper around generate_decks_html.py (mode=war).

Kept for backward compatibility. Prefer: generate_decks_html.py --mode war
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv = [a if a != sys.argv[0] else "generate_decks_html.py" for a in sys.argv] + ["--mode", "war"]

from generate_decks_html import main
main()
