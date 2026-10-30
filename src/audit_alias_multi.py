# -*- coding: utf-8 -*-
"""别名盲区批量审计：给定人物，列出「只靠别称才命中」的场景，按句数排序。
用来找简介里可能漏掉的剧情（唐布衣卧云岗败北就是这么做出来的）。
"""
import io, sys, json, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()
fix = json.load(open(B + r"\chars_fix.json", encoding="utf-8"))
MERGE = fix.get("merge") or {}

rev = collections.defaultdict(set)
for a, real in MERGE.items():
    if a != real:
        rev[real].add(a)

NAMES = sys.argv[1:] or ["叶云裳", "虞小梅", "郁竹", "夏侯兰", "魏菊", "龙湘", "叶云舟", "上官萤"]


def blind(name):
    al = [x for x in (rev.get(name) or []) if len(x) >= 2]
    al.sort(key=len, reverse=True)
    direct = {sc for sc, in c.execute("select script from lines where text like ?", ("%" + name + "%",))}
    hit = collections.Counter()
    for sc, tx in c.execute("select script,text from lines"):
        t = tx or ""
        if name in t:
            continue
        for a in al:
            if a in t:
                hit[sc] += 1
                break
    return [(sc, n) for sc, n in hit.most_common() if sc not in direct]


for nm in NAMES:
    rows = blind(nm)[:6]
    print("\n=== %s（只靠别称命中的场景）" % nm)
    for sc, n in rows:
        t = c.execute("select title from scenes where script=?", (sc,)).fetchone()
        print("   %-26s %3d 句 ｜ %s" % (sc, n, (t[0] if t else "")[:30]))
    if not rows:
        print("   （无）")
