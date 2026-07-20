GAP_SECONDS = 2  * 60 * 60


def normalize(match):
    s = match["stats"]
    adr = s.get("ADR")
    return {
        "ts": s["Match Finished At"] / 1000, #ms to seconds btw
        "won": s.get("Result") == "1",
        "kd": float(s["K/D Ratio"]),
        "adr": float(adr) if adr is not None else None,
        "map": s.get("Map", "")
    }
    
    
    
def group_sessions(matches, now=None):
    ms = sorted((normalize(m) for m in matches), key=lambda m: -m["ts"])
    if not ms:
        return[], None
    sessions = [[ms[0]]]
    for m in ms[1:]:
        if sessions[-1][-1]["ts"] - m["ts"] < GAP_SECONDS:
            sessions[-1].append(m)
        else:
            sessions.append([m])
    active = None
    if now is not None and now - sessions[0][0]["ts"] < GAP_SECONDS:
        active =  sessions[0]
    return sessions, active