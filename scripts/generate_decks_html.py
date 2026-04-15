# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Generate Clash Royale-styled HTML deck reports.

Modes:
  war  — War decks with Best Unused Cards section (no card overlap).
  best — Best decks with Shared Cards section (cards can repeat).

Deck definitions are passed in via --decks JSON file or use built-in defaults.
"""

import argparse
import json
import os
import sys
import tempfile
from html import escape

try:
    from cr_styles import (get_cr_css, get_evo_hero, build_card_map,
                           render_deck_html, unused_card_tile,
                           SHARED_DECKS_CSS, COPYRIGHT_HTML)
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from cr_styles import (get_cr_css, get_evo_hero, build_card_map,
                           render_deck_html, unused_card_tile,
                           SHARED_DECKS_CSS, COPYRIGHT_HTML)


# ═══════════════════════════════════════════════════════════════════════════
# Default deck definitions (agent should customize based on meta + player)
# ═══════════════════════════════════════════════════════════════════════════

DEFAULT_WAR_DECKS = [
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

DEFAULT_BEST_DECKS = [
    {
        "title": "Lumberloon",
        "archetype": "Beatdown / Surprise Push",
        "strategy": "Lumberjack tanks in front of Balloon. When LJ dies, Rage drops on Balloon for devastating damage. Valkyrie and Musketeer handle ground defense, Mega Minion covers air.",
        "cards": ["Lumberjack", "Balloon", "Valkyrie", "Musketeer", "Mega Minion", "Tombstone", "Arrows", "Bats"],
        "enabled_hero": "Mega Minion", "enabled_evo": "Lumberjack", "enabled_flex": "Valkyrie", "flex_type": "Evo",
        "synergy_notes": [
            "Lumberjack (Evo) dies in front of Balloon dropping Rage",
            "Valkyrie (Evo) splash defense + counter-push",
            "Mega Minion (Hero) reliable air DPS in hero slot",
            "Musketeer + Tombstone solid defense",
            "Arrows clear swarms, Bats cycle + tank shred",
        ],
    },
    {
        "title": "Spell Bait",
        "archetype": "Log Bait / Control",
        "strategy": "Bait out small spells with Goblin Gang, Dart Goblin, Goblins. Once Log/Zap is spent, punish with Goblin Barrel. Knight tanks, Goblin Cage defends.",
        "cards": ["Goblin Gang", "Dart Goblin", "Goblins", "Goblin Barrel", "Knight", "Goblin Cage", "Fireball", "The Log"],
        "enabled_hero": "Goblins", "enabled_evo": "Dart Goblin", "enabled_flex": "Knight", "flex_type": "Hero",
        "synergy_notes": [
            "Goblins (Hero) hero slot — harder to spell down",
            "Dart Goblin (Evo) fast chip + range snipe",
            "Knight (Hero) flex slot mini-tank for Barrel pushes",
            "Goblin Gang + Goblin Barrel classic bait combo",
            "Goblin Cage (Evo) defense + Brawler counter-push",
            "Fireball + The Log spell coverage",
        ],
    },
    {
        "title": "P.E.K.K.A Bridge Spam",
        "archetype": "Bridge Spam / Counter-Push",
        "strategy": "P.E.K.K.A shuts down tanks on defense, then counter-push. Bandit, Dark Prince, Royal Ghost pressure opposite lane. Magic Archer piercing value.",
        "cards": ["P.E.K.K.A", "Bandit", "Dark Prince", "Royal Ghost", "Magic Archer", "Electro Wizard", "Poison", "Zap"],
        "enabled_hero": "Magic Archer", "enabled_evo": "P.E.K.K.A", "enabled_flex": "Royal Ghost", "flex_type": "Evo",
        "synergy_notes": [
            "P.E.K.K.A (Evo) dominates defense + massive counter-push",
            "Magic Archer (Hero) piercing geometry behind P.E.K.K.A",
            "Royal Ghost (Evo) invisible bridge spam",
            "Bandit dash + Dark Prince charge pressure",
            "Electro Wizard stun resets Inferno",
            "Poison + Zap area control",
        ],
    },
    {
        "title": "Hog Cycle",
        "archetype": "Cycle / Chip Damage",
        "strategy": "Fast cycle back to Hog Rider for constant pressure. Musketeer provides DPS, Valkyrie splash defense. Cheap cards keep the cycle fast.",
        "cards": ["Hog Rider", "Musketeer", "Valkyrie", "Cannon", "Fireball", "The Log", "Skeletons", "Ice Spirit"],
        "enabled_hero": None, "enabled_evo": "Valkyrie", "enabled_flex": "Musketeer", "flex_type": "Evo",
        "synergy_notes": [
            "Hog Rider constant pressure win condition",
            "Valkyrie (Evo) splash defense + counter-push tank",
            "Musketeer (Evo flex) ranged DPS backbone",
            "Cannon pulls tanks, cheap defensive building",
            "Fireball + The Log spell combo",
            "Skeletons + Ice Spirit fast cycle cards",
        ],
    },
]


# ═══════════════════════════════════════════════════════════════════════════
# HTML generation
# ═══════════════════════════════════════════════════════════════════════════

def _header_html(data: dict, title: str, cm: dict) -> str:
    """Render the player header panel."""
    pn = escape(data["name"])
    pt = escape(data["tag"])
    tr = data["trophies"]
    ar = escape(data["arena"]["name"])
    heroes = [n for n, c in cm.items() if c["has_hero"]]
    evos = [n for n, c in cm.items() if c["has_evo"] and not c["has_hero"]]
    return f"""<div class="cr-panel"><div class="cr-header"><h1>{escape(title)}</h1>
