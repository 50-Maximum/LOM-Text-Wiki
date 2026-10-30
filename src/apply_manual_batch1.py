# -*- coding: utf-8 -*-
"""把 021-130 的人工地点写入 place_manual.json；新建缺失地点页；加别名；改 094 标题。"""
import io, json, os, re, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
D = os.path.join(BASE, "data")

# 编号 → 脚本号
num2sc = {}
for line in open(os.path.join(D, "待定地点清单_带摘要.txt"), encoding="utf-8"):
    m = re.match(r"^(\d{3}) (\S+)", line)
    if m:
        num2sc[int(m.group(1))] = m.group(2)

BATCH = []
BATCH.append(([21, 27], "唐门-炼丹房", None))
BATCH.append(([22, 23, 29], "唐门-弟子房", None))
BATCH.append(([24, 25, 26], "", "回忆"))
BATCH.append(([28, 38, 39, 42, 43] + list(range(44, 55)), "唐门-后山", None))
BATCH.append((list(range(30, 38)), "江陵", None))
BATCH.append(([40, 41, 65, 106], "唐门", None))
BATCH.append(([55], "唐门-讲经楼", None))
BATCH.append((list(range(56, 65)), "崆峒-半雨屏", None))
BATCH.append(([66], "崆峒山", None))
BATCH.append(([67], "崆峒-铁拳巷", None))
BATCH.append((list(range(68, 76)), "襄阳", None))
BATCH.append(([76, 77], "崆峒-夺魄森林", None))
BATCH.append(([78, 79, 80], "大雪山", None))
BATCH.append((list(range(81, 85)), "崆峒-飞天殿", None))
BATCH.append(([85, 87], "崆峒-铁拳巷", None))
BATCH.append(([86], "崆峒-镇魂狱", None))
BATCH.append((list(range(88, 95)), "老虎山", None))
BATCH.append(([95, 97], "崆峒-大铁铺", None))
BATCH.append(([96], "唐门-后山", None))
BATCH.append(([98], "眉山镇", None))
BATCH.append(([99, 100], "青城山", None))
BATCH.append(([101, 102], "唐门-练功场", None))
BATCH.append(([103, 104, 105], "", "梦境"))
BATCH.append(([107], "唐门-正心堂", None))
BATCH.append(([108, 109], "唐门", None))
BATCH.append((list(range(110, 125)), "唐门-后山", None))
BATCH.append(([126], "", "梦境"))
BATCH.append((list(range(127, 130)), "崆峒-无色广场赌坊", None))
BATCH.append(([130], "唐门-练功场", None))

P = os.path.join(D, "place_manual.json")
cur = json.load(open(P, encoding="utf-8")) if os.path.exists(P) else {}
cnt = 0
for nums, place, note in BATCH:
    for n in nums:
        sc = num2sc.get(n)
        if not sc:
            print("!! 编号缺脚本:", n)
            continue
        if place:
            cur[sc] = {"place": place, "src": "人工指定"}
        else:
            cur[sc] = {"note": note, "src": "人工指定"}
        cnt += 1
json.dump(cur, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("place_manual 累计", len(cur), "条（本次写入", cnt, "）")

# 新建地点
PE = json.load(open(os.path.join(D, "place_edits.json"), encoding="utf-8"))
newp = PE.setdefault("new_places", [])
have = {x.get("name") for x in newp}
add = [
    {"name": "崆峒-半雨屏", "parent": "崆峒山",
     "lead": "崆峒山半雨屏，崆峒派季试与掌派人比试的场地，四掌门、四护法于此齐聚。"},
    {"name": "崆峒-大铁铺", "parent": "崆峒山",
     "lead": "崆峒山大铁铺，山中打铁锻造的铺子，兼管刀剑火炉，伙计在此替人打造修补兵器。"},
    {"name": "崆峒-无色广场赌坊", "parent": "崆峒-无色广场",
     "lead": "无色广场上的赌坊，山中弟子与外来客聚赌之处，老千设局诈财时有耳闻。"},
]
for x in add:
    if x["name"] not in have:
        newp.append(x)
PE["new_places"] = newp

ren = PE.setdefault("rename", {})
ren.setdefault("讲经堂", "唐门-讲经楼")
ren.setdefault("练武场", "唐门-练功场")
json.dump(PE, open(os.path.join(D, "place_edits.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1, sort_keys=True)
print("地点新建/别名已写入；new_places", len(newp))

# 标题修正
T = os.path.join(D, "title_override.json")
tt = json.load(open(T, encoding="utf-8")) if os.path.exists(T) else {}
tt["S2901_04_02_break_start_01"] = "与郁竹夜谈至天明"
json.dump(tt, open(T, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("标题修正:", len(tt), "条")
