# -*- coding: utf-8 -*-
"""看 O_Door_001_007 这类没有文案的键，文案是不是在别的命名空间。"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
TXT = json.load(open(os.path.join(B, "build", "text.json"), encoding="utf-8"))
for k in ("O_Door_001_007", "Door_001_007", "D_Door_001_007"):
    print(k, "→", repr(TXT.get(k)))
hits = [k for k in TXT if "Door_001" in k]
print("含 Door_001 的键:", hits[:10])
print("\n以 O_Door 开头的键数:", len([k for k in TXT if k.startswith("O_Door")]))
# 看 raw 里这个键怎么用
import re
p = r"D:\LegendOfMortal Wiki\data\raw\scripts"
import glob
for f in glob.glob(os.path.join(p, "*.txt")):
    s = open(f, encoding="utf-8", errors="replace").read()
    if "O_Door_001_007" in s:
        i = s.find("O_Door_001_007")
        print("\n在", os.path.basename(f), "位置", i)
        print(s[max(0, i - 300):i + 200])
        break
