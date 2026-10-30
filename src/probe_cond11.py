# -*- coding: utf-8 -*-
import io, sys, sqlite3, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("branch_nodes 带 scenes 的行:", c.execute("select count(*) from branch_nodes where scenes<>'[]' and scenes is not null").fetchone()[0])
for r in c.execute("select script,seq,kind,text,cond,scenes from branch_nodes where scenes<>'[]' and scenes is not null limit 8"):
    print(" ", r[0], r[1], r[2], "|", (r[3] or "")[:40], "|", r[4], "->", r[5][:120])
# 反查：有多少目标脚本存在
tgt = collections.Counter()
for (s,) in c.execute("select scenes from branch_nodes where scenes is not null and scenes<>'[]'"):
    try:
        for x in json.loads(s):
            tgt[x] += 1
    except Exception:
        pass
print("\n目标数:", len(tgt), "总边:", sum(tgt.values()))
print("样例:", tgt.most_common(8))
# 事件页脚本覆盖：guide_index scripts 列
print("\nguide_index scripts 非空:", c.execute("select count(*) from guide_index where scripts is not null and scripts<>''").fetchone()[0])
print(c.execute("select name,scripts from guide_index where scripts<>'' limit 3").fetchall())
