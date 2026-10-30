# -*- coding: utf-8 -*-
"""复核「编号规律（推断）」238 档：看剧本名前缀与实际正文是否冲突。"""
import io, json, os, re, sqlite3, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
RAW = os.path.join(BASE, "data", "raw", "scripts")
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.row_factory = sqlite3.Row

rows = []
for r in c.execute("select slug,sections from pages where type='场景'"):
    t = ""
    for s in json.loads(r["sections"] or "[]"):
        if s.get("h") == "场景信息":
            t = s.get("html") or ""
            break
    if "（依据：编号规律（推断））" not in t:
        continue
    sc = r["slug"][len("场景/"):]
    m = re.search(r"地点：([^（。]+)（", t)
    rows.append((sc, m.group(1) if m else ""))

print("编号规律档", len(rows))
pref = collections.Counter(sc.split("_")[0] for sc, p in rows)
print("剧本前缀:", pref.most_common(12))
print("地点分布:", collections.Counter(p for sc, p in rows).most_common(10))

# 冲突检测：正文里出现「不是该地点」的强地名（其它门派/城市），且无该地点词
CITIES = ["临安", "襄阳", "眉山", "开封", "洛阳", "广州", "江陵", "成都", "崆峒", "青城", "锦香宫", "唐门", "华山", "少林"]
bad = []
for sc, p in rows:
    f = os.path.join(RAW, sc + ".txt")
    if not os.path.exists(f):
        continue
    t = open(f, encoding="utf-8", errors="ignore").read()
    short = p.split("-")[-1]
    hit_self = short in t or p in t
    other = [x for x in CITIES if x in t and x not in p]
    if not hit_self and other:
        bad.append((sc, p, other[:3], len(t)))

print("\n正文未提本地名、却提了别处地名:", len(bad))
for x in bad[:12]:
    print("   %-28s 判 %-12s 文中:%s" % (x[0], x[1], ",".join(x[2])))
