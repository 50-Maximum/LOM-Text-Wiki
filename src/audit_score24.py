# -*- coding: utf-8 -*-
"""抽检 score 2~4 的年表命中：列出场景标题与它自己的全部选项，便于判断是否撞车。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()
ref = json.load(open(B + r"\scene_time_ref.json", encoding="utf-8"))
titles = dict(c.execute("select script,title from scenes"))

def opts(sc):
    out = []
    for seq, o in c.execute("select seq,options from choices where script=? order by seq", (sc,)):
        try:
            arr = json.loads(o or "[]")
        except Exception:
            continue
        for x in arr:
            t = (x.get("text") or x.get("label") or "").replace("\n", " ").strip()
            if t:
                out.append(t)
    return out

targets = [(sc, v) for sc, v in ref.items() if 2 <= (v.get("score") or 0) <= 4]
print("score 2~4 共 %d 条\n" % len(targets))
for sc, v in sorted(targets, key=lambda x: x[1].get("score") or 0):
    os_ = opts(sc)
    print("%-24s %s年%s月%s ｜ 年表:%s ｜ 分%s"
          % (sc, v.get("year"), v.get("month"), v.get("xun"), v.get("name"), v.get("score")))
    print("    场景标题: %s" % (titles.get(sc) or "-"))
    print("    场景选项: %s" % ("／".join(os_[:6])[:150] if os_ else "（无选项）"))
