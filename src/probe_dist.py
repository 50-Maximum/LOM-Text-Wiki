# -*- coding: utf-8 -*-
"""①打包后 ROOT 指向哪 ②dist 里 web 在哪 ③线上返回的 html 是否含最新修复"""
import io, sys, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki"

print("=== app.py 1-20 行")
for i, ln in enumerate(open(os.path.join(B, "src", "app.py"), encoding="utf-8", errors="replace")):
    if i < 20:
        print("  %2d| %s" % (i + 1, ln.rstrip()))

print("\n=== dist 下所有 wiki.html")
for p in glob.glob(os.path.join(B, "dist", "**", "wiki.html"), recursive=True):
    txt = open(p, encoding="utf-8", errors="replace").read()
    print("  %-70s %8d 字节 修复=%s" %
          (os.path.relpath(p, B), len(txt), "parseInt(qs.get('o')" in txt))

print("\n=== dist 目录结构（两级）")
for d in sorted(glob.glob(os.path.join(B, "dist", "活侠传Wiki", "*"))):
    print("  ", os.path.basename(d), "(dir)" if os.path.isdir(d) else "")
    if os.path.isdir(d) and os.path.basename(d).startswith("_"):
        for x in sorted(glob.glob(os.path.join(d, "*")))[:12]:
            print("      ", os.path.basename(x))
