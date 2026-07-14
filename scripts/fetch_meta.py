import json, os, urllib.request, urllib.error

token = open(os.path.expanduser('~/.cr_token')).read().strip()

def api_get(endpoint):
    url = f"https://api.clashroyale.com/v1{endpoint}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"  HTTP Error {e.code}: {e.read().decode('utf-8')}")
        return None

# First get top PoL players
data = api_get("/locations/global/pathoflegend/players?limit=15")
if not data or 'items' not in data:
    print("Failed to get top players")
    exit(1)

tags = [p['tag'].replace('#', '') for p in data['items'][:15]]
print(f"Found {len(tags)} top players")

all_cards = {}
all_decks = []

for tag in tags:
    pdata = api_get(f"/players/%23{tag}")
    if pdata and 'currentDeck' in pdata:
        deck = [c['name'] for c in pdata['currentDeck']]
        all_decks.append(deck)
        for card in deck:
            all_cards[card] = all_cards.get(card, 0) + 1
        print(f"  Got deck for {pdata.get('name', tag)}")

print(f"\nAnalyzed {len(all_decks)} top player decks")
print()
print("=== MOST USED CARDS (top 30) ===")
sorted_cards = sorted(all_cards.items(), key=lambda x: -x[1])
for name, count in sorted_cards[:30]:
    pct = count / len(all_decks) * 100
    print(f"  {name}: {count}/{len(all_decks)} decks ({pct:.0f}%)")

print()
print("=== TOP DECKS ===")
for i, deck in enumerate(all_decks[:10], 1):
    print(f"  Deck {i}: {', '.join(deck)}")

# Save meta data
meta = {
    "top_cards": sorted_cards[:30],
    "top_decks": all_decks[:10],
    "total_decks_analyzed": len(all_decks)
}
with open("meta_data.json", "w") as f:
    json.dump(meta, f, indent=2)
print("\nMeta data saved to meta_data.json")
