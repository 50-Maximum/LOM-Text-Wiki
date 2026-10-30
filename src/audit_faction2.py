# -*- coding: utf-8 -*-
"""广义势力取证：人名与势力词同句共现，按占比判定，输出可审清单。"""
import io, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
FAC = [("飞天", "崆峒派"), ("玄功", "崆峒派"), ("崆峒", "崆峒派"), ("青城", "青城派"),
       ("峨嵋", "峨嵋派"), ("峨眉", "峨嵋派"), ("唐门", "唐门"), ("丐帮", "丐帮"),
       ("锦香", "锦香宫"), ("点苍", "点苍派"), ("铁拳", "铁拳门"), ("嵩山", "嵩山派"),
       ("雪山", "雪山派"), ("岭南", "岭南派"), ("南宫", "南宫世家"), ("少林", "少林"),
       ("全真", "全真派"), ("飞石", "飞石帮"), ("泥教", "泥教"), ("千灯", "千灯楼"),
       ("西夏", "西夏"), ("金国", "金国"), ("夺魄", "夺魄门")]
rows = list(c.execute("select name from pages where type='人物' and name like '江湖·%'"))
res = []
for r in rows:
    base = r["name"].split("·")[-1]
    if len(base) < 2:
        continue
    votes = collections.Counter()
    hits = 0
    for x in c.execute("select text from lines where text like ? limit 300", ("%" + base + "%",)):
        t = x["text"] or ""
        fs = []
        for k, f in FAC:
            if k in t and f not in fs:
                fs.append(f)
        if fs:
            hits += 1
            for f in fs:
                votes[f] += 1
    if votes and hits >= 2:
        fac, n = votes.most_common(1)[0]
        share = n / hits
        res.append((base, fac, n, hits, share))
res.sort(key=lambda x: (-x[4], -x[3]))
print("可判 %d 个" % len(res))
for base, fac, n, hits, share in res:
    mark = "★" if (share >= 0.7 and n >= 2) else " "
    print(" %s %-10s → %-8s %d/%d (%.0f%%)" % (mark, base, fac, n, hits, share * 100))
