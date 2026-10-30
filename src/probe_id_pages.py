# -*- coding: utf-8 -*-
"""三个名字在库里的现状：页面是否存在、别名指向谁、简介多长。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()

for n in ("无相祖师", "铁冠道人", "释明", "画中仙", "千面人魔", "无念僧", "老和尚"):
    pg = c.execute("select slug,type,name from pages where name=? or slug=?", (n, "人物/" + n)).fetchone()
    al = list(c.execute("select alias,slug from aliases where alias=?", (n,)))
    print("%-6s 页面 %-18s ｜ 别名 %s" % (n, (pg[0] if pg else "无"), al or "无"))

print("\n=== intros_char 里这些词条")
d = json.load(open(B + r"\intros_char.json", encoding="utf-8"))
for k in list(d):
    if any(x in k for x in ("无相", "铁冠", "释明", "画中仙", "千面")):
        v = d[k]
        print("  %-14s %d 字 ｜ 脚注 %d" % (k, len(v.get("text") or ""), len(v.get("footnotes") or [])))
