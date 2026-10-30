# -*- coding: utf-8 -*-
"""收尾审查：类型、归属、命名一致性。"""
import sqlite3, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")

print("== 1. 势力实体里是否还混着地名 ==")
PLACE_SUF = ("山", "镇", "城", "村", "院", "堂", "房", "街", "店", "谷", "洞", "林",
             "寺", "观", "塔", "桥", "渡", "峡", "潭", "苑", "斋", "寨")
bad = []
for name, m in c.execute("select name,mentions from entities where type='势力'"):
    if name.endswith(PLACE_SUF) and not name.endswith(("剑阁", "嵩山寺", "锦香宫")):
        bad.append((name, m))
print("   可疑", len(bad), bad)

print()
print("== 2. 地点实体里是否混着门派 ==")
bad2 = [(n, m) for n, m in c.execute("select name,mentions from entities where type='地点'")
        if n.endswith(("派", "帮", "教", "盟", "会", "门")) and n not in ("紫阳门", "朝天门", "清波门")]
print("   可疑", len(bad2), bad2[:15])

print()
print("== 3. 人物归属抽查 ==")
for n in ("赵活", "虞小梅", "龙渊", "谭霸刀", "石公远", "刘颚", "宋悲", "瑞笙"):
    r = c.execute("select faction,faction_ev from entities where type='人物' and name=?", (n,)).fetchone()
    print(f"   {n:<6} {r[0] if r else '?'}   {((r[1] if r else '') or '')[:40]}")

print()
print("== 4. 无归属人物（应为游侠/路人/身份不明）==")
rows = [r[0] for r in c.execute(
    "select name from entities where type='人物' and (faction='' or faction is null) "
    "order by mentions desc limit 20")]
print("   ", "、".join(rows))

print()
print("== 5. 关系名是否还有旧名残留 ==")
old = ("峨嵋—", "崆峒—", "点苍—", "青城—", "全真教—", "上官家—", "广州唐门—", "泥教地狱道—")
hit = [r[0] for r in c.execute("select name from ledger where type='关系'")
       if any(r[0].startswith(o) or o in r[0] for o in old)]
print("   残留", len(hit), hit[:8])

print()
print("== 6. 统计 ==")
print("   实体", c.execute("select count(*) from entities").fetchone()[0],
      "｜台账", c.execute("select count(*) from ledger").fetchone()[0],
      "｜势力", c.execute("select count(*) from entities where type='势力'").fetchone()[0],
      "｜地点", c.execute("select count(*) from entities where type='地点'").fetchone()[0],
      "｜有归属人物", c.execute("select count(*) from entities where type='人物' and faction<>''").fetchone()[0])
print("   事件名 llm", c.execute("select count(*) from scenes where title_src='llm'").fetchone()[0])
