# -*- coding: utf-8 -*-
"""扫全站：还有多少页面里残留裸的 O_ 选项键 / 判定键，各自在哪一段。"""
import io, sys, json, re, sqlite3, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db").cursor()
pat = re.compile(r"O_[A-Za-z0-9_]{4,}")
hit = collections.Counter()
samples = []
for slug, secs in c.execute("select slug,sections from pages"):
    S = secs or ""
    n = len(pat.findall(S))
    if n:
        hit[slug.split("/")[0]] += n
        if len(samples) < 6:
            for s in json.loads(S):
                for r in (s.get("rows") or []):
                    if pat.search(r.get("note") or ""):
                        samples.append((slug, s.get("h"), (r.get("note") or "")[:90]))
                        break
print("残留 O_ 键的页面（按类型）:", dict(hit))
print("合计", sum(hit.values()))
for x in samples:
    print("  ", x[0], "|", x[1], "|", x[2])
