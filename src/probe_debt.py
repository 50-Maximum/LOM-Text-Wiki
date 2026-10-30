# -*- coding: utf-8 -*-
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
for n in ["cond_lib.json", "scene_gates.json", "scene_conds.json"]:
    p = os.path.join(B, n)
    if not os.path.exists(p):
        continue
    s = open(p, encoding="utf-8").read()
    hits = [k for k in ["负债", "资产", "欠债", "上官萤"] if k in s]
    print(n, "命中关键词:", hits, "长度", len(s))
    if "负债" in s:
        d = json.load(open(p, encoding="utf-8"))
        cnt = 0
        if isinstance(d, dict):
            for k, v in d.items():
                t = json.dumps(v, ensure_ascii=False)
                if "负债" in t or "资产" in t:
                    print("   ", k, "→", t[:160])
                    cnt += 1
                    if cnt >= 6:
                        break
