# -*- coding: utf-8 -*-
"""核实：谁都没选 → 大师兄结局；以及四条支线的收尾。"""
import sqlite3, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
sf = json.load(open(r"D:\LegendOfMortal Wiki\data\scene_flags.json", encoding="utf-8"))

sc = "ch8_6_3_2"
print("== scene_flags ==", json.dumps(sf.get(sc, {}), ensure_ascii=False)[:400])
print("\n== branch_nodes ==")
for r in c.execute("select seq,kind,idx,text,cond,flags from branch_nodes where script=? order by seq,idx", (sc,)):
    print("  ", r)
print("\n== 相声段落分支 ==")
for r in c.execute("""select seq,speaker,text,branch from lines where script=? and seq between 175 and 190 order by seq""", (sc,)):
    print(f"  {r[0]:3} {r[1]}：{(r[2] or '').replace(chr(10),' ')[:80]}  <<{(r[3] or '')[:60]}>>")
