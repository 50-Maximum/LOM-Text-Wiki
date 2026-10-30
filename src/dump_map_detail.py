# -*- coding: utf-8 -*-
"""打印 level2 Map 面板：每个节点的 UI 组件（Sprite 名 / 文本 / 按钮），用来认清大地图。"""
import io, os, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import UnityPy

ROOT = r"E:\Game\steamapps\common\LegendOfMortal\Mortal_Data"
env = UnityPy.load(os.path.join(ROOT, "level2"))

go_name = {}
go_comp = {}
comp_obj = {}
tr = {}
for obj in env.objects:
    tn = obj.type.name
    if tn == "GameObject":
        d = obj.read(check_read=False)
        go_name[obj.path_id] = d.m_Name
        ids = []
        for c in (d.m_Component or []):
            p = getattr(c, "component", c)
            pid = getattr(p, "m_PathID", None)
            if pid is None:
                pid = getattr(p, "path_id", None)
            if pid:
                ids.append(pid)
        go_comp[obj.path_id] = ids
    elif tn in ("Transform", "RectTransform"):
        d = obj.read(check_read=False)
        rec = {"go": d.m_GameObject.path_id if d.m_GameObject else 0}
        rec["fa"] = d.m_Father.path_id if getattr(d, "m_Father", None) else 0
        rec["ch"] = [c.path_id for c in (d.m_Children or [])]
        for k, a in (("ap", "m_AnchoredPosition"), ("sd", "m_SizeDelta")):
            v = getattr(d, a, None)
            rec[k] = []
            if v is not None:
                try:
                    rec[k] = [round(float(v.x), 1), round(float(v.y), 1)]
                except Exception:
                    pass
        tr[obj.path_id] = rec
    else:
        comp_obj[obj.path_id] = obj

# 解析组件内容
comp_info = {}
for pid, obj in comp_obj.items():
    tn = obj.type.name
    if tn == "MonoBehaviour":
        continue
    try:
        d = obj.read(check_read=False)
    except Exception:
        continue
    nm = getattr(d, "m_Name", "") or ""
    t = getattr(d, "m_Text", None)
    info = {"type": tn, "name": nm}
    if t:
        info["text"] = t
    sp = getattr(d, "m_Sprite", None)
    if sp:
        info["sprite_path_id"] = sp.path_id
    comp_info[pid] = info

# Sprite path_id -> 名字
sprite_name = {}
for pid, obj in comp_obj.items():
    if obj.type.name in ("Sprite", "Texture2D"):
        try:
            sprite_name[pid] = obj.read(check_read=False).m_Name
        except Exception:
            pass

roots = [tid for tid, r in tr.items() if go_name.get(r["go"]) == "Map"]
print("Map 根:", roots)

stack = [(roots[0], 0, "")]
seen = set()
while stack:
    tid, dep, path = stack.pop()
    if tid in seen:
        continue
    seen.add(tid)
    r = tr[tid]
    gid = r["go"]
    nm = go_name.get(gid, "?")
    tags = []
    for cid in go_comp.get(gid, []):
        ci = comp_info.get(cid)
        if not ci:
            continue
        if ci["type"] == "Image" and ci.get("sprite_path_id"):
            sp = sprite_name.get(ci["sprite_path_id"], "?")
            tags.append("img:" + sp)
        elif ci["type"] == "Text":
            tags.append("txt:" + (ci.get("text") or "").replace("\n", "\\n")[:24])
    line = "%s%s  ap=%s%s" % ("  " * dep, nm, r["ap"],
                              ("   [" + " | ".join(tags) + "]") if tags else "")
    print(line)
    for c in reversed(r["ch"]):
        if c in tr:
            stack.append((c, dep + 1, path + "/" + nm))
