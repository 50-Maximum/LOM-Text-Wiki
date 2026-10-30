# -*- coding: utf-8 -*-
"""61 条无正文事件：列出 family 基名与 raw 里同前缀的全部剧本，找准剧本。"""
import io, json, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
RAW_S = os.path.join(BASE, "data", "raw", "scripts")
rows = json.load(open(os.path.join(BASE, "data", "_map_evt_todo.json"), encoding="utf-8"))
fam = json.load(open(os.path.join(BASE, "data", "position_script_family.json"), encoding="utf-8"))
allf = {}
for fn in os.listdir(RAW_S):
    if fn.endswith(".txt"):
        allf[fn[:-4]] = fn

empty = [x for x in rows if not x["text"]]
print("空", len(empty))
for x in empty:
    code, v = x["code"], (x["value"] or "")
    bases = fam.get(code) or []
    if isinstance(bases, str):
        bases = [bases]
    cands = []
    for b in bases:
        cands += [k for k in allf if k.startswith(b)]
    chk = []
    for k in cands:
        t = open(os.path.join(RAW_S, allf[k]), encoding="utf-8", errors="ignore").read()
        n = len(re.findall(r"[\u4e00-\u9fff]", t))
        chk.append("%s(%d)" % (k, n))
    print("%-26s v=%-4s base=%-26s → %s" % (code, v, (bases[0] if bases else "-"), ", ".join(chk[:6])))
