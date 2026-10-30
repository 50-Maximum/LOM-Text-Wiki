# -*- coding: utf-8 -*-
"""核对大地图 13 个命名点在我们的 pages 里有没有对应条目。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
con = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
con.row_factory = sqlite3.Row
names = ["唐门", "江陵", "锦香宫", "点苍山", "青城山", "大雪山", "崆峒山",
         "六道峡", "嵩山", "峨嵋山", "卧云岗", "襄阳", "全真教", "全真", "剑阁"]
for n in names:
    rows = con.execute("select slug,type,name from pages where name=?", (n,)).fetchall()
    print("%-6s -> %s" % (n, [(r["slug"], r["type"]) for r in rows]))
print("--- 世界观 / 主页类 ---")
for r in con.execute("select slug,type,name from pages where type in ('世界观','地图')"):
    print(r["slug"], "|", r["type"], "|", r["name"])
print("--- 页面总数 ---")
print(con.execute("select count(*) from pages").fetchone()[0])
