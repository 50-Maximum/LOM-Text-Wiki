# -*- coding: utf-8 -*-
"""修正命名冗余、补一条缺名。"""
import io, json, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\data\map_event_names.json"
d = json.load(open(p, encoding="utf-8"))
fix = {
    "Alchemy_Work_BF_01": "操作失误遭二师兄痛骂",
    "Alchemy_Work_BS_01": "获二师兄称许",
    "Alchemy_Work_N_01": "照毒经炼制",
    "Alchemy_Work_S_01": "触类旁通出佳作",
    "Alchemy_Work_F_02": "自创配方致同门中毒",
    "Center_Work_N_01": "清扫场中顽垢",
    "Center_Work_S_01": "除草补砖洗刷",
    "Section_01_02_Start_E_06": "崆峒入门・开场特殊六",
}
d.update(fix)
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("条目", len(d))
