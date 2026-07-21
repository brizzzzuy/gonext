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
            "wr": sim(1 for m in matches if m["won"]) / len(matches) * 100,        
        }
    
    return {
        "lifetime": block(history),
        "baseline": block(history[:10]),
        "toatal": len(history),
        "wins": wins,
        "loses": len(history) - wins,
        "backtest": backtest(history),
    }

def backtest(history):
    chrono = list(reversed(history))
    stops = sum(
        1 for i in range (2, len(chrono))
        if not chrono[i - 1]["won"] and not chrono[i - 2]["won"]
    )
    return {"stop_signals" : stops}