# -*- coding: utf-8 -*-
"""战斗关卡编号补前缀对齐：剧本里是 1001_2，资源里是 CL_1001_2 / BL_1001_2。

输出 data/battle_level_map.json：{"<script>|<line>": {"id":"CL_1001_2","desc":"…"}}
"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from opencc import OpenCC
cc = OpenCC("t2s")

BASE = r"D:\LegendOfMortal Wiki"
data = json.load(open(os.path.join(BASE, "data", "combat_levels.json"), encoding="utf-8"))
by_name = {x["name"]: x for x in data}
raw_map = json.load(open(os.path.join(BASE, "data", "battle_level_map_raw.json"), encoding="utf-8")) \
    if os.path.exists(os.path.join(BASE, "data", "battle_level_map_raw.json")) else {}
if not raw_map:
    raw_map = json.load(open(os.path.join(BASE, "data", "battle_level_map.json"), encoding="utf-8"))

def simplify(s):
    try:
        return cc.convert(s or "")
    except Exception:
        return s or ""

ET = {}
_etp = os.path.join(BASE, "data", "enemy_team_names.json")
if os.path.exists(_etp):
    ET = json.load(open(_etp, encoding="utf-8"))

out, hit, miss = {}, 0, []
bl_named = 0
for k, v in raw_map.items():
    cands = [v, "CL_" + v, "BL_" + v, "CL_" + v.upper(), "BL_" + v.upper()]
    got = next((c for c in cands if c in by_name), None)
    if got:
        desc = simplify(by_name[got]["desc"])
        cls = by_name[got]["cls"]
        if cls == "BattleLevel":
            nm = ET.get("EnemyTeam/" + (by_name[got]["desc"] or ""))
            if nm:
                desc = nm
                bl_named += 1
        out[k] = {"id": got, "desc": desc, "cls": cls}
        hit += 1
    else:
        miss.append(v)

print("对齐 %d / %d，漏 %d，战役名解出 %d" % (hit, len(raw_map), len(miss), bl_named))
print("漏的样例:", sorted(set(miss))[:12])
json.dump(out, open(os.path.join(BASE, "data", "battle_level_map.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0, sort_keys=True)
for k in list(out)[:10]:
    print("   %-22s %-12s %s" % (k, out[k]["id"], out[k]["desc"][:40]))
