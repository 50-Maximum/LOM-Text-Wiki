# -*- coding: utf-8 -*-
"""地点补充：只用「场景标题里明确出现的地名」做证据，同剧情段推断已撤（会错）。

结论来自抽样：
  · 同剧情段推断把「舟中/夜市/岸边」的戏推成唐门，明显错误 → 撤掉
  · 标题里出现地名的（如「炼丹房浓烟…」「赵活闯玄功洞被囚夺魄门」）才算证据
"""
import io, sys, os, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(B, "data", "wiki.db")).cursor()

WORDS = ["飞天殿", "夺魄森林", "铁拳巷", "玄功洞", "夺魄峰", "无色广场", "常风观", "上清宫",
         "青城山镇", "唐门", "锦香宫", "南宫世家", "飞石帮", "崆峒", "青城", "江陵",
         "正心堂", "炼丹房", "伙房", "锻冶场", "讲经堂", "练功场", "男弟子房", "女弟子房",
         "义田", "茶肆", "药铺", "闹市", "温泉", "大门", "后山", "外堡", "夺魄"]
WORDS.sort(key=len, reverse=True)

ROWS = list(c.execute("select script,coalesce(title,''),coalesce(place,'') from scenes"))
out = {}
for sc, title, p in ROWS:
    if p:
        continue
    for w in WORDS:
        if w and w in title:
            out[sc] = {"place": w, "src": "场景标题", "title": title}
            break

json.dump(out, open(os.path.join(B, "data", "scene_place_infer.json"), "w", encoding="utf-8"),
          ensure_ascii=False)
print("按场景标题补地点 %d 条" % len(out))
for k, v in list(out.items())[:8]:
    print("  %-20s %-18s → %s" % (k, v["title"][:16], v["place"]))
