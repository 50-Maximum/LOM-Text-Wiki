# -*- coding: utf-8 -*-
"""复查地图事件命名结果：原生 / 剧本标题 / 地点＋结果 三档占比与抽样。"""
import io, json, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
c = sqlite3.connect(r"D:\LegendOfMortal Wiki\data\wiki.db")
c.row_factory = sqlite3.Row
rows = list(c.execute("select name,slug,infobox from pages where type='地图事件' and slug!='地图事件/索引'"))
cnt = collections.Counter()
samples = collections.defaultdict(list)
for r in rows:
    try:
        inf = json.loads(r["infobox"] or "{}")
    except Exception:
        inf = {}
    src = inf.get("名称来源") or "原生标题"
    cnt[src] += 1
    if len(samples[src]) < 6:
        samples[src].append(r["name"])
print("总 %d" % len(rows))
for k, v in cnt.most_common():
    print("\n%s: %d" % (k, v))
    for x in samples[k]:
        print("    ", x)

