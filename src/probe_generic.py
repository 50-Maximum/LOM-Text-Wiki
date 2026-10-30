# -*- coding: utf-8 -*-
"""① 看「赵活唐默铃后山诀别」页为什么没有可点词；② 找应该排除的泛称人物页。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

r = c.execute("select sections from pages where slug='事件/赵活唐默铃后山诀别'").fetchone()
secs = json.loads(r[0]) if r else []
print("=== 段落结构")
for s in secs:
    rws = s.get("rows") or []
    nq = sum(1 for x in rws if x.get("quote"))
    print("  %-10s rows=%-3d 带引文 %d" % (s.get("h"), len(rws), nq))
    for x in rws[:2]:
        print("       note=%s | quote=%s" % ((x.get("note") or "")[:26], (x.get("quote") or "")[:40]))

GENERIC = ["掌门", "长老", "师兄", "师姐", "师弟", "师妹", "师父", "弟子", "妇人", "路人",
           "乞丐", "店小二", "大妈", "大汉", "老者", "少年", "女孩", "男子", "女子",
           "家丁", "护卫", "官兵", "差役", "掌柜", "老板", "客人", "众人", "旁白", "汉子"]
print("\n=== 泛称词里已建页的")
for g in GENERIC:
    row = c.execute("select slug from pages where name=? and type='人物'", (g,)).fetchone()
    if row:
        print("  %-6s → %s" % (g, row[0]))
