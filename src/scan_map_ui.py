# -*- coding: utf-8 -*-
"""重建 UI 层级：找出大地图预制体，打印整棵树与坐标。
RectTransform 的 anchoredPosition 就是地点在图上的坐标。"""
import io, os, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

ROOT = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
OUT = r"D:\LegendOfMortal Wiki\data\ui_map_tree.txt"

files = [f for f in os.listdir(ROOT) if f.endswith((".assets", ".resource"))]
lines = []
hits = []

for f in sorted(files):
    try:
        env = UnityPy.load(os.path.join(ROOT, f))
    except Exception:
        continue
    # 第一遍：收集 GameObject 名字与 Transform 关系
    go_name = {}       # path_id -> name
    go_active = {}
    rt_info = {}       # transform path_id -> dict
    children = {}      # father -> [transform]
    for obj in env.objects:
        tn = obj.type.name
        if tn == "GameObject":
            try:
                d = obj.read(check_read=False)
                go_name[obj.path_id] = d.m_Name
                go_active[obj.path_id] = getattr(d, "m_IsActive", 1)
            except Exception:
                pass
        elif tn in ("Transform", "RectTransform"):
            try:
                d = obj.read(check_read=False)
                fa = d.m_Father.path_id if getattr(d, "m_Father", None) else 0
                go = d.m_GameObject.path_id if getattr(d, "m_GameObject", None) else 0
                rec = {"file": f, "type": tn, "father": fa, "go": go,
                       "pos": tuple(round(x, 1) for x in getattr(d, "m_LocalPosition", (0, 0, 0))),
                       "scale": tuple(round(x, 3) for x in getattr(d, "m_LocalScale", (1, 1, 1))),
                       "size": None, "anch": None}
                sz = getattr(d, "m_SizeDelta", None)
                if sz is not None:
                    rec["size"] = tuple(round(x, 1) for x in sz)
                ap = getattr(d, "m_AnchoredPosition", None)
                if ap is not None:
                    rec["anch"] = tuple(round(x, 1) for x in ap)
                rt_info[obj.path_id] = rec
                children.setdefault(fa, []).append(obj.path_id)
            except Exception:
                pass

    if not go_name:
        continue

    def label(tid):
        r = rt_info.get(tid, {})
        return go_name.get(r.get("go"), "")

    # 找名字像地图的节点
    for tid, r in rt_info.items():
        nm = label(tid)
        if re.search(r"^(Map|map|World|世界|大地图)", nm or "") or re.search(r"(MapPanel|MapUI|MapCanvas|WorldMap|MapView)", nm or ""):
            hits.append((f, tid, nm))

    for f2, tid, nm in hits:
        pass

    # 有命中就整棵打印
    if any(h[0] == f for h in hits):
        roots = [h[1] for h in hits if h[0] == f]
        for root in roots:
            lines.append("=== %s  根=%s  path_id=%s ===" % (f, label(root), root))
            stack = [(root, 0)]
            seen = set()
            while stack:
                tid, depth = stack.pop()
                if tid in seen:
                    continue
                seen.add(tid)
                r = rt_info.get(tid, {})
                nm = label(tid)
                info = ""
                if r.get("anch"):
                    info += " anch=%s" % (r["anch"],)
                if r.get("size"):
                    info += " size=%s" % (r["size"],)
                if r.get("pos") and r["pos"] != (0.0, 0.0, 0.0):
                    info += " pos=%s" % (r["pos"],)
                lines.append("%s%s%s" % ("  " * depth, nm, info))
                for c in reversed(children.get(tid, [])):
                    stack.append((c, depth + 1))
            lines.append("")

open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print("命中节点 %d，输出 %s（%d 行）" % (len(hits), OUT, len(lines)))
for f, tid, nm in hits[:60]:
    print(f, tid, nm)
