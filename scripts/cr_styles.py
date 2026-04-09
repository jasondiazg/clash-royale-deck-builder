"""Shared Clash Royale UI styles and HTML helpers for reports.

Visual reference: dark blue-gray quilted background, medium-blue rounded panels,
white bold text with dark outlines, colored rarity card borders, elixir drop
top-left of cards, gold resource accents. Based on in-game screenshots.
"""

import base64
import os
from html import escape

RARITY_COLORS = {
    "common":    {"border": "#9aa4af", "glow": "rgba(154,164,175,0.3)"},
    "rare":      {"border": "#ff8c1a", "glow": "rgba(255,140,26,0.35)"},
    "epic":      {"border": "#c830e8", "glow": "rgba(200,48,232,0.35)"},
    "legendary": {"border": "#ffd84a", "glow": "rgba(255,216,74,0.4)"},
    "champion":  {"border": "#38e8c8", "glow": "rgba(56,232,200,0.4)"},
    "unknown":   {"border": "#666", "glow": "rgba(100,100,100,0.2)"},
}


def get_evo_hero(card: dict) -> tuple[bool, bool, str]:
    max_evo = card.get("maxEvolutionLevel", 0)
    evo_lv = card.get("evolutionLevel", 0)
    has_evo = evo_lv >= 1
    has_hero = max_evo >= 2 and evo_lv >= 2
    hero_info = f"Lv {evo_lv - 1}/{max_evo - 1}" if has_hero else ""
    return has_evo, has_hero, hero_info


def card_icon_url(card: dict, force_variant: str = "auto") -> str:
    """Return the appropriate card image URL.

    force_variant:
      "hero"  — use heroMedium (for hero slot in war decks)
      "evo"   — use evolutionMedium (for evo/flex-evo slot in war decks)
      "normal"— use medium (base card art)
      "auto"  — pick based on what the player has unlocked:
                 hero unlocked → heroMedium, evo unlocked → evolutionMedium, else medium
    """
    urls = card.get("iconUrls", {})
    if force_variant == "hero":
        return urls.get("heroMedium", urls.get("medium", ""))
    if force_variant == "evo":
        return urls.get("evolutionMedium", urls.get("medium", ""))
    if force_variant == "normal":
        return urls.get("medium", "")
    # auto: pick best available based on player unlock state
    max_evo = card.get("maxEvolutionLevel", 0)
    evo_lv = card.get("evolutionLevel", 0)
    if max_evo >= 2 and evo_lv >= 2 and "heroMedium" in urls:
        return urls["heroMedium"]
    if evo_lv >= 1 and "evolutionMedium" in urls:
        return urls["evolutionMedium"]
    return urls.get("medium", "")


def level_pct(card: dict) -> int:
    return round(card["level"] / card["maxLevel"] * 100)


def badge_html(has_evo: bool, has_hero: bool, is_maxed: bool) -> str:
    badges = []
    if has_hero:
        badges.append('<span class="cr-badge cr-badge-hero">HERO</span>')
    elif has_evo:
        badges.append('<span class="cr-badge cr-badge-evo">EVO</span>')
    if is_maxed:
        badges.append('<span class="cr-badge cr-badge-max">MAX</span>')
    return " ".join(badges)


