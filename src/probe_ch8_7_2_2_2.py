# -*- coding: utf-8 -*-
"""ch8_7_2_2_2 全场景（唐铮自陈三重身份那场），看老和尚是谁、毒倒与斩杀怎么发生。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("=== ch8_7_2_2_2 全场（前 70 句）")
for seq, sp, tx in c.execute("""select seq,speaker,text from lines
                                where script='ch8_7_2_2_2' order by seq limit 70"""):
    print("  %-4s %-8s %s" % (seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:88]))
print("\n=== 出现「无念僧」的句子")
for sc, seq, sp, tx in c.execute("""select script,seq,speaker,text from lines
                                    where text like '%无念僧%' order by script,seq limit 15"""):
    print("  %-24s %-4s %-8s %s" % (sc, seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:80]))
