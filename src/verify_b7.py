# -*- coding: utf-8 -*-
"""第 7 批核验。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
kids = {r[0] for r in c.execute("select slug from place_children")}


def info(nm):
    r = c.execute("select slug,infobox,facet,facet2,hidden from pages where type='地点' and name=?",
                  (nm,)).fetchone()
    if not r:
        return "（无）"
    inf = json.loads(r["infobox"] or "{}")
    return "%s 区域=%s 类型=%s 上级=%s %s%s" % (
        r["slug"], r["facet"], r["facet2"], inf.get("上级") or "-",
        "子级" if r["slug"] in kids else "顶层", " [hidden]" if r["hidden"] else "")


for nm in ("青城山镇", "成都", "山神龛", "金国", "剑庐", "剑圣故居", "绵州", "绵阳",
           "腾云寨", "谭州腾云山", "锦香宫", "风雨山", "岳阳", "黄龙泉", "香露池",
           "南嵩山寺", "新野", "红岭", "松烟阁", "般若院", "春雨楼", "锦绣轩"):
    print("%-10s %s" % (nm, info(nm)))

print("\n区域档:", [(r[0], r[1]) for r in c.execute(
    "select facet,count(*) from pages where type='地点' and hidden=0 "
    "and slug not in (select slug from place_children) group by facet order by 2 desc")])
print("类型档:", [(r[0], r[1]) for r in c.execute(
    "select facet2,count(*) from pages where type='地点' and hidden=0 "
    "and slug not in (select slug from place_children) group by facet2 order by 2 desc")])
print("顶层合计:", c.execute(
    "select count(*) from pages where type='地点' and hidden=0 "
    "and slug not in (select slug from place_children)").fetchone()[0])
r = c.execute("select lead from pages where name='腾云寨'").fetchone()
print("腾云寨导语末:", (r["lead"] or "")[-70:] if r else "")
