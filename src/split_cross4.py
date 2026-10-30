# -*- coding: utf-8 -*-
"""四个跨阶段事件：把「复述/第二次」的写成独立事件名，各自落在一个阶段。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
p = os.path.join(B, "notes_patch.json")
d = json.load(open(p, encoding="utf-8"))

RENAME = {
    ("S2321_02_05_03", "江陵事变"): "旧事重提：江陵事变",
    ("S2321_07_02", "赵活禀报大师兄行刺金人"): "旧事重提：禀报大师兄行刺",
    ("ch7_2_4", "唐门商议应对飞石帮"): "唐门商议应对飞石帮（檄书至后）",
    ("ch5_6_8_3_4", "赵活向郁竹求婚"): "郁竹答应求婚（崆峒）",
}
for (sc, old), new in RENAME.items():
    d.setdefault(sc, {}).setdefault(old, {})["name"] = new
    print("%s#%s → %s" % (sc, old, new))
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
