# -*- coding: utf-8 -*-
import io, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy
GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
allnames = []
for f in ("resources.assets", "sharedassets0.assets"):
    env = UnityPy.load(GAME + "\\" + f)
    for o in env.objects:
        if o.type.name == "TextAsset":
            try:
                allnames.append(o.read().m_Name)
            except Exception:
                pass
print("TextAsset 总数:", len(allnames))
kw = ("event", "schedule", "mission", "quest", "table", "data", "cond", "trigger")
hit = [n for n in allnames if any(k in n.lower() for k in kw)]
print("关键词命中:", len(hit))
for n in hit[:60]:
    print("  ", n)
