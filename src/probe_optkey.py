# -*- coding: utf-8 -*-
"""①O_6_6_2_Break_01_014 的文案在哪 ②ch6_6_2_break_start_01 选项结构 ③switch_008 对应哪条判定"""
import io, sys, json, os, re, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"
KEY = "O_6_6_2_Break_01_014"

print("=== text.json 里有没有这个 key")
p = os.path.join(B, "data", "build", "text.json")
if os.path.exists(p):
    d = json.load(open(p, encoding="utf-8"))
    print(" 条数", len(d))
    for k in d:
        if KEY in k:
            print("  命中:", k, "→", str(d[k])[:120])
    hit = [k for k in d if k.startswith("O_6_6_2")]
    print(" 同场 O 键 %d 个，例：%s" % (len(hit), hit[:6]))
    for k in hit[:4]:
        print("   ", k, "→", str(d[k])[:80])

print("\n=== 原始剧本里搜这个 key")
f = os.path.join(B, "data", "raw", "scripts", "ch6_6_2_break_start_01.txt")
s = open(f, encoding="utf-8", errors="replace").read()
i = s.find(KEY)
print(" 位置", i)
print(s[max(0, i - 900):i + 700] if i >= 0 else "（未找到）")
