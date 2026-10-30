# -*- coding: utf-8 -*-
"""估算：地图事件条件能补到多少「目前没有触发条件」的事件页。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
pos = {(d["name"]): d for d in json.load(open(r"D:\LegendOfMortal Wiki\data\position_events.json", encoding="utf-8"))}
mp = json.load(open(r"D:\LegendOfMortal Wiki\data\position_script_map.json", encoding="utf-8"))
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
# 事件名 -> 脚本
ev_scripts = {}
for nm, sc in c.execute("select name,script from notes where type='事件'"):
    ev_scripts.setdefault(nm, set()).add(sc)
# 已带触发条件的页
has = {nm for (nm,) in c.execute("select name from pages where slug like '事件/%' and sections like '%触发条件%'")}
script2ev = {}
for nm, scs in ev_scripts.items():
    for sc in scs:
        script2ev.setdefault(sc, []).append(nm)
cover = set()
for name, sc in mp.items():
    for nm in script2ev.get(sc, []):
        if nm not in has:
            cover.add(nm)
print("已带触发条件事件页:", len(has))
print("地图条件可新补事件页:", len(cover))
print("样例:", list(cover)[:10])
