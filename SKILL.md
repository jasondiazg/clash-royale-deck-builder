---
name: clash-royale-deck-builder
description: "This skill fetches and analyzes a Clash Royale player's full card collection via the official API, generates formatted card deck reports, builds optimized war decks with synergy-first strategy, and builds best decks (4 different archetypes where cards can repeat). This skill should be used when the user mentions 'Clash Royale', 'CR deck', 'war decks', 'best decks', 'card collection', 'clash royale cards', or 'CR player'. Triggers include: 'clash royale', 'CR deck', 'war decks', 'best decks', 'card deck', 'clash royale player', 'CR cards', 'evo', 'hero cards'."
license: Proprietary
compatibility: "Requires Python 3.10+, curl, and a valid Clash Royale API token stored at ~/.cr_token. Token can be generated at https://developer.clashroyale.com"
runtimes:
  - kiro
metadata:
  version: "0.6.0"
  short_description: "Fetch CR player cards and build meta-informed war decks and best decks"
---

# Clash Royale Deck Builder

## Purpose

Fetch a Clash Royale player's full card collection from the official API, generate formatted reports showing card levels, evolution status, and hero status, build optimized war decks prioritizing synergy and current meta, and build best decks (4 different archetypes where cards can repeat across decks).

## When to Use

Activate when the user wants to:
- View a Clash Royale player's card collection
- Generate a formatted card deck report
- Build optimized war decks for Clan War
- Build best decks (4 archetypes, cards can repeat across decks)
- Analyze which evos and heroes a player has unlocked

## Configuration

### API Token

The skill reads the Clash Royale API bearer token from `~/.cr_token`. If the file does not exist, prompt the user to:
1. Go to https://developer.clashroyale.com
2. Create an API key tied to their current public IP
3. Save the token to `~/.cr_token`

The user can also provide a token directly via the `--token` flag on any script.

### Default Player

Default player tag: `#P0RURJYV`. The user can provide any valid player tag in the format `#XXXXXXXX`.

## API Reference

### Official Clash Royale API

Base URL: `https://api.clashroyale.com/v1`
Auth: `Authorization: Bearer <token>` header
Swagger spec: `GET https://api.clashroyale.com/v1` (returns YAML)

Key endpoints used by this skill:
- `GET /players/{playerTag}` — Full player profile with cards, deck, support cards
- `GET /players/{playerTag}/battlelog` — Recent battles (useful for meta analysis)
- `GET /locations/global/pathoflegend/{seasonId}/rankings/players` — Top Path of Legends players
- `GET /locations/{locationId}/pathoflegend/players` — Regional PoL rankings
- `GET /locations/global/rankings/players` — Global trophy rankings
- `GET /cards` — All cards in the game with current stats
- `GET /challenges` — Active challenges
- `GET /globaltournaments` — Active global tournaments

Player tags must be URL-encoded: `#P0RURJYV` becomes `%23P0RURJYV`.

### RoyaleAPI Proxy (optional)

If the developer's IP is dynamic, use `https://proxy.royaleapi.dev` as a drop-in replacement for `https://api.clashroyale.com`. The API key must whitelist IP `45.79.218.79`. Same endpoints, same auth.

## Workflow

### 0. Check Current Meta (REQUIRED before building war decks)

Before building war decks, ALWAYS check the current meta. This step is mandatory.

#### Method: Top Player Deck Analysis (Official API)

Fetch the current decks of top Path of Legends players to identify what's strong in the meta:

```bash
# Get top 100 Path of Legends players
TOKEN=$(cat ~/.cr_token)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.clashroyale.com/v1/locations/global/pathoflegend/players?limit=100"

# For each top player, fetch their current deck
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.clashroyale.com/v1/players/%23{TAG}"
```

From the top player decks, identify:
1. Which win conditions appear most frequently
2. Which cards are common across multiple top decks
3. Which deck archetypes are represented
4. Which evos and heroes top players are using

#### Method: Web Search (supplementary)

Additionally search the web for:
- "Clash Royale best decks [current month] [current year]"
- "Clash Royale meta [current month] [current year]"
- "Clash Royale tier list [current month] [current year]"

Document meta findings in the war decks output file header under a "META CONTEXT" section.

### 1. Fetch Player Data

Run `scripts/fetch_player.py` to retrieve the player's full profile.

```bash
python ~/.kiro/skills/clash-royale-deck-builder/scripts/fetch_player.py --tag "P0RURJYV"
```

Optional flags:
- `--tag TAG`: Player tag without `#` (default: `P0RURJYV`)
- `--token-file PATH`: Path to token file (default: `~/.cr_token`)
- `--token TOKEN`: Provide token directly instead of file
- `--output PATH`: Output JSON path (default: `cr_player_data.json`)

### 2. Generate Card Collection Report

Run `scripts/generate_card_report.py` to produce a Clash Royale-styled `.html` report.

```bash
python ~/.kiro/skills/clash-royale-deck-builder/scripts/generate_card_report.py --input cr_player_data.json
```

