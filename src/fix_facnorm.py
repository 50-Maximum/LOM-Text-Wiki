# -*- coding: utf-8 -*-
"""校正 FAC_NORM：孤云山 → 孤云山派（此前写反了方向）。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\LegendOfMortal Wiki\src\build_wiki2.py"
s = open(p, encoding="utf-8").read()
old = '"孤云山派": "孤云山",'
new = '"孤云山": "孤云山派",'
if old in s:
    s = s.replace(old, new, 1)
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("已改正 FAC_NORM：孤云山 → 孤云山派")
else:
    print("未找到目标行，当前含孤云山的行：")
    for line in s.splitlines():
        if "孤云山" in line and "FAC" not in line:
            print("   ", line.strip())
