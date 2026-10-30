# -*- coding: utf-8 -*-
"""盘点 133 个「江湖·」人物：哪些是真实人名，哪些是通用称谓（应隐藏）。"""
import io, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
ROLE = ("掌门", "长老", "弟子", "帮主", "大哥", "老汉", "妇人", "姑娘", "公子", "前辈",
        "老人", "少年", "男子", "女子", "汉子", "头目", "掌柜", "小二", "店家", "船夫",
        "士兵", "将军", "大夫", "郎中", "和尚", "道士", "侠", "客", "某", "人")
rows = list(c.execute("select name from pages where type='人物' and name like '江湖·%'"))
real, role = [], []
for r in rows:
    b = r["name"].split("·")[-1]
    (role if (len(b) <= 4 and any(k in b for k in ROLE)) else real).append(b)
print("江湖· 共 %d：疑似通用称谓 %d，疑似真名 %d" % (len(rows), len(role), len(real)))
print("\n通用称谓:", "、".join(sorted(role)[:40]))
print("\n真名:", "、".join(sorted(real)[:80]))
