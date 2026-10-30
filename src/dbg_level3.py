# -*- coding: utf-8 -*-
import io, os, sys, traceback
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

ROOT = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
env = UnityPy.load(os.path.join(ROOT, "level3"))
go, tr, err = {}, {}, []
for obj in env.objects:
    tn = obj.type.name
    if tn == "GameObject":
        d = obj.read(check_read=False)
        go[obj.path_id] = d.m_Name
    elif tn in ("Transform", "RectTransform"):
        try:
            d = obj.read(check_read=False)
            tr[obj.path_id] = d
        except Exception as e:
            err.append((obj.path_id, repr(e)))
print("go", len(go), "tr", len(tr), "err", len(err), err[:3])
main = [pid for pid, nm in go.items() if nm == "MainMap"]
print("MainMap go ids", main)
for pid in main[:1]:
    d = go and [o for o in env.objects if o.path_id == pid][0].read(check_read=False)
    comps = []
    for c in d.m_Component:
        try:
            comps.append((c.component if hasattr(c, "component") else None,
                          type(c).__name__, getattr(c, "class_id", None)))
        except Exception as e:
            comps.append(("?", repr(e)))
    print("components", comps[:6])
# 看某个 RectTransform 的字段
sample = [t for t in tr.values()][:1]
if sample:
    s = sample[0]
    print("rt fields sample:", {k: v for k, v in list(vars(s).items())[:0]})
    print("has father?", hasattr(s, "m_Father"), getattr(s, "m_Father", None))
