# -*- coding: utf-8 -*-
"""验证战斗胜负方向：目标场景标题含「胜/败」时是否与标签一致。"""
import io, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
title = {r[0]: (r[1] or "") for r in c.execute("select script,title from scenes")}

def win_res(sw):
    if sw.startswith("Combat_Result"):
        return 1 if sw.endswith("_02") else 2
    if sw.startswith("Battle_Result"):
        return 1 if sw.endswith("_001") else 2
    return None

stat = collections.Counter()
agree, disagree = [], []
for r in c.execute("select src,dst,switch,result from scene_edges where switch like 'Combat_Result%' or switch like 'Battle_Result%'"):
    wr = win_res(r["switch"] or "")
    if wr is None:
        continue
    try:
        res = int(r["result"] or 0)
    except Exception:
        continue
    lab = "胜" if res == wr else "败"
    t = title.get(r["dst"], "") or ""
    if "胜" in t or "败" in t:
        stat[lab] += 1
        (agree if (("胜" in t and lab == "胜") or ("败" in t and lab == "败")) else disagree).append((r["src"], r["dst"], r["switch"], res, lab, t))

print("目标标题带胜负字样的边:", dict(stat))
print("一致:", len(agree), "不一致:", len(disagree))
for x in disagree[:10]:
    print("   不一致", x)
for x in agree[:6]:
    print("   一致", x)
