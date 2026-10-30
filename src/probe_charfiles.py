# -*- coding: utf-8 -*-
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
for n in ["chars_fix.json", "chars_prefix.json", "chars_title.json"]:
    p = os.path.join(B, n)
    print("==", n, os.path.exists(p))
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        print("   type", type(d).__name__, "keys", list(d)[:8])
        if isinstance(d, dict):
            print("   sample", json.dumps(list(d.items())[:2], ensure_ascii=False)[:200])
