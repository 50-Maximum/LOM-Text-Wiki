# -*- coding: utf-8 -*-
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
slug, secs = c.execute("select slug,sections from pages where sections like '%分支与后果%' limit 1").fetchone()
print(slug)
for s in json.loads(secs):
    if s.get("h") == "分支与后果":
        print(json.dumps(s, ensure_ascii=False)[:600])
