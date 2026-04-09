# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Fetch a Clash Royale player's full profile from the official API."""

import argparse
import json
import os
import subprocess
import sys
import tempfile


def resolve_token(token: str | None, token_file: str) -> str:
    if token:
        return token.strip()
    path = os.path.expanduser(token_file)
    if not os.path.isfile(path):
        print(f"Error: Token file not found at {path}", file=sys.stderr)
        print("Create an API key at https://developer.clashroyale.com", file=sys.stderr)
        print(f"and save it to {token_file}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r") as f:
        return f.read().strip()


def fetch_player(tag: str, token: str) -> dict:
    url = f"https://api.clashroyale.com/v1/players/%23{tag}"
    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {token}",
         "-H", "Accept: application/json", url],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Error: curl failed with code {result.returncode}", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Error: Invalid JSON response from API", file=sys.stderr)
        print(result.stdout[:500], file=sys.stderr)
        sys.exit(1)

    if "reason" in data:
        print(f"API Error: {data.get('reason')} - {data.get('message')}", file=sys.stderr)
        sys.exit(1)

    return data


def main():
    parser = argparse.ArgumentParser(description="Fetch Clash Royale player data")
    parser.add_argument("--tag", default="P0RURJYV", help="Player tag without # (default: P0RURJYV)")
    parser.add_argument("--token-file", default="~/.cr_token", help="Path to token file")
    parser.add_argument("--token", default=None, help="API token directly")
    parser.add_argument("--output", default=None, help="Output JSON path")
    args = parser.parse_args()

    tag = args.tag.lstrip("#")
    token = resolve_token(args.token, args.token_file)
    output = args.output or f"cr_player_data.json"

    print(f"Fetching player #{tag}...")
    data = fetch_player(tag, token)

    # Write to temp first, then move
    output_path = os.path.realpath(output)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, dir=os.path.dirname(output_path) or ".") as tmp:
        json.dump(data, tmp, indent=2)
        tmp_path = tmp.name

    os.replace(tmp_path, output_path)
    print(f"Player data saved to {output_path}")
    print(f"Player: {data.get('name')} ({data.get('tag')})")
    print(f"Trophies: {data.get('trophies')} | Arena: {data.get('arena', {}).get('name')}")
    print(f"Cards: {len(data.get('cards', []))} | Support: {len(data.get('supportCards', []))}")


if __name__ == "__main__":
    main()
