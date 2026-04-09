# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Generate Clash Royale-styled HTML war decks report with Best Unused Cards."""

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


def build_card_map(data: dict) -> dict[str, dict]:
    m = {}
    for c in data.get("cards", []):
        has_evo, has_hero, hero_info = get_evo_hero(c)
        m[c["name"]] = {**c, "has_evo": has_evo, "has_hero": has_hero, "hero_info": hero_info}
    return m


DECK_DEFINITIONS = [
    {
        "title": "Lumberloon",
        "archetype": "Beatdown / Surprise Push",
        "strategy": "Lumberjack tanks in front of Balloon. When LJ dies, Rage drops on Balloon for devastating damage. Valkyrie and Musketeer handle ground defense, Mega Minion covers air. Tombstone distracts tanks.",
        "cards": ["Lumberjack", "Balloon", "Valkyrie", "Musketeer", "Mega Minion", "Tombstone", "Arrows", "Bats"],
        "enabled_hero": "Mega Minion", "enabled_evo": "Lumberjack", "enabled_flex": "Valkyrie", "flex_type": "Evo",
        "synergy_notes": [
            "Lumberjack (Evo, 8/8 MAX) dies in front of Balloon (11/11 MAX) dropping Rage",
            "Valkyrie (Evo, 14/14 MAX) splash defense + counter-push",
            "Mega Minion (Hero, 13/14) reliable air DPS in hero slot",
            "Musketeer (14/14 MAX) + Tombstone (14/14 MAX) solid defense",
            "Arrows (16/16 MAX) clear swarms, Bats (15/16) cycle + tank shred",
        ],
    },
    {
        "title": "Spell Bait",
        "archetype": "Log Bait / Control",
        "strategy": "Bait out small spells with Goblin Gang, Dart Goblin, Goblins. Once Log/Zap is spent, punish with Goblin Barrel. Knight tanks, Goblin Cage defends.",
        "cards": ["Goblin Gang", "Dart Goblin", "Goblins", "Goblin Barrel", "Knight", "Goblin Cage", "Fireball", "The Log"],
        "enabled_hero": "Goblins", "enabled_evo": "Dart Goblin", "enabled_flex": "Knight", "flex_type": "Hero",
        "synergy_notes": [
            "Goblins (Hero, 15/16) hero slot - harder to spell down",
            "Dart Goblin (Evo, 14/14 MAX) fast chip + range snipe",
            "Knight (Hero, 14/16) flex slot mini-tank for Barrel pushes",
            "Goblin Gang (16/16 MAX) + Goblin Barrel classic bait combo",
            "Goblin Cage (Evo, 13/14) defense + Brawler counter-push",
            "Fireball (13/14) + The Log (8/8 MAX) spell coverage",
        ],
    },
    {
        "title": "P.E.K.K.A Bridge Spam",
        "archetype": "Bridge Spam / Counter-Push",
        "strategy": "P.E.K.K.A shuts down tanks on defense, then counter-push. Bandit, Dark Prince, Royal Ghost pressure opposite lane. Magic Archer piercing value. E-Wiz stuns.",
        "cards": ["P.E.K.K.A", "Bandit", "Dark Prince", "Royal Ghost", "Magic Archer", "Electro Wizard", "Poison", "Zap"],
        "enabled_hero": "Magic Archer", "enabled_evo": "P.E.K.K.A", "enabled_flex": "Royal Ghost", "flex_type": "Evo",
        "synergy_notes": [
            "P.E.K.K.A (Evo, 11/11 MAX) dominates defense + massive counter-push",
            "Magic Archer (Hero, 5/8) piercing geometry behind P.E.K.K.A",
            "Royal Ghost (Evo, 6/8) invisible bridge spam",
            "Bandit (7/8) dash + Dark Prince (10/11) charge pressure",
            "Electro Wizard (6/8) stun resets Inferno",
            "Poison (10/11) + Zap (15/16) area control",
        ],
    },
    {
        "title": "Royal Hogs Split Lane",
        "archetype": "Split Lane / Fireball Bait",
        "strategy": "Split Royal Hogs both lanes. Furnace provides constant pressure and fireball bait. Flying Machine + Archers ranged DPS. Mini PEKKA + Cannon handle tanks.",
        "cards": ["Royal Hogs", "Furnace", "Flying Machine", "Archers", "Mini P.E.K.K.A", "Cannon", "Firecracker", "Hog Rider"],
        "enabled_hero": None, "enabled_evo": "Royal Hogs", "enabled_flex": "Archers", "flex_type": "Evo",
        "synergy_notes": [
            "Royal Hogs (Evo, 13/14) split both lanes relentless pressure",
            "Furnace (14/14 MAX) baits Fireball + chip damage",
            "Archers (Evo, 15/16) flex evo slot upgraded ranged defense",
            "Flying Machine (14/14 MAX) safe air DPS",
            "Mini P.E.K.K.A (13/14) melts tanks at bridge",
            "Hog Rider (14/14 MAX) secondary win condition",
            "Cannon (14/16) + Firecracker (14/16) defensive backbone",
        ],
    },
]


