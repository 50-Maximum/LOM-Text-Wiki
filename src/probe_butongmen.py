# -*- coding: utf-8 -*-
"""找「赵活自白不舍唐门」那场，并看它属于哪个剧情段、前后如何衔接。"""
import io, sys, json, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\LegendOfMortal Wiki\data"
c = sqlite3.connect(B + r"\wiki.db").cursor()
SG = json.load(open(B + r"\story_segments.json", encoding="utf-8"))
SEG = {s["id"]: s for s in SG["segments"]}
SEGOF = SG.get("seg_of") or {}

print("=== 赵活 台词含 不舍/舍不下/留恋/不想走/舍不得")
for sc, seq, tx in c.execute("""select script,seq,text from lines where speaker='赵活'
    and (text like '%不舍%' or text like '%舍不下%' or text like '%留恋%'
         or text like '%不想走%' or text like '%舍不得%')
    order by script,seq limit 16"""):
    print("  %-26s %-4s %s" % (sc, seq, (tx or "").replace("\n", " ")[:78]))

print("\n=== 这些场景所属剧情段")
seen = set()
for sc, in c.execute("""select distinct script from lines where speaker='赵活'
    and (text like '%不舍%' or text like '%舍不下%' or text like '%留恋%'
         or text like '%不想走%' or text like '%舍不得%')"""):
    if sc in seen:
        continue
    seen.add(sc)
    sid = SEGOF.get(sc) or "-"
    s = SEG.get(sid) or {}
    print("  %-26s 段 %-6s %s" % (sc, sid, (s.get("title") or "")[:26]))
    print("      段内场次:", "、".join((s.get("scenes") or [])[:6]))
