# -*- coding: utf-8 -*-
"""合并两路战斗胜负判定：块解析（准，31 剧本）+ 场景图（覆盖另一批，15 剧本）。

冲突处理：同一 (剧本, 开关, 结果) 两路相反时，记入冲突清单，并采用块解析（直接读的控制流）。
"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki\data"
blk = json.load(open(os.path.join(BASE, "battle_results_block.json"), encoding="utf-8"))
grf = json.load(open(os.path.join(BASE, "battle_results_graph.json"), encoding="utf-8"))

merged, conflict = {}, []
for src, tag in ((blk, "block"), (grf, "graph")):
    for sc, sws in src.items():
        for sw, mp in sws.items():
            for res, lb in mp.items():
                cur = merged.setdefault(sc, {}).setdefault(sw, {})
                if res in cur and cur[res] != lb:
                    conflict.append((sc, sw, res, cur[res], lb, tag))
                    continue
                cur.setdefault(res, lb)

# 只留胜负齐全的开关
clean = {}
for sc, sws in merged.items():
    keep = {sw: mp for sw, mp in sws.items() if "胜" in mp.values() and "败" in mp.values()}
    if keep:
        clean[sc] = keep

json.dump(clean, open(os.path.join(BASE, "battle_results.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0, sort_keys=True)
print("合并后剧本 %d（块 %d / 图 %d）" % (len(clean), len(blk), len(grf)))
print("冲突 %d 条" % len(conflict))
for x in conflict[:8]:
    print("   ", x)
