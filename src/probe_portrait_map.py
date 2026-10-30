# -*- coding: utf-8 -*-
import sqlite3, os, sys, io, re, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
files = os.listdir(r"D:\LegendOfMortal Wiki\data\portraits")
print("文件数", len(files))
print("样例：")
for f in files[:12]:
    print("   ", f)
keys = sorted({f.split("__")[0] for f in files})
print("bundle keys", len(keys))
print("、".join(keys[:60]))
print()
ids = [r[0] for r in c.execute("select id from names")]
print("names ids", len(ids), "样例", ids[:20])
hit = [i for i in ids if any(f.startswith(i.lower() + "__") for f in files)]
print("按前缀命中", len(hit), "/", len(ids))
miss = [i for i in ids if i not in hit][:15]
print("未命中样例", miss)
