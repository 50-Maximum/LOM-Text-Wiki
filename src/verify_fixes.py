# -*- coding: utf-8 -*-
"""核验：并义后旧角色页是否消失、势力前缀是否正确、地点是否去重。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row

print("== 应已消失的旧角色页 ==")
for nm in ["叶云啾", "鞠师姐", "阿花", "阎尖锐", "阎掌门", "赵师兄", "赖某人", "赵活师父"]:
    rows = list(c.execute("select slug,name from pages where type='人物' and (name=? or name like ?)",
                          (nm, "%·" + nm)))
    print("   %-6s %s" % (nm, rows[:3] if rows else "已无独立页"))

print("\n== 并义后的目标页 ==")
for nm in ["叶云裳", "鞠冬音", "虞小梅", "无相祖师", "赵活", "赖裕廷", "夏侯兰", "野利察汉",
           "觉空大师", "许胜", "老和尚"]:
    rows = list(c.execute("select slug,name from pages where type='人物' and name like ?", ("%" + nm,)))
    print("   %-6s %s" % (nm, [r["name"] for r in rows][:3]))

print("\n== 地点 ==")
for nm in ["半雨屏", "福州", "福建", "崆峒-大铁铺", "崆峒-无色广场赌坊"]:
    rows = list(c.execute("select slug,name from pages where type='地点' and slug like ?", ("%" + nm + "%",)))
    print("   %-14s %s" % (nm, [r["slug"] for r in rows]))
