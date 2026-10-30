# -*- coding: utf-8 -*-
"""核验第三、四轮角色修正结果。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row

print("== 应已并入的旧页 ==")
for nm in ["王公子", "辣手相公", "胡壹千", "火护法", "点苍剑圣"]:
    rows = list(c.execute("select name from pages where type='人物' and name like ?", ("%" + nm + "%",)))
    print("   %-6s %s" % (nm, [r["name"] for r in rows] or "已无独立页"))

print("\n== 目标页现状 ==")
for nm in ["王二壮", "唐铮", "裴红腊", "胡离火", "百万赵活", "白猿祖师", "象池修士",
           "翼王", "剑圣", "七星剑主", "泥教法王", "全真道兄", "金乌", "颜疆"]:
    rows = list(c.execute("select name,lead from pages where type='人物' and name like ?", ("%" + nm,)))
    for r in rows[:2]:
        print("   %-22s %s" % (r["name"], (r["lead"] or "")[:60]))
