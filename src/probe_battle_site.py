# -*- coding: utf-8 -*-
"""看战斗边的 site 字段是不是关卡编号，能否对上 CombatLevel 名。"""
import io, json, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(BASE + r"\data\wiki.db")
c.row_factory = sqlite3.Row
lv = {}
for x in json.load(open(BASE + r"\data\combat_levels.json", encoding="utf-8")):
    lv[x["name"]] = x["desc"]
rows = list(c.execute("select src,dst,type,site from scene_edges where dst like 'Combat%' or dst like 'Battle%'"))
print("战斗边", len(rows))
print("site 取值样例:", collections.Counter(r["site"] or "" for r in rows).most_common(8))
hit = sum(1 for r in rows if (r["site"] or "") in lv)
print("site 命中关卡名:", hit, "/", len(rows))
for r in rows[:8]:
    print("   %-24s dst=%-10s site=%-14s → %s" % (r["src"], r["dst"], r["site"], lv.get(r["site"] or "", "")))
print("\nCombatLevel 名总数", len(lv))
