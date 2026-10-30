# -*- coding: utf-8 -*-
"""按事件对应剧本的场景页地点，生成 data/map_event_place.json（证据取自场景页，不用前缀猜）。"""
import io, json, os, re, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
RAW_S = os.path.join(BASE, "data", "raw", "scripts")
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.row_factory = sqlite3.Row
pm = json.load(open(os.path.join(BASE, "data", "position_script_map.json"), encoding="utf-8"))
fam = json.load(open(os.path.join(BASE, "data", "position_script_family.json"), encoding="utf-8"))
pe = json.load(open(os.path.join(BASE, "data", "position_events.json"), encoding="utf-8"))
files = {fn[:-4] for fn in os.listdir(RAW_S) if fn.endswith(".txt")}

def section_base(code):
    m = re.match(r"Section_(\d+)_(\d+)_(\d+)_", code)
    if m:
        return "section_%s_free_%s_%s" % m.groups()
    m = re.match(r"Section_(\d+)_(\d+)_Start_", code)
    if m:
        return "section_%s_free_%s_start" % (m.group(1), m.group(2))
    return None

def resolve(code, value):
    v = (value or "").strip()
    bases = []
    if pm.get(code):
        bases.append(pm[code])
    sb = section_base(code)
    if sb:
        bases.append(sb)
    fl = fam.get(code) or []
    if isinstance(fl, str):
        fl = [fl]
    bases += [b for b in fl if b not in bases]
    for b in bases:
        if v:
            for cand in (b + "_" + v, b + "_" + v + "_01"):
                if cand in files:
                    return cand
            hits = sorted(k for k in files if k.startswith(b + "_" + v))
            if hits:
                return hits[0]
    for b in bases:
        if b in files:
            return b
    return None

out = {}
for x in pe:
    code = x.get("name")
    if not code or code in out:
        continue
    sc = resolve(code, x.get("value"))
    if not sc:
        continue
    r = c.execute("select sections from pages where slug=?", ("场景/" + sc,)).fetchone()
    if not r:
        continue
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") != "场景信息":
            continue
        m = re.search(r"地点：([^（。]+)（", s.get("html") or "")
        if m:
            out[code] = m.group(1).strip()

json.dump(out, open(os.path.join(BASE, "data", "map_event_place.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("地点映射", len(out), "条")
for k in list(out)[:8]:
    print("   ", k, "→", out[k])
