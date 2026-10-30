# -*- coding: utf-8 -*-
import io, json, os, sqlite3, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
r = c.execute("select slug,name,substr(lead,1,60) as ld,mentions,facet,cats from pages where type='人物' and name like '%毛二壮%'").fetchone()
print("页:", r["slug"], r["name"], "| 提及", r["mentions"], "| 筛", r["facet"], "|", r["ld"])
print("cats", r["cats"])
cf = json.load(open(r"D:\LegendOfMortal Wiki\data\chars_fix.json", encoding="utf-8"))
print("\nchars_fix.merge 毛二壮 →", cf["merge"].get("毛二壮"))
ic = json.load(open(r"D:\LegendOfMortal Wiki\data\intros_char.json", encoding="utf-8"))
print("intros 里有毛二壮键:", [k for k in ic if "毛二壮" in k])
B = r"D:\LegendOfMortal Wiki\data"
for n in os.listdir(B):
    if n.endswith(".json"):
        s = open(os.path.join(B, n), encoding="utf-8").read()
        if "毛二壮" in s:
            print("  含毛二壮:", n, s.count("毛二壮"))
