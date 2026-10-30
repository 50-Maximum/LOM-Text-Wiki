# -*- coding: utf-8 -*-
"""核验大批量修正结果。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row

print("== 改名/并义后 ==")
for nm in ["司徒玄空", "完颜珣", "金乌上人", "福韫", "南溪", "温夫人", "观云客", "听海生"]:
    rows = list(c.execute("select name,title from pages where type='人物' and name like ?", ("%" + nm,)))
    print("   %-8s %s" % (nm, ["%s（%s）" % (r["name"], r["title"]) for r in rows] or "无页"))

print("\n== 应已删除 ==")
for nm in ["点苍双尊", "白猿祖师", "翼王", "苏迎香", "福韫禅师", "七星剑主"]:
    rows = list(c.execute("select name from pages where type='人物' and name like ?", ("%" + nm + "%",)))
    print("   %-8s %s" % (nm, [r["name"] for r in rows] or "已无"))

print("\n== 势力 ==")
for nm in ["谭霸刀", "牛长寿", "吕员外", "朱婶", "孟仙谣"]:
    rows = list(c.execute("select name from pages where type='人物' and name like ?", ("%" + nm,)))
    print("   %-6s %s" % (nm, [r["name"] for r in rows] or "无页"))

print("\n== 绰号抽查 ==")
for nm in ["唐铮", "唐升", "温夫人", "颜疆", "上官隼", "段智秀", "宋悲", "申屠龙", "解无尘", "丹霞子"]:
    rows = list(c.execute("select name,title from pages where type='人物' and name like ?", ("%" + nm,)))
    for r in rows[:1]:
        print("   %-18s 绰号 %s" % (r["name"], r["title"] or "-"))
