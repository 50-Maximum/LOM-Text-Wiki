# -*- coding: utf-8 -*-
"""重建 level 场景内指定根节点的 UI 树（名字 + anchoredPosition + sizeDelta）。"""
import io, os, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

ROOT = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
OUTDIR = r"D:\LegendOfMortal Wiki\data"


def _xy(v):
    if v is None:
        return []
    try:
        return [round(float(v[0]), 1), round(float(v[1]), 1)]
    except Exception:
        pass
    try:
        return [round(float(v.x), 1), round(float(v.y), 1)]
    except Exception:
        return []


def load_scene(f):
    env = UnityPy.load(os.path.join(ROOT, f))
    go = {}
    rt = {}
    for obj in env.objects:
        tn = obj.type.name
        if tn == "GameObject":
            go[obj.path_id] = obj.read(check_read=False).m_Name
        elif tn in ("Transform", "RectTransform"):
            d = obj.read(check_read=False)
            rec = {}
            for k, a in (("go", "m_GameObject"), ("fa", "m_Father")):
                try:
                    p = getattr(d, a, None)
                    rec[k] = p.path_id if p else 0
                except Exception:
                    rec[k] = 0
            rec["ap"] = _xy(getattr(d, "m_AnchoredPosition", None))
            rec["sd"] = _xy(getattr(d, "m_SizeDelta", None))
            rec["ch"] = []
            try:
                rec["ch"] = [c.path_id for c in (d.m_Children or [])]
            except Exception:
                pass
            rec["rt"] = tn == "RectTransform"
            rt[obj.path_id] = rec
    return go, rt


def walk(go, rt, rootname):
    roots = [tid for tid, r in rt.items() if go.get(r["go"]) == rootname]
    out = []
    for root in roots:
        stack = [(root, 0, "")]
        seen = set()
        while stack:
            tid, dep, path = stack.pop()
            if tid in seen:
                continue
            seen.add(tid)
            r = rt[tid]
            nm = go.get(r["go"], "?")
            p = (path + "/" + nm) if path else nm
            out.append({"d": dep, "n": nm, "p": p, "ap": r["ap"], "sd": r["sd"], "tid": tid})
            for c in reversed(r["ch"]):
                if c in rt:
                    stack.append((c, dep + 1, p))
    return out


for f, rootname in (("level3", "MainMap"), ("level6", "UI_World"), ("level2", "Map")):
    try:
        go, rt = load_scene(f)
    except Exception as e:
        print(f, "load fail", e)
        continue
    nodes = walk(go, rt, rootname)
    print("\n=== %s / %s : %d 节点 ===" % (f, rootname, len(nodes)))
    for n in nodes[:70]:
        print("%s%s   ap=%s sd=%s" % ("  " * n["d"], n["n"], n["ap"], n["sd"]))
    json.dump(nodes, open(os.path.join(OUTDIR, "map_tree_%s.json" % f), "w",
                          encoding="utf-8"), ensure_ascii=False, indent=0)
