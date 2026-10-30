# -*- coding: utf-8 -*-
"""查用户举例的几个条件键的定义与用法。"""
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"E:\Game\steamapps\common\LegendOfMortal\BepInEx\plugins\LOMAssistant\StoryReview\conditions.json"
d = json.load(open(P, encoding="utf-8"))
SW, CD = d.get("Switches") or {}, d.get("Conditions") or {}
print("Switches", len(SW), "Conditions", len(CD))

for k in ["Ch_6_7_1_004", "Ch_6_7_1_005", "Ch_6_7_1_006", "Ch_6_7_1_004_001",
          "M60015_01", "M60006_01", "M60003", "S_Beh_LT_60", "S_Beh_LE_40"]:
    v = SW.get(k) or CD.get(k)
    print("%-18s %s" % (k, json.dumps(v, ensure_ascii=False) if v else "（无此键）"))

# 前缀统计
import collections
pre = collections.Counter()
for k in list(SW) + list(CD):
    pre[k.split("_")[0]] += 1
print("\n前缀分布 top10:", pre.most_common(10))

# 我们库里 cond 表长什么样
con = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
con.row_factory = sqlite3.Row
print("\ncond 表列:", [x[1] for x in con.execute("PRAGMA table_info(cond)")])
for r in con.execute("select * from cond limit 3"):
    print(dict(r))
