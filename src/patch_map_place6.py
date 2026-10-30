# -*- coding: utf-8 -*-
"""地图事件地点改用剧本场景页证据（data/map_event_place.json），并修掉前缀猜的错误映射。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(P, encoding="utf-8").read()

# 1) 载入地点证据表
anchor = "MAP_EVT_NAME = {}"
add = '''MAP_EVT_PLACE = {}
try:
    _mp = os.path.join(BASE, "data", "map_event_place.json")
    if os.path.exists(_mp):
        MAP_EVT_PLACE = json.load(open(_mp, encoding="utf-8"))
except Exception:
    MAP_EVT_PLACE = {}

MAP_EVT_NAME = {}'''
assert anchor in s and "MAP_EVT_PLACE" not in s
s = s.replace(anchor, add, 1)

# 2) place 取证据表，前缀表仅兜底
old = '''    pre = nm.split("_")[0] if nm else ""
    place = MAP_PLACE.get(pre, "")'''
new = '''    pre = nm.split("_")[0] if nm else ""
    place = MAP_EVT_PLACE.get(nm) or MAP_PLACE.get(pre, "")'''
assert old in s
s = s.replace(old, new, 1)

# 3) 兜底表按证据修正
s = s.replace('''"Alchemy": "炼丹房", "Back": "后山", "Door": "大门", "Mall": "闹市",
    "Craft": "锻冶场", "Forge": "锻冶场", "Center": "正心堂", "Kitchen": "伙房",
    "Fortress": "外堡", "Pharmacy": "药房", "Casino": "赌坊", "Teashop": "茶室",
    "Room": "男弟子房", "GirlRoom": "女弟子房", "Spa": "温泉", "Chess": "棋室",''',
              '''"Alchemy": "唐门-炼丹房", "Back": "唐门-后山", "Door": "唐门-大门",
    "Mall": "唐门-正心堂", "Craft": "唐门-锻冶场", "Forge": "唐门-锻冶场",
    "Center": "唐门-练功场", "Kitchen": "唐门-伙房", "Fortress": "唐门-外堡",
    "Pharmacy": "唐门-药房", "Casino": "崆峒-无色广场赌坊", "Teashop": "唐门-茶室",
    "Room": "唐门-男弟子房", "GirlRoom": "唐门-女弟子房", "Spa": "唐门-温泉",
    "Chess": "唐门-棋室", "Study": "唐门-讲经堂",''', 1)

open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("地点证据已接入")
