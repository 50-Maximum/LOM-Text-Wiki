# -*- coding: utf-8 -*-
import io, sys, sqlite3, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
for slug in ("事件/万里鹏程挑战赵活", "事件/三人处理匪类尸身"):
    r = c.execute("select name,infobox,lead,sections from pages where slug=?", (slug,)).fetchone()
    if not r:
        print("缺", slug); continue
    print("==", r[0], "==")
    print(" 信息框:", r[1][:160])
    secs = json.loads(r[3] or "[]")
    for s in secs[:3]:
        print("  [%s]" % s.get("h"), (s.get("html") or "")[:60])
        for row in (s.get("rows") or [])[:8]:
            print("      -", row.get("note", "")[:90])
print("\n带触发条件的页数:", c.execute("select count(*) from pages where sections like '%触发条件%'").fetchone()[0])
