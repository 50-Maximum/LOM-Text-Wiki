# -*- coding: utf-8 -*-
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
n = 0
sample = None
for r in c.execute("select name,sections from pages where type='场景'"):
    try:
        secs = json.loads(r["sections"] or "[]")
    except Exception:
        continue
    hit = [s for s in secs if s.get("h") == "分支选项"]
    if hit:
        n += 1
        if sample is None:
            sample = (r["name"], hit[0].get("rows") or [])
print("带「分支选项」栏的场景页：", n)
if sample:
    print("样例：", sample[0])
    for rw in sample[1][:5]:
        print("   -", rw.get("note", "")[:90])
