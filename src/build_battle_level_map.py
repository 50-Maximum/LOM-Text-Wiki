# -*- coding: utf-8 -*-
"""把战斗边对到具体关卡编号：读剧本对应行的 ChangeScene("Combat"/"Battle", "ID")。

输出 data/battle_level_map.json：{"<script>|<line>": "<关卡编号>"}
"""
import io, json, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
RAW = os.path.join(BASE, "data", "raw", "scripts")
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.row_factory = sqlite3.Row

levels = {x["name"] for x in json.load(open(os.path.join(BASE, "data", "combat_levels.json"), encoding="utf-8"))}
CS = re.compile(r'ChangeScene\(\s*"(Combat|Battle)"\s*,\s*"([^"]*)"')

edges = list(c.execute("select src,dst,type,line,site from scene_edges where dst like 'Combat%' or dst like 'Battle%'"))
print("战斗边", len(edges))

out, miss = {}, 0
for e in edges:
    sc, ln = e["src"], e["line"]
    p = os.path.join(RAW, sc + ".txt")
    if not ln or not os.path.exists(p):
        miss += 1
        continue
    lines = open(p, encoding="utf-8", errors="ignore").read().splitlines()
    idx = int(ln) - 1
    got = None
    # 行号可能有 1 行偏差，附近 ±2 行找
    for k in (idx, idx - 1, idx + 1, idx - 2, idx + 2):
        if 0 <= k < len(lines):
            m = CS.search(lines[k])
            if m:
                got = m.group(2)
                break
    if got:
        out["%s|%s" % (sc, ln)] = got
    else:
        miss += 1

hit = sum(1 for v in out.values() if v in levels)
print("解出行", len(out), "其中命中关卡表", hit, "漏", miss)
print("未命中关卡的编号样例:", [v for v in list(out.values()) if v not in levels][:8])
json.dump(out, open(os.path.join(BASE, "data", "battle_level_map.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0, sort_keys=True)
