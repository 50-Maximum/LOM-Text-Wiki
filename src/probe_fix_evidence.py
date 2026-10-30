# -*- coding: utf-8 -*-
"""取证：铁拳长老与小梅的关系；福建/福州 用哪个多；老和尚页 slug。"""
import io, json, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(BASE + r"\data\wiki.db")
c.row_factory = sqlite3.Row

print("== 含「铁拳」且含「小梅」的句子 ==")
n = 0
for r in c.execute("select script,seq,speaker,text from lines where text like '%铁拳%' and (text like '%小梅%' or text like '%勒索%' or text like '%长老%') limit 120"):
    t = r["text"] or ""
    if "长老" in t or "勒索" in t:
        print("   [%s#%d] %s：%s" % (r["script"], r["seq"], r["speaker"] or "-", t[:90]))
        n += 1
        if n >= 8:
            break

print("\n== 福建 / 福州 ==")
for nm in ["福建", "福州"]:
    slug = "地点/" + nm
    r = c.execute("select slug,lead,infobox from pages where slug=?", (slug,)).fetchone()
    cnt = c.execute("select count(*) from pages where cats like ?", ("%" + nm + "%",)).fetchone()[0]
    print("   %-4s 页=%s 引用页数=%d lead=%s" % (nm, bool(r), cnt, (r["lead"] or "")[:60] if r else ""))

print("\n== 老和尚 / 铁拳长老 页 ==")
for nm in ["老和尚", "铁拳长老"]:
    for r in c.execute("select slug,name from pages where type='人物' and name like ?", ("%" + nm + "%",)):
        print("   ", r["slug"], "|", r["name"])
