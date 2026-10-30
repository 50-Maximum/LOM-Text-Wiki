# -*- coding: utf-8 -*-
"""看页面上还残留哪些「条件 X｜…」串，定位需要展开的位置。"""
import io, json, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
hit = collections.Counter()
samples = []
for r in c.execute("select slug,type,sections from pages where type='场景'"):
    for s in json.loads(r["sections"] or "[]"):
        blob = json.dumps(s, ensure_ascii=False)
        if "条件 " in blob and "｜" in blob:
            hit[s.get("h")] += 1
            if len(samples) < 2:
                for x in (s.get("choices") or [])[:3]:
                    if "条件 " in (x.get("cond") or ""):
                        samples.append((r["slug"], s.get("h"), x.get("cond")[:100]))
            for x in (s.get("rows") or [])[:2]:
                if "条件 " in (x.get("note") or ""):
                    samples.append((r["slug"], s.get("h"), x.get("note")[:100]))
print("栏目命中:", dict(hit))
for s in samples[:6]:
    print("  ", s)
