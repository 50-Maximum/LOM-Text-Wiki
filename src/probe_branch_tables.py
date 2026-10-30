# -*- coding: utf-8 -*-
"""看 branches/choices 表结构，以及 ch6_7_1 里条件是怎么存的。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
con = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
con.row_factory = sqlite3.Row
for t in ["branches", "choices", "branch_nodes", "cond"]:
    try:
        print(t, "列:", [x[1] for x in con.execute("PRAGMA table_info(%s)" % t)])
        n = con.execute("select count(*) from %s" % t).fetchone()[0]
        print("   行数:", n)
    except Exception as e:
        print(t, "缺失", e)

print("\nbranches 样例（ch6_7_1）:")
for r in con.execute("select * from branches where script='ch6_7_1' limit 5"):
    print("  ", {k: (str(r[k])[:80] if r[k] is not None else "") for k in r.keys()})

print("\nbranch_nodes 样例:")
for r in con.execute("select * from branch_nodes where script='ch6_7_1' limit 6"):
    print("  ", {k: (str(r[k])[:90] if r[k] is not None else "") for k in r.keys()})
