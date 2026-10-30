# -*- coding: utf-8 -*-
"""① choices 表里已存的 cond 有多少非空；② 选项是否用 = nil 动态禁用；③ 选项序号跳到别的脚本的写法。"""
import io, sys, json, sqlite3, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(os.path.join(B, "wiki.db")).cursor()

n = 0; cond_n = 0; sample = []
for sc, seq, opt in c.execute("select script,seq,options from choices"):
    try:
        arr = json.loads(opt or "[]")
    except Exception:
        continue
    for o in arr:
        n += 1
        if (o.get("cond") or "").strip():
            cond_n += 1
            if len(sample) < 5:
                sample.append((sc, seq, o.get("text"), o.get("cond")))
print("选项总数 %d，带条件 %d" % (n, cond_n))
for s in sample:
    print("   %s#%s %s ｜ 条件 %s" % s)

D = os.path.join(B, "raw", "scripts")
nil_re = re.compile(r"option_\d+\[\d+\]\s*=\s*nil")
found = 0
for f in os.listdir(D):
    if not f.endswith(".txt"):
        continue
    t = open(os.path.join(D, f), encoding="utf-8", errors="replace").read()
    if nil_re.search(t):
        found += 1
        if found <= 3:
            for line in t.split("\n"):
                if "= nil" in line and "option_" in line:
                    print("   %-28s %s" % (f, line.strip()))
print("用 = nil 禁用选项的脚本：%d 个" % found)
