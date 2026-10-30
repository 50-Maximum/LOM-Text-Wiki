# -*- coding: utf-8 -*-
"""看薄导语类型的样例页面，判断有没有可用的原始描述。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

for t in ("天赋", "物品", "装备", "武学", "成就", "战斗效果", "战斗角色", "设施", "战技"):
    r = c.execute("""select slug,name,lead,sections from pages where type=? and hidden=0
                     and length(lead)<12 limit 2""", (t,)).fetchall()
    print("=" * 60, t)
    for slug, name, lead, secs in r:
        print(" ", slug, "|", name, "| lead:", lead)
        for s in json.loads(secs or "[]")[:3]:
            print("   段:", {k: (str(v)[:120]) for k, v in s.items()})
