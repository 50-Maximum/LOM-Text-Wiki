# -*- coding: utf-8 -*-
"""路线结构摸底：条件标签 → 旗标字典；每场景的进入条件与设置旗标。"""
import json, os, re, sys, io, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

CP = r"E:\Game\steamapps\common\LegendOfMortal\BepInEx\plugins\LOMAssistant\StoryReview\conditions.json"
d = json.load(open(CP, encoding="utf-8"))
sw, cd = d["Switches"], d["Conditions"]

# 从条件文本里抽「名称 (旗标ID) 需…」
RX = re.compile(r"([^\s且或]+?)\s*\(([A-Z]\d{4,6}|[A-Z]{1,3}\d+)\)\s*需\s*([<>=!]+)\s*([-\d]+)")
labels = collections.defaultdict(lambda: {"label": "", "refs": 0, "reqs": []})
for sid, reqs in sw.items():
    for rq in reqs:
        for m in RX.finditer(str(rq)):
            lab, fid = m.group(1).strip(), m.group(2)
            labels[fid]["label"] = labels[fid]["label"] or lab
            labels[fid]["refs"] += 1
for cid, txt in cd.items():
    for m in RX.finditer(str(txt)):
        lab, fid = m.group(1).strip(), m.group(2)
        labels[fid]["label"] = labels[fid]["label"] or lab
        labels[fid]["refs"] += 1

print("旗标字典", len(labels))
KEY = [k for k in labels if re.search(r"攻略|路线|结局|在唐门|留学|拜入|结缘|身死|存活|掌门|传承", labels[k]["label"])]
print("路线相关旗标", len(KEY))
for k in sorted(KEY, key=lambda x: -labels[x]["refs"])[:45]:
    print(f"   {k:<8} {labels[k]['label']:<16} 引用 {labels[k]['refs']}")

# 每场景用到哪些旗标
SD = r"D:\LegendOfMortal Wiki\data\raw\scripts"
RXS = re.compile(r'checkpointmanager\.(?:Switch|Condition)\(\s*"([^"]+)"')
RXF = re.compile(r'SetFlag\(\s*"([^"]+)"\s*,\s*([-\d.]+)')
scene_flags = {}
set_flags = {}
for fn in sorted(os.listdir(SD)):
    if not fn.endswith(".txt"):
        continue
    s = open(os.path.join(SD, fn), encoding="utf-8").read()
    used = set()
    for m in RXS.finditer(s):
        cid = m.group(1)
        # 条件 id 本身也可能直接是旗标
        used.add(cid)
        for rq in (sw.get(cid) or ([cd[cid]] if cid in cd else [])):
            for mm in RX.finditer(str(rq)):
                used.add(mm.group(2))
    scene_flags[fn[:-4]] = used
    set_flags[fn[:-4]] = collections.Counter(m.group(1) for m in RXF.finditer(s))

print()
print("用到路线旗标的场景数")
for k in sorted(KEY, key=lambda x: -labels[x]["refs"])[:20]:
    cnt = sum(1 for v in scene_flags.values() if k in v)
    print(f"   {k:<8} {labels[k]['label']:<16} {cnt} 场")
