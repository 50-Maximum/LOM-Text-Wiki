# -*- coding: utf-8 -*-
"""同姓同人审计：找出「姓+称谓」与「姓+名」的重合候选，附共现场景证据。

只列候选，不自动并；唐姓排除（用户明示）。
"""
import io, json, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row

TITLES = ("长老", "掌门", "师姐", "师兄", "师父", "师傅", "大侠", "前辈", "公子",
          "姑娘", "夫人", "帮主", "某", "某人", "老儿", "老丈", "先生", "道长", "大师")

people = []
for r in c.execute("select slug,name from pages where type='人物'"):
    nm = r["name"]
    base = nm.split("·")[-1] if "·" in nm else nm
    if not base or base.startswith("唐"):
        continue
    people.append((base, nm, r["slug"]))

by_sur = collections.defaultdict(list)
for base, nm, slug in people:
    by_sur[base[0]].append((base, nm, slug))

cands = []
for sur, lst in by_sur.items():
    if len(lst) < 2:
        continue
    names = {b for b, _, _ in lst}
    for base, nm, slug in lst:
        if len(base) < 2:
            continue
        rest = base[1:]
        if not any(t in rest for t in TITLES):
            continue
        full = [(b, n, s) for b, n, s in lst if b != base and b.startswith(sur) and len(b) > len(base) - 1]
        if len(full) == 1:
            cands.append((base, full[0][0], nm, full[0][1]))

print("同姓「称谓↔全名」候选 %d 组" % len(cands))
# 共现证据：同一场景里两人都出现
for a, b, na, nb in cands:
    scenes_a = {r[0] for r in c.execute(
        "select distinct script from lines where speaker like ? or text like ?", ("%" + a + "%", "%" + a + "%"))}
    scenes_b = {r[0] for r in c.execute(
        "select distinct script from lines where speaker like ? or text like ?", ("%" + b + "%", "%" + b + "%"))}
    both = len(scenes_a & scenes_b)
    print("   %-8s ↔ %-8s  共现场景 %-3d  (%s / %s)" % (a, b, both, na, nb))
