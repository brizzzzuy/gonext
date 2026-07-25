from datetime import datetime
from zoneinfo import ZoneInfo

TASHKENT = ZoneInfo("Asia/Tashkent")


def _avg(vals):
    vals = [v for v in vals if v is not None]
    return sum(vals)  / len(vals) if vals else None



def compute_stats(history):
    if not history:
        return None
    wins = sum(1 for m in history if m["won"])

    def block(matches):
        return{
            "n": len(matches),
            "kd": _avg([m["kd"] for m in matches]),
            "adr": _avg([m["adr"] for m in matches]),
            "hs": _avg([m["hs"] for m in matches]),
            "kr": _avg([m["kr"] for m in matches]),
            "wr": sum(1 for m in matches if m["won"]) / len(matches) * 100,        
        }
    
    return {
        "lifetime": block(history),
        "baseline": block(history[:10]),
        "total": len(history),
        "wins": wins,
        "losses": len(history) - wins,
        "backtest": backtest(history),
        "tod": time_of_day(history),
        "maps": map_perfomance(history)
    }

def backtest(history):
    chrono = list(reversed(history))
    stops = sum(
        1 for i in range (2, len(chrono))
        if not chrono[i - 1]["won"] and not chrono[i - 2]["won"]
    )
    return {"stop_signals" : stops}\
        
        
def time_of_day(history):
    day = [
        m for m in history
        if datetime.fromtimestamp(m["ts"], TASHKENT).hour < 18
    ]
    night = [
         m for m in history
        if datetime.fromtimestamp(m["ts"], TASHKENT).hour >= 18
    ]
    def wr(ms):
        return sum(1 for m in ms if m["won"]) / len(ms) * 100 if ms else None
    return {
        "day_wr": wr(day), "day_n": len(day),
        "night_wr": wr(night), "night_n": len(night),
    }
    
def map_performance(history):
    maps={}
    for m in history:
        name = m["map"] or "Unknown"
        maps.setdefault(name, []).append(m)
    rows = []
    for name, ms in maps.items():
        if len(ms) < 2:
            continue
        rows.append({
            "map": name.split("_")[-1].title(),
            "n": len(ms),
            "wr": sum(1 for x in ms if x["won"]) / len(ms) * 100,
            "kd":  sum(x["kd"] for x in ms) / len(ms),
        })
    return sorted(rows, key=lambda r: -r["n"])