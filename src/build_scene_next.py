# -*- coding: utf-8 -*-
"""解析剧本转场：if/elseif 分支里的 SetNextScript/ChangeScene，以及无条件的接续。
输出 data/scene_next.json：{script: {"next": 目标, "edges":[{target,cond}], "kind": ...}}
"""
import io, os, re, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
SRC = os.path.join(BASE, "data", "raw", "scripts")

TRANS = [
    ("SetNextScript", "next"),
    ("SetCurrentStoryScript", "story"),
    ("SetCurrentTravelScript", "travel"),
    ("SetTempScript", "temp"),
    ("ChangeScene", "scene"),
]
RE_CALL = re.compile(r'(SetNextScript|SetCurrentStoryScript|SetCurrentTravelScript|SetTempScript|ChangeScene)\s*\(\s*(?:\d+\s*,\s*)?"([^"]+)"')
RE_IF = re.compile(r'^\s*(if|elseif)\b(.*?)\bthen\b')
RE_ELSE = re.compile(r'^\s*else\s*$')
RE_LOCAL = re.compile(r'^\s*local\s+(\w+)\s*=\s*checkpointmanager\.(\w+)\("([^"]+)"\)')
RE_END = re.compile(r'^\s*end\s*$')


def parse(path):
    edges = []
    stack = []          # ["if cond", "elseif cond", ...]
    ck = {}             # 变量 → checkpoint 说明
    pending_var = None
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        for ln in f:
            m = RE_LOCAL.match(ln)
            if m:
                ck[m.group(1)] = (m.group(2), m.group(3))
                continue
            m = RE_IF.match(ln)
            if m:
                cond = m.group(2).strip()
                if m.group(1) == "elseif":
                    if stack:
                        stack[-1] = cond
                else:
                    stack.append(cond)
                continue
            if RE_ELSE.match(ln):
                if stack:
                    stack[-1] = "否则（" + (stack[-1] or "") + "）"
                continue
            if RE_END.match(ln):
                if stack:
                    stack.pop()
                continue
            m = RE_CALL.search(ln)
            if m:
                edges.append({"target": m.group(2), "cond": " / ".join(stack), "kind": m.group(1)})
    return edges, ck


def main():
    out = {}
    total = uncond = 0
    for fn in sorted(os.listdir(SRC)):
        if not fn.endswith(".txt"):
            continue
        name = fn[:-4]
        edges, ck = parse(os.path.join(SRC, fn))
        if not edges:
            continue
        total += len(edges)
        top = [e for e in edges if not e["cond"]]
        if top:
            uncond += 1
            nxt = top[-1]["target"]
        else:
            nxt = None
        out[name] = {"next": nxt, "edges": edges[:20],
                     "labels": {k: v[1] for k, v in ck.items()}}
    json.dump(out, open(os.path.join(BASE, "data", "scene_next.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("剧本 %d 个有转场，转场 %d 条；无条件接续 %d 个剧本" % (len(out), total, uncond))


main()
