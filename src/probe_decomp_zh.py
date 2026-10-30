# -*- coding: utf-8 -*-
"""扫 Mortal.Combat 反编译结果：找含中文字面量的文件，判断战斗名/事件名是否存在。"""
import io, os, re, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"D:\LegendOfMortal Wiki\data\decomp\combat"
CJK = re.compile(r"[\u4e00-\u9fff]")
LIT = re.compile(r'"([^"\\\n]{2,60})"')
files = []
for dirpath, _, names in os.walk(ROOT):
    for n in names:
        if n.endswith(".cs"):
            files.append(os.path.join(dirpath, n))
print("cs 文件", len(files))

per = []
allzh = collections.Counter()
for p in files:
    t = open(p, encoding="utf-8", errors="ignore").read()
    zs = [m for m in LIT.findall(t) if CJK.search(m)]
    if zs:
        per.append((len(zs), os.path.relpath(p, ROOT), zs[:6]))
        for z in zs:
            allzh[z] += 1

per.sort(reverse=True)
print("含中文的文件", len(per))
for n, f, s in per[:12]:
    print("\n%-52s 中文串 %d" % (f, n))
    print("   例:", " | ".join(s))

print("\n中文串总数", len(allzh))
