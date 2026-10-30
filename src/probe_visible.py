# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
rows = c.execute("""select name,mentions from pages where type='人物' and hidden=0
                    order by mentions desc limit 60""").fetchall()
print("可见人物前 60：")
out = ["%s(%d)" % (n.split("·")[-1], m) for n, m in rows]
for i in range(0, len(out), 6):
    print("  " + "  ".join(out[i:i + 6]))
