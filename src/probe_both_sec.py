# -*- coding: utf-8 -*-
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
n = 0
for slug, secs in c.execute("select slug,sections from pages where sections like '%分支与后果%'"):
    S = json.loads(secs or "[]")
    h = [s.get("h") for s in S]
    if "分支选项" in h:
        print("页", slug, "｜段:", h)
        for s in S:
            if s.get("h") == "分支与后果":
                print("   分支与后果:", json.dumps(s, ensure_ascii=False)[:300])
            if s.get("h") == "分支选项":
                print("   分支选项:", json.dumps(s, ensure_ascii=False)[:200])
        n += 1
        if n >= 3:
            break
