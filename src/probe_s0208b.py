# -*- coding: utf-8 -*-
"""S0208_05_05 里「病根得除」出现在第几句、由谁说。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
for seq, sp, tx in c.execute("""select seq,speaker,text from lines where script='S0208_05_05'
    and (text like '%病根%' or text like '%救活%' or text like '%活转%' or text like '%李元弃%')
    order by seq"""):
    print("  %-4s %-8s %s" % (seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:80]))
