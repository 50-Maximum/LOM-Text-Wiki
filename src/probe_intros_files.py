# -*- coding: utf-8 -*-
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
for n in sorted(os.listdir(B)):
    if n.startswith("intro") and n.endswith(".json"):
        p = os.path.join(B, n)
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception as e:
            print(n, "读取失败", e)
            continue
        hits = [k for k in d if "毛二壮" in k or "申屠道长" in k or "申屠" in k]
        print("==", n, len(d), "命中", hits[:8])
