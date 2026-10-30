# -*- coding: utf-8 -*-
"""在游戏全部资源二进制里搜地图事件代码名，看有没有配套的显示名表。"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
NEEDLES = [b"Alchemy_Work_BF_01", b"Door_02_E_01", b"Fortress_02_E_01", b"GirlRoom_Free_BF_01"]
found = {}
for root, ds, fs in os.walk(GAME):
    for f in fs:
        if not f.lower().endswith((".assets", ".resS", ".bundle", ".dat", ".json", ".txt", ".csv")):
            continue
        p = os.path.join(root, f)
        try:
            b = open(p, "rb").read()
        except Exception:
            continue
        for n in NEEDLES:
            if n in b:
                found.setdefault(n.decode(), []).append((os.path.relpath(p, GAME), len(b)))
for k, v in found.items():
    print(k, "→", v[:4])
print("\n合计命中类型:", len(found))
