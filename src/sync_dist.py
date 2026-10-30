# -*- coding: utf-8 -*-
"""安全复制库到打包目录（用 sqlite backup，避免写到一半）。"""
import sqlite3, sys, io, os, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
src = os.path.join(BASE, "data", "wiki.db")
dst = os.path.join(BASE, "dist", "活侠传Wiki", "data", "wiki.db")
s = sqlite3.connect(src)
d = sqlite3.connect(dst)
with d:
    s.backup(d)
d.close(); s.close()
print("库已复制", os.path.getsize(dst))

for name in ("wiki.html",):
    a = os.path.join(BASE, "web", name)
    b = os.path.join(BASE, "dist", "活侠传Wiki", "web", name)
    shutil.copy2(a, b)
    print("已复制", name, os.path.getsize(b))
