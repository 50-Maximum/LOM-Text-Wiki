# -*- coding: utf-8 -*-
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()
print("scene_order:", [r[1] for r in c.execute("pragma table_info(scene_order)")],
      c.execute("select count(*) from scene_order").fetchone()[0])
sg = json.load(open(B + r"\story_segments.json", encoding="utf-8"))
print("story_segments keys:", list(sg.keys()))
for k in sg:
    v = sg[k]
    print("  ", k, type(v).__name__, (len(v) if hasattr(v, "__len__") else ""))
segs = sg.get("segments") or []
if segs:
    print("段样例:", json.dumps(segs[0], ensure_ascii=False)[:300])
so = json.load(open(B + r"\scene_order.json", encoding="utf-8")) if __import__("os").path.exists(B + r"\scene_order.json") else {}
print("scene_order.json:", type(so).__name__, len(so))
