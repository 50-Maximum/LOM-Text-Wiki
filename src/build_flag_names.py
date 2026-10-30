# -*- coding: utf-8 -*-
"""从判定库文本里抽「中文名 (旗标ID)」对照表 → data/flag_names.json

判定库把旗标写成「成为崆峒掌派人 (M60015) 需=1」，可反解出 ID → 中文名。
"""
import io, json, os, re, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
SRC = os.path.join(BASE, "data", "cond_lib.json")
OUT = os.path.join(BASE, "data", "flag_names.json")

lib = json.load(open(SRC, encoding="utf-8"))
PAT = re.compile(r"([^，。；、\s()（）|>]+)\s*[（(]\s*([A-Za-z][A-Za-z0-9_]{2,})\s*[)）]")

names = {}
multi = collections.Counter()
for cid, info in lib.items():
    for a in info.get("attrs") or []:
        for nm, fid in PAT.findall(a):
            nm = nm.strip()
            if not nm or nm == fid:
                continue
            if fid in names and names[fid] != nm:
                multi[fid] += 1
                continue
            names[fid] = nm

json.dump(names, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
print("旗标中文名 %d 条（冲突 %d 个 ID）" % (len(names), len(multi)))
for k in ["M60015", "M60003", "M60006", "G11007", "M50024", "S_Beh_LT_60"]:
    print("  %-12s %s" % (k, names.get(k, "（无）")))
print("\n样例：", list(names.items())[:6])
