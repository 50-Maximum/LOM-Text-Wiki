# -*- coding: utf-8 -*-
"""导出每场景的旗标依赖：requires（进入条件）/ sets（场景内设置）。
产出 data/scene_flags.json
"""
import json, os, re, sys, io, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = r"D:\LegendOfMortal Wiki"
CP = r"E:\Game\steamapps\common\LegendOfMortal\BepInEx\plugins\LOMAssistant\StoryReview\conditions.json"
SD = os.path.join(BASE, "data", "raw", "scripts")
d = json.load(open(CP, encoding="utf-8"))
sw, cd = d["Switches"], d["Conditions"]

RX_REQ = re.compile(r"([^\s且或]+?)\s*\(([A-Z]\w{3,})\)\s*需\s*([<>=!]+)\s*([-\d]+)")
RX_SW = re.compile(r'checkpointmanager\.(?:Switch|Condition)\(\s*"([^"]+)"')
RX_SET = re.compile(r'SetFlag\(\s*"([^"]+)"\s*,\s*([-\d.]+)')

out = {}
for fn in sorted(os.listdir(SD)):
    if not fn.endswith(".txt"):
        continue
    sid = fn[:-4]
    s = open(os.path.join(SD, fn), encoding="utf-8").read()
    reqs = []
    for m in RX_SW.finditer(s):
        cid = m.group(1)
        for rq in (sw.get(cid) or ([cd[cid]] if cid in cd else [])):
            for mm in RX_REQ.finditer(str(rq)):
                reqs.append({"flag": mm.group(2), "op": mm.group(3), "val": mm.group(4),
                             "label": mm.group(1).strip()})
    sets = collections.OrderedDict()
    for m in RX_SET.finditer(s):
        sets.setdefault(m.group(1), []).append(m.group(2))
    out[sid] = {"requires": reqs, "sets": sets}

json.dump(out, open(os.path.join(BASE, "data", "scene_flags.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)
n_req = sum(1 for v in out.values() if v["requires"])
n_set = sum(1 for v in out.values() if v["sets"])
print("场景", len(out), "有进入条件", n_req, "有设旗标", n_set)
