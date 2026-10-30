# -*- coding: utf-8 -*-
"""查：同一页里「分支选项」是否重复列同一场/同一次提问；以及事件页选项是否跨到无关场景。"""
import io, sys, json, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
dup = collections.Counter()
ex = []
scn_rows = collections.Counter()
for slug, secs in c.execute("select slug,sections from pages where sections like '%choice_rows%'"):
    S = json.loads(secs or "[]")
    seen = collections.Counter()
    for s in S:
        for b in (s.get("choice_rows") or []):
            key = (b.get("script"), b.get("prompt"))
            seen[key] += 1
    d = sum(v - 1 for v in seen.values() if v > 1)
    if d:
        dup[slug.split("/")[0]] += d
        if len(ex) < 5:
            ex.append((slug, d))
print("有重复选项块的页面（按类型）:", dict(dup))
for s, d in ex:
    print("  ", s, d)

# 事件页里选项块对应的场景数量分布
dist = collections.Counter()
for slug, secs in c.execute("select slug,sections from pages where type='事件' and sections like '%choice_rows%'"):
    S = json.loads(secs or "[]")
    n = sum(len(s.get("choice_rows") or []) for s in S)
    dist[n] += 1
print("\n事件页选项块数量分布:", dict(sorted(dist.items())))
