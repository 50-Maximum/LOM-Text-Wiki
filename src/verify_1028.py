# -*- coding: utf-8 -*-
import io, json, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
print("== 五零指名四人 ==")
for kw in ["王二壮", "雷谦", "火龙仙君", "吕翁", "毛二壮"]:
    rows = [r for r in c.execute("select name,title from pages where type='人物' and name like ?", ("%" + kw + "%",))]
    if not rows:
        print("   %-6s 无页" % kw)
    for r in rows:
        print("   %-6s %-16s 称号=%s" % (kw, r["name"], r["title"] or "-"))
print("\n== 崆峒· 相关页 ==")
for r in c.execute("select name from pages where type='人物' and name like '崆峒%'"):
    print("   ", r["name"])
d = json.load(open(r"D:\LegendOfMortal Wiki\data\intros_char.json", encoding="utf-8"))
print("\nintros 里含崆峒的键：")
for k in d:
    if "崆峒" in k:
        print("   ", k, type(d[k]).__name__)