def deck_card_html(card: dict, is_enabled: bool, slot_label: str = "", img_variant: str = "normal") -> str:
    r = card.get("rarity", "unknown").lower()
    name = escape(card["name"])
    cost = card.get("elixirCost", "?")
    pct = level_pct(card)
    level = f"{card['level']}/{card['maxLevel']}"
    icon = card_icon_url(card, img_variant)
    has_evo, has_hero, _ = get_evo_hero(card)
    is_maxed = card["level"] == card["maxLevel"]
    cls = f"cr-card r-{r}" + (" enabled" if is_enabled else "")
    img = (f'<img class="cr-card-img" src="{escape(icon)}" alt="{name}" loading="lazy">'
           if icon else f'<div class="cr-card-img-ph">{name[0]}</div>')
    badges = []
    if has_hero: badges.append('<span class="cr-badge cr-badge-hero">HERO</span>')
    elif has_evo: badges.append('<span class="cr-badge cr-badge-evo">EVO</span>')
    if is_maxed: badges.append('<span class="cr-badge cr-badge-max">MAX</span>')
    if is_enabled and slot_label: badges.append(f'<span class="cr-badge cr-badge-slot">{escape(slot_label)}</span>')
    return f"""<div class="{cls}"><div class="cr-elixir">{cost}</div>{img}
  <div class="cr-card-name">{name}</div>
  <div class="cr-lvl-bar"><div class="cr-lvl-fill" style="width:{pct}%"></div></div>
  <div class="cr-lvl-text">Lv {level}</div>
  <div class="cr-badges">{"".join(badges)}</div></div>"""


def unused_card_tile(card: dict) -> str:
    """Render a card tile for the Best Unused Cards section."""
    r = card.get("rarity", "unknown").lower()
    name = escape(card["name"])
    cost = card.get("elixirCost", "?")
    pct = level_pct(card)
    level = f"{card['level']}/{card['maxLevel']}"
    icon = card_icon_url(card, "auto")
    has_evo, has_hero, _ = get_evo_hero(card)
    is_maxed = card["level"] == card["maxLevel"]
    badges = badge_html(has_evo, has_hero, is_maxed)
    img = (f'<img class="cr-card-img" src="{escape(icon)}" alt="{name}" loading="lazy">'
           if icon else f'<div class="cr-card-img-ph">{name[0]}</div>')
    return f"""<div class="cr-card r-{r}"><div class="cr-elixir">{cost}</div>{img}
  <div class="cr-card-name">{name}</div>
  <div class="cr-lvl-bar"><div class="cr-lvl-fill" style="width:{pct}%"></div></div>
  <div class="cr-lvl-text">Lv {level}</div>
  <div class="cr-badges">{badges}</div></div>"""


