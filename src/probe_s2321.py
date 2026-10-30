# -*- coding: utf-8 -*-
"""查 S2321_02_01 到底是什么：看原始剧本内容与同族脚本。"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
RAW = r"D:\LegendOfMortal Wiki\data\raw"
target = None
for dirpath, _, fs in os.walk(RAW):
    for f in fs:
        if f.startswith("S2321_02_01"):
            target = os.path.join(dirpath, f)
            break
    if target:
        break
print("文件:", target)
if target:
    s = open(target, encoding="utf-8", errors="ignore").read()
    print("字节:", len(s.encode("utf-8")), "字符:", len(s))
    print("---- 全文 ----")
    print(s[:1500])

print("\n=== 同族 S2321_02_* ===")
for dirpath, _, fs in os.walk(RAW):
    for f in sorted(fs):
        if f.startswith("S2321_02"):
            p = os.path.join(dirpath, f)
            print("  %-24s %6d" % (f, os.path.getsize(p)))
