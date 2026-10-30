# -*- coding: utf-8 -*-
"""从全部台词里挖势力名、地名候选。"""
import sqlite3, re, collections, json

DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row

SUFFIX = "派门楼阁教帮宫庄谷山会堂盟寨岛城寺观宗世家"
# 两到六个汉字 + 后缀
pat = re.compile(r"([\u4e00-\u9fff]{2,6})(派|门|楼|阁|教|帮|宫|庄|谷|山|会|堂|盟|寨|岛|城|寺|观|宗|世家)")

STOP = set("""
这个 那个 一个 一门 这门 那门 你们 我们 他们 咱们 什么 怎么 如此 这般 那帮 这伙
大门 后山 上山 下山 山中 山上 山下 门口 门人 弟子 门派 帮派 教派 世家 世家子弟
不会 能会 开会 一会 大会 机会 学会 体会 领会 江湖  hallway
""".split())

cnt = collections.Counter()
for r in c.execute("SELECT text FROM lines WHERE text<>''"):
    t = r["text"]
    for m in pat.finditer(t):
        name = m.group(1) + m.group(2)
        if len(name) < 3:
            continue
        if m.group(1) in STOP or name in STOP:
            continue
        if any(x in m.group(1) for x in ("这", "那", "哪", "什", "怎", "我", "你", "他", "她")):
            continue
        cnt[name] += 1

# 过滤：出现至少 3 次
items = [(n, k) for n, k in cnt.items() if k >= 3]
items.sort(key=lambda x: -x[1])
print("候选数:", len(items))
for n, k in items[:80]:
    print(f"{k:5d}  {n}")

json.dump(items, open(r"D:\LegendOfMortal Wiki\data\summary\势力候选.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
