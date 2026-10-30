# -*- coding: utf-8 -*-
"""战斗胜负判定 v5：改用已解析的场景图（scene_edges），比扫 Lua 块更全。

规则（同一剧本同一战斗开关内）：
- 某结果的目标是 GameOver…            → 败
- 某结果的目标是同一剧本自己（重打）   → 败
- 某结果的目标是 Combat/Battle 且同开关另有剧情去向 → 败（打回去重来）
- 另有结果指向剧情场景                → 胜
只保留同开关内同时存在胜与败的情况，单边不猜。
"""
import io, json, os, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.row_factory = sqlite3.Row

groups = collections.defaultdict(lambda: collections.defaultdict(list))
for r in c.execute("""select src,dst,type,switch,result from scene_edges
                      where switch like 'Combat_Result%' or switch like 'Battle_Result%'"""):
    groups[(r["src"], r["switch"])][str(r["result"])].append((r["dst"], r["type"]))

def is_battle_node(d):
    return d.startswith(("Combat", "Battle"))

out, stat = {}, collections.Counter()
for (src, sw), resmap in groups.items():
    labels = {}
    for res, edges in resmap.items():
        dsts = [d for d, t in edges]
        types = [t for d, t in edges]
        if any(d.startswith("GameOver") for d in dsts):
            labels[res] = "败"
        elif src in dsts:
            labels[res] = "败"
        elif all(is_battle_node(d) for d in dsts) and dsts:
            labels[res] = "败"
        elif any(not is_battle_node(d) for d in dsts):
            labels[res] = "胜"
        else:
            labels[res] = ""
    if "胜" in labels.values() and "败" in labels.values():
        out.setdefault(src, {})[sw] = {k: v for k, v in labels.items() if v}
        stat[sw] += 1

# 与旧版对比
old = {}
p = os.path.join(BASE, "data", "battle_results_graph.json")
if os.path.exists(p):
    old = json.load(open(p, encoding="utf-8"))

json.dump(out, open(os.path.join(BASE, "data", "battle_results_graph.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0, sort_keys=True)
print("图判定剧本 %d（旧 %d）" % (len(out), len(old)))
print("开关分布:", dict(stat))
for sc in list(out)[:6]:
    print("   ", sc, json.dumps(out[sc], ensure_ascii=False))