def _load_font_base64(filename: str) -> str:
    """Load a font file as base64 for embedding in HTML."""
    ref_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references")
    path = os.path.join(ref_dir, filename)
    if os.path.isfile(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("ascii")
    return ""


def build_font_faces() -> str:
    """Build @font-face CSS with embedded Clash Royale fonts."""
    bold_b64 = _load_font_base64("clash_royale_bold.otf")
    regular_b64 = _load_font_base64("clash_royale_regular.otf")
    css = ""
    if bold_b64:
        css += f"""@font-face {{
  font-family: 'ClashRoyale';
  src: url(data:font/opentype;base64,{bold_b64}) format('opentype');
  font-weight: 700;
  font-style: normal;
}}
"""
    if regular_b64:
        css += f"""@font-face {{
  font-family: 'ClashRoyale';
  src: url(data:font/opentype;base64,{regular_b64}) format('opentype');
  font-weight: 400;
  font-style: normal;
}}
"""
    return css


# CSS that matches the actual Clash Royale in-game UI from screenshots:
# - Dark blue-gray quilted/diamond background texture
# - Medium blue rounded panels
# - White bold text with dark text-stroke outlines
# - Elixir cost circles (colored by rarity) top-left of cards
# - Gold accents for resources/highlights
# - Actual Clash Royale font embedded via @font-face

CR_CSS_TEMPLATE = """
{font_faces}

:root {{
  /* Background — dark blue-gray like the game menu */
  --bg: #1e2a3a;
  --bg-pattern: #243244;

  /* Panel blue — the rounded blue containers */
  --panel: #2d5a8a;
  --panel-light: #3a72a8;
  --panel-dark: #1e4268;
  --panel-border: #1a3858;

  /* Gold accents */
  --gold: #f0b020;
  --gold-light: #ffd060;

  /* Text */
  --white: #ffffff;
  --white-soft: rgba(255,255,255,0.85);
  --text-stroke: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
  --text-stroke-sm: -0.5px -0.5px 0 rgba(0,0,0,0.6), 0.5px -0.5px 0 rgba(0,0,0,0.6), -0.5px 0.5px 0 rgba(0,0,0,0.6), 0.5px 0.5px 0 rgba(0,0,0,0.6);

  /* Elixir */
  --elixir: #e848f0;
  --elixir-dark: #b030c0;

  /* Green button (like "Battle") */
  --green: #5cb85c;
  --green-dark: #3d8b3d;
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  font-family: 'ClashRoyale', 'Nunito', 'Segoe UI', sans-serif;
  min-height: 100vh;
  color: var(--white);

  /* Dark blue-gray with diamond/quilted pattern */
  background-color: var(--bg);
  background-image:
    linear-gradient(45deg, var(--bg-pattern) 25%, transparent 25%),
    linear-gradient(-45deg, var(--bg-pattern) 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, var(--bg-pattern) 75%),
    linear-gradient(-45deg, transparent 75%, var(--bg-pattern) 75%);
  background-size: 20px 20px;
  background-position: 0 0, 0 10px, 10px -10px, -10px 0;
}}

.container {{
  max-width: 1100px;
  margin: 0 auto;
  padding: 12px;
}}

/* ═══════════════════════════════════════
   PANEL — Rounded blue container
   ═══════════════════════════════════════ */
.cr-panel {{
  background: linear-gradient(180deg, var(--panel-light) 0%, var(--panel) 30%, var(--panel-dark) 100%);
  border: 3px solid var(--panel-border);
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.12);
  margin-bottom: 16px;
  overflow: hidden;
}}

/* ═══════════════════════════════════════
   HEADER
   ═══════════════════════════════════════ */
.cr-header {{
  text-align: center;
  padding: 24px 20px 18px;
}}
.cr-header h1 {{
  font-size: 2em;
  font-weight: 700;
  color: var(--white);
  text-shadow: var(--text-stroke), 0 3px 6px rgba(0,0,0,0.4);
  letter-spacing: 1px;
  text-transform: uppercase;
}}
.cr-header .player-info {{
  margin-top: 8px;
  font-size: 1em;
  font-weight: 700;
  color: var(--white-soft);
  text-shadow: var(--text-stroke-sm);
}}
.cr-header .tag {{ color: var(--gold-light); }}

/* Stats row */
.cr-stats {{
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 14px;
  flex-wrap: wrap;
}}
.cr-stat {{
  background: rgba(0,0,0,0.3);
  border: 2px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 6px 16px;
  text-align: center;
}}
.cr-stat .stat-value {{
  font-size: 1.2em;
  font-weight: 700;
  color: var(--gold);
  text-shadow: var(--text-stroke-sm);
}}
.cr-stat .stat-label {{
  font-size: 0.65em;
  color: rgba(255,255,255,0.6);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 700;
}}

/* ═══════════════════════════════════════
   SECTION TITLE — Blue banner bar
   ═══════════════════════════════════════ */
.cr-section-title {{
  font-size: 1em;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: var(--white);
  text-shadow: var(--text-stroke-sm);
  padding: 10px 18px;
  background: linear-gradient(90deg, rgba(0,0,0,0.3), rgba(0,0,0,0.1) 80%, transparent);
  border-left: 4px solid var(--gold);
  margin-bottom: 12px;
}}

/* ═══════════════════════════════════════
   CARD GRID
   ═══════════════════════════════════════ */
.cr-card-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 10px;
  padding: 0 14px 14px;
}}

/* ═══════════════════════════════════════
   CARD TILE
   ═══════════════════════════════════════ */
.cr-card {{
  background: linear-gradient(180deg, #3a6ea5 0%, #2a5080 60%, #1e3d60 100%);
  border: 2.5px solid #4a80b0;
  border-radius: 10px;
  padding: 8px 6px 6px;
  text-align: center;
  position: relative;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.15), 0 3px 8px rgba(0,0,0,0.4);
  transition: transform 0.12s ease;
}}
.cr-card:hover {{
  transform: translateY(-3px);
}}

/* Rarity borders */
.cr-card.r-common    {{ border-color: #9aa4af; }}
.cr-card.r-rare      {{ border-color: #ff8c1a; }}
.cr-card.r-epic      {{ border-color: #c830e8; }}
.cr-card.r-legendary {{ border-color: #ffd84a; box-shadow: inset 0 1px 0 rgba(255,255,255,0.15), 0 3px 8px rgba(0,0,0,0.4), 0 0 8px rgba(255,216,74,0.25); }}
.cr-card.r-champion  {{ border-color: #38e8c8; box-shadow: inset 0 1px 0 rgba(255,255,255,0.15), 0 3px 8px rgba(0,0,0,0.4), 0 0 8px rgba(56,232,200,0.25); }}

/* Enabled card (in a deck slot) */
.cr-card.enabled {{
  border-color: var(--gold);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.15), 0 0 10px rgba(240,176,32,0.4);
}}

/* Elixir cost — circle top-left like in-game */
.cr-elixir {{
  position: absolute;
  top: 4px;
  left: 4px;
  width: 24px;
  height: 24px;
  background: radial-gradient(circle at 40% 35%, #f868ff, var(--elixir) 60%, var(--elixir-dark));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8em;
  font-weight: 700;
  color: #fff;
  text-shadow: var(--text-stroke-sm);
  border: 1.5px solid rgba(255,255,255,0.3);
  z-index: 2;
}}

.cr-card-img {{
  width: 64px;
  height: 76px;
  object-fit: contain;
  filter: drop-shadow(0 2px 3px rgba(0,0,0,0.5));
  margin: 0 auto 4px;
  display: block;
}}
.cr-card-img-ph {{
  width: 64px; height: 76px;
  margin: 0 auto 4px;
  background: rgba(0,0,0,0.2);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.6em;
  color: rgba(255,255,255,0.3);
}}

.cr-card-name {{
  font-size: 0.72em;
  font-weight: 700;
  color: var(--white);
  text-shadow: var(--text-stroke-sm);
  margin-bottom: 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}

/* Level bar */
.cr-lvl-bar {{
  height: 5px;
  background: rgba(0,0,0,0.35);
  border-radius: 3px;
  overflow: hidden;
  margin: 0 4px 2px;
}}
.cr-lvl-fill {{
  height: 100%;
  background: linear-gradient(90deg, #e0a010, var(--gold), var(--gold-light));
  border-radius: 3px;
}}
.cr-lvl-text {{
  font-size: 0.65em;
  color: rgba(255,255,255,0.65);
  font-weight: 700;
}}

/* Badges */
.cr-badges {{ margin-top: 4px; display: flex; gap: 2px; justify-content: center; flex-wrap: wrap; }}
.cr-badge {{
  font-size: 0.55em;
  padding: 1px 6px;
  border-radius: 6px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}}
.cr-badge-hero {{ background: #38e8c8; color: #1a2a3a; }}
.cr-badge-evo  {{ background: #ff8c1a; color: #fff; }}
.cr-badge-max  {{ background: var(--gold); color: #1a2a3a; }}
.cr-badge-slot {{ background: rgba(0,0,0,0.4); color: var(--gold-light); border: 1px solid rgba(240,176,32,0.4); }}

/* ═══════════════════════════════════════
   DECK PANEL
   ═══════════════════════════════════════ */
.cr-deck-header {{
  padding: 12px 18px;
  background: rgba(0,0,0,0.2);
  border-bottom: 2px solid rgba(0,0,0,0.15);
  display: flex;
  align-items: center;
  gap: 12px;
}}
.cr-deck-num {{
  width: 40px; height: 40px;
  background: var(--gold);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.4em;
  font-weight: 700;
  color: #1a2a3a;
  text-shadow: 0 1px 0 rgba(255,255,255,0.3);
  border: 2px solid rgba(0,0,0,0.2);
}}
.cr-deck-title-wrap {{ flex: 1; }}
.cr-deck-title {{
  font-size: 1.1em;
  font-weight: 700;
  color: var(--white);
  text-shadow: var(--text-stroke-sm);
  text-transform: uppercase;
  letter-spacing: 1px;
}}
.cr-deck-archetype {{
  font-size: 0.75em;
  color: rgba(255,255,255,0.55);
  font-weight: 700;
}}
.cr-deck-elixir {{
  background: radial-gradient(circle at 40% 35%, #f868ff, var(--elixir) 60%, var(--elixir-dark));
  border-radius: 14px;
  padding: 4px 14px;
  font-size: 0.85em;
  font-weight: 700;
  color: #fff;
  text-shadow: var(--text-stroke-sm);
  border: 1.5px solid rgba(255,255,255,0.2);
}}

.cr-deck-strategy {{
  padding: 8px 18px;
  font-size: 0.8em;
  color: rgba(255,255,255,0.65);
  line-height: 1.4;
  font-weight: 700;
  border-bottom: 1px solid rgba(0,0,0,0.1);
}}

.cr-deck-cards {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 8px;
  padding: 12px 18px;
}}

/* Slots */
.cr-slots {{
  display: flex; gap: 8px; padding: 8px 18px; flex-wrap: wrap;
  border-top: 1px solid rgba(0,0,0,0.1);
}}
.cr-slot {{
  background: rgba(0,0,0,0.25);
  border: 1.5px solid rgba(240,176,32,0.3);
  border-radius: 8px;
  padding: 4px 12px;
  font-size: 0.72em;
}}
.cr-slot-label {{ color: rgba(255,255,255,0.5); text-transform: uppercase; font-size: 0.8em; letter-spacing: 0.5px; font-weight: 700; }}
.cr-slot-name {{ color: var(--gold); font-weight: 700; }}

/* Synergy */
.cr-synergy {{
  padding: 10px 18px 14px;
  border-top: 1px solid rgba(0,0,0,0.1);
}}
.cr-synergy h3 {{
  font-size: 0.78em;
  color: var(--gold);
  text-shadow: var(--text-stroke-sm);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 6px;
}}
.cr-synergy ul {{ list-style: none; }}
.cr-synergy li {{
  font-size: 0.73em;
  color: rgba(255,255,255,0.6);
  padding: 2px 0 2px 14px;
  position: relative;
  line-height: 1.4;
  font-weight: 700;
}}
.cr-synergy li::before {{
  content: '';
  position: absolute; left: 0; top: 7px;
  width: 6px; height: 6px;
  background: var(--gold);
  border-radius: 50%;
}}

/* Table */
.cr-table {{
  width: 100%;
  border-collapse: collapse;
  margin: 0 0 8px;
}}
.cr-table th, .cr-table td {{
  padding: 8px 14px;
  text-align: left;
  border-bottom: 1px solid rgba(0,0,0,0.12);
  font-weight: 700;
}}
.cr-table th {{
  color: var(--gold);
  text-transform: uppercase;
  font-size: 0.7em;
  letter-spacing: 1px;
  text-shadow: var(--text-stroke-sm);
}}
.cr-table td {{ font-size: 0.82em; }}
.cr-table tr:hover {{ background: rgba(0,0,0,0.1); }}

/* Footer */
.cr-footer {{
  text-align: center;
  padding: 14px;
  color: rgba(255,255,255,0.4);
  font-size: 0.75em;
  font-weight: 700;
}}

/* Responsive */
@media (max-width: 768px) {{
  .cr-card-grid {{ grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); }}
  .cr-deck-cards {{ grid-template-columns: repeat(4, 1fr); }}
  .cr-header h1 {{ font-size: 1.4em; }}
}}
@media (max-width: 480px) {{
  .cr-card-grid {{ grid-template-columns: repeat(2, 1fr); }}
  .cr-deck-cards {{ grid-template-columns: repeat(2, 1fr); }}
  .container {{ padding: 6px; }}
}}
"""


def get_cr_css() -> str:
    """Return the full CSS with embedded fonts."""
    font_faces = build_font_faces()
    return CR_CSS_TEMPLATE.format(font_faces=font_faces)


COPYRIGHT_HTML = """<div class="cr-footer" style="margin-top:24px;padding:16px 14px;line-height:1.6;">
  <div>This content is not affiliated with, endorsed, sponsored, or specifically approved by Supercell and Supercell is not responsible for it.</div>
  <div style="margin-top:6px;">For more information see Supercell's Fan Content Policy: <a href="https://supercell.com/en/fan-content-policy/" style="color:rgba(255,255,255,0.5);text-decoration:underline;">supercell.com/en/fan-content-policy</a></div>
  <div style="margin-top:8px;">&copy; Supercell Oy. Clash Royale, Supercell, and all associated logos and characters are trademarks of Supercell Oy.</div>
</div>"""
