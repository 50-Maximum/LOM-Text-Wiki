# -*- coding: utf-8 -*-
"""看场景页/段页的「剧情衔接」为什么空：chain_rows 的实现与实际输出。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()

for slug in ("场景/ch4_6_6", "场景/ch4_6_11", "剧情段/S797", "剧情段/S784"):
    row = c.execute("select sections from pages where slug=?", (slug,)).fetchone()
    print("\n=== %s" % slug)
    if not row:
        print("  页面不存在")
        continue
    secs = json.loads(row[0])
    for s in secs:
        hs = s.get("h")
        n = len(s.get("rows") or [])
        print("   段: %-8s rows=%d" % (hs, n))
        if hs in ("剧情衔接", "分支去路"):
            for r in (s.get("rows") or [])[:6]:
                print("      - %s %s" % (r.get("title") or r.get("note"), r.get("slug") or r.get("script") or ""))

src = open(r"D:\LegendOfMortal Wiki\src\build_wiki2.py", encoding="utf-8").read().split("\n")
for i, l in enumerate(src):
    if l.startswith("def chain_rows"):
        print("\n=== chain_rows 实现")
        for j in range(i, min(i + 26, len(src))):
            print("  " + src[j])
        break
