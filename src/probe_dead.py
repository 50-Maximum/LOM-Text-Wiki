# -*- coding: utf-8 -*-
"""定位 _DEAD / pages = _pp 的位置，判断执行顺序。"""
import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
s = open(r"D:\LegendOfMortal Wiki\src\build_wiki2.py", encoding="utf-8").read()
for pat in ("_DEAD = set()", "if _DEAD:", "pages = _pp", "_DEAD.add(_so)"):
    print("===", pat)
    for m in re.finditer(re.escape(pat), s):
        print("   L%d" % (s[: m.start()].count("\n") + 1))
