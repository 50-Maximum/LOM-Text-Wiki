# -*- coding: utf-8 -*-
import io, sys, sqlite3, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
print("pages 字段:", [r[1] for r in c.execute("PRAGMA table_info(pages)")])
print("按 slug 前缀:")
for pref, n in c.execute("select substr(slug,1,instr(slug,'/')-1) t,count(*) from pages group by t order by 2 desc"):
    print("   %-8s %d" % (pref, n))
for slug in ("地图事件/Alchemy_Work_E_01", "地图事件/Back_02_E_01"):
    r = c.execute("select name,lead,infobox,sections from pages where slug=?", (slug,)).fetchone()
    if not r:
        print("缺", slug); continue
    print("\n==", r[0])
    print(" 导语:", r[1])
    print(" 信息框:", r[2][:180])
    for s in json.loads(r[3])[:4]:
        print("  [%s]" % s.get("h"))
        for row in (s.get("rows") or [])[:4]:
            print("     -", row.get("note", "")[:80])
