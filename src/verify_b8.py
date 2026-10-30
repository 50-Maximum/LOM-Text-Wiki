# -*- coding: utf-8 -*-
"""第 8 批核验。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row


def get(nm):
    return c.execute("select slug,name,lead,facet,facet2,infobox,hidden from pages "
                     "where type='地点' and name=?", (nm,)).fetchone()


for nm in ("腾云山", "腾云寨", "福建", "上官交引舖", "烟花阁", "栖霞太虚观",
           "剑门关", "锦香宫", "渡口", "岳阳", "朱仙镇"):
    r = get(nm)
    if not r:
        print("%-10s 无条目" % nm)
        continue
    inf = json.loads(r["infobox"] or "{}")
    print("%-10s %-18s 区域=%-5s 类型=%-6s 上级=%-6s %s"
          % (nm, r["slug"], r["facet"], r["facet2"], inf.get("上级") or "-",
             "[hidden]" if r["hidden"] else ""))
    print("     简介：%s" % (r["lead"] or "")[:110])

print("\n=== 括号注释残留检查（应只剩临镇） ===")
for r in c.execute("select name,lead from pages where type='地点' and "
                   "(lead like '%（校订%' or lead like '%（修订者%' or lead like '%（分支%')"):
    print("  ", r["name"], "→", (r["lead"] or "")[-60:])

print("\n=== 类型档 ===")
print([(r[0], r[1]) for r in c.execute(
    "select facet2,count(*) from pages where type='地点' and hidden=0 "
    "and slug not in (select slug from place_children) group by facet2 order by 2 desc")])
print("=== 区域档 ===")
print([(r[0], r[1]) for r in c.execute(
    "select facet,count(*) from pages where type='地点' and hidden=0 "
    "and slug not in (select slug from place_children) group by facet order by 2 desc")])
