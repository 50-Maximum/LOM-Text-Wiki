# -*- coding: utf-8 -*-
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
for nm in ["华山派", "全真派", "孤云山派", "养龙苑", "蝴蝶帮"]:
    r = c.execute("select infobox,sections from pages where type='势力' and name=?", (nm,)).fetchone()
    if not r:
        print(nm, "无页")
        continue
    inf = json.loads(r["infobox"] or "{}")
    secs = json.loads(r["sections"] or "[]")
    mem = next((s for s in secs if (s.get("h") or "").startswith("本派成员")), None)
    up = next((s for s in secs if (s.get("h") or "").startswith("上级势力")), None)
    print("%-6s 上级=%-5s 成员=%-4s 上级栏=%s 成员栏=%s" % (
        nm, inf.get("上级", "-"), inf.get("成员", "-"), "有" if up else "无", "有" if mem else "无"))
    if mem:
        for rw in (mem.get("rows") or [])[:5]:
            print("      ·", rw.get("note", "")[:40])
print("\n裘志攘/周浊页名：")
for r in c.execute("select name from pages where type='人物' and (name like '%裘志攘%' or name like '%周浊%')"):
    print("   ", r["name"])
