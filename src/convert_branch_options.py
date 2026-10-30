# -*- coding: utf-8 -*-
"""把子任务盘出的 552 场景/1646 选项转成站点用的 branch_options.json。"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
src = json.load(open(os.path.join(B, "research", "branch_options.json"), encoding="utf-8"))
out = {}
tot = linked = 0
for script, v in src.items():
    opts = v.get("options") or []
    if not opts:
        continue
    groups = {}
    for o in opts:
        g = int(o.get("group") or 1)
        note = (o.get("note") or "")
        prompt = ""
        if note.startswith("选项提示："):
            prompt = note.split("；")[0].replace("选项提示：", "").strip()
            note = "；".join(note.split("；")[1:]).strip()
        groups.setdefault(g, {"prompt": prompt, "options": []})
        txt = (o.get("text") or "").strip()
        if not txt:
            continue
        tot += 1
        nxt = o.get("next") or None
        if nxt:
            linked += 1
        groups[g]["options"].append({
            "order": g, "idx": o.get("order") or len(groups[g]["options"]) + 1,
            "text": txt, "cond": (o.get("cond") or "").strip(),
            "effects": [], "next": nxt, "note": note[:80],
            "key": o.get("key") or "",
        })
    gs = [groups[k] for k in sorted(groups) if groups[k]["options"]]
    if gs:
        out[script] = {"title": v.get("title") or "", "groups": gs}

json.dump(out, open(os.path.join(B, "branch_options.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("场景 %d，选项 %d，有去向 %d（%.1f%%）"
      % (len(out), tot, linked, 100.0 * linked / max(1, tot)))
