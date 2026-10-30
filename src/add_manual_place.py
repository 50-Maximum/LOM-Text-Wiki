# -*- coding: utf-8 -*-
"""记录人工指定的地点（第一批 001-020），并核对地点页是否存在。"""
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
P = os.path.join(BASE, "data", "place_manual.json")

BATCH = {
    "S0003_01_02": "眉山镇",
    "S0003_01_04": "眉山镇",
    "S0003_02_06_02": "眉山镇",
    "S0003_03_02": "唐门",
    "S0012_01_03": "唐门",
    "S0014_01_01": "崆峒-夺魄森林",
    "S0014_01_02": "崆峒-夺魄森林",
    "S0014_01_04": "崆峒-夺魄森林",
    "S0014_01_05_break_start_01": "崆峒-夺魄森林",
    "S0020_02_03": "唐门-后山",
    "S0020_02_03_01": "唐门-后山",
    "S0020_02_04_part_2": "唐门-后山",
    "S0021_02_01": "唐门-后山",
    "S0023_01_03_03": "唐门-后山",
    "S0028_02_02": "唐门",
    "S0032_03": "唐门-弟子房",
    "S0032_04": "唐门-弟子房",
    "S0033_02": "崆峒-夺魄森林",
    "S0105_01_01": "眉山镇",
    "S0105_01_02": "眉山镇",
}

cur = {}
if os.path.exists(P):
    cur = json.load(open(P, encoding="utf-8"))
for k, v in BATCH.items():
    cur[k] = {"place": v, "src": "人工指定"}

json.dump(cur, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print("place_manual.json 累计", len(cur), "条")

con = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
names = {r[0] for r in con.execute("select name from pages where type='地点'")}
bad = sorted({v for v in BATCH.values() if v not in names})
print("地点页不存在的:", bad if bad else "无")
