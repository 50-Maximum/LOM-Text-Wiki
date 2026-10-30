# -*- coding: utf-8 -*-
"""核南溪脚注2：ch8_7_2_1 第247句前后，看是谁在说话、是否梦境。"""
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("场景标题:", c.execute("select title,place,time_from from scenes where script='ch8_7_2_1'").fetchone())
for seq, sp, tx, mode in c.execute("""select seq,speaker,text,mode from lines
                                      where script='ch8_7_2_1' and seq between 240 and 256
                                      order by seq"""):
    print(" %4d %-8s %s" % (seq, (sp or "")[:8], (tx or "").replace("\n", " ")[:110]))
