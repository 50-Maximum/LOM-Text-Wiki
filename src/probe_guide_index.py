# -*- coding: utf-8 -*-
"""看攻略「全事件索引」的结构：条目怎么命名、有没有地图/设施事件。"""
import io, re, sys, os, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"D:\攻略\全事件索引.html"
t = open(p, encoding="utf-8", errors="replace").read()
body = t[t.find("<body"):]
heads = [(m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip())
         for m in re.finditer(r"<h([1-4])[^>]*>(.*?)</h\1>", body, re.S)]
print("标题数", len(heads))
for lv, h in heads[:40]:
    print("  h%s  %s" % (lv, h))
print("\n含『炼丹房/伙房/药房/外堡/后山』的标题:")
for lv, h in heads:
    if any(w in h for w in ("炼丹", "伙房", "药房", "外堡", "后山", "锻冶", "正心堂", "赌坊", "茶室", "温泉", "棋")):
        print("   h%s %s" % (lv, h))
