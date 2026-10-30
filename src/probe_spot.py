# -*- coding: utf-8 -*-
"""抽查：招亲场景的分支表与笔记引文；若干页面的段落数。"""
import sqlite3, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

r = c.execute("select sections from pages where slug='场景/ch5_3_1'").fetchone()
secs = json.loads(r[0])
print("ch5_3_1 sections:", [s["h"] for s in secs])
for s in secs:
    if s["h"] == "分支与后果":
        print("  分支", len(s["choices"]))
        for x in s["choices"][:10]:
            print(f"   [{x['kind']}#{x['idx']}] {x['text'][:24]} cond={x['cond']} flags={x['flags']} scenes={x['scenes']}")
    if s["h"] == "出场人物":
        print("  人物", [p["name"] for p in s["people"][:8]])

print("\n笔记抽查（ch5_3_1 前 3 条）:")
for row in c.execute("select seq_from,seq_to,name,note,quote from notes where script='ch5_3_1' limit 3"):
    print("  ", row)

print("\n引文回查:")
for s_from, s_to, nm, note, quote in c.execute("select seq_from,seq_to,name,note,quote from notes where script='ch5_3_1' limit 3"):
    pool = "".join((t or "") for (t,) in c.execute(
        "select text from lines where script='ch5_3_1' and seq between ? and ?", (min(s_from,s_to), max(s_from,s_to))))
    print("  ", nm, "命中" if quote and quote.replace(" ","") in pool.replace("\n","").replace(" ","") else "未命中", "|", quote[:30])
