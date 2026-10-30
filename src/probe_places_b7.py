# -*- coding: utf-8 -*-
"""本轮涉及地点的现状（名称、上级、区域、类型）。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
kids = {r[0] for r in c.execute("select slug from place_children")}

WANT = ["青城山镇", "成都", "成都府", "黄龙泉", "剑圣故居", "剑庐", "夔州巫山县衙大牢",
        "夔门", "山神龛", "白帝城遗迹", "绵阳", "绵州", "朽木桥", "兴元府", "孟章厢房",
        "陵光厢房", "插香台", "监兵厢房", "香露池", "锦香宫", "风雨山", "岳阳",
        "春雨楼", "腾云寨", "谭州腾云山", "锦绣轩", "南嵩山寺", "红岭", "新野",
        "般若院", "嵩山", "嵩山寺", "松烟阁", "金国", "夔州"]
for w in WANT:
    rows = list(c.execute("select slug,name,type,facet,facet2,infobox,hidden from pages where name=?", (w,)))
    if not rows:
        print("%-12s 无条目" % w)
        continue
    for r in rows:
        inf = json.loads(r["infobox"] or "{}")
        print("%-12s %-22s %-4s 区域=%-6s 类型=%-6s 上级=%-8s %s"
              % (w, r["slug"], r["type"], r["facet"], r["facet2"], inf.get("上级") or "-",
                 "子级" if r["slug"] in kids else "顶层"))
print("\n区域档:", [(r[0], r[1]) for r in c.execute(
    "select facet,count(*) from pages where type='地点' and hidden=0 "
    "and slug not in (select slug from place_children) group by facet order by 2 desc")])
print("类型档:", [(r[0], r[1]) for r in c.execute(
    "select facet2,count(*) from pages where type='地点' and hidden=0 "
    "and slug not in (select slug from place_children) group by facet2 order by 2 desc")])
