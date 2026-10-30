# -*- coding: utf-8 -*-
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for kw in ["王二壮", "雷谦", "火龙仙君", "吕翁", "毛二壮"]:
    print("==", kw)
    for r in c.execute("select type,name,title from pages where name like ?", ("%" + kw + "%",)):
        print("   ", r["type"], r["name"], "|", r["title"])
print("== 势力页 ==")
names = [r["name"] for r in c.execute("select name from pages where type='势力' order by name")]
print(len(names))
print("  ".join(names))
