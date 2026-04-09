# Clash Royale Deck Builder

A Kiro agent skill that fetches a Clash Royale player's card collection via the official API and generates styled HTML reports — card collection overviews and optimized war decks with synergy-first strategy.

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Fetch player data** from the official Clash Royale API
- **Card collection report** — HTML page showing all cards with images, levels, evo/hero badges, and rarity-colored borders
- **War decks builder** — 4 optimized war decks with synergy analysis, evo/hero slot assignments, and a "Best Unused Cards" section
- **Clash Royale UI styling** — dark blue-gray quilted background, actual Clash Royale fonts, in-game card frames, elixir drop icons, and text-stroke outlines matching the game
- **Smart card images** — hero art for hero slots, evo art for evo slots, and auto-detection based on player unlock state for collection views
- **Best Unused Cards** — sorted by level completion percentage (level/maxLevel), so a 10/11 epic ranks above a 14/16 rare

## Prerequisites

- Python 3.10+
- `curl` (used by the fetch script)
- A valid Clash Royale API token

## Setup

### 1. Get an API token

1. Go to [developer.clashroyale.com](https://developer.clashroyale.com)
2. Create an API key tied to your current public IP
3. Save the token:

```bash
echo "your-token-here" > ~/.cr_token
```

### 2. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/clash-royale-deck-builder.git
cd clash-royale-deck-builder
```

No dependencies to install — all scripts use Python stdlib only.

## Usage

### Fetch player data

```bash
python scripts/fetch_player.py --tag "P0RURJYV"
```

Options:
- `--tag TAG` — Player tag without `#` (default: `P0RURJYV`)
- `--token TOKEN` — Provide token directly instead of file
- `--token-file PATH` — Path to token file (default: `~/.cr_token`)
- `--output PATH` — Output JSON path (default: `cr_player_data.json`)

### Generate card collection report

```bash
python scripts/generate_card_report.py --input cr_player_data.json
```

Outputs `clash-royale-deck-{TAG}.html` — open in any browser.

### Generate war decks

```bash
python scripts/generate_war_decks_html.py --input cr_player_data.json
```

Outputs `clash-royale-war-decks-{TAG}.html` with 4 war decks and the top 25 best unused cards.

### Build reference (text-based analysis)

```bash
python scripts/build_war_decks.py --input cr_player_data.json
```

Outputs a text file with top cards by level for manual deck building reference.

## Project Structure

```
clash-royale-deck-builder/
├── SKILL.md                          # Kiro skill definition
├── README.md                         # This file
├── LICENSE                           # MIT License
├── .gitignore
├── references/
│   ├── deck-archetypes.md            # War deck archetypes and synergy patterns
│   ├── clash_royale_bold.otf         # Clash Royale Bold font
│   └── clash_royale_regular.otf      # Clash Royale Regular font
└── scripts/
    ├── cr_styles.py                  # Shared CSS, fonts, helpers, copyright
    ├── fetch_player.py               # Fetch player data from CR API
    ├── generate_card_report.py       # HTML card collection report
    ├── generate_war_decks_html.py    # HTML war decks report
    └── build_war_decks.py            # Text-based card analysis
```

## Card Image Logic

| Context | Image shown |
|---|---|
| War deck — hero slot | Hero art (`heroMedium`) |
| War deck — evo/flex-evo slot | Evo art (`evolutionMedium`) |
| War deck — other cards | Normal art (`medium`) |
| Collection / unused — hero unlocked | Hero art |
| Collection / unused — evo unlocked | Evo art |
| Collection / unused — neither | Normal art |

## Evo / Hero Detection

From the API fields `evolutionLevel` and `maxEvolutionLevel`:

| Condition | Status |
|---|---|
| `evolutionLevel >= 1` | Evo unlocked |
| `maxEvolutionLevel >= 2` and `evolutionLevel >= 2` | Hero unlocked |

## War Deck Rules

- 4 decks, 8 cards each, **no card overlap**
- Each deck has 3 evo/hero activation slots: 1 Hero + 1 Evo + 1 Flex
- Priority: Synergy → Card Level → Heroes → Evos

## Legal

This content is not affiliated with, endorsed, sponsored, or specifically approved by Supercell and Supercell is not responsible for it. For more information see [Supercell's Fan Content Policy](https://supercell.com/en/fan-content-policy/).

© Supercell Oy. Clash Royale, Supercell, and all associated logos and characters are trademarks of Supercell Oy.

The Clash Royale fonts included in `references/` are property of Supercell and are provided here under their [Fan Content Policy](https://supercell.com/en/fan-content-policy/) for non-commercial fan content use only.
