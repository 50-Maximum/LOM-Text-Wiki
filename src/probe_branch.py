# -*- coding: utf-8 -*-
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(os.path.join(B, "wiki.db"))
c.row_factory = sqlite3.Row
tabs = [r[0] for r in c.execute("select name from sqlite_master where type='table' order by name")]
print("表：", tabs)
for t in tabs:
    if any(k in t.lower() for k in ("choice", "option", "branch", "edge")):
        cols = [d[1] for d in c.execute("pragma table_info(%s)" % t)]
        n = c.execute("select count(*) from %s" % t).fetchone()[0]
        print("\n== %s (%d 行) 列：%s" % (t, n, cols))
        for r in c.execute("select * from %s limit 2" % t):
            print("   ", {k: (str(r[k])[:60]) for k in r.keys()})

p = os.path.join(B, "choice_branch.json")
if os.path.exists(p):
    d = json.load(open(p, encoding="utf-8"))
    print("\nchoice_branch.json 类型", type(d).__name__, "长度", len(d))
    if isinstance(d, dict):
        k = list(d)[0]
        print("样例键", k, "→", json.dumps(d[k], ensure_ascii=False)[:400])
    else:
        print("样例", json.dumps(d[0], ensure_ascii=False)[:400])
