# -*- coding: utf-8 -*-
"""合并 LLM 分块台账到 ledger 表。"""
import os, json, sqlite3, collections

LED = r"D:\LegendOfMortal Wiki\data\ledger"
DB = r"D:\LegendOfMortal Wiki\data\wiki.db"
ALLOWED = {"势力", "地点", "人物", "关系", "书物", "事件"}

c = sqlite3.connect(DB)
c.execute("PRAGMA journal_mode=WAL")

def chapter_of(fn):
    base = fn[:-5]  # strip .json
    if ".part" in base:
        ch, p = base.split(".part")
        return f"{ch}·{p}"
    return base

files = sorted(f for f in os.listdir(LED) if f.endswith(".json"))
added = 0
skipped = 0
per = collections.Counter()
for fn in files:
    ch = chapter_of(fn)
    try:
        ents = json.load(open(os.path.join(LED, fn), encoding="utf-8"))
    except Exception:
        continue
    for e in ents if isinstance(ents, list) else []:
        t = (e.get("type") or "").strip()
        name = (e.get("name") or "").strip()
        if t not in ALLOWED or not name:
            skipped += 1
            continue
        note = (e.get("note") or "").strip()[:400]
        ev = (e.get("evidence") or "").strip()[:200]
        exists = c.execute("SELECT 1 FROM ledger WHERE chapter=? AND type=? AND name=?",
                           (ch, t, name)).fetchone()
        if exists:
            skipped += 1
            continue
        c.execute("INSERT INTO ledger(chapter,type,name,note,evidence) VALUES(?,?,?,?,?)",
                  (ch, t, name, note, ev))
        added += 1
        per[ch] += 1
c.commit()
print("files", len(files), "added", added, "skipped", skipped)
print("total", c.execute("SELECT COUNT(*) FROM ledger").fetchone()[0])
for ch, n in sorted(per.items()):
    print(f"  {ch} {n}")
