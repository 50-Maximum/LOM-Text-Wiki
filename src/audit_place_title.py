# -*- coding: utf-8 -*-
"""改用「场景标题里出现地名」作为唯一可用证据，看看覆盖多少；对比旧推断的错误。"""
import io, sys, os, json, sqlite3, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(B, "data", "wiki.db")).cursor()

WORDS = ["飞天殿", "夺魄森林", "铁拳巷", "玄功洞", "夺魄峰", "无色广场", "常风观", "上清宫",
         "青城山镇", "唐门", "锦香宫", "南宫世家", "飞石帮", "崆峒", "青城", "江陵",
         "正心堂", "炼丹房", "伙房", "锻冶场", "讲经堂", "练功场", "大门", "后山", "外堡",
         "男弟子房", "女弟子房", "义田", "茶肆", "药铺", "闹市", "温泉", "夺魄"]
WORDS.sort(key=len, reverse=True)

rows = list(c.execute("select script,title,coalesce(place,'') from scenes where coalesce(place,'')=''"))
hit = []
for sc, title, _ in rows:
    t = title or ""
    for w in WORDS:
        if w in t:
            hit.append((sc, t, w))
            break
print("空地点 %d，标题里能看出来的 %d" % (len(rows), len(hit)))
for x in hit[:15]:
    print("  %-20s %-18s → %s" % (x[0], x[1][:16], x[2]))

print("\n=== 旧推断里明显错的（舟/船/夜市/岸/客栈）")
INF = json.load(open(os.path.join(B, "data", "scene_place_infer.json"), encoding="utf-8"))
bad = 0
for sc, v in INF.items():
    txt = "".join(r[0] for r in c.execute(
        "select text from lines where script=? limit 40", (sc,)) if r[0])
    if re.search(r"(舟|船|夜市|岸边|客栈|客栈|山林|路上|途中)", txt) and v["place"] in ("唐门", "崆峒山"):
        bad += 1
        if bad <= 6:
            print("  %-22s 推成 %s" % (sc, v["place"]))
print(" 可疑推断 %d / %d" % (bad, len(INF)))
