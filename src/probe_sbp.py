# -*- coding: utf-8 -*-
"""看 place_of / SCENES_BY_PLACE / _SC_AT 在源码里的先后。"""
import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
s = open(r"D:\LegendOfMortal Wiki\src\build_wiki2.py", encoding="utf-8").read()
for pat in ("def place_of(", "SCENES_BY_PLACE = {}", "CH_ORDER = ", "_SC_AT = sorted"):
    ln = [s[: m.start()].count("\n") + 1 for m in re.finditer(re.escape(pat), s)]
    print("%-22s %s" % (pat, ln))
i = s.find("SCENES_BY_PLACE = {}")
print("\n建表代码：\n", s[i - 120:i + 420])
