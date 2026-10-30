# -*- coding: utf-8 -*-
"""看年表里没定位的 8 行，以及它们所在年月旬附近有哪些已定位事件（用于按时间窗定位）。"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
keep = json.load(open(B + r"\scene_time_ref.json", encoding="utf-8"))
tl = json.load(open(B + r"\ref_wiki\timeline.json", encoding="utf-8"))

names = [v["name"] for v in keep.values() if v.get("name")]
print("已定位事件名 %d 个" % len(names))

rows = []
for r in tl:
    if r["kind"] not in ("主线", "支线"):
        continue
    hit = [n for n in names if n and n in r["event"]]
    if not hit:
        rows.append(r)
print("\n未定位的年表行 %d 条：" % len(rows))
for r in rows:
    print("  [%s] %s | %s年%s月%s | %s" % (
        r["kind"], r.get("id", "")[:8], r.get("year"), r.get("month"),
        r.get("xun", ""), r["event"][:90]))
print("\n--- 字段样例 ---")
if rows:
    print(json.dumps(rows[0], ensure_ascii=False, indent=1)[:600])
