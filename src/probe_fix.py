# -*- coding: utf-8 -*-
"""把别名接进检索：某人的所有称呼 → 命中台词。
用途：避免「只搜正名」漏掉关键剧情（无相祖师＝老和尚＝无念僧 就是这么漏的）。
"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()
fix = json.load(open(B + r"\chars_fix.json", encoding="utf-8"))
print("chars_fix 类型", type(fix).__name__, "数量", len(fix))
print("样例", json.dumps(list(fix.items())[:3] if isinstance(fix, dict) else fix[:3], ensure_ascii=False))
