# -*- coding: utf-8 -*-
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
print("势力页", c.execute("select count(*) from pages where type='势力'").fetchone()[0])
for nm in ["华山派", "全真派", "孤云山派", "养龙苑", "金国", "唐门", "丐帮"]:
    r = c.execute("select infobox,sections from pages where type='势力' and name=?", (nm,)).fetchone()
    if not r:
        print("%-6s 无页" % nm)
        continue
    inf = json.loads(r["infobox"] or "{}")
    secs = json.loads(r["sections"] or "[]")
    tags = [s.get("h") for s in secs if (s.get("h") or "").startswith(("上级势力", "下辖势力", "本派成员"))]
    print("%-6s 上级=%-5s 下辖=%-4s 成员=%-4s 章节=%s" % (
        nm, inf.get("上级", "-"), inf.get("下辖", "-"), inf.get("成员", "-"), "／".join(tags) or "无"))
    for s in secs:
        if (s.get("h") or "").startswith("本派成员"):
            for rw in (s.get("rows") or [])[:6]:
                print("      ·", rw.get("note", "")[:40])
print("\n瑞笙页名：", c.execute("select name from pages where type='人物' and name like '%瑞笙'").fetchone()["name"])
print("毛二壮页：", "存在" if c.execute("select 1 from pages where type='人物' and name like '%毛二壮%'").fetchone() else "已合并")
