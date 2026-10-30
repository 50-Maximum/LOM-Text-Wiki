# -*- coding: utf-8 -*-
"""① 梦境场景产生的事件页是否带提示；② 有没有人物简介把梦境当事实引用。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()
dream = json.load(open(B + r"\dream_scenes.json", encoding="utf-8"))

print("=== 梦境场景对应的事件页")
evs = []
for sc in dream:
    for (nm,) in c.execute("select distinct name from notes where script=? and type='事件'", (sc,)):
        if nm not in evs:
            evs.append(nm)
for nm in evs[:6]:
    row = c.execute("select sections from pages where slug=?", ("事件/" + nm,)).fetchone()
    has = bool(row and "梦境提示" in (row[0] or ""))
    print("  %-24s 提示 %s" % (nm, "有" if has else "无"))
print("  合计事件 %d" % len(evs))

print("\n=== 简介里引用梦境场景的脚注")
d = json.load(open(B + r"\intros_char.json", encoding="utf-8"))
bad = 0
for slug, v in d.items():
    for fn in (v.get("footnotes") or []):
        if fn.get("script") in dream:
            print("  %-18s 脚注%s → %s ｜ %s" % (slug, fn.get("n"), fn.get("script"), (fn.get("text") or "")[:30]))
            bad += 1
print("  合计 %d 条" % bad)
