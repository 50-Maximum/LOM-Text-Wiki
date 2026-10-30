# -*- coding: utf-8 -*-
"""确认地点名与页面名是否一致（崆峒山- vs 崆峒-）。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row

print("A. 页面里以「崆峒山-」开头的地点:", c.execute(
    "select count(*) from pages where type='地点' and name like '崆峒山-%'").fetchone()[0])
print("B. 页面里以「崆峒-」开头的地点:", c.execute(
    "select count(*) from pages where type='地点' and name like '崆峒-%'").fetchone()[0])
print("C. 地点/崆峒山-铁拳巷 是否存在:", bool(c.execute(
    "select 1 from pages where slug='地点/崆峒山-铁拳巷'").fetchone()))
print("D. 地点/崆峒-铁拳巷 是否存在:", bool(c.execute(
    "select 1 from pages where slug='地点/崆峒-铁拳巷'").fetchone()))

r = c.execute("select sections from pages where slug='场景/section_01_free_03_01'").fetchone()
for s in json.loads(r["sections"] or "[]"):
    if s.get("h") == "场景信息":
        print("E. 场景信息:", (s.get("html") or "")[:160])

r = c.execute("select sections from pages where slug='地点/崆峒-铁拳巷'").fetchone()
for s in json.loads(r["sections"] or "[]"):
    print("F. 崆峒-铁拳巷 section:", s.get("h"), len(s.get("rows") or []))
