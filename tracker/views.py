import time
from datetime import datetime
from zoneinfo import ZoneInfo

from django.shortcuts import render
import json
from . import faceit
from .decider import baseline_from, decide
from .sessions import group_sessions, normalize
TASHKENT = ZoneInfo("Asia/Tashkent")
# Create your views here.

def lookup(request):
    ctx = {}
    nickname = request.GET.get("nickname", "").strip()
    if nickname:
        ctx["nickname"] = nickname
        player = faceit.get_player(nickname)
        if player is None:
            ctx["error"] = f"'{nickname} not found or error occured"
        else:
            cs2 = player.get("games", {}).get("cs2") or {}
            ctx["player"] = {
                "nickname": player["nickname"],
                "avatar": player.get("avatar", ""),
                "level": cs2.get("skill_level"),
                "elo": cs2.get("faceit_elo"),
                "country": player.get("country", "").upper(),
            }
            raw = faceit.get_player_stats(player["player_id"])
            if not raw:
                ctx["error"] = "No CS2 match history for this player."
            else:
                now = time.time()
                history = sorted(
                    (normalize(m) for m in raw), key=lambda m: -m["ts"]
                )
                _, active = group_sessions(raw, now=now)
                ctx["verdict"] = decide(
                    active, baseline_from(history), history, now
                )
                if active:
                    ctx["session_str"] = "".join(
                        "W" if m["won"] else "L" for m in reversed(active)
                    )
    return render(request, "tracker/lookup.html", ctx)      


def stats(request):
    ctx = {}
    nickname = request.GET.get("nickname", "").strip()
    if nickname:
        ctx["nickname"] = nickname
        player = faceit.get_player(nickname)       
        if player is None:
            ctx["error"] = f"'{nickname}' not found or API error occured"
        else:
            raw = faceit.get_player_stats(player["player_id"])  
            if not raw:
                ctx["error"] = "No CS2 match history" 
            else:
                from .stats import compute_stats
                history = sorted(
                    (normalize(m) for m in raw), key=lambda m: -m["ts"]
                )      
                ctx["stats"] = compute_stats(history)
    return render(request, "tracker/stats.html", ctx)            
            
            
def history(request):
    ctx =  {}
    nickname = request.GET.get("nickname", "").strip()
    if nickname:
        ctx["nickname"] = nickname
        player = faceit.get_player(nickname)       
        if player is None:
            ctx["error"] = f"'{nickname}' not found or API error occured"
        else:
            raw = faceit.get_player_stats(player["player_id"])  
            if not raw:
                ctx["error"] = "No CS2 match history" 
            else:
                sessions, _ = group_sessions(raw)
                rows = []
                for sess in sessions:
                    wl = "".join("W" if m["won"] else "L" for m in reversed(sess))
                    wins = sum(1 for m in sess if m["won"])
                    rows.append({
                        "date": datetime.fromtimestamp(
                            sess[0]["ts"], TASHKENT
                        ).strftime("%b %d, %H:%M"),
                        "n": len(sess),
                        "wl": wl,
                        "wins": wins,
                        "losses": len(sess) -  wins,
                        "kd": sum(m["kd"] for m in sess) / len(sess)
                    })
                ctx["rows"] = rows
    return render(request, "tracker/history.html", ctx)
    