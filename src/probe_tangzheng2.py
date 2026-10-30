# -*- coding: utf-8 -*-
"""初识唐铮第二路定位：① 全库选项搜「工作/找死/毒」；② 列出 S8xxx/S9xxx 小事件场景标题。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()
titles = dict(c.execute("select script,title from scenes"))

rows = list(c.execute("select script,seq,options from choices"))
for kw in ("工作", "找死", "毒死", "下毒"):
    hit = []
    for sc, seq, opt in rows:
        if opt and kw in opt:
            try:
                arr = json.loads(opt)
            except Exception:
                continue
            for o in arr:
                tx = (o.get("text") or o.get("label") or "")
                if kw in tx:
                    hit.append((sc, seq, tx.replace("\n", " ")))
    print("\n=== 选项含「%s」：%d 条" % (kw, len(hit)))
    for sc, seq, tx in hit[:6]:
        print("   %-26s %-4s %s ｜ %s" % (sc, seq, tx[:52], (titles.get(sc) or "")[:24]))

print("\n=== S8xxx / S9xxx 小事件场景（前 40）")
n = 0
for sc, t in c.execute("""select script,title from scenes
                          where script like 'S8%' or script like 'S9%'
                          order by script"""):
    print("   %-24s %s" % (sc, (t or "")[:34]))
    n += 1
    if n >= 40:
        break
print("   …共 %d 个" % len(list(c.execute(
    "select script from scenes where script like 'S8%' or script like 'S9%'"))))
