# -*- coding: utf-8 -*-
"""在 MonoBehaviour 里找含「医术」「心相」等属性名的资产，打印 pathID/尺寸/上下文，用来校验引用是否正确。"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy
GAME = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
NEEDLES = ["医术", "心相", "贡献度", "银两", "名声"]
files = ("resources.assets", "sharedassets2.assets")
hits = {k: [] for k in NEEDLES}
for f in files:
    env = UnityPy.load(GAME + "\\" + f)
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            raw = o.get_raw_data()
        except Exception:
            continue
        for k in NEEDLES:
            b = k.encode("utf-8")
            if b in raw:
                i = raw.find(b)
                hits[k].append((f, o.path_id, len(raw), raw[max(0, i - 8):i + 12]))
                break
for k in NEEDLES:
    print("\n==", k, "命中", len(hits[k]))
    for f, pid, sz, ctx in hits[k][:6]:
        print("   %-20s path %-6d size %4d  ctx=%r" % (f, pid, sz, ctx))
