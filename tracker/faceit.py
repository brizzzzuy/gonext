import os
import requests

BASE = "https://open.faceit.com/data/v4"

def _headers():
    return {"Authorization": f"Bearer {os.getenv('FACEIT_API_KEY')}"}


def _get(url, params=None):
    try:
        r = requests.get(url, headers = _headers(), params=params, timeout=10)
    except requests.RequestException:
        return None
    return r.json() if r.status_code == 200 else None

def get_player(nickname):
    return _get(f"{BASE}/players", {"nickname": nickname} )


def get_player_stats(player_id, limit=50):
    data = _get(f"{BASE}/players/{player_id}/games/cs2/stats", {"limit": limit})
    return None if data is None else data.get("items", [])        