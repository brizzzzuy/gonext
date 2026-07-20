from datetime import datetime
from zoneinfo import ZoneInfo

TASHKENT = ZoneInfo("Asia/Tashkent")
DAY = 24 * 3600

def baseline_from(history, n=10):
    if len(history) < n:
        return None
    recent = history[:n]
    adrs = [m["adr"] for m in recent if m["adr"] is not None]
    return {
        "kd": sum(m["kd"] for m in recent) / n,
        "adr": sum(adrs) / len(adrs) if adrs else None,
    }
    

def decide(session, baseline, history, now):
    if session:
        if len(session) >= 2 and not session[0]["won"] and not session[1]["won"]:
            return {"verdict": "STOP", "score": None, "reasons": [
                "2 losses in a row — this is the tilt zone, the next queue rarely saves it"]}
        if len(session) >= 3 and session[0]["won"]:
            return {"verdict": "BANK IT", "score": None, "reasons": [
                f"{len(session)} matches deep and the last one was a win — log off on top"]}
    score = 100
    reasons = []
    
    if session:
        if not session[0]["won"]:
            score -= 15
            reasons.append("Lost the last match (-15)")
            if len(session) >= 3 and sum(1 for m in session[:3] if not m["won"]) >=2:
                score -= 10
                reasons.append("Lost 2 of the last 3 (-10)")
        else:
            score += 10
            reasons.append("Won the last match (+10)")
            
        if baseline and baseline["kd"]:
            ratio = (sum(m["kd"] for m in session) / len(session)) / baseline["kd"]
            if ratio < 0.8:
                score -= 20
                reasons.append(f"Session K/D  at {ratio:.0%} of ypur usual - way off form (-20)")
            elif ratio < 0.95:
                score -= 10
                reasons.append("Session K/D slightly below your usual (-10)")
            elif ratio > 1.1:
                score += 10
                reasons.append("Fragging above ur usual level (+10)")    
        if len(session) >= 4:
            chrono = list(reversed(session))
            vals = [m["adr"] if m["adr"] is not None else m["kd"] for m in chrono]
            half = len(vals) // 2
            if sum(vals[half:]) / len(vals[half:]) < sum(vals[:half]) / half:
                score -= 15
                reasons.append("Damage output declining as the session goes on (-15)")
        
        if len(session) >= 5:
            score -= 10
            reasons.append(f"{len(session)} matches this session already (-10)")


    played_24h = sum(1 for m in history if now - m["ts"] < DAY)
    if played_24h >=6:
        score -= 15 
        reasons.append(f"{played_24h} matches  in the last 24h - fatigue (-15)")
    elif played_24h >=4:
        score -= 8
        reasons.append(f"{played_24h} matches in the last 24h (-8)")
    
    if 1 <= datetime.fromtimestamp(now, TASHKENT). hour < 8:
        score -= 10
        reasons.append(f"Its deep night in Tashkent (-10)")
    
    
    verdict = "QUEUE" if score  >= 70 else "RISKY" if score >= 40 else "STOP"
    if not reasons:
        reasons.append("Fresh queue, annihilate them!")
    return {"verdict": verdict, "score": score, "reasons": reasons}
                    
                            