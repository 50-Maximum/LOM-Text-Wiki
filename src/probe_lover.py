# -*- coding: utf-8 -*-
"""查单值选择器：心上人、留学、门派等。"""
import os, sys, io, sqlite3, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

for f in ("心上人", "M20008", "M20011", "M50024"):
    print(f"\n===== {f}")
    rows = c.execute("""select f.script, f.seq, f.value, f.branch,
                               s.title, s.chapter
                        from flags f left join scenes s on s.script=f.script
                        where f.flag=? order by f.script, f.seq""", (f,)).fetchall()
    for r in rows:
        print(f"  {r[0]} seq{r[1]} = {r[2]}  《{r[4]}》{r[5]}")
        if r[3]:
            print(f"      分支: {r[3][:100]}")
    # 该设置点的选项
    seen = set()
    for r in rows:
        if (r[0], r[1]) in seen:
            continue
        seen.add((r[0], r[1]))
        opts = c.execute("""select idx,text,cond,flags from branch_nodes
                            where script=? and seq=? order by idx""", (r[0], r[1])).fetchall()
        for o in opts:
            print(f"      选[{o[0]}] {o[1]}  ({o[2]})  设:{o[3][:60]}")

print("\n===== 留学相关文本（meeting_option_01 / ch3_3_1_1）")
for sc in ("meeting_option_01", "ch3_3_1_1"):
    print("---", sc)
    for r in c.execute("select seq,speaker,text from lines where script=? order by seq", (sc,)):
        t = (r[2] or "").replace("\n", " ")
        if "留学" in t or "青城" in t or "崆峒" in t:
            print(f"  {r[0]:3} {r[1]}：{t[:70]}")
