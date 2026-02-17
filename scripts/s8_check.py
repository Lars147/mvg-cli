#!/usr/bin/env python3
"""Check next S8 trains approaching Daglfing direction Innenstadt."""
import json, subprocess, tempfile, os

GEOPS_WS_URL = "wss://api.geops.io/realtime-ws/v1/"
GEOPS_API_KEY = "5cc87b12d7c5370001c1d655112ec5c21e0f441792cfc2fafe3e7a1e"
GEOPS_ORIGIN = "https://s-bahn-muenchen-live.de"

# S8 stations Flughafen → Innenstadt with precise EPSG:3857 coords from MVG API
S8_STATIONS_INBOUND = [
    ("Flughafen", 1312038, 6165913),
    ("Besucherpark", 1309570, 6165738),
    ("Hallbergmoos", 1303993, 6158387),
    ("Ismaning", 1300109, 6144523),
    ("Unterföhring", 1296567, 6138766),
    ("Johanneskirchen", 1296422, 6134937),
    ("Englschalking", 1296693, 6132938),
    ("Daglfing", 1296800, 6131703),
    ("Berg am Laim", 1295025, 6129373),
    ("Leuchtenbergring", 1293080, 6129221),
]

# Approximate minutes from station to Daglfing
# Inbound = Flughafen → Daglfing → Herrsching
MINUTES_TO_DAGLFING_INBOUND = {
    "Flughafen": 20, "Besucherpark": 18, "Hallbergmoos": 14,
    "Ismaning": 10, "Unterföhring": 6, "Johanneskirchen": 4,
    "Englschalking": 2, "Daglfing": 0,
}
# Outbound = Herrsching/Pasing → Daglfing → Flughafen
MINUTES_TO_DAGLFING_OUTBOUND = {
    "Leuchtenbergring": 4, "Berg am Laim": 2, "Daglfing": 0,
    "Englschalking": 2, "Johanneskirchen": 4, "Unterföhring": 6,
    "Ismaning": 10, "Hallbergmoos": 14, "Besucherpark": 18, "Flughafen": 20,
}

# Destinations for display
INBOUND_DEST = "Herrsching"
OUTBOUND_DEST = "Flughafen"

def fetch_s8():
    js_code = """
const paths = [process.env.HOME+'/.openclaw/workspace/node_modules/ws','/app/node_modules/.pnpm/ws@8.19.0/node_modules/ws'];
let WS; for(const p of paths){try{WS=require(p);break}catch(e){}} if(!WS)try{WS=require('ws')}catch(e){process.exit(1)}
const ws=new WS(process.argv[2],{headers:{Origin:process.argv[3]}});
const t=[];
ws.on('open',()=>{ws.send('GET sbm_full');ws.send('SUB sbm_full');ws.send('BBOX 1268000 6110000 1350000 6200000 14')});
ws.on('message',r=>{try{const d=JSON.parse(r.toString());if(d.source==='trajectory'&&d.content?.properties?.line?.name==='S8')t.push(d.content)}catch(e){}});
setTimeout(()=>{ws.close();require('fs').writeFileSync(process.argv[4],JSON.stringify(t));process.exit(0)},10000);
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(js_code)
        jp = f.name
    of = jp + ".json"
    try:
        subprocess.run(
            ["node", jp, f"{GEOPS_WS_URL}?key={GEOPS_API_KEY}", GEOPS_ORIGIN, of],
            capture_output=True, text=True, timeout=15
        )
        if os.path.exists(of):
            with open(of) as fh:
                data = json.load(fh)
            os.unlink(of)
            return data
        return []
    finally:
        try:
            os.unlink(jp)
        except:
            pass


def nearest_station(pos):
    """Find nearest S8 station to EPSG:3857 coordinate."""
    x, y = pos
    best = None
    best_dist = float("inf")
    for name, sx, sy in S8_STATIONS_INBOUND:
        d = (x - sx) ** 2 + (y - sy) ** 2
        if d < best_dist:
            best_dist = d
            best = name
    return best


def main():
    trajs = fetch_s8()
    if not trajs:
        print(json.dumps({"error": "no data"}))
        return

    # Deduplicate: keep latest per train_id
    by_id = {}
    for t in trajs:
        tid = t.get("properties", {}).get("train_id", "")
        ts = t.get("properties", {}).get("timestamp", 0)
        if tid not in by_id or ts > by_id[tid].get("properties", {}).get("timestamp", 0):
            by_id[tid] = t

    inbound = []
    outbound = []
    for t in by_id.values():
        p = t.get("properties", {})
        route = p.get("route_identifier", "")
        parts = route.split("-")

        # Determine direction from route end station
        # 8002792 = Herrsching (inbound/westbound), 8004168 = Flughafen (outbound/eastbound)
        is_outbound = len(parts) >= 3 and parts[2] == "8004168"
        direction = OUTBOUND_DEST if is_outbound else INBOUND_DEST
        eta_table = MINUTES_TO_DAGLFING_OUTBOUND if is_outbound else MINUTES_TO_DAGLFING_INBOUND

        coords = t.get("geometry", {}).get("coordinates", [])
        if not coords:
            continue
        station = nearest_station(coords[0])

        # Only include trains that haven't passed Daglfing yet
        if station not in eta_table:
            continue
        # For inbound: only stations Flughafen..Daglfing (before passing)
        if not is_outbound and station in ("Berg am Laim", "Leuchtenbergring"):
            continue
        # For outbound: only stations Leuchtenbergring..Daglfing (before passing)
        if is_outbound and station in MINUTES_TO_DAGLFING_INBOUND and station != "Daglfing" and eta_table.get(station, 99) > 6:
            continue

        delay = p.get("delay")
        dm = round(delay / 60000) if delay else 0
        eta = eta_table.get(station, 99) + (dm if dm > 0 else 0)

        entry = {
            "train": p.get("train_number"),
            "at": station,
            "eta": eta,
            "delay": dm,
            "state": p.get("state"),
            "direction": direction,
        }
        if is_outbound:
            outbound.append(entry)
        else:
            inbound.append(entry)

    inbound.sort(key=lambda x: x["eta"])
    outbound.sort(key=lambda x: x["eta"])
    result = {"inbound": inbound[:3], "outbound": outbound[:3]}
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
