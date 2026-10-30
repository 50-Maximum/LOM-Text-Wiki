# -*- coding: utf-8 -*-
import io, sys, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("=== 江湖· 前缀中提及 ≥4 的：")
rows = c.execute("""select name, mentions from pages where type='人物'
                    and name like '江湖·%' and mentions>=4 order by mentions desc""").fetchall()
out = ["%s(%d)" % (n.split("·")[1], m) for n, m in rows]
for i in range(0, len(out), 6):
    print("  " + "  ".join(out[i:i + 6]))
print("\n共", len(rows), "人")
