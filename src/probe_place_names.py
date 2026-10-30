# -*- coding: utf-8 -*-
"""找「市镇街道/客舟」在原文里的具体地名（眉山、渡口、客栈名…）与现有地点页。"""
import io, sys, os, json, re, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(B, "data", "wiki.db")).cursor()

print("=== 现有地点页里含 眉山/镇/渡/江/街 的")
for nm, up in c.execute("""select name, json_extract(infobox,'$.上级') from pages
                           where type='地点' and (name like '%眉山%' or name like '%镇%'
                             or name like '%渡%' or name like '%江%' or name like '%街%')
                           order by name"""):
    print("  %-18s 上级=%s" % (nm, up))

print("\n=== S0003 系列里的地名候选句")
pat = re.compile(r"(眉山|镇|县城|渡口|码头|江边|河岸|客栈|街|集|市|铺)")
for sc in ("S0003_01", "S0003_01_01", "S0003_01_03", "S0003_02_01", "S0003_02_02", "S0003_02_03"):
    print(" --", sc)
    for seq, sp, tx in c.execute("""select seq,speaker,text from lines where script=? order by seq""", (sc,)):
        if pat.search(tx or ""):
            print("   %3d %-6s %s" % (seq, (sp or "")[:6], (tx or "").replace("\n", " ")[:80]))
