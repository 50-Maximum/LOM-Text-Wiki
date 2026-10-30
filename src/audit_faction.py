# -*- coding: utf-8 -*-
"""1) 找青城/道士/裴相关人物页；2) 对「江湖·」人物做势力证据审计（看说话人标记）。"""
import io, sqlite3, sys, collections, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row

print("== 青城/道士/裴 相关人物页 ==")
for r in c.execute("select name,slug from pages where type='人物'"):
    if any(k in r["name"] for k in ("道士", "裴", "青城")):
        print("   %-22s %s" % (r["name"], r["slug"]))

LBL2FAC = [
    (("飞天",), "崆峒派"), (("玄功",), "崆峒派"), (("崆峒",), "崆峒派"),
    (("青城",), "青城派"), (("峨嵋", "峨眉"), "峨嵋派"), (("唐门",), "唐门"),
    (("丐帮",), "丐帮"), (("锦香",), "锦香宫"), (("点苍",), "点苍派"),
    (("铁拳",), "铁拳门"), (("少林",), "少林"), (("嵩山",), "嵩山派"),
    (("雪山",), "雪山派"), (("岭南",), "岭南派"), (("南宫",), "南宫世家"),
]

def fac_of_label(lb):
    for keys, fac in LBL2FAC:
        if any(k in (lb or "") for k in keys):
            return fac
    return ""

print("\n== 江湖· 人物势力证据（说话人标记）==")
rows = list(c.execute("select name,slug from pages where type='人物' and name like '江湖·%'"))
print("江湖前缀人物 %d 个" % len(rows))
out = []
for r in rows:
    base = r["name"].split("·")[-1]
    if len(base) < 2:
        continue
    labs = collections.Counter()
    for x in c.execute("select speaker,text from lines where text like ? limit 200", ("%" + base + "%",)):
        f = fac_of_label(x["speaker"])
        if f:
            labs[f] += 1
    tot = sum(labs.values())
    if tot >= 3:
        fac, n = labs.most_common(1)[0]
        share = n / tot
        if share >= 0.6:
            out.append((base, fac, n, tot, round(share, 2)))
out.sort(key=lambda x: -x[3])
print("候选 %d 个：" % len(out))
for base, fac, n, tot, share in out[:40]:
    print("   %-10s → %-8s %d/%d (%.0f%%)" % (base, fac, n, tot, share * 100))
