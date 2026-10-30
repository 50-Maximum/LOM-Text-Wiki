# -*- coding: utf-8 -*-
import io, sys, json, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
cnt = collections.Counter()
pages = 0
both = 0
for slug, secs in c.execute("select slug,sections from pages where sections like '%分支与后果%'"):
    pages += 1
    S = json.loads(secs or "[]")
    h = [s.get("h") for s in S]
    if "分支选项" in h:
        both += 1
    for s in S:
        if s.get("h") == "分支与后果":
            for r in s.get("choices") or []:
                cnt[r.get("kind") or "?"] += 1
print("页面 %d，其中同时有分支选项 %d" % (pages, both))
for k, v in cnt.most_common():
    print("  %-10s %d" % (k, v))