The report is a self-contained HTML file styled after the Clash Royale in-game UI (dark blue/navy backgrounds, gold accents, rarity-colored card borders, elixir cost bubbles, level progress bars, and evo/hero/maxed badges). It includes card artwork from the API's `iconUrls`. The report ALWAYS includes a **BEST UNUSED CARDS** section listing all cards not in the player's current battle deck, sorted with maxed cards (level == maxLevel) first, then by descending level, then alphabetically. Each card tile shows rarity border color, evo/hero badges, and a MAX badge where applicable. This section appears right after the current battle deck and before the full collection breakdown. The output file extension is `.html` (default: `clash-royale-deck-{TAG}.html`).

### 3. Build War Decks

Build 4 war decks incorporating meta findings and player card data.

Run `scripts/build_decks.py --mode war` for card analysis reference:

```bash
python ~/.kiro/skills/clash-royale-deck-builder/scripts/build_decks.py --mode war --input cr_player_data.json
```

Then generate the HTML report:

```bash
python ~/.kiro/skills/clash-royale-deck-builder/scripts/generate_decks_html.py --mode war --input cr_player_data.json
```

Legacy wrappers `build_war_decks.py` and `generate_war_decks_html.py` still work for backward compatibility.

The agent MUST:
1. Incorporate meta findings from Step 0
2. Prioritize archetypes currently strong in the meta
3. Avoid recently nerfed cards/archetypes
4. Include a "Meta Context" section in the output
5. ALWAYS include a "Best Unused Cards" section at the end listing the top 25
   unused cards ranked by combined meta usage rate + card level, with specific
   swap recommendations explaining which deck card they could replace and why

### User Card Preferences

The user may request specific cards to be included. When this happens:
- Treat as hard requirements — requested cards MUST appear in one of the 4 decks
- Build synergistic decks around the requested cards first
- Then fill remaining decks with the best available cards

This applies to both war decks (Step 3) and best decks (Step 4).

### 4. Build Best Decks

Build 4 best decks with different archetypes. Unlike war decks, cards CAN repeat across decks. This mode focuses purely on building the strongest possible decks for the player regardless of card overlap.

Run `scripts/build_decks.py --mode best` for card analysis reference:

```bash
python ~/.kiro/skills/clash-royale-deck-builder/scripts/build_decks.py --mode best --input cr_player_data.json
```

Then generate the HTML report:

```bash
python ~/.kiro/skills/clash-royale-deck-builder/scripts/generate_decks_html.py --mode best --input cr_player_data.json
```

Both scripts also accept `--decks <file.json>` to pass custom deck definitions (agent-generated from meta analysis). Legacy wrappers `build_best_decks.py` and `generate_best_decks_html.py` still work for backward compatibility.

#### Key Differences from War Decks

| Aspect | War Decks (Step 3) | Best Decks (Step 4) |
|--------|-------------------|---------------------|
| Card overlap | No card can repeat across decks | Cards CAN repeat across decks |
| Purpose | Clan War (need 4 unique decks) | General play (strongest possible decks) |
| Output file | `clash-royale-war-decks-{TAG}.html` | `clash-royale-best-decks-{TAG}.html` |
| Shared cards section | N/A | Shows which cards appear in multiple decks |

The agent MUST:
1. Incorporate meta findings from Step 0
2. Use 4 different archetypes (e.g., Beatdown, Bait, Bridge Spam, Cycle)
3. Prioritize the player's highest-level cards across all decks
4. Allow the same card in multiple decks when it fits the archetype
5. Include a "Shared Cards Across Decks" section showing cards used in 2+ decks
6. Each deck still has 3 evo/hero slots (1 Hero + 1 Evo + 1 Flex)

#### Running Only Best Decks

The user can request only the best decks report without generating war decks. When the user asks for "best decks" specifically (not "war decks"), run only Steps 0, 1, and 4. Skip Step 3 entirely.

## Key Domain Knowledge

### Evolution and Hero Detection

The API uses `evolutionLevel` and `maxEvolutionLevel` fields:

- **Evo unlocked**: `evolutionLevel >= 1`
- **Hero unlocked**: `maxEvolutionLevel >= 2` AND `evolutionLevel >= 2`

Level breakdown:
- `maxEvolutionLevel == 0`: No evo or hero exists
- `maxEvolutionLevel == 1`: Only evo exists
- `maxEvolutionLevel == 2`: Evo at level 1, Hero at level 2
- `maxEvolutionLevel == 3`: Evo at levels 1-2, Hero starts at level 2

### War Deck Evo/Hero Slots

Each war deck has exactly 3 evo/hero activation slots:
1. **Hero slot** (1): Dedicated to a hero card
2. **Evo slot** (1): Dedicated to an evo card
3. **Flex slot** (1): Can be either hero or evo

More evo/hero cards can be in the deck, but only 3 are "enabled" during battle.

### War Deck Building Priority

1. **Synergy**: Deck archetype and card interactions first
2. **Card Level**: Higher level preferred regardless of evo/hero
3. **Heroes**: Prefer hero-unlocked cards for hero/flex slots
4. **Evos**: Prefer evo-unlocked cards for evo/flex slots

### Card Rarity Max Levels

| Rarity    | Max Level |
|-----------|-----------|
| Common    | 16        |
| Rare      | 14        |
| Epic      | 11        |
| Legendary | 8         |
| Champion  | 6         |

## References

Refer to `references/deck-archetypes.md` for common deck archetypes and synergy patterns.
