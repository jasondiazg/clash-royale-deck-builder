# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Build 4 optimized war decks from Clash Royale player data.

Priority: 1) Synergy 2) Card Level 3) Heroes 4) Evos
Each deck has 3 evo/hero slots: 1 Hero + 1 Evo + 1 Flex (Hero or Evo).
No card is repeated across decks.
"""

import argparse
import json
import os
import sys
import tempfile


def analyze_card(card: dict) -> dict:
    """Extract key info from a card."""
    max_evo = card.get("maxEvolutionLevel", 0)
    evo_lv = card.get("evolutionLevel", 0)
    has_evo = evo_lv >= 1
    has_hero = max_evo >= 2 and evo_lv >= 2
    level_pct = round(card["level"] / card["maxLevel"] * 100)

    hero_info = ""
    if has_hero:
        hero_lv = evo_lv - 1
        max_hero_lv = max_evo - 1
        hero_info = f"Lv {hero_lv}/{max_hero_lv}"

    return {
        "name": card["name"],
        "level": f"{card['level']}/{card['maxLevel']}",
        "level_pct": level_pct,
        "cost": card.get("elixirCost", 0),
        "rarity": card.get("rarity", "unknown"),
        "has_evo": has_evo,
        "has_hero": has_hero,
        "hero_info": hero_info,
    }


def format_evo_hero(info: dict, enabled: bool = False) -> str:
    """Format the evo/hero column for a card."""
    parts = []
    if info["has_hero"]:
        parts.append(f"Hero+Evo")
    elif info["has_evo"]:
        parts.append("Evo")
    else:
        parts.append("-")

    if enabled:
        parts.append("[ENABLED]")
    return " ".join(parts)


def format_deck(deck_num: int, title: str, strategy: str, cards: list[dict],
                enabled_hero: str, enabled_evo: str, enabled_flex: str,
                flex_type: str, synergy_notes: list[str]) -> list[str]:
    """Format a single deck section."""
    avg_elixir = sum(c["cost"] for c in cards) / len(cards)
    enabled_names = {enabled_hero, enabled_evo, enabled_flex}

    lines = []
    lines.append("=" * 75)
    lines.append(f"DECK {deck_num} - {title}")
    lines.append("-" * 75)
    lines.append(f"Strategy: {strategy}")
    lines.append(f"Avg Elixir: {avg_elixir:.1f}")
    lines.append("-" * 75)
    lines.append(f"{'#':<4} {'Card Name':<25} {'Level':<10} {'Cost':<6} {'Evo/Hero':<20}")
    lines.append("-" * 75)

    for i, c in enumerate(cards, 1):
        is_enabled = c["name"] in enabled_names
        eh = format_evo_hero(c, is_enabled)
        lines.append(f"{i:<4} {c['name']:<25} {c['level']:<10} {c['cost']:<6} {eh:<20}")

    lines.append("-" * 75)
    lines.append("Enabled slots:")

    hero_card = next((c for c in cards if c["name"] == enabled_hero), None)
    evo_card = next((c for c in cards if c["name"] == enabled_evo), None)
    flex_card = next((c for c in cards if c["name"] == enabled_flex), None)

    if hero_card:
        lines.append(f"  Hero slot  -> {hero_card['name']} ({hero_card['hero_info']})")
    if evo_card:
        lines.append(f"  Evo slot   -> {evo_card['name']}")
    if flex_card:
        lines.append(f"  Flex slot  -> {flex_card['name']} ({flex_type})")

    lines.append("")
    lines.append("Why it works:")
    for note in synergy_notes:
        lines.append(f"- {note}")

    return lines


def build_decks(data: dict) -> str:
    """Build 4 war decks and return formatted text."""
    card_map = {}
    for c in data["cards"]:
        info = analyze_card(c)
        card_map[info["name"]] = info

    player_name = data["name"]
    player_tag = data["tag"]

    # Identify heroes and evos
    heroes = {n: c for n, c in card_map.items() if c["has_hero"]}
    evos = {n: c for n, c in card_map.items() if c["has_evo"] and not c["has_hero"]}

    lines = []
    lines.append("=" * 75)
    lines.append("CLASH ROYALE - WAR DECKS")
    lines.append(f"Player: {player_name} ({player_tag})")
    lines.append("=" * 75)
    lines.append("Priority: 1) Synergy  2) Card Level  3) Heroes  4) Evos")
    lines.append("Evo/Hero slots: 1 Hero + 1 Evo + 1 Flex (Hero or Evo) = 3 max")
    lines.append("Cards marked [ENABLED] are the 3 active evo/hero slots.")
    lines.append("Each card used only once across all 4 decks.")
    lines.append("")

    # --- DECK DEFINITIONS ---
    # These are synergy-first archetypes using the player's best cards.
    # The agent should customize these based on the actual player data.
    # Below is a template structure showing how decks are formatted.

    lines.append("=" * 75)
    lines.append("NOTE: War decks are built by the agent based on the player's")
    lines.append("card collection, prioritizing synergy, card levels, heroes,")
    lines.append("and evos. Run this script then review and adjust as needed.")
    lines.append("")
    lines.append(f"Player has {len(heroes)} heroes: {', '.join(heroes.keys())}")
    lines.append(f"Player has {len(evos)} evos: {', '.join(evos.keys())}")
    lines.append("")

    # Print top cards by level for reference
    lines.append("-" * 75)
    lines.append("TOP CARDS BY LEVEL (for deck building reference)")
    lines.append("-" * 75)
    lines.append(f"{'Card Name':<25} {'Level':<10} {'Lv%':<6} {'Cost':<6} {'Evo/Hero':<15}")
    lines.append("-" * 75)

    sorted_cards = sorted(card_map.values(), key=lambda x: x["level_pct"], reverse=True)
    for c in sorted_cards[:40]:
        tag = ""
        if c["has_hero"]:
            tag = "HERO+EVO"
        elif c["has_evo"]:
            tag = "EVO"
        lines.append(f"{c['name']:<25} {c['level']:<10} {c['level_pct']}%{'':<3} {c['cost']:<6} {tag:<15}")

    lines.append("")
    lines.append("=" * 75)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Build CR war decks")
    parser.add_argument("--input", default="cr_player_data.json", help="Input JSON path")
    parser.add_argument("--output", default=None, help="Output txt path")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        print("Run fetch_player.py first to get player data.", file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r") as f:
        data = json.load(f)

    tag = data.get("tag", "#UNKNOWN").lstrip("#")
    output = args.output or f"clash-royale-war-decks-{tag}.txt"

    report = build_decks(data)

    output_path = os.path.realpath(output)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False,
                                     dir=os.path.dirname(output_path) or ".") as tmp:
        tmp.write(report)
        tmp_path = tmp.name

    os.replace(tmp_path, output_path)
    print(f"War decks saved to {output_path}")


if __name__ == "__main__":
    main()
