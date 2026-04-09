# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Generate a Clash Royale-styled HTML card collection report from player data."""

import argparse
import json
import os
import sys
import tempfile
from html import escape

try:
    from cr_styles import get_cr_css, get_evo_hero, card_icon_url, level_pct, badge_html, COPYRIGHT_HTML
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from cr_styles import get_cr_css, get_evo_hero, card_icon_url, level_pct, badge_html, COPYRIGHT_HTML


def card_tile(card: dict) -> str:
    r = card.get("rarity", "unknown").lower()
    name = escape(card["name"])
    level = f"{card['level']}/{card['maxLevel']}"
    pct = level_pct(card)
    cost = card.get("elixirCost", "?")
    has_evo, has_hero, _ = get_evo_hero(card)
    badges = badge_html(has_evo, has_hero, card["level"] == card["maxLevel"])
    icon = card_icon_url(card, "auto")
    img = (f'<img class="cr-card-img" src="{escape(icon)}" alt="{name}" loading="lazy">'
           if icon else f'<div class="cr-card-img-ph">{name[0]}</div>')
    return f"""<div class="cr-card r-{r}">
  <div class="cr-elixir">{cost}</div>{img}
  <div class="cr-card-name">{name}</div>
  <div class="cr-lvl-bar"><div class="cr-lvl-fill" style="width:{pct}%"></div></div>
  <div class="cr-lvl-text">Lv {level}</div>
  <div class="cr-badges">{badges}</div>
</div>"""


def section(title: str, cards: list[dict]) -> str:
    tiles = "\n".join(card_tile(c) for c in cards)
    return f'<div class="cr-section-title">{escape(title)}</div>\n<div class="cr-card-grid">{tiles}</div>'


def generate_report(data: dict) -> str:
    pn = escape(data["name"])
    pt = escape(data["tag"])
    tr = data["trophies"]
    ar = escape(data["arena"]["name"])
    deck = data.get("currentDeck", [])
    deck_sup = data.get("currentDeckSupportCards", [])
    cards = data.get("cards", [])
    sup = data.get("supportCards", [])
    css = get_cr_css()

    deck_ids = {c.get("id") for c in deck}
    unused = sorted(
        [c for c in cards if c.get("id") not in deck_ids],
        key=lambda c: (-c["level"] / c["maxLevel"], c["name"]),
    )

    rarity_order = ["common", "rare", "epic", "legendary", "champion"]
    grouped: dict[str, list] = {}
    for c in cards:
        grouped.setdefault(c.get("rarity", "unknown"), []).append(c)

    h = [f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>CR Cards - {pn}</title><style>{css}</style></head><body><div class="container">
<div class="cr-panel"><div class="cr-header"><h1>Card Collection</h1>
<div class="player-info">{pn} <span class="tag">{pt}</span></div>
<div class="cr-stats">
<div class="cr-stat"><div class="stat-value">{tr}</div><div class="stat-label">Trophies</div></div>
<div class="cr-stat"><div class="stat-value">{ar}</div><div class="stat-label">Arena</div></div>
<div class="cr-stat"><div class="stat-value">{len(cards)}</div><div class="stat-label">Cards</div></div>
<div class="cr-stat"><div class="stat-value">{len(sup)}</div><div class="stat-label">Support</div></div>
</div></div></div>"""]

    h.append(f'<div class="cr-panel">{section("Current Battle Deck", deck)}</div>')

    if deck_sup:
        rows = "".join(f"<tr><td>{escape(c['name'])}</td><td>{c['level']}/{c['maxLevel']}</td></tr>" for c in deck_sup)
        h.append(f'<div class="cr-panel"><div class="cr-section-title">Support Cards in Deck</div>'
                 f'<table class="cr-table"><thead><tr><th>Name</th><th>Level</th></tr></thead><tbody>{rows}</tbody></table></div>')

    if unused:
        h.append(f'<div class="cr-panel">{section("Best Unused Cards", unused)}</div>')

    for r in rarity_order:
        grp = grouped.get(r, [])
        if grp:
            grp.sort(key=lambda x: x["name"])
            h.append(f'<div class="cr-panel">{section(f"{r.upper()} Cards ({len(grp)})", grp)}</div>')

    if sup:
        rows = "".join(f"<tr><td>{i}</td><td>{escape(c['name'])}</td><td>{c['level']}/{c['maxLevel']}</td></tr>" for i, c in enumerate(sup, 1))
        h.append(f'<div class="cr-panel"><div class="cr-section-title">Support / Tower Cards ({len(sup)})</div>'
                 f'<table class="cr-table"><thead><tr><th>#</th><th>Name</th><th>Level</th></tr></thead><tbody>{rows}</tbody></table></div>')

    h.append(f'<div class="cr-footer">Total: {len(cards)} cards &middot; Support: {len(sup)} &middot; Unused: {len(unused)}</div>')
    h.append(COPYRIGHT_HTML)
    h.append("</div></body></html>")
    return "\n".join(h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="cr_player_data.json")
    ap.add_argument("--output", default=None)
    args = ap.parse_args()
    if not os.path.isfile(args.input):
        print(f"Error: {args.input} not found", file=sys.stderr); sys.exit(1)
    with open(args.input) as f:
        data = json.load(f)
    tag = data.get("tag", "#X").lstrip("#")
    out = args.output or f"clash-royale-deck-{tag}.html"
    report = generate_report(data)
    out_path = os.path.realpath(out)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False,
                                     dir=os.path.dirname(out_path) or ".", encoding="utf-8") as tmp:
        tmp.write(report)
    os.replace(tmp.name, out_path)
    print(f"HTML card report saved to {out_path}")

if __name__ == "__main__":
    main()
