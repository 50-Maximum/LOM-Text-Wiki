# -*- coding: utf-8 -*-
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
print("势力页 %d / 人物页 %d" % (
    c.execute("select count(*) from pages where type='势力'").fetchone()[0],
    c.execute("select count(*) from pages where type='人物'").fetchone()[0]))
r = c.execute("select lead from pages where type='势力' and name='蝴蝶帮'").fetchone()
print("\n蝴蝶帮简介：", (r["lead"] or "")[:120])
print("\n毛二壮页：", "存在" if c.execute("select 1 from pages where name like '%毛二壮%'").fetchone() else "已并入王二壮")
r = c.execute("select lead from pages where type='人物' and name='丐帮·王二壮'").fetchone()
print("王二壮备注：", (r["lead"] or "")[-60:])
print("\n前缀与势力页不匹配者：")
fac = set(x["name"] for x in c.execute("select name from pages where type='势力'"))
from collections import Counter
cnt = Counter()
for x in c.execute("select name from pages where type='人物'"):
    p = x["name"].split("·")[0] if "·" in x["name"] else "（无）"
    if p not in fac:
        cnt[p] += 1
for k, v in cnt.most_common():
    print("   %-6s %d" % (k, v))
