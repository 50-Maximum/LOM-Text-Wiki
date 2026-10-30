# -*- coding: utf-8 -*-
"""导出全部地点名，供区域归类。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
names = [r[0] for r in c.execute("select name from pages where type='地点' order by name")]
json.dump(names, open(r"D:\LegendOfMortal Wiki\data\_places_all.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)
print("地点 %d 个" % len(names))
print("、".join(names))
