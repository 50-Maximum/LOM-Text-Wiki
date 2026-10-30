# -*- coding: utf-8 -*-
"""看 12 条无正文事件的最接近剧本候选，取中文字句用于命名。"""
import io, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
S = r"D:\LegendOfMortal Wiki\data\raw\scripts"
cands = ["section_01_free_02_start_001", "section_01_free_07_101", "section_01_free_07_102",
         "section_01_free_07_201", "section_01_free_07_301", "section_01_free_07_302",
         "section_01_free_07_401", "section_01_free_07_402", "section_01_free_07_403",
         "section_01_free_07_02_501", "section_01_free_07_02_502", "section_01_free_07_02_504"]
for sc in cands:
    p = os.path.join(S, sc + ".txt")
    if not os.path.exists(p):
        print("\n==", sc, "缺失")
        continue
    raw = open(p, encoding="utf-8", errors="ignore").read()
    zh = re.findall(r'"([^"]{2,})"', raw)
    zh = [x for x in zh if re.search(r"[\u4e00-\u9fff]", x) and not re.search(r"[\\/]|\.png|\.jpg", x)]
    print("\n==", sc, "字句", len(zh))
    print("   ", "".join(zh)[:160])
