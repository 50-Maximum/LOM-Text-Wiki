# -*- coding: utf-8 -*-
"""①练功塔 / 第三关楼主 在原文与页面里的出处 ②相关事件怎么触发 ③是否废案"""
import io, sys, json, sqlite3, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(B + r"\data\wiki.db").cursor()

print("=== 原文含「练功塔」的句子")
rows = list(c.execute("""select script,seq,speaker,text from lines
                         where text like '%练功塔%' order by script,seq"""))
print(" 命中", len(rows))
for sc, seq, sp, tx in rows[:20]:
    print("  %-24s %4d %-8s %s" % (sc, seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:100]))

print("\n=== 原文含「楼主」")
rows2 = list(c.execute("select script,seq,speaker,text from lines where text like '%楼主%'"))
print(" 命中", len(rows2))
for sc, seq, sp, tx in rows2[:12]:
    print("  %-24s %4d %-8s %s" % (sc, seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:100]))

print("\n=== 页面里提到练功塔")
for slug, typ, name in c.execute("""select slug,type,name from pages
                                    where (lead like '%练功塔%' or sections like '%练功塔%') limit 20"""):
    print("  ", typ, slug)

print("\n=== 页面里提到 第三关 / 关楼主")
for slug, typ, name in c.execute("""select slug,type,name from pages
                                    where lead like '%第三关%' or sections like '%第三关%' limit 20"""):
    print("  ", typ, slug)
