# -*- coding: utf-8 -*-
"""取证：点名人物在正文里的自称/他称与势力线索。"""
import io, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row

NAMES = ["赖裕廷", "赖某人", "觉空", "许胜", "老和尚", "阎尖锐", "阎掌门", "阿花",
         "叶云啾", "鞠师姐", "鞠冬音", "野利察汉", "李云弃", "赵师兄", "赵活师父"]
FAC = ["峨嵋", "峨眉", "嵩山", "崆峒", "青城", "唐门", "丐帮", "锦香", "点苍", "铁拳", "千灯", "少林"]

for nm in NAMES:
    rows = list(c.execute("select script,seq,speaker,text from lines where text like ? limit 40", ("%" + nm + "%",)))
    if not rows:
        print("\n== %s 无正文命中" % nm)
        continue
    fac = collections.Counter()
    for r in rows:
        for f in FAC:
            if f in (r["text"] or ""):
                fac[f] += 1
    print("\n== %-8s 命中 %d 句，共现势力 %s" % (nm, len(rows), fac.most_common(4)))
    for r in rows[:3]:
        print("   [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", (r["text"] or "")[:80]))
