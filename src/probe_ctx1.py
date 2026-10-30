# -*- coding: utf-8 -*-
import io, sys, sqlite3, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
q = sys.argv[1] if len(sys.argv) > 1 else ""
n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
rows = c.execute("select script,seq,speaker,text from lines where text like ? order by id",
                 ("%" + q + "%",)).fetchall()
print("### %s 共 %d 句" % (q, len(rows)))
for sc, sq, sp, tx in rows[:n]:
    print(" [%s#%s %s] %s" % (sc, sq, sp or "-", tx[:110].replace("\n", " ")))
print("\n--- 说话人分布")
for sp, k in c.execute("""select speaker,count(*) from lines where text like ?
                          group by 1 order by 2 desc""", ("%" + q + "%",)).fetchall()[:12]:
    print("   %-10s %d" % (sp or "-", k))
