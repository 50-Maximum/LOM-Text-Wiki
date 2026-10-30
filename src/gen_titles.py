# -*- coding: utf-8 -*-
"""给未命名场景起名：0 句转场按下一场命名，泛标题人工命名。"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
D = os.path.join(BASE, "data")
con = sqlite3.connect(os.path.join(D, "wiki.db"))
con.row_factory = sqlite3.Row
rows = {r["script"]: dict(r) for r in con.execute(
    "select script,title,line_count,chapter from scenes")}
NXT = json.load(open(os.path.join(D, "scene_next.json"), encoding="utf-8"))
if "NXT" in NXT:
    NXT = NXT["NXT"]

T = os.path.join(D, "title_override.json")
tt = json.load(open(T, encoding="utf-8")) if os.path.exists(T) else {}

HAND = {
    "S0014_01_01": "赵活衣物被窃遭峨嵋弟子点穴",
    "S0213_02": "叶云裳锁门让赵活参悟剑圣极招",
    "S0502_01": "赵活回想猴儿酒失手滑落",
    "S2914_02": "赵活帮手修装备反遭同门抱怨",
    "S2901_03_01_06_02": "赵活替郁父投壶翻本",
}
tt.update(HAND)

GEN = {"结果", "这是因为", "你的领悟", "你的干劲"}
n_auto = 0
for sc, d in rows.items():
    t = (d.get("title") or "").strip()
    if t and t not in GEN:
        continue
    if sc in HAND:
        continue
    if (d.get("line_count") or 0) > 0:
        continue
    nx = NXT.get(sc)
    if isinstance(nx, dict):
        nx = nx.get("next") or (list(nx.values())[0] if nx else None)
    if isinstance(nx, list):
        nx = nx[0] if nx else None
    nt = ""
    if nx and nx in rows:
        nt = (rows[nx].get("title") or "").strip()
        if nt in GEN:
            nt = ""
    if nt:
        tt[sc] = "转场：接「%s」" % nt
    elif nx:
        tt[sc] = "转场：接 %s" % nx
    else:
        tt[sc] = "转场（无台词）"
    n_auto += 1

json.dump(tt, open(T, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("人工命名", len(HAND), "条；自动命名转场", n_auto, "条；合计", len(tt))
for k in list(HAND):
    print("   %-24s %s" % (k, tt[k]))
