# -*- coding: utf-8 -*-
"""别名盲区审计：找出「只出现别称、不出现正名」的场景。
这类场景正是「无相祖师＝老和尚」这种漏检的来源。
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

def scenes_of(name):
    al = sorted(rev.get(name) or [], key=len, reverse=True)
    al = [x for x in al if len(x) >= 2]
    hit = collections.Counter()
    direct = set()
    for sc, tx in c.execute("select script,text from lines"):
        t = tx or ""
        if name in t:
            direct.add(sc)
            hit[sc] += 1
            continue
        for a in al:
            if a in t:
                hit[sc] += 1
                break
    return hit, direct, al

for name in ("唐铮", "唐布衣", "唐惟元", "唐中翎", "唐默铃"):
    hit, direct, al = scenes_of(name)
    blind = [(sc, n) for sc, n in hit.most_common() if sc not in direct][:8]
    print("\n=== %s ｜ 别称 %d 个：%s" % (name, len(al), "、".join(al[:10])))
    print("    只靠别称才命中的场景 %d 处，前 8：" % len(blind))
    for sc, n in blind:
        t = c.execute("select title from scenes where script=?", (sc,)).fetchone()
        print("      %-26s %3d 句 ｜ %s" % (sc, n, (t[0] if t else "")[:26]))
