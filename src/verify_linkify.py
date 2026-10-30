# -*- coding: utf-8 -*-
"""验证：事件条目里的原文摘录，能命中多少个可跳转的词（复现前端 linkify 逻辑）。"""
import io, sys, json, re, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

# 复现 /api/nameindex
rows = list(c.execute("""select name,slug from (
    select name,slug from pages where type in ('势力','地点','书物','物品','武学','装备')
      and length(name) between 2 and 10
    union all
    select alias as name, slug from aliases where length(alias) between 2 and 10)
    order by length(name) desc"""))
MAP = {}
GENERIC = set("掌门 长老 师兄 师姐 师弟 师妹 师父 弟子 妇人 路人 乞丐 店小二 大妈 少年 "
              "官兵 掌柜 少侠 家丁 护卫 差役 客人 众人 旁白 汉子 老板 小厮 侍女 丫寰 仆役 "
              "老丈 姑娘 老汉 青年".split())
for n, s in rows:
    if n in GENERIC:
        continue
    MAP.setdefault(n, s)
names = sorted(MAP, key=len, reverse=True)
PAT = re.compile("(" + "|".join(re.escape(x) for x in names) + ")")

# 取一个事件页的原文摘录
for slug in ("事件/唐中翎传位唐布衣", "事件/赵活唐默铃后山诀别", "事件/金乌上人画皮败露"):
    r = c.execute("select sections from pages where slug=?", (slug,)).fetchone()
    if not r:
        continue
    secs = json.loads(r[0])
    print("\n=== %s" % slug)
    n_q = 0
    for s in secs:
        for row in (s.get("rows") or []):
            q = row.get("quote") or ""
            if not q:
                continue
            hits = [m for m in PAT.findall(q)]
            if hits:
                print("  「%s」" % q.replace("\n", " ")[:46])
                print("     可点：%s" % "／".join("%s→%s" % (h, MAP[h]) for h in dict.fromkeys(hits)))
                n_q += 1
            if n_q >= 4:
                break
        if n_q >= 4:
            break
    if not n_q:
        print("  （本页原文摘录里没有可点词）")
