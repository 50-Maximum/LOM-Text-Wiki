# -*- coding: utf-8 -*-
"""看 branch_nodes.cond 与 choices.options 里的条件字符串长什么样。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

print("=== branch_nodes.cond 样例")
for (cond,) in c.execute("""select cond from branch_nodes
                            where cond is not null and cond<>'' limit 8"""):
    print("  ", cond[:90])

print("\n=== 含 switch 的 cond 数量")
print("  ", c.execute("""select count(*) from branch_nodes where cond like '%switch%'""").fetchone()[0])
print("  ", c.execute("""select count(*) from branch_nodes where cond like '%choice%'""").fetchone()[0])

print("\n=== choices.options 里的 cond 样例")
n = 0
for (opt,) in c.execute("select options from choices limit 400"):
    try:
        arr = json.loads(opt or "[]")
    except Exception:
        continue
    for o in arr:
        cd = (o.get("cond") or "").strip()
        if cd:
            print("  ", cd[:60])
            n += 1
    if n >= 6:
        break
