# -*- coding: utf-8 -*-
"""逐个候选剧本，打印标题、选项与首尾台词，用于确认是否就是这个年表事件。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()

TARGETS = ["ch1_1", "ch1_1_break_option", "S8300_01_01",
           "S9904_01", "S8400_01", "S8400_02"]
for sc in TARGETS:
    t = c.execute("select title from scenes where script=?", (sc,)).fetchone()
    print("\n" + "=" * 70)
    print("### %s ｜ %s" % (sc, (t[0] if t else "?")[:40]))
    print("--- 选项 ---")
    for seq, opt in c.execute("select seq,options from choices where script=? order by seq", (sc,)):
        try:
            arr = json.loads(opt or "[]")
        except Exception:
            continue
        for o in arr:
            tx = (o.get("text") or o.get("label") or "").replace("\n", " ")
            if tx:
                print("   seq%-4s %s" % (seq, tx[:70]))
    print("--- 台词前 6 条 ---")
    for seq, sp, tx in c.execute(
            "select seq,speaker,text from lines where script=? order by seq limit 6", (sc,)):
        print("   %-6s %-8s %s" % (seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:64]))
