# -*- coding: utf-8 -*-
import io, sys, sqlite3, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
rows = c.execute("select slug,infobox from pages where slug like '地点/%'").fetchall()
parent = {}
for slug, inf in rows:
    nm = slug.split("/", 1)[1]
    d = json.loads(inf or "{}")
    parent[nm] = d.get("上级")
print("地点", len(rows), " 有上级", sum(1 for v in parent.values() if v))
tree = collections.defaultdict(list)
for k, v in parent.items():
    tree[v].append(k)
for root in [None, ""]:
    if tree.get(root):
        print("\n顶层:", sorted(tree[root])[:40])
print("\n每位上级的下辖数（前 15）:")
for k, v in sorted(((k, v) for k, v in tree.items() if k), key=lambda x: -len(x[1]))[:15]:
    print("   %-8s %2d  %s" % (k, len(v), "、".join(sorted(v)[:8])))