def render_deck(num: int, d: dict, cm: dict) -> str:
    cards = [cm[n] for n in d["cards"] if n in cm]
    avg = sum(c.get("elixirCost", 0) for c in cards) / max(len(cards), 1)
    en = set()
    sl = {}
    img_variants = {}
    for k, lbl in [("enabled_hero", "Hero"), ("enabled_evo", "Evo"), ("enabled_flex", "Flex")]:
        if d.get(k):
            en.add(d[k]); sl[d[k]] = lbl
    # Determine image variant for each card based on slot assignment
    if d.get("enabled_hero"):
        img_variants[d["enabled_hero"]] = "hero"
    if d.get("enabled_evo"):
        img_variants[d["enabled_evo"]] = "evo"
    if d.get("enabled_flex"):
        img_variants[d["enabled_flex"]] = "hero" if d.get("flex_type") == "Hero" else "evo"
    tiles = "\n".join(
        deck_card_html(c, c["name"] in en, sl.get(c["name"], ""), img_variants.get(c["name"], "normal"))
        for c in cards
    )
    syn = "\n".join(f"<li>{escape(n)}</li>" for n in d["synergy_notes"])
    slots = "\n".join(
        f'<div class="cr-slot"><span class="cr-slot-label">{lbl} Slot</span> <span class="cr-slot-name">{escape(d[k])}</span></div>'
        for k, lbl in [("enabled_hero", "Hero"), ("enabled_evo", "Evo"), ("enabled_flex", "Flex")] if d.get(k)
    )
    return f"""<div class="cr-panel">
  <div class="cr-deck-header">
    <div class="cr-deck-num">{num}</div>
    <div class="cr-deck-title-wrap"><div class="cr-deck-title">{escape(d['title'])}</div>
    <div class="cr-deck-archetype">{escape(d['archetype'])}</div></div>
    <div class="cr-deck-elixir">{avg:.1f}</div>
  </div>
  <div class="cr-deck-strategy">{escape(d['strategy'])}</div>
  <div class="cr-deck-cards">{tiles}</div>
  <div class="cr-slots">{slots}</div>
  <div class="cr-synergy"><h3>Why It Works</h3><ul>{syn}</ul></div>
</div>"""


def generate_war_decks_html(data: dict) -> str:
    pn = escape(data["name"])
    pt = escape(data["tag"])
    tr = data["trophies"]
    ar = escape(data["arena"]["name"])
    cm = build_card_map(data)
    css = get_cr_css()

    heroes = [n for n, c in cm.items() if c["has_hero"]]
    evos = [n for n, c in cm.items() if c["has_evo"] and not c["has_hero"]]

    # Cards used across all 4 decks
    used_names = set()
    for d in DECK_DEFINITIONS:
        used_names.update(d["cards"])

    # Best Unused Cards — top 25 not used in any war deck, sorted by level
    all_cards = data.get("cards", [])
    unused = [c for c in all_cards if c["name"] not in used_names]
    unused.sort(key=lambda c: (-c["level"] / c["maxLevel"], c["name"]))
    top_unused = unused[:25]

    decks = "\n".join(render_deck(i + 1, d, cm) for i, d in enumerate(DECK_DEFINITIONS))

    unused_tiles = "\n".join(unused_card_tile(c) for c in top_unused)

    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>CR War Decks - {pn}</title><style>{css}</style></head><body><div class="container">

<div class="cr-panel"><div class="cr-header"><h1>War Decks</h1>
<div class="player-info">{pn} <span class="tag">{pt}</span></div>
<div class="cr-stats">
<div class="cr-stat"><div class="stat-value">{tr}</div><div class="stat-label">Trophies</div></div>
<div class="cr-stat"><div class="stat-value">{ar}</div><div class="stat-label">Arena</div></div>
<div class="cr-stat"><div class="stat-value">{len(heroes)}</div><div class="stat-label">Heroes</div></div>
<div class="cr-stat"><div class="stat-value">{len(evos)}</div><div class="stat-label">Evos</div></div>
<div class="cr-stat"><div class="stat-value">4</div><div class="stat-label">Decks</div></div>
</div></div></div>

{decks}

<div class="cr-panel">
  <div class="cr-section-title">Best Unused Cards (Top 25)</div>
  <div class="cr-card-grid">{unused_tiles}</div>
</div>

<div class="cr-footer">
  Priority: Synergy &gt; Card Level &gt; Heroes &gt; Evos &middot;
  Each card once across all 4 decks &middot;
  3 Evo/Hero slots per deck
</div>

{COPYRIGHT_HTML}

</div></body></html>"""


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
    out = args.output or f"clash-royale-war-decks-{tag}.html"
    report = generate_war_decks_html(data)
    out_path = os.path.realpath(out)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False,
                                     dir=os.path.dirname(out_path) or ".", encoding="utf-8") as tmp:
        tmp.write(report)
    os.replace(tmp.name, out_path)
    print(f"War decks HTML saved to {out_path}")

if __name__ == "__main__":
    main()
