# -*- coding: utf-8 -*-
"""从 level3 取出 MainMap 整棵 UI 树（含 RectTransform 坐标），以及 level6 的 UI_World。"""
import io, os, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

ROOT = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
OUT = r"D:\LegendOfMortal Wiki\data\map_ui_tree.json"

TARGETS = {("level3", "MainMap"), ("level6", "UI_World"), ("level2", "Map")}

for f, rootname in sorted(TARGETS):
    env = UnityPy.load(os.path.join(ROOT, f))
    go = {}
    tr = {}
    for obj in env.objects:
        tn = obj.type.name
        if tn == "GameObject":
            try:
                d = obj.read(check_read=False)
                go[obj.path_id] = d.m_Name
            except Exception:
                pass
        elif tn in ("Transform", "RectTransform"):
            try:
                d = obj.read(check_read=False)
                tr[obj.path_id] = {
                    "go": d.m_GameObject.path_id,
                    "fa": d.m_Father.path_id if getattr(d, "m_Father", None) else 0,
                    "ap": list(getattr(d, "m_AnchoredPosition", ()) or []),
                    "sd": list(getattr(d, "m_SizeDelta", ()) or []),
                    "lp": list(getattr(d, "m_LocalPosition", ()) or []),
                    "am": list(getattr(d, "m_AnchorMin", ()) or []),
                    "aM": list(getattr(d, "m_AnchorMax", ()) or []),
                    "pv": list(getattr(d, "m_Pivot", ()) or []),
                    "ch": [c.path_id for c in (getattr(d, "m_Children", None) or [])],
                    "type": tn,
                }
            except Exception:
                pass
    kids = {}
    for tid, r in tr.items():
        kids.setdefault(r["fa"], []).append(tid)

    roots = [tid for tid, r in tr.items()
             if go.get(r["go"]) == rootname and not r["fa"]]
    if not roots:
        roots = [tid for tid, r in tr.items() if go.get(r["go"]) == rootname]
    print("\n=== %s / %s : 根 %d 个 ===" % (f, rootname, len(roots)))

    nodes = []
    for root in roots:
        stack = [(root, 0, "")]
        seen = set()
        while stack:
            tid, depth, path = stack.pop()
            if tid in seen:
                continue
            seen.add(tid)
            r = tr.get(tid, {})
            nm = go.get(r.get("go"), "")
            p = path + "/" + nm if path else nm
            nodes.append({"depth": depth, "name": nm, "path": p,
                          "anch": r.get("ap"), "size": r.get("sd"),
                          "amin": r.get("am"), "amax": r.get("aM")})
            for c in reversed(r.get("ch", [])):
                stack.append((c, depth + 1, p))

    for n in nodes[:80]:
        print("%s%s  anch=%s size=%s" % ("  " * n["depth"], n["name"], n["anch"], n["size"]))
    print("... 共 %d 节点" % len(nodes))
    json.dump(nodes, open(OUT.replace(".json", "_%s_%s.json" % (f, rootname)), "w",
                          encoding="utf-8"), ensure_ascii=False, indent=0)
