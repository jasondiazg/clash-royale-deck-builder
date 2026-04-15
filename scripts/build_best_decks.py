# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Build 4 optimized best decks — thin wrapper around build_decks.py (mode=best).

Kept for backward compatibility. Prefer: build_decks.py --mode best
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv = [a if a != sys.argv[0] else "build_decks.py" for a in sys.argv] + ["--mode", "best"]

from build_decks import main
main()
