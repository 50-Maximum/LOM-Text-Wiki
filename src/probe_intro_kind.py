# -*- coding: utf-8 -*-
"""判断简介是「人工写的剧情叙述」还是「自动模板」：看是否含元叙述词、字数。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()
intro = json.load(open(B + r"\intros_char.json", encoding="utf-8"))
cnt = dict(c.execute("select name,count(*) from notes where type='人物' group by name"))

META = ("原文", "提及", "提及次数", "出现", "资料", "记载", "本条目", "暂无", "待补")
def kind(v):
    t = v.get("intro") if isinstance(v, dict) else (v if isinstance(v, str) else "")
    t = t or ""
    if any(m in t for m in META):
        return "模板", t
    if len(t) < 60:
        return "过短", t
    return "成文", t

todo = sorted(((n, k) for n, k in cnt.items() if k >= 6), key=lambda x: -x[1])
for n, k in todo:
    v = intro.get("人物/" + n) or intro.get(n)
    if v is None:
        print("  %-10s 笔记%-4d 无简介" % (n, k)); continue
    kd, t = kind(v)
    if kd != "成文":
        print("  %-10s 笔记%-4d %s ｜ %s" % (n, k, kd, t[:36]))
