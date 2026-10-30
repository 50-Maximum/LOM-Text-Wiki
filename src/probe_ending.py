# -*- coding: utf-8 -*-
"""找结局：脚本名 + 文本 + 末章收尾。"""
import os, sys, io, sqlite3, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"D:\LegendOfMortal Wiki"
c = sqlite3.connect(os.path.join(BASE, "data", "wiki.db"))

print("== 脚本名含 end/ending/final/true ==")
for (s,) in c.execute("select script from scenes"):
    if re.search(r"end|final|true|ed_", s, re.I):
        t = c.execute("select title,chapter,line_count from scenes where script=?", (s,)).fetchone()
        print(f"  {s:34} {t[2]:4} {t[0]}")
print("（以上为空则无命名结局场景）")

print("\n== 正文含「结局」的台词（前 20）==")
t = json.load(open(os.path.join(BASE, "data", "build", "text.json"), encoding="utf-8"))
hits = [(k, v) for k, v in t.items() if "结局" in (v or "")]
print("  共", len(hits))
for k, v in hits[:20]:
    print(f"   {k}: {v[:70]}")

print("\n== 第8章最后 15 个场景 ==")
for r in c.execute("""select script,title,line_count from scenes
                      where chapter='第8章' order by script desc limit 15"""):
    print(f"  {r[0]:30} {r[2]:4}  {r[1]}")
