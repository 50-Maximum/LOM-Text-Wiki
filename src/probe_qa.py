# -*- coding: utf-8 -*-
"""内容 QA：扫可疑字符串与空段。"""
import io, sys, sqlite3, json, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()

bad_words = ["None", "undefined", "NaN", "{", "}", "&lt;", "\\n"]
hit = collections.Counter()
samples = {}
for slug, lead, inf, secs in c.execute("select slug,lead,infobox,sections from pages"):
    blob = (lead or "") + (inf or "") + (secs or "")
    for w in bad_words:
        if w in blob:
            hit[w] += 1
            samples.setdefault(w, (slug, blob[max(0, blob.find(w) - 40):blob.find(w) + 40]))
print("可疑串统计:")
for w, n in hit.most_common():
    s, ctx = samples[w]
    print("   %-10r %5d 例：%s | %s" % (w, n, s, ctx.replace("\n", " ")[:70]))

empty = 0
for slug, secs in c.execute("select slug,sections from pages"):
    for s in json.loads(secs or "[]"):
        if "rows" in s and not s["rows"]:
            empty += 1
            break
print("\n有空 rows 段的页面:", empty)

noq = c.execute("select count(*) from pages where lead like '%原文中出现 0 处%'").fetchone()[0]
print("导语写「0 处」的页面:", noq)
