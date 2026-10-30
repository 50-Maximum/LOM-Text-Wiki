# -*- coding: utf-8 -*-
"""看 眉山/渡口/都江客栈/千金方医馆/岷江 现有归属与出现场景，决定子级关系。"""
import io, sys, os, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

for nm in ("眉山", "渡口", "都江客栈", "千金方医馆", "岷江", "临镇", "唐门-登山道"):
    r = c.execute("""select slug,lead,infobox from pages where type='地点' and name=?""", (nm,)).fetchone()
    if not r:
        print(nm, "→ 无地点页")
        continue
    inf = json.loads(r[2] or "{}")
    n = c.execute("select count(*) from scenes where place=?", (nm,)).fetchone()[0]
    print("%-10s 上级=%s 场景=%d | %s" % (nm, inf.get("上级"), n, (r[1] or "")[:48]))

print("\n=== 场景里 place 用到这些名的样例")
for nm in ("眉山", "渡口", "都江客栈", "千金方医馆"):
    rows = c.execute("select script,title from scenes where place=? limit 3", (nm,)).fetchall()
    for sc, t in rows:
        print("  %-10s %-18s %s" % (nm, sc, (t or "")[:16]))
