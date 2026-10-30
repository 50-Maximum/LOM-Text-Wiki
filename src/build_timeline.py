# -*- coding: utf-8 -*-
"""场景时间线 v2：先按章节分块，再在块内用旗标依赖微调。

v1 的教训：把全库放进同一张依赖图，序章的 act2_2 被后面的旗标拖到 1404，
章节全被打散。v2 只在同一章节块内建边。
"""
import os, sys, io, re, json, sqlite3, heapq, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))
c.execute("PRAGMA journal_mode=WAL")

sf = json.load(open(os.path.join(BASE, "data", "scene_flags.json"), encoding="utf-8"))
scenes = {r[0]: {"title": r[1], "chapter": r[2], "lines": r[3], "tf": r[4], "tt": r[5]}
          for r in c.execute("select script,title,chapter,line_count,time_from,time_to from scenes")}

def bucket(ch):
    ch = (ch or "").strip()
    if ch == "序章":
        return 0
    m = re.match(r"第(\d+)章", ch)
    if m:
        return 1 + int(m.group(1))
    if ch == "支线":
        return 100
    if ch == "角色线":
        return 200
    if ch == "其他":
        return 300
    return 400

RX_ACT = re.compile(r"^act(\d+)(?:_(\d+))?(?:_(\d+))?")
RX_CH = re.compile(r"^ch(\d+)_(\d+)(?:_(\d+))?(?:_(\d+))?")
RX_S = re.compile(r"^S(\d{4})(?:_(\d{2}))?(?:_(\d{2}))?")
def natkey(s):
    m = RX_ACT.match(s)
    if m:
        return (0, [int(x) if x else 0 for x in m.groups()])
    m = RX_CH.match(s)
    if m:
        return (1, [int(x) if x else 0 for x in m.groups()])
    m = RX_S.match(s)
    if m:
        return (2, [int(x) if x else 0 for x in m.groups()])
    nums = [int(x) for x in re.findall(r"\d+", s)]
    return (3, nums)

# 旗标设置者 & 依赖（仅同块）
setters = collections.defaultdict(set)
for s, info in sf.items():
    for f, vals in (info.get("sets") or {}).items():
        for v in (vals or []):
            setters[(f, str(v))].add(s)

by_bucket = collections.defaultdict(list)
for s, info in scenes.items():
    by_bucket[bucket(info["chapter"])].append(s)

edges = collections.defaultdict(set)
indeg = collections.Counter()
for s, info in sf.items():
    b = bucket(scenes.get(s, {}).get("chapter"))
    for rq in (info.get("requires") or []):
        if not isinstance(rq, dict) or rq.get("op") != "=" or rq.get("val") is None:
            continue
        for src in setters.get((rq.get("flag"), str(rq.get("val"))), ()):
            if src == s or bucket(scenes.get(src, {}).get("chapter")) != b:
                continue
            if s not in edges[src]:
                edges[src].add(s)
                indeg[s] += 1

order = []
for b in sorted(by_bucket):
    group = by_bucket[b]
    heap = []
    for s in group:
        if indeg.get(s, 0) == 0:
            heapq.heappush(heap, (natkey(s), s))
    done, seq = set(), []
    while heap:
        _, s = heapq.heappop(heap)
        if s in done:
            continue
        done.add(s)
        seq.append(s)
        for t in edges.get(s, ()):
            indeg[t] = indeg.get(t, 0) - 1
            if indeg[t] == 0:
                heapq.heappush(heap, (natkey(t), t))
    rest = sorted((s for s in group if s not in done), key=natkey)
    order += seq + rest

print("分块", len(by_bucket), "总场景", len(order), "块内依赖边",
      sum(len(v) for v in edges.values()))

c.executescript("""drop table if exists scene_order;
create table scene_order(script TEXT PRIMARY KEY, ord INT, bucket INT, chapter TEXT,
                         time_label TEXT, title TEXT);""")
rows, tl = [], {}
for i, s in enumerate(order):
    info = scenes[s]
    label = info["tf"] or info["tt"] or ""
    if info["tf"] and info["tt"] and info["tf"] != info["tt"]:
        label = info["tf"] + "~" + info["tt"]
    rows.append((s, i, bucket(info["chapter"]), info["chapter"], label, info["title"]))
    tl[s] = i
c.executemany("insert or replace into scene_order values(?,?,?,?,?,?)", rows)
c.commit()
json.dump(tl, open(os.path.join(BASE, "data", "scene_order.json"), "w", encoding="utf-8"),
          ensure_ascii=False)

for s in order[:12]:
    print(f"  {tl[s]:4} {s:24} {scenes[s]['chapter']:6} {scenes[s]['title']}")
print("  --- 第5章开头 ---")
ch5 = [s for s in order if scenes[s]["chapter"] == "第5章"][:8]
for s in ch5:
    print(f"  {tl[s]:4} {s:24} {scenes[s]['chapter']:6} {scenes[s]['title']}")
print("  --- 末段 ---")
for s in order[-5:]:
    print(f"  {tl[s]:4} {s:24} {scenes[s]['chapter']:6} {scenes[s]['title']}")
