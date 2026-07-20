from django.shortcuts import render
import json
from . import faceit

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
            stats = faceit.get_player_stats(player["player_id"])
            ctx["player_json"] = json.dumps(player, indent=2)
            ctx["stats_json"] = json.dumps(stats, indent=2)
            
    return render(request, "tracker/lookup.html", ctx)