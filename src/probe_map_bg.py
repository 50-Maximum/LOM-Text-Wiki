# -*- coding: utf-8 -*-
"""查 level2 Map 的 Background 贴图引用，以及 [Name] 下 001..017 的文字（TMPro / Text）。"""
import io, os, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

ROOT = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
env = UnityPy.load(os.path.join(ROOT, "level2"))

objs = {o.path_id: o for o in env.objects}
go_name, go_comp, tr = {}, {}, {}
sprite_name = {}
for o in env.objects:
    if o.type.name == "GameObject":
        d = o.read(check_read=False)
        go_name[o.path_id] = d.m_Name
        ids = []
        for c in (d.m_Component or []):
            p = getattr(c, "component", c)
            pid = getattr(p, "m_PathID", None) or getattr(p, "path_id", None)
            if pid:
                ids.append(pid)
        go_comp[o.path_id] = ids
    elif o.type.name in ("Transform", "RectTransform"):
        d = o.read(check_read=False)
        tr[o.path_id] = {
            "go": d.m_GameObject.path_id if d.m_GameObject else 0,
            "ch": [c.path_id for c in (d.m_Children or [])],
        }
    elif o.type.name in ("Sprite", "Texture2D"):
        try:
            sprite_name[o.path_id] = (o.type.name, o.read(check_read=False).m_Name)
        except Exception:
            pass

by_name = {}
for tid, r in tr.items():
    by_name.setdefault(go_name.get(r["go"], ""), []).append(tid)

print("--- Background 组件 ---")
for tid in by_name.get("Background", []) + by_name.get("Sample", []):
    gid = tr[tid]["go"]
    for cid in go_comp.get(gid, []):
        o = objs.get(cid)
        if not o:
            continue
        try:
            d = o.read(check_read=False)
        except Exception:
            continue
        sp = getattr(d, "m_Sprite", None)
        mat = getattr(d, "m_Material", None)
        extra = ""
        if sp:
            extra = " sprite=%s" % (sprite_name.get(sp.path_id, ("?", "?")),)
        if mat:
            extra += " mat_path=%s" % (mat.path_id,)
        print("  node=%-10s comp=%-12s%s" % (go_name.get(gid), o.type.name, extra))

print("\n--- 001..017 组件类型 ---")
for n in ["001", "002", "003", "010", "017"]:
    for tid in by_name.get(n, [])[:1]:
        gid = tr[tid]["go"]
        print(" node", n, "gid", gid)
        for cid in go_comp.get(gid, []):
            o = objs.get(cid)
            if not o:
                continue
            tn = o.type.name
            txt = ""
            if tn == "MonoBehaviour":
                try:
                    tt = o.read_typetree()
                    for k in ("m_text", "m_Text", "text", "m_textString"):
                        if k in tt:
                            txt = repr(tt[k])[:80]
                            break
                    if not txt:
                        txt = "keys:" + ",".join(list(tt.keys())[:8])
                except Exception as e:
                    txt = "typetree fail " + repr(e)[:60]
            elif tn == "Text":
                d = o.read(check_read=False)
                txt = repr(d.m_Text)[:80]
            print("    ", tn, txt)
