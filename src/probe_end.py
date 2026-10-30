# -*- coding: utf-8 -*-
"""第8章余下场景 + 结局相关文本 + 进度。"""
import os, sys, io, sqlite3, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))

print("== 进度 ==", c.execute("select count(*) from notes").fetchone()[0], "条 /",
      c.execute("select count(distinct script) from notes").fetchone()[0], "场景")

print("\n== 第8章（ch8_2_3 之后）==")
rows = c.execute("""select script,title,line_count from scenes
                    where chapter='第8章' and line_count>=8 order by script""").fetchall()
start = False
for r in rows:
    if r[0] == "ch8_2_3":
        start = True
        continue
    if start:
        print(f"  {r[0]:30} {r[2]:4}  {r[1]}")

print("\n== 标题/文本含「结局」 ==")
t = json.load(open(os.path.join(BASE, "data", "build", "text.json"), encoding="utf-8"))
hits = [(k, v) for k, v in t.items() if "结局" in (v or "")]
print("  含结局台词", len(hits))
for k, v in hits[:15]:
    print(f"   {k}: {v[:60]}")