<div class="player-info">{pn} <span class="tag">{pt}</span></div>
<div class="cr-stats">
<div class="cr-stat"><div class="stat-value">{tr}</div><div class="stat-label">Trophies</div></div>
<div class="cr-stat"><div class="stat-value">{ar}</div><div class="stat-label">Arena</div></div>
<div class="cr-stat"><div class="stat-value">{len(heroes)}</div><div class="stat-label">Heroes</div></div>
<div class="cr-stat"><div class="stat-value">{len(evos)}</div><div class="stat-label">Evos</div></div>
<div class="cr-stat"><div class="stat-value">4</div><div class="stat-label">Decks</div></div>
</div></div></div>"""


def generate_war_decks_html(data: dict, deck_defs: list[dict] | None = None) -> str:
    """Generate war decks HTML (no card overlap, with Best Unused Cards)."""
    cm = build_card_map(data)
    css = get_cr_css()
    defs = deck_defs or DEFAULT_WAR_DECKS

    used_names = set()
    for d in defs:
        used_names.update(d["cards"])

    unused = [c for c in data.get("cards", []) if c["name"] not in used_names]
    unused.sort(key=lambda c: (-c["level"] / c["maxLevel"], c["name"]))
    top_unused = unused[:25]

    header = _header_html(data, "War Decks", cm)
    decks = "\n".join(render_deck_html(i + 1, d, cm) for i, d in enumerate(defs))
    unused_tiles = "\n".join(unused_card_tile(c) for c in top_unused)

    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>CR War Decks - {escape(data['name'])}</title><style>{css}</style></head>
<body><div class="container">
{header}
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


def generate_best_decks_html(data: dict, deck_defs: list[dict] | None = None) -> str:
    """Generate best decks HTML (cards can repeat, with Shared Cards section)."""
    cm = build_card_map(data)
    css = get_cr_css()
    defs = deck_defs or DEFAULT_BEST_DECKS

    header = _header_html(data, "Best Decks", cm)
    decks = "\n".join(render_deck_html(i + 1, d, cm) for i, d in enumerate(defs))

    # Card usage frequency across decks
    card_freq: dict[str, int] = {}
    for d in defs:
        for name in d["cards"]:
            card_freq[name] = card_freq.get(name, 0) + 1
    shared_cards = {n: f for n, f in card_freq.items() if f > 1}

    shared_html = ""
    if shared_cards:
        shared_items = "\n".join(
            f'<div class="cr-shared-card"><span class="cr-shared-name">{escape(n)}</span>'
            f'<span class="cr-shared-count">in {f} decks</span></div>'
            for n, f in sorted(shared_cards.items(), key=lambda x: -x[1])
        )
        shared_html = f"""<div class="cr-panel">
  <div class="cr-section-title">Shared Cards Across Decks</div>
  <div class="cr-shared-grid">{shared_items}</div>
</div>"""

    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>CR Best Decks - {escape(data['name'])}</title>
<style>{css}{SHARED_DECKS_CSS}</style></head>
<body><div class="container">
{header}
{decks}
{shared_html}
<div class="cr-footer">
  Priority: Synergy &gt; Card Level &gt; Heroes &gt; Evos &middot;
  Cards may repeat across decks &middot;
  4 different archetypes &middot;
  3 Evo/Hero slots per deck
</div>
{COPYRIGHT_HTML}
</div></body></html>"""


def main():
    ap = argparse.ArgumentParser(description="Generate CR deck HTML report")
    ap.add_argument("--input", default="cr_player_data.json")
    ap.add_argument("--output", default=None)
    ap.add_argument("--mode", choices=["war", "best"], default="war",
                    help="war = no card overlap, best = cards can repeat")
    ap.add_argument("--decks", default=None,
                    help="JSON file with custom deck definitions (overrides defaults)")
    args = ap.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: {args.input} not found", file=sys.stderr)
        sys.exit(1)

    with open(args.input) as f:
        data = json.load(f)

    deck_defs = None
    if args.decks and os.path.isfile(args.decks):
        with open(args.decks) as f:
            deck_defs = json.load(f)

    tag = data.get("tag", "#X").lstrip("#")
    suffix = "war-decks" if args.mode == "war" else "best-decks"
    out = args.output or f"clash-royale-{suffix}-{tag}.html"

    if args.mode == "war":
        report = generate_war_decks_html(data, deck_defs)
    else:
        report = generate_best_decks_html(data, deck_defs)

    out_path = os.path.realpath(out)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False,
                                     dir=os.path.dirname(out_path) or ".",
                                     encoding="utf-8") as tmp:
        tmp.write(report)
    os.replace(tmp.name, out_path)
    print(f"{args.mode.title()} decks HTML saved to {out_path}")


if __name__ == "__main__":
    main()
